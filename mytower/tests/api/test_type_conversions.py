# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

"""
Direct tests for mytower.api.type_conversions.

Each test builds a snapshot whose fields all hold different values, converts it, and checks every
field of the GraphQL type, so a field mapped from the wrong source shows up as a failure.

Unit values are compared through `.value`. `==` on Blocks and Time allows a tolerance
(see mytower/game/core/units.py), which would hide a small error in a conversion.
"""

from dataclasses import replace

import pytest

from mytower.api.graphql_types import (
    BuildingSnapshotGQL,
    ColorGQL,
    ElevatorBankSnapshotGQL,
    ElevatorSnapshotGQL,
    ElevatorStateGQL,
    FloorSnapshotGQL,
    FloorTypeGQL,
    PersonSnapshotGQL,
    PersonStateGQL,
    VerticalDirectionGQL,
)
from mytower.api.type_conversions import (
    convert_building_snapshot,
    convert_elevator_bank_snapshot,
    convert_elevator_snapshot,
    convert_floor_snapshot,
    convert_person_snapshot,
)
from mytower.game.core.types import ElevatorState, FloorType, PersonState, VerticalDirection
from mytower.game.core.units import Blocks, Time
from mytower.game.models.model_snapshots import (
    BuildingSnapshot,
    ElevatorBankSnapshot,
    ElevatorSnapshot,
    FloorSnapshot,
    PersonSnapshot,
)


@pytest.fixture
def person_snapshot() -> PersonSnapshot:
    """A person with a different value in every field."""
    return PersonSnapshot(
        person_id="person_a",
        current_floor_num=3,
        current_vertical_position=Blocks(3.25),
        current_horizontal_position=Blocks(7.5),
        destination_floor_num=9,
        destination_horizontal_position=Blocks(14.75),
        state=PersonState.WALKING,
        waiting_time=Time(42.5),
        mad_fraction=0.625,
        draw_color=(10, 20, 30),
    )


@pytest.fixture
def elevator_snapshot() -> ElevatorSnapshot:
    """An elevator with a different value in every field."""
    return ElevatorSnapshot(
        id="elevator_a",
        vertical_position=Blocks(12.5),
        horizontal_position=Blocks(6.25),
        destination_floor=8,
        elevator_state=ElevatorState.LOADING,
        nominal_direction=VerticalDirection.DOWN,
        door_open=True,
        passenger_count=4,
        available_capacity=11,
        max_capacity=15,
    )


@pytest.fixture
def elevator_bank_snapshot() -> ElevatorBankSnapshot:
    """An elevator bank with a different value in every field."""
    return ElevatorBankSnapshot(
        id="bank_a",
        horizontal_position=Blocks(6.75),
        min_floor=2,
        max_floor=17,
        floor_requests={5: {VerticalDirection.UP}},
    )


@pytest.fixture
def floor_snapshot() -> FloorSnapshot:
    """A floor with a different value in every field and RGB (three-element) colors."""
    return FloorSnapshot(
        floor_type=FloorType.OFFICE,
        floor_number=7,
        floor_height=Blocks(1.5),
        left_edge_block=Blocks(2.25),
        floor_width=Blocks(20.75),
        person_count=5,
        floor_color=(11, 22, 33),
        floorboard_color=(44, 55, 66),
    )


class TestConvertPersonSnapshot:
    """convert_person_snapshot: PersonSnapshot to PersonSnapshotGQL."""

    def test_converts_every_field(self, person_snapshot: PersonSnapshot) -> None:
        result = convert_person_snapshot(person_snapshot)

        assert isinstance(result, PersonSnapshotGQL)
        assert result.person_id == "person_a"
        assert result.current_floor_num == 3
        assert result.destination_floor_num == 9
        assert result.state is PersonStateGQL.WALKING
        assert result.mad_fraction == 0.625

    def test_positions_stay_blocks_with_the_same_value(self, person_snapshot: PersonSnapshot) -> None:
        result = convert_person_snapshot(person_snapshot)

        assert isinstance(result.current_vertical_position, Blocks)
        assert result.current_vertical_position.value == 3.25
        assert isinstance(result.current_horizontal_position, Blocks)
        assert result.current_horizontal_position.value == 7.5
        assert isinstance(result.destination_horizontal_position, Blocks)
        assert result.destination_horizontal_position.value == 14.75

    def test_waiting_time_stays_time_with_the_same_value(self, person_snapshot: PersonSnapshot) -> None:
        result = convert_person_snapshot(person_snapshot)

        assert isinstance(result.waiting_time, Time)
        assert result.waiting_time.value == 42.5

    def test_draw_color_is_stored_for_the_draw_color_field(self, person_snapshot: PersonSnapshot) -> None:
        """The converter stores the RGB tuple in _draw_color; the draw_color GraphQL field resolves from it."""
        result = convert_person_snapshot(person_snapshot)

        assert result._draw_color == (10, 20, 30)

    @pytest.mark.parametrize("state", list(PersonState))
    def test_maps_every_person_state(self, person_snapshot: PersonSnapshot, state: PersonState) -> None:
        result = convert_person_snapshot(replace(person_snapshot, state=state))

        assert result.state is PersonStateGQL[state.name]
        assert result.state.value == state.value


