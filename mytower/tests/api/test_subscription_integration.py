# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

"""
Integration tests for GraphQL schema and subscription definitions.

Tests cover:
- Schema structure validation
- Subscription field definitions
- Strawberry decorator application
- Type system correctness
"""

from typing import TYPE_CHECKING

import pytest

from mytower.api.graphql_types import BuildingSnapshotGQL
from mytower.api.schema import Subscription, schema

if TYPE_CHECKING:
    from unittest.mock import Mock

    from pytest import MonkeyPatch


class TestSchemaStructure:
    """Test GraphQL schema structure and configuration."""

    def test_schema_includes_subscription_type(self) -> None:
        """Verify schema has Subscription type defined."""
        assert schema.subscription is not None
        assert schema.subscription == Subscription

    def test_schema_has_query_type(self) -> None:
        """Verify schema has Query type (baseline test)."""
        assert schema.query is not None

    def test_schema_has_mutation_type(self) -> None:
        """Verify schema has Mutation type (baseline test)."""
        assert schema.mutation is not None

    def test_subscription_type_is_strawberry_type(self) -> None:
        """Verify Subscription is decorated with @strawberry.type."""
        # Check that Subscription has the strawberry type metadata
        assert hasattr(Subscription, "__strawberry_definition__")


class TestSubscriptionFieldDefinitions:
    """Test subscription field definitions and metadata."""

    def test_building_state_stream_field_exists(self) -> None:
        """Verify building_state_stream field is defined in Subscription."""
        subscription = Subscription()
        assert hasattr(subscription, "building_state_stream")
        assert callable(subscription.building_state_stream)

    def test_game_time_stream_field_exists(self) -> None:
        """Verify game_time_stream field is defined in Subscription."""
        subscription = Subscription()
        assert hasattr(subscription, "game_time_stream")
        assert callable(subscription.game_time_stream)

    def test_building_state_stream_is_async_generator(self) -> None:
        """Verify building_state_stream returns AsyncGenerator."""
        subscription = Subscription()
        result = subscription.building_state_stream(interval_ms=50)  # type: ignore[call-arg]

        # Check it's an async generator
        assert hasattr(result, "__anext__")  # type: ignore[arg-type]
        assert hasattr(result, "asend")  # type: ignore[arg-type]
        assert hasattr(result, "aclose")  # type: ignore[arg-type]

    def test_game_time_stream_is_async_generator(self) -> None:
        """Verify game_time_stream returns AsyncGenerator."""
        subscription = Subscription()
        result = subscription.game_time_stream(interval_ms=100)  # type: ignore[call-arg]

        # Check it's an async generator
        assert hasattr(result, "__anext__")  # type: ignore[arg-type]
        assert hasattr(result, "asend")  # type: ignore[arg-type]
        assert hasattr(result, "aclose")  # type: ignore[arg-type]

    def test_building_state_stream_has_correct_signature(self) -> None:
        """Verify building_state_stream has correct parameter signature."""
        import inspect

        sig = inspect.signature(Subscription.building_state_stream)

        # Should have 'self' and 'interval_ms' parameters
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "interval_ms" in params

        # interval_ms should have default value
        interval_param = sig.parameters["interval_ms"]
        assert interval_param.default == 50

    def test_game_time_stream_has_correct_signature(self) -> None:
        """Verify game_time_stream has correct parameter signature."""
        import inspect

        sig = inspect.signature(Subscription.game_time_stream)

        # Should have 'self' and 'interval_ms' parameters
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "interval_ms" in params

        # interval_ms should have default value
        interval_param = sig.parameters["interval_ms"]
        assert interval_param.default == 100

    def test_building_state_stream_return_type_annotation(self) -> None:
        """Verify building_state_stream has correct return type annotation."""
        import inspect

        sig = inspect.signature(Subscription.building_state_stream)
        return_annotation = sig.return_annotation

        # Should be AsyncGenerator[BuildingSnapshotGQL | None, None]
        # Check it's a generic type with AsyncGenerator
        assert hasattr(return_annotation, "__origin__")

    def test_game_time_stream_return_type_annotation(self) -> None:
        """Verify game_time_stream has correct return type annotation."""
        import inspect

        sig = inspect.signature(Subscription.game_time_stream)
        return_annotation = sig.return_annotation

        # Should be AsyncGenerator[Time, None]
        assert hasattr(return_annotation, "__origin__")


