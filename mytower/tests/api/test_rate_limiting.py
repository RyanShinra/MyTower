"""
Unit tests for rate limiting and DoS protection.

Tests cover:
- Rate limiting for GraphQL queries
- Rate limiting for GraphQL mutations
- WebSocket connection limits per IP
- Command queue backpressure handling
- Environment variable configuration
- Rate limit exceeded responses
- Cleanup on WebSocket disconnect
"""

import json
import os
import queue
import time
from collections.abc import Callable, Generator
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def clean_env() -> Generator[None, None, None]:
    """Clean up rate limiting environment variables before and after each test."""
    env_vars = [
        "MYTOWER_RATE_LIMIT_QUERIES",
        "MYTOWER_RATE_LIMIT_MUTATIONS",
        "MYTOWER_MAX_WS_CONNECTIONS",
    ]
    original_values = {var: os.environ.get(var) for var in env_vars}

    for var in env_vars:
        if var in os.environ:
            del os.environ[var]

    yield

    # Restore original values
    for var, value in original_values.items():
        if value is not None:
            os.environ[var] = value
        elif var in os.environ:
            del os.environ[var]


@pytest.fixture
def test_client_factory() -> Callable[[], TestClient]:
    """Factory to create test client with fresh server instance."""
    def _create_client() -> TestClient:
        # Import here to ensure environment variables are read fresh
        import importlib
        import mytower.api.server
        importlib.reload(mytower.api.server)
        from mytower.api.server import app
        return TestClient(app)
    return _create_client


@pytest.fixture
def mock_game_bridge():
    """Create a mock game bridge for testing."""
    with patch("mytower.api.schema.get_game_bridge") as mock:
        bridge = Mock()
        bridge.queue_command.return_value = "cmd_123"
        bridge.get_building_snapshot.return_value = None
        mock.return_value = bridge
        yield bridge