class TestConvertElevatorSnapshot:
    """convert_elevator_snapshot: ElevatorSnapshot to ElevatorSnapshotGQL."""

    def test_converts_every_field(self, elevator_snapshot: ElevatorSnapshot) -> None:
        result = convert_elevator_snapshot(elevator_snapshot)

        assert isinstance(result, ElevatorSnapshotGQL)
        assert result.id == "elevator_a"
        assert result.destination_floor == 8
        assert result.state is ElevatorStateGQL.LOADING
        assert result.nominal_direction is VerticalDirectionGQL.DOWN
        assert result.door_open is True
        assert result.passenger_count == 4
        assert result.available_capacity == 11
        assert result.max_capacity == 15

    def test_positions_stay_blocks_with_the_same_value(self, elevator_snapshot: ElevatorSnapshot) -> None:
        result = convert_elevator_snapshot(elevator_snapshot)

        assert isinstance(result.vertical_position, Blocks)
        assert result.vertical_position.value == 12.5
        assert isinstance(result.horizontal_position, Blocks)
        assert result.horizontal_position.value == 6.25

    @pytest.mark.parametrize("door_open", [True, False])
    def test_door_open_in_both_states(self, elevator_snapshot: ElevatorSnapshot, door_open: bool) -> None:
        result = convert_elevator_snapshot(replace(elevator_snapshot, door_open=door_open))

        assert result.door_open is door_open

    @pytest.mark.parametrize("state", list(ElevatorState))
    def test_maps_every_elevator_state(self, elevator_snapshot: ElevatorSnapshot, state: ElevatorState) -> None:
        result = convert_elevator_snapshot(replace(elevator_snapshot, elevator_state=state))

        assert result.state is ElevatorStateGQL[state.name]
        assert result.state.value == state.value

    @pytest.mark.parametrize("direction", list(VerticalDirection))
    def test_maps_every_nominal_direction(
        self, elevator_snapshot: ElevatorSnapshot, direction: VerticalDirection
    ) -> None:
        result = convert_elevator_snapshot(replace(elevator_snapshot, nominal_direction=direction))

        assert result.nominal_direction is VerticalDirectionGQL[direction.name]
        assert result.nominal_direction.value == direction.value


class TestConvertElevatorBankSnapshot:
    """convert_elevator_bank_snapshot: ElevatorBankSnapshot to ElevatorBankSnapshotGQL."""

    def test_converts_every_field(self, elevator_bank_snapshot: ElevatorBankSnapshot) -> None:
        result = convert_elevator_bank_snapshot(elevator_bank_snapshot)

        assert isinstance(result, ElevatorBankSnapshotGQL)
        assert result.id == "bank_a"
        assert isinstance(result.horizontal_position, Blocks)
        assert result.horizontal_position.value == 6.75
        assert result.min_floor == 2
        assert result.max_floor == 17


