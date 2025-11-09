from typing import Any
from collections.abc import AsyncGenerator

import asyncio
import strawberry

from mytower.api import unit_scalars  # Import the module to register scalars
from mytower.api.game_bridge import get_game_bridge
from mytower.api.game_bridge_protocol import GameBridgeProtocol
from mytower.api.graphql_types import BuildingSnapshotGQL, FloorTypeGQL, PersonSnapshotGQL
from mytower.api.input_types import AddElevatorBankInput, AddElevatorInput, AddFloorInput, AddPersonInput
from mytower.api.type_conversions import convert_building_snapshot, convert_person_snapshot
from mytower.game.controllers.controller_commands import (
    AddElevatorBankCommand,
    AddElevatorCommand,
    AddFloorCommand,
    AddPersonCommand,
    Command,
)
from mytower.game.core.types import FloorType
from mytower.game.core.units import Blocks, Meters, Pixels, Time, Velocity
from mytower.game.models.model_snapshots import BuildingSnapshot

# Convenience functions
def queue_command(command: Command[Any]) -> str:
    return get_game_bridge().queue_command(command)

def get_building_state() -> BuildingSnapshot | None:
    return get_game_bridge().get_building_snapshot()


@strawberry.type
class Query:

    @strawberry.field
    def hello(self) -> str:
        return "Hello World from MyTower!"

    @strawberry.field
    def game_time(self) -> Time:
        snapshot: BuildingSnapshot | None = get_building_state()
        return snapshot.time if snapshot else Time(0.0)

    @strawberry.field
    def is_running(self) -> bool:
        return get_building_state() is not None

    @strawberry.field
    def building_state(self) -> BuildingSnapshotGQL | None:
        snapshot: BuildingSnapshot | None = get_building_state()
        return convert_building_snapshot(snapshot) if snapshot else None

    @strawberry.field
    def all_people(self) -> list[PersonSnapshotGQL] | None:
        snapshot: BuildingSnapshot | None = get_building_state()
        if not snapshot:
            return None
        return [convert_person_snapshot(p) for p in snapshot.people]


@strawberry.type
class Mutation:

    @strawberry.mutation
    def add_floor(self, input: AddFloorInput) -> str:
        domain_floor_type = FloorType(input.floor_type.value)
        command = AddFloorCommand(floor_type=domain_floor_type)
        return queue_command(command)

    @strawberry.mutation
    def add_person(self, input: AddPersonInput) -> str:
        command = AddPersonCommand(
            floor=input.floor,
            init_horiz_position=input.init_horiz_position,
            dest_floor=input.dest_floor,
            dest_horiz_position=input.dest_horiz_position
        )
        return queue_command(command)

    @strawberry.mutation
    def add_elevator_bank(self, input: AddElevatorBankInput) -> str:
        command = AddElevatorBankCommand(
            horiz_position=input.horiz_position,
            min_floor=input.min_floor,
            max_floor=input.max_floor
        )
        return queue_command(command)

    @strawberry.mutation
    def add_elevator(self, input: AddElevatorInput) -> str:
        command = AddElevatorCommand(elevator_bank_id=input.elevator_bank_id)
        return queue_command(command)

    # Debug / synchronous versions of the above mutations
    # These block until the command is processed and return the result directly
    # Useful for testing and simple scripts
    # Not recommended for production use due to blocking nature
    @strawberry.mutation
    def add_floor_sync(self, input: AddFloorInput) -> int:
        domain_floor_type = FloorType(input.floor_type.value)
        return get_game_bridge().execute_add_floor_sync(domain_floor_type)

    @strawberry.mutation
    def add_person_sync(self, input: AddPersonInput) -> str:
        return get_game_bridge().execute_add_person_sync(
            input.floor,
            input.init_horiz_position,
            input.dest_floor,
            input.dest_horiz_position
        )

    @strawberry.mutation
    def add_elevator_bank_sync(self, input: AddElevatorBankInput) -> str:
        return get_game_bridge().execute_add_elevator_bank_sync(
            input.horiz_position,
            input.min_floor,
            input.max_floor
        )

    @strawberry.mutation
    def add_elevator_sync(self, input: AddElevatorInput) -> str:
        return get_game_bridge().execute_add_elevator_sync(input.elevator_bank_id)