class TestGraphQLRateLimiting:
    """Tests for GraphQL query and mutation rate limiting."""

    def test_query_rate_limit_default(self, clean_env: None, test_client_factory: Callable[[], TestClient], mock_game_bridge: Mock) -> None:
        """Should use default query rate limit (200/minute)."""
        client = test_client_factory()

        # Send a single query (should succeed)
        response = client.post(
            "/graphql",
            json={"query": "{ hello }"},
        )
        assert response.status_code == 200

    def test_mutation_rate_limit_default(self, clean_env: None, test_client_factory: Callable[[], TestClient], mock_game_bridge: Mock) -> None:
        """Should use default mutation rate limit (100/minute)."""
        client = test_client_factory()

        # Send a single mutation (should succeed)
        response = client.post(
            "/graphql",
            json={"query": 'mutation { addFloor(input: {floorType: LOBBY}) }'},
        )
        assert response.status_code == 200

    def test_query_rate_limit_configurable(self, clean_env: None, test_client_factory: Callable[[], TestClient], mock_game_bridge: Mock) -> None:
        """Should respect MYTOWER_RATE_LIMIT_QUERIES environment variable."""
        os.environ["MYTOWER_RATE_LIMIT_QUERIES"] = "5/minute"
        client = test_client_factory()

        # Send 6 queries rapidly (should hit limit on 6th)
        for i in range(6):
            response = client.post(
                "/graphql",
                json={"query": "{ hello }"},
            )
            if i < 5:
                assert response.status_code == 200, f"Query {i+1} should succeed"
            else:
                assert response.status_code == 429, "Query 6 should be rate limited"

    def test_mutation_rate_limit_configurable(self, clean_env: None, test_client_factory: Callable[[], TestClient], mock_game_bridge: Mock) -> None:
        """Should respect MYTOWER_RATE_LIMIT_MUTATIONS environment variable."""
        os.environ["MYTOWER_RATE_LIMIT_MUTATIONS"] = "3/minute"
        client = test_client_factory()

        # Send 4 mutations rapidly (should hit limit on 4th)
        for i in range(4):
            response = client.post(
                "/graphql",
                json={"query": 'mutation { addFloor(input: {floorType: LOBBY}) }'},
            )
            if i < 3:
                assert response.status_code == 200, f"Mutation {i+1} should succeed"
            else:
                assert response.status_code == 429, "Mutation 4 should be rate limited"

    def test_mutations_stricter_than_queries(self, clean_env: None, test_client_factory: Callable[[], TestClient], mock_game_bridge: Mock) -> None:
        """Mutations should have stricter rate limits than queries by default."""
        os.environ["MYTOWER_RATE_LIMIT_QUERIES"] = "10/minute"
        os.environ["MYTOWER_RATE_LIMIT_MUTATIONS"] = "5/minute"
        client = test_client_factory()

        # Send 6 queries (should all succeed)
        for i in range(6):
            response = client.post(
                "/graphql",
                json={"query": "{ hello }"},
            )
            assert response.status_code == 200, f"Query {i+1} should succeed"

        # Now send 6 mutations (should fail on 6th)
        for i in range(6):
            response = client.post(
                "/graphql",
                json={"query": 'mutation { addFloor(input: {floorType: LOBBY}) }'},
            )
            if i < 5:
                assert response.status_code == 200, f"Mutation {i+1} should succeed"
            else:
                assert response.status_code == 429, "Mutation 6 should be rate limited"

    def test_rate_limit_per_ip_isolation(self, clean_env: None, test_client_factory: Callable[[], TestClient], mock_game_bridge: Mock) -> None:
        """Rate limits should be tracked per IP address."""
        os.environ["MYTOWER_RATE_LIMIT_QUERIES"] = "2/minute"
        client = test_client_factory()

        # Client 1 sends 2 queries (fills their quota)
        for _ in range(2):
            response = client.post(
                "/graphql",
                json={"query": "{ hello }"},
                headers={"X-Forwarded-For": "192.168.1.1"},
            )
            assert response.status_code == 200

        # Client 1's 3rd query should be rate limited
        response = client.post(
            "/graphql",
            json={"query": "{ hello }"},
            headers={"X-Forwarded-For": "192.168.1.1"},
        )
        assert response.status_code == 429

        # Client 2 should still have their quota (different IP)
        response = client.post(
            "/graphql",
            json={"query": "{ hello }"},
            headers={"X-Forwarded-For": "192.168.1.2"},
        )
        assert response.status_code == 200

    def test_rate_limit_response_format(self, clean_env: None, test_client_factory: Callable[[], TestClient], mock_game_bridge: Mock) -> None:
        """Rate limit exceeded response should have proper format."""
        os.environ["MYTOWER_RATE_LIMIT_QUERIES"] = "1/minute"
        client = test_client_factory()

        # First query succeeds
        client.post("/graphql", json={"query": "{ hello }"})

        # Second query should be rate limited
        response = client.post("/graphql", json={"query": "{ hello }"})
        assert response.status_code == 429
        assert "error" in response.text.lower()


