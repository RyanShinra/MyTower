# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

"""
Unit tests for CORS middleware configuration.

Tests cover:
- CORS header presence and correct values
- Environment variable handling (MYTOWER_CORS_ORIGINS)
- Wildcard origin behavior (credentials disabled)
- Specific origin behavior (credentials enabled)
- Whitespace stripping from environment variables
- CORS security policy compliance
"""

import os
from collections.abc import Callable, Generator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def clean_env() -> Generator[None]:
    """Clean up MYTOWER_CORS_ORIGINS environment variable before and after each test."""
    original_value = os.environ.get("MYTOWER_CORS_ORIGINS")
    if "MYTOWER_CORS_ORIGINS" in os.environ:
        del os.environ["MYTOWER_CORS_ORIGINS"]
    yield
    # Restore original value
    if original_value is not None:
        os.environ["MYTOWER_CORS_ORIGINS"] = original_value
    elif "MYTOWER_CORS_ORIGINS" in os.environ:
        del os.environ["MYTOWER_CORS_ORIGINS"]


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


class TestCORSDefaultConfiguration:
    """Tests for default CORS configuration (no environment variable set)."""

    def test_wildcard_origins_by_default(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Should use wildcard origins (*) when MYTOWER_CORS_ORIGINS is not set."""
        client = test_client_factory()
        response = client.options(
            "/graphql",
            headers={"Origin": "https://example.com", "Access-Control-Request-Method": "POST"},
        )
        assert response.headers["access-control-allow-origin"] == "*"

    def test_credentials_disabled_with_wildcard(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Should disable credentials when using wildcard origins (CORS security requirement)."""
        client = test_client_factory()
        response = client.options(
            "/graphql",
            headers={"Origin": "https://example.com", "Access-Control-Request-Method": "POST"},
        )
        # Credentials should not be allowed with wildcard origins
        assert response.headers.get("access-control-allow-credentials") != "true"

    def test_all_methods_allowed(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Should allow all HTTP methods."""
        client = test_client_factory()
        response = client.options(
            "/graphql",
            headers={"Origin": "https://example.com", "Access-Control-Request-Method": "POST"},
        )
        allowed_methods = response.headers.get("access-control-allow-methods", "")
        assert "GET" in allowed_methods
        assert "POST" in allowed_methods
        assert "OPTIONS" in allowed_methods

    def test_all_headers_allowed(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Should allow all headers."""
        client = test_client_factory()
        response = client.options(
            "/graphql",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type,authorization",
            },
        )
        allowed_headers = response.headers.get("access-control-allow-headers", "")
        assert "content-type" in allowed_headers.lower()
        assert "authorization" in allowed_headers.lower()


class TestCORSEnvironmentVariableHandling:
    """Tests for MYTOWER_CORS_ORIGINS environment variable handling."""

    def test_single_origin(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Should accept single origin from environment variable."""
        os.environ["MYTOWER_CORS_ORIGINS"] = "https://example.com"
        client = test_client_factory()
        response = client.options(
            "/graphql",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.headers["access-control-allow-origin"] == "https://example.com"

    def test_multiple_origins(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Should accept multiple comma-separated origins."""
        os.environ["MYTOWER_CORS_ORIGINS"] = "https://example.com,https://app.example.com"
        client = test_client_factory()

        # Test first origin
        response = client.options(
            "/graphql",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.headers["access-control-allow-origin"] == "https://example.com"

        # Test second origin
        response = client.options(
            "/graphql",
            headers={
                "Origin": "https://app.example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.headers["access-control-allow-origin"] == "https://app.example.com"

    def test_whitespace_stripping(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Should strip whitespace from environment variable values."""
        os.environ["MYTOWER_CORS_ORIGINS"] = "https://example.com , https://app.example.com"
        client = test_client_factory()

        # Origins with whitespace in the env var should still work
        response = client.options(
            "/graphql",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.headers["access-control-allow-origin"] == "https://example.com"

    def test_credentials_enabled_with_specific_origins(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Should enable credentials when using specific origins (not wildcard)."""
        os.environ["MYTOWER_CORS_ORIGINS"] = "https://example.com,https://app.example.com"
        client = test_client_factory()
        response = client.options(
            "/graphql",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.headers.get("access-control-allow-credentials") == "true"

    def test_wildcard_in_list_disables_credentials(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Should disable credentials if wildcard appears anywhere in the origins list."""
        os.environ["MYTOWER_CORS_ORIGINS"] = "https://example.com,*,https://app.example.com"
        client = test_client_factory()
        response = client.options(
            "/graphql",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        # Credentials should be disabled because wildcard is present
        assert response.headers.get("access-control-allow-credentials") != "true"


class TestCORSSecurityCompliance:
    """Tests for CORS security policy compliance."""

    def test_wildcard_with_credentials_not_allowed(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """
        Should NOT allow credentials with wildcard origins.

        This is a CORS security requirement: The combination of allow_origins=["*"]
        with allow_credentials=True violates the CORS specification.
        """
        os.environ["MYTOWER_CORS_ORIGINS"] = "*"
        client = test_client_factory()
        response = client.options(
            "/graphql",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        # Must not allow credentials with wildcard
        assert response.headers.get("access-control-allow-credentials") != "true"

    def test_production_configuration(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Should work correctly with production-like configuration."""
        os.environ["MYTOWER_CORS_ORIGINS"] = "https://mytower.example.com,https://app.mytower.example.com"
        client = test_client_factory()

        # Test allowed origin
        response = client.options(
            "/graphql",
            headers={
                "Origin": "https://mytower.example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.headers["access-control-allow-origin"] == "https://mytower.example.com"
        assert response.headers.get("access-control-allow-credentials") == "true"

        # Test disallowed origin (should still get a response, but browser will block it)
        response = client.options(
            "/graphql",
            headers={
                "Origin": "https://malicious.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        # FastAPI CORS middleware should not set the origin header for disallowed origins
        assert response.headers.get("access-control-allow-origin") != "https://malicious.com"


class TestCORSEndpointCoverage:
    """Tests ensuring CORS works across all endpoints."""

    def test_cors_on_root_endpoint(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Should apply CORS to root endpoint."""
        client = test_client_factory()
        response = client.options(
            "/",
            headers={"Origin": "https://example.com", "Access-Control-Request-Method": "GET"},
        )
        assert "access-control-allow-origin" in response.headers

    def test_cors_on_health_endpoint(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Should apply CORS to health check endpoint."""
        client = test_client_factory()
        response = client.options(
            "/health",
            headers={"Origin": "https://example.com", "Access-Control-Request-Method": "GET"},
        )
        assert "access-control-allow-origin" in response.headers

    def test_cors_on_graphql_endpoint(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Should apply CORS to GraphQL endpoint."""
        client = test_client_factory()
        response = client.options(
            "/graphql",
            headers={"Origin": "https://example.com", "Access-Control-Request-Method": "POST"},
        )
        assert "access-control-allow-origin" in response.headers


class TestCORSEdgeCases:
    """Tests for edge case handling in CORS configuration."""

    def test_empty_string_fallback_to_wildcard(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Should fallback to wildcard when MYTOWER_CORS_ORIGINS is empty string."""
        os.environ["MYTOWER_CORS_ORIGINS"] = ""
        client = test_client_factory()
        response = client.options(
            "/graphql",
            headers={"Origin": "https://example.com", "Access-Control-Request-Method": "POST"},
        )
        assert response.headers["access-control-allow-origin"] == "*"
        # Credentials should be disabled with wildcard
        assert response.headers.get("access-control-allow-credentials") != "true"

    def test_whitespace_only_fallback_to_wildcard(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Should fallback to wildcard when MYTOWER_CORS_ORIGINS is whitespace only."""
        os.environ["MYTOWER_CORS_ORIGINS"] = "   "
        client = test_client_factory()
        response = client.options(
            "/graphql",
            headers={"Origin": "https://example.com", "Access-Control-Request-Method": "POST"},
        )
        assert response.headers["access-control-allow-origin"] == "*"
        assert response.headers.get("access-control-allow-credentials") != "true"

    def test_empty_list_items_fallback_to_wildcard(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Should fallback to wildcard when MYTOWER_CORS_ORIGINS has only empty items."""
        os.environ["MYTOWER_CORS_ORIGINS"] = " , , "
        client = test_client_factory()
        response = client.options(
            "/graphql",
            headers={"Origin": "https://example.com", "Access-Control-Request-Method": "POST"},
        )
        assert response.headers["access-control-allow-origin"] == "*"
        assert response.headers.get("access-control-allow-credentials") != "true"

    def test_mixed_valid_and_empty_origins(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Should filter out empty origins and keep valid ones."""
        os.environ["MYTOWER_CORS_ORIGINS"] = "https://example.com, ,https://app.example.com, "
        client = test_client_factory()
        response = client.options(
            "/graphql",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert response.headers["access-control-allow-origin"] == "https://example.com"
        # Credentials should be enabled (no wildcard in the filtered list)
        assert response.headers.get("access-control-allow-credentials") == "true"

    def test_commas_only_fallback_to_wildcard(self, clean_env: None, test_client_factory: Callable[[], TestClient]) -> None:
        """Should fallback to wildcard when MYTOWER_CORS_ORIGINS is only commas."""
        os.environ["MYTOWER_CORS_ORIGINS"] = ",,,"
        client = test_client_factory()
        response = client.options(
            "/graphql",
            headers={"Origin": "https://example.com", "Access-Control-Request-Method": "POST"},
        )
        assert response.headers["access-control-allow-origin"] == "*"
        assert response.headers.get("access-control-allow-credentials") != "true"