class TestConvertFloorSnapshot:
    """convert_floor_snapshot: FloorSnapshot to FloorSnapshotGQL."""

    def test_converts_every_field(self, floor_snapshot: FloorSnapshot) -> None:
        result = convert_floor_snapshot(floor_snapshot)

        assert isinstance(result, FloorSnapshotGQL)
        assert result.floor_type is FloorTypeGQL.OFFICE
        assert result.floor_number == 7
        assert result.person_count == 5

    def test_dimensions_stay_blocks_with_the_same_value(self, floor_snapshot: FloorSnapshot) -> None:
        result = convert_floor_snapshot(floor_snapshot)

        assert isinstance(result.floor_height, Blocks)
        assert result.floor_height.value == 1.5
        assert isinstance(result.left_edge_block, Blocks)
        assert result.left_edge_block.value == 2.25
        assert isinstance(result.floor_width, Blocks)
        assert result.floor_width.value == 20.75

    def test_rgb_colors_become_opaque(self, floor_snapshot: FloorSnapshot) -> None:
        """A three-element color has no alpha, so the GraphQL color gets 255."""
        result = convert_floor_snapshot(floor_snapshot)

        assert isinstance(result.floor_color, ColorGQL)
        assert result.floor_color.as_rgba_tuple() == (11, 22, 33, 255)
        assert isinstance(result.floorboard_color, ColorGQL)
        assert result.floorboard_color.as_rgba_tuple() == (44, 55, 66, 255)

    def test_rgba_colors_keep_their_alpha(self, floor_snapshot: FloorSnapshot) -> None:
        snapshot = replace(floor_snapshot, floor_color=(11, 22, 33, 128), floorboard_color=(44, 55, 66, 0))

        result = convert_floor_snapshot(snapshot)

        assert result.floor_color.as_rgba_tuple() == (11, 22, 33, 128)
        assert result.floorboard_color.as_rgba_tuple() == (44, 55, 66, 0)

    @pytest.mark.parametrize("floor_type", list(FloorType))
    def test_maps_every_floor_type(self, floor_snapshot: FloorSnapshot, floor_type: FloorType) -> None:
        result = convert_floor_snapshot(replace(floor_snapshot, floor_type=floor_type))

        assert result.floor_type is FloorTypeGQL[floor_type.name]
        assert result.floor_type.value == floor_type.value


class TestConvertBuildingSnapshot:
    """convert_building_snapshot: the top-level fields and the four nested lists."""

    def test_converts_time_and_money(self, mock_building_snapshot: BuildingSnapshot) -> None:
        result = convert_building_snapshot(replace(mock_building_snapshot, time=Time(123.5), money=54321))

        assert isinstance(result, BuildingSnapshotGQL)
        assert isinstance(result.time, Time)
        assert result.time.value == 123.5
        assert result.money == 54321

    def test_empty_building_converts_to_empty_lists(self, mock_empty_snapshot: BuildingSnapshot) -> None:
        result = convert_building_snapshot(mock_empty_snapshot)

        assert result.time.value == 0.0
        assert result.money == 10000
        assert result.floors == []
        assert result.elevators == []
        assert result.elevator_banks == []
        assert result.people == []

    def test_nested_items_are_converted_to_graphql_types(self, mock_building_snapshot: BuildingSnapshot) -> None:
        """One item per list, each checked by a field that only the right source item carries."""
        result = convert_building_snapshot(mock_building_snapshot)

        assert [type(f) for f in result.floors] == [FloorSnapshotGQL]
        assert result.floors[0].floor_type is FloorTypeGQL.LOBBY
        assert [type(e) for e in result.elevators] == [ElevatorSnapshotGQL]
        assert result.elevators[0].id == "elevator_123"
        assert [type(b) for b in result.elevator_banks] == [ElevatorBankSnapshotGQL]
        assert result.elevator_banks[0].id == "bank_456"
        assert [type(p) for p in result.people] == [PersonSnapshotGQL]
        assert result.people[0].person_id == "person_456"

    def test_lists_keep_their_order_and_length(
        self,
        floor_snapshot: FloorSnapshot,
        elevator_snapshot: ElevatorSnapshot,
        elevator_bank_snapshot: ElevatorBankSnapshot,
        person_snapshot: PersonSnapshot,
    ) -> None:
        """Each list has a different length and is out of sorted order, so a reordering or a swap of lists shows."""
        snapshot = BuildingSnapshot(
            time=Time(1.0),
            money=1,
            floors=[replace(floor_snapshot, floor_number=n) for n in (4, 2, 9, 1)],
            elevators=[replace(elevator_snapshot, id=i) for i in ("elevator_c", "elevator_a", "elevator_b")],
            elevator_banks=[replace(elevator_bank_snapshot, id=i) for i in ("bank_b", "bank_a")],
            people=[replace(person_snapshot, person_id=i) for i in ("p_e", "p_b", "p_d", "p_a", "p_c")],
        )

        result = convert_building_snapshot(snapshot)

        assert [f.floor_number for f in result.floors] == [4, 2, 9, 1]
        assert [e.id for e in result.elevators] == ["elevator_c", "elevator_a", "elevator_b"]
        assert [b.id for b in result.elevator_banks] == ["bank_b", "bank_a"]
        assert [p.person_id for p in result.people] == ["p_e", "p_b", "p_d", "p_a", "p_c"]