# TODO: Consider using the logging library instead of print statements for better control over output
@strawberry.type
class Subscription:
    """
    GraphQL subscriptions for real-time building state updates via WebSocket.

    Supports dependency injection for testing by accepting an optional game_bridge parameter.
    """

    def __init__(self, game_bridge: GameBridgeProtocol | None = None) -> None:
        """
        Initialize the Subscription with an optional game bridge for dependency injection.

        Note: When Strawberry creates instances via the schema, __init__() is called with no arguments (game_bridge=None).
        Tests can directly instantiate with a mock game_bridge for dependency injection.

        Args:
            game_bridge: Optional GameBridgeProtocol instance for testing. If None, uses get_game_bridge()
        """
        self._game_bridge: GameBridgeProtocol | None = game_bridge

    @strawberry.subscription
    async def building_state_stream(
        self,
        interval_ms: int = 50,  # ~20 FPS by default
    ) -> AsyncGenerator[BuildingSnapshotGQL | None, None]:  # noqa: UP043
        """
        Stream building state updates in real-time.

        Args:
            interval_ms: Polling interval in milliseconds (5 to 10000, default: 50ms for ~20 FPS)

        Raises:
            ValueError: If interval_ms is out of allowed range (5 to 10000)

        Yields:
            BuildingSnapshotGQL: Current building state snapshot, or None if game not running
        """
        if not (5 <= interval_ms <= 10000):
            raise ValueError("interval_ms must be between 5 and 10000")

        interval_seconds: float = interval_ms / 1000.0
        # Use getattr for safe access - _game_bridge will be None when called via Strawberry schema
        game_bridge: GameBridgeProtocol = getattr(self, '_game_bridge', None) or get_game_bridge()

        try:
            while True:
                snapshot: BuildingSnapshot | None = game_bridge.get_building_snapshot()
                yield convert_building_snapshot(snapshot) if snapshot else None
                await asyncio.sleep(interval_seconds)

        except asyncio.CancelledError:
            # Client disconnected or subscription was cancelled
            # This is NORMAL - not an error condition
            print(f"Subscription cancelled (client likely disconnected)")  # noqa: F541
            raise  # Re-raise so Strawberry knows we handled it

        except Exception as e:
            # Unexpected error - log it
            print(f"Subscription error: {e}")
            raise

        finally:
            # Cleanup code runs whether cancelled, errored, or completed
            print("Building State Subscription stream cleaned up")
            # Could release resources, decrement counter, etc.


    @strawberry.subscription
    async def game_time_stream(
        self,
        interval_ms: int = 100,  # 10 FPS by default
    ) -> AsyncGenerator[Time, None]:  # noqa: UP043
        """
        Stream game time updates.

        Args:
            interval_ms: Polling interval in milliseconds (5 to 10000, default: 100ms for 10 FPS)

        Raises:
            ValueError: If interval_ms is out of allowed range (5 to 10000)

        Yields:
            Time: Current game time in seconds
        """
        if not (5 <= interval_ms <= 10000):
            raise ValueError("interval_ms must be between 5 and 10000")

        interval_seconds: float = interval_ms / 1000.0
        # Use getattr for safe access - _game_bridge will be None when called via Strawberry schema
        game_bridge: GameBridgeProtocol = getattr(self, '_game_bridge', None) or get_game_bridge()

        try:
            while True:
                snapshot: BuildingSnapshot | None = game_bridge.get_building_snapshot()
                yield snapshot.time if snapshot else Time(0.0)
                await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            # Client disconnected or subscription was cancelled
            print(f"Game time subscription cancelled (client likely disconnected)")  # noqa: F541
            raise
        except Exception as e:
            print(f"Game time subscription error: {e}")
            raise
        finally:
            print("Game time subscription stream cleaned up")


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
    scalar_overrides={
        Time: unit_scalars.Time,
        Blocks: unit_scalars.Blocks,
        Meters: unit_scalars.Meters,
        Pixels: unit_scalars.Pixels,
        Velocity: unit_scalars.Velocity,
    },
)