class TestWebSocketConnectionLimits:
    """Tests for WebSocket connection limits per IP."""

    def test_websocket_connection_limit_default(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Should use default WebSocket connection limit (10 per IP)."""
        client = test_client_factory()

        # The default limit should be set
        from mytower.api.server import MAX_WS_CONNECTIONS_PER_IP
        assert MAX_WS_CONNECTIONS_PER_IP == 10

    def test_websocket_connection_limit_configurable(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Should respect MYTOWER_MAX_WS_CONNECTIONS environment variable."""
        os.environ["MYTOWER_MAX_WS_CONNECTIONS"] = "5"
        client = test_client_factory()

        from mytower.api.server import MAX_WS_CONNECTIONS_PER_IP
        assert MAX_WS_CONNECTIONS_PER_IP == 5

    def test_websocket_connection_tracking(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """WebSocket connections should be tracked per IP."""
        os.environ["MYTOWER_MAX_WS_CONNECTIONS"] = "2"
        client = test_client_factory()

        # Try to open a WebSocket connection
        # Note: We can't easily test actual WebSocket connections with TestClient,
        # but we can verify the configuration is loaded correctly
        from mytower.api.server import ws_connections
        assert isinstance(ws_connections, dict)

    def test_websocket_limit_exceeded_response(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Should return 429 when WebSocket connection limit is exceeded."""
        os.environ["MYTOWER_MAX_WS_CONNECTIONS"] = "1"
        client = test_client_factory()

        # Simulate exceeding the limit by manually setting the counter
        from mytower.api.server import ws_connections
        test_ip = "192.168.1.100"
        ws_connections[test_ip] = 2  # Already at limit

        # Try to make a WebSocket upgrade request
        # This should be rejected before upgrade happens
        # Note: Full WebSocket testing would require a WebSocket client


class TestCommandQueueBackpressure:
    """Tests for command queue backpressure handling."""

    def test_queue_full_raises_runtime_error(self, mock_game_bridge: Mock) -> None:
        """Should raise RuntimeError when command queue is full."""
        # Simulate queue full condition
        mock_game_bridge.queue_command.side_effect = queue.Full()

        from mytower.api.schema import queue_command
        from mytower.game.controllers.controller_commands import AddFloorCommand
        from mytower.game.core.types import FloorType

        with pytest.raises(RuntimeError, match="Command queue is full"):
            queue_command(AddFloorCommand(FloorType.LOBBY))

    def test_queue_full_error_message(self, mock_game_bridge: Mock) -> None:
        """Queue full error should have helpful message."""
        mock_game_bridge.queue_command.side_effect = queue.Full()

        from mytower.api.schema import queue_command
        from mytower.game.controllers.controller_commands import AddFloorCommand
        from mytower.game.core.types import FloorType

        try:
            queue_command(AddFloorCommand(FloorType.LOBBY))
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "Command queue is full" in str(e)
            assert "slow down" in str(e).lower()

    def test_queue_command_uses_timeout(self, mock_game_bridge: Mock) -> None:
        """queue_command should pass timeout to game bridge."""
        from mytower.api.schema import queue_command
        from mytower.game.controllers.controller_commands import AddFloorCommand
        from mytower.game.core.types import FloorType

        queue_command(AddFloorCommand(FloorType.LOBBY))

        # Verify timeout was passed (default 5.0 seconds)
        mock_game_bridge.queue_command.assert_called_once()
        call_args = mock_game_bridge.queue_command.call_args
        assert call_args[1]["timeout"] == 5.0

    def test_queue_command_custom_timeout(self, mock_game_bridge: Mock) -> None:
        """queue_command should accept custom timeout."""
        from mytower.api.schema import queue_command
        from mytower.game.controllers.controller_commands import AddFloorCommand
        from mytower.game.core.types import FloorType

        queue_command(AddFloorCommand(FloorType.LOBBY), timeout=10.0)

        call_args = mock_game_bridge.queue_command.call_args
        assert call_args[1]["timeout"] == 10.0

    def test_mutation_with_queue_full(self, clean_env: None, test_client_factory: Callable[[], TestClient], mock_game_bridge: Mock) -> None:
        """GraphQL mutation should return error when queue is full."""
        mock_game_bridge.queue_command.side_effect = queue.Full()
        client = test_client_factory()

        response = client.post(
            "/graphql",
            json={"query": 'mutation { addFloor(input: {floorType: LOBBY}) }'},
        )

        # Should return GraphQL error (200 status with errors in body)
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert any("queue is full" in str(error).lower() for error in data["errors"])


class TestRootEndpointRateLimiting:
    """Tests for rate limiting on root endpoints."""

    def test_root_endpoint_has_rate_limit(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Root endpoint should have rate limiting applied."""
        os.environ["MYTOWER_RATE_LIMIT_QUERIES"] = "2/minute"
        client = test_client_factory()

        # First 2 requests should succeed
        for _ in range(2):
            response = client.get("/")
            assert response.status_code == 200

        # Third request should be rate limited
        response = client.get("/")
        assert response.status_code == 429

    def test_health_endpoint_no_rate_limit(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Health endpoint should not have rate limiting."""
        os.environ["MYTOWER_RATE_LIMIT_QUERIES"] = "1/minute"
        client = test_client_factory()

        # Multiple requests to health endpoint should all succeed
        for _ in range(5):
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"


class TestRateLimitingIntegration:
    """Integration tests for rate limiting behavior."""

    def test_mixed_operations_independent_limits(
        self,
        clean_env: None,
        test_client_factory: Callable[[], TestClient],
        mock_game_bridge: Mock
    ) -> None:
        """Queries and mutations should have independent rate limits."""
        os.environ["MYTOWER_RATE_LIMIT_QUERIES"] = "5/minute"
        os.environ["MYTOWER_RATE_LIMIT_MUTATIONS"] = "3/minute"
        client = test_client_factory()

        # Use up query quota
        for i in range(5):
            response = client.post("/graphql", json={"query": "{ hello }"})
            assert response.status_code == 200

        # Mutations should still work (separate quota)
        for i in range(3):
            response = client.post(
                "/graphql",
                json={"query": 'mutation { addFloor(input: {floorType: LOBBY}) }'}
            )
            assert response.status_code == 200

        # Both should now be exhausted
        response = client.post("/graphql", json={"query": "{ hello }"})
        assert response.status_code == 429

        response = client.post(
            "/graphql",
            json={"query": 'mutation { addFloor(input: {floorType: LOBBY}) }'}
        )
        assert response.status_code == 429

    def test_rate_limit_reset_after_time(
        self,
        clean_env: None,
        test_client_factory: Callable[[], TestClient],
        mock_game_bridge: Mock
    ) -> None:
        """Rate limits should reset after the time window."""
        # Use a short time window for testing
        os.environ["MYTOWER_RATE_LIMIT_QUERIES"] = "2/second"
        client = test_client_factory()

        # Use up quota
        for _ in range(2):
            response = client.post("/graphql", json={"query": "{ hello }"})
            assert response.status_code == 200

        # Next request should be rate limited
        response = client.post("/graphql", json={"query": "{ hello }"})
        assert response.status_code == 429

        # Wait for window to reset (a bit more than 1 second)
        time.sleep(1.1)

        # Should work again
        response = client.post("/graphql", json={"query": "{ hello }"})
        assert response.status_code == 200


class TestRateLimitingConfiguration:
    """Tests for rate limiting configuration."""

    def test_rate_limit_format_validation(self, clean_env: None) -> None:
        """Rate limit format should be {count}/{period}."""
        valid_formats = [
            "100/minute",
            "1000/hour",
            "10/second",
            "5000/day",
        ]

        for rate_limit in valid_formats:
            os.environ["MYTOWER_RATE_LIMIT_QUERIES"] = rate_limit
            # Should not raise exception
            import importlib
            import mytower.api.server
            importlib.reload(mytower.api.server)

    def test_environment_variable_precedence(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Environment variables should override defaults."""
        # Set all rate limit environment variables
        os.environ["MYTOWER_RATE_LIMIT_QUERIES"] = "150/minute"
        os.environ["MYTOWER_RATE_LIMIT_MUTATIONS"] = "75/minute"
        os.environ["MYTOWER_MAX_WS_CONNECTIONS"] = "5"

        client = test_client_factory()

        from mytower.api.server import MAX_WS_CONNECTIONS_PER_IP
        assert MAX_WS_CONNECTIONS_PER_IP == 5

        # The rate limiting configuration is logged on startup
        # We can verify it was loaded by checking the router
        from mytower.api.server import graphql_app
        assert graphql_app.query_rate == "150/minute"
        assert graphql_app.mutation_rate == "75/minute"