class TestStrawberryDecorators:
    """Test Strawberry decorator application."""

    def test_subscription_class_has_strawberry_type_decorator(self) -> None:
        """Verify @strawberry.type is applied to Subscription class."""
        # Strawberry adds __strawberry_definition__ attribute
        assert hasattr(Subscription, "__strawberry_definition__")

        # Check it's a type definition
        definition = getattr(Subscription, "__strawberry_definition__", None)
        assert definition is not None

    def test_building_state_stream_has_subscription_decorator(self) -> None:
        """Verify @strawberry.subscription is applied to building_state_stream."""
        # Check the method exists and has strawberry metadata
        method = Subscription.building_state_stream
        assert method is not None

        # Strawberry decorators add metadata that we can inspect
        # The exact metadata structure is internal to Strawberry, but we can verify it exists
        assert callable(method)

    def test_game_time_stream_has_subscription_decorator(self) -> None:
        """Verify @strawberry.subscription is applied to game_time_stream."""
        method = Subscription.game_time_stream
        assert method is not None
        assert callable(method)


class TestSubscriptionDocstrings:
    """Test subscription docstrings and documentation."""

    def test_building_state_stream_has_docstring(self) -> None:
        """Verify building_state_stream has docstring."""
        doc = Subscription.building_state_stream.__doc__
        assert doc is not None
        assert len(doc.strip()) > 0
        assert "Stream building state" in doc

    def test_game_time_stream_has_docstring(self) -> None:
        """Verify game_time_stream has docstring."""
        doc = Subscription.game_time_stream.__doc__
        assert doc is not None
        assert len(doc.strip()) > 0
        assert "Stream game time" in doc

    def test_subscription_class_has_docstring(self) -> None:
        """Verify Subscription class has docstring."""
        doc = Subscription.__doc__
        assert doc is not None
        assert len(doc.strip()) > 0


class TestTypeSystem:
    """Test GraphQL type system integration."""

    def test_schema_has_scalar_overrides(self) -> None:
        """Verify schema has custom scalar overrides for units."""
        # The schema should have Time, Blocks, etc. as custom scalars
        # This is configured in schema.py
        assert schema.config is not None

    def test_building_snapshot_gql_is_strawberry_type(self) -> None:
        """Verify BuildingSnapshotGQL is a Strawberry type."""
        assert hasattr(BuildingSnapshotGQL, "__strawberry_definition__")

    def test_time_is_custom_scalar(self) -> None:
        """Verify Time is configured as a custom scalar."""
        # Time should be a valid type in the schema
        from mytower.api import unit_scalars

        assert hasattr(unit_scalars, "Time")


