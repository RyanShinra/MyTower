# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

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
from mytower.game.models.model_snapshots import (
    BuildingSnapshot,
    ElevatorBankSnapshot,
    ElevatorSnapshot,
    FloorSnapshot,
    PersonSnapshot,
)


def convert_building_snapshot(snapshot: BuildingSnapshot) -> BuildingSnapshotGQL:
    return BuildingSnapshotGQL(
        time=snapshot.time,
        money=snapshot.money,
        floors=[convert_floor_snapshot(f) for f in snapshot.floors],
        elevators=[convert_elevator_snapshot(e) for e in snapshot.elevators],
        elevator_banks=[convert_elevator_bank_snapshot(b) for b in snapshot.elevator_banks],
        people=[convert_person_snapshot(p) for p in snapshot.people],
    )


def convert_person_snapshot(person: PersonSnapshot) -> PersonSnapshotGQL:
    return PersonSnapshotGQL(
        person_id=person.person_id,
        current_floor_num=person.current_floor_num,
        current_vertical_position=person.current_vertical_position,  # Already Blocks, passes through
        current_horizontal_position=person.current_horizontal_position,  # Already Blocks
        destination_floor_num=person.destination_floor_num,
        destination_horizontal_position=person.destination_horizontal_position,  # Already Blocks
        state=PersonStateGQL(person.state.value),
        waiting_time=person.waiting_time,
        mad_fraction=person.mad_fraction,
        _draw_color=person.draw_color,
    )


def convert_elevator_snapshot(elevator: ElevatorSnapshot) -> ElevatorSnapshotGQL:
    return ElevatorSnapshotGQL(
        id=elevator.id,
        vertical_position=elevator.vertical_position,  # Blocks type passes through
        horizontal_position=elevator.horizontal_position,  # Blocks type passes through
        destination_floor=elevator.destination_floor,
        state=ElevatorStateGQL(elevator.elevator_state.value),
        door_open=elevator.door_open,
        passenger_count=elevator.passenger_count,
        available_capacity=elevator.available_capacity,
        max_capacity=elevator.max_capacity,
        nominal_direction=VerticalDirectionGQL(elevator.nominal_direction.value),
    )


def convert_elevator_bank_snapshot(bank: ElevatorBankSnapshot) -> ElevatorBankSnapshotGQL:
    return ElevatorBankSnapshotGQL(
        id=bank.id,
        horizontal_position=bank.horizontal_position,  # Blocks type passes through
        min_floor=bank.min_floor,
        max_floor=bank.max_floor,
    )


def convert_floor_snapshot(floor: FloorSnapshot) -> FloorSnapshotGQL:
    return FloorSnapshotGQL(
        floor_number=floor.floor_number,
        floor_type=FloorTypeGQL(floor.floor_type.value),
        floor_height=floor.floor_height,  # Blocks type passes through
        person_count=floor.person_count,
        left_edge_block=floor.left_edge_block,  # Blocks type passes through
        floor_width=floor.floor_width,  # Blocks type passes through
        floor_color=ColorGQL.from_tuple(floor.floor_color),
        floorboard_color=ColorGQL.from_tuple(floor.floorboard_color),
    )