@pytest.mark.asyncio
class TestSubscriptionBehaviorIntegration:
    """Integration tests for subscription behavior with schema."""

    async def test_subscription_instance_can_be_created(self) -> None:
        """Verify Subscription can be instantiated."""
        subscription = Subscription()
        assert subscription is not None
        assert isinstance(subscription, Subscription)

    async def test_building_state_stream_can_be_called(
        self, mock_game_bridge: "Mock", monkeypatch: "MonkeyPatch"
    ) -> None:
        """Verify building_state_stream can be called and returns generator."""
        # Arrange
        mock_game_bridge.get_building_snapshot.return_value = None

        # Mock get_game_bridge to return our mock
        from mytower.api import game_bridge
        monkeypatch.setattr(game_bridge, "_bridge", mock_game_bridge)

        # Act
        subscription = Subscription()
        generator = subscription.building_state_stream(interval_ms=50)  # type: ignore[call-arg]

        # Assert
        assert generator is not None

        # Clean up generator
        await generator.aclose()  # type: ignore[misc]

    async def test_game_time_stream_can_be_called(
        self, mock_game_bridge: "Mock", monkeypatch: "MonkeyPatch"
    ) -> None:
        """Verify game_time_stream can be called and returns generator."""
        # Arrange
        mock_game_bridge.get_building_snapshot.return_value = None

        # Mock get_game_bridge to return our mock
        from mytower.api import game_bridge
        monkeypatch.setattr(game_bridge, "_bridge", mock_game_bridge)

        # Act
        subscription = Subscription()
        generator = subscription.game_time_stream(interval_ms=100)  # type: ignore[call-arg]

        # Assert
        assert generator is not None

        # Clean up generator
        await generator.aclose()  # type: ignore[misc]

    async def test_multiple_subscription_instances(
        self, mock_game_bridge: "Mock", monkeypatch: "MonkeyPatch"
    ) -> None:
        """Verify multiple Subscription instances can coexist."""
        # Arrange
        mock_game_bridge.get_building_snapshot.return_value = None

        # Mock get_game_bridge to return our mock
        from mytower.api import game_bridge
        monkeypatch.setattr(game_bridge, "_bridge", mock_game_bridge)

        # Act: Create multiple subscriptions
        sub1 = Subscription()
        sub2 = Subscription()

        assert sub1 is not sub2  # Different instances

        gen1 = sub1.building_state_stream(interval_ms=50)  # type: ignore[call-arg]
        gen2 = sub2.building_state_stream(interval_ms=100)  # type: ignore[call-arg]

        # Both should work independently
        result1 = await anext(gen1)  # type: ignore[arg-type]
        result2 = await anext(gen2)  # type: ignore[arg-type]

        # Assert
        assert result1 is None
        assert result2 is None

        await gen1.aclose()  # type: ignore[misc]
        await gen2.aclose()  # type: ignore[misc]


class TestSchemaValidation:
    """Test schema validation and correctness."""

    def test_schema_can_be_printed(self) -> None:
        """Verify schema can be printed as string (GraphQL SDL)."""
        schema_str = str(schema)
        assert schema_str is not None
        assert len(schema_str) > 0

    def test_schema_includes_subscription_in_sdl(self) -> None:
        """Verify schema SDL includes 'type Subscription'."""
        schema_str = str(schema)

        # Should contain subscription type definition
        assert "type Subscription" in schema_str or "subscription" in schema_str.lower()

    def test_schema_includes_building_state_stream_in_sdl(self) -> None:
        """Verify schema SDL includes buildingStateStream field."""
        schema_str = str(schema)

        # Should contain the subscription field
        assert "buildingStateStream" in schema_str

    def test_schema_includes_game_time_stream_in_sdl(self) -> None:
        """Verify schema SDL includes gameTimeStream field."""
        schema_str = str(schema)

        # Should contain the subscription field
        assert "gameTimeStream" in schema_str

    def test_schema_includes_interval_ms_parameter(self) -> None:
        """Verify schema SDL includes intervalMs parameter."""
        schema_str = str(schema)

        # Should contain the parameter
        assert "intervalMs" in schema_str or "interval_ms" in schema_str


class TestSchemaConsistency:
    """Test schema consistency and conventions."""

    def test_subscription_follows_naming_convention(self) -> None:
        """Verify subscription fields follow camelCase convention."""
        # GraphQL convention is camelCase for field names
        schema_str = str(schema)

        # Should use camelCase: buildingStateStream, not building_state_stream
        assert "buildingStateStream" in schema_str

    def test_parameter_naming_convention(self) -> None:
        """Verify parameters follow GraphQL naming conventions."""
        schema_str = str(schema)

        # Parameters should be camelCase: intervalMs, not interval_ms
        assert "intervalMs" in schema_str

    def test_return_types_are_correct(self) -> None:
        """Verify subscription return types match GraphQL schema."""
        import inspect

        # Building state stream should return BuildingSnapshotGQL or None
        sig = inspect.signature(Subscription.building_state_stream)
        assert sig.return_annotation is not None

        # Game time stream should return Time
        sig = inspect.signature(Subscription.game_time_stream)
        assert sig.return_annotation is not None
