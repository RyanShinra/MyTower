from __future__ import annotations

from typing import TYPE_CHECKING

from mytower.game.entities.entities_protocol import (
    ElevatorBankProtocol,
    ElevatorProtocol,
    FloorProtocol,
    PersonProtocol,
)
from mytower.game.models.model_snapshots import ElevatorBankSnapshot, ElevatorSnapshot, FloorSnapshot, PersonSnapshot

if TYPE_CHECKING:
    pass  # No longer need concrete imports


def build_floor_snapshot(floor: FloorProtocol) -> FloorSnapshot:
    """Build a snapshot for a single floor"""
    return FloorSnapshot(
        floor_type=floor.floor_type,
        floor_number=floor.floor_num,
        floor_height=floor.floor_height,
        left_edge_block=floor.left_edge,
        floor_width=floor.floor_width,
        floor_color=floor.color,
        floorboard_color=floor.floorboard_color,
        person_count=floor.number_of_people,
    )


def build_elevator_snapshot(elevator: ElevatorProtocol) -> ElevatorSnapshot:
    """Build a snapshot for a single elevator"""
    return ElevatorSnapshot(
        id=elevator.elevator_id,
        vertical_position=elevator.vertical_position,
        horizontal_position=elevator.horizontal_position,
        destination_floor=elevator.destination_floor,
        elevator_state=elevator.elevator_state,
        nominal_direction=elevator.nominal_direction,
        door_open=elevator.door_open,
        passenger_count=elevator.passenger_count,
        available_capacity=elevator.avail_capacity,
        max_capacity=elevator.max_capacity,
    )


def build_elevator_bank_snapshot(elevator_bank: ElevatorBankProtocol) -> ElevatorBankSnapshot:
    """Build a snapshot for a single elevator bank"""
    return ElevatorBankSnapshot(
        id=elevator_bank.elevator_bank_id,
        horizontal_position=elevator_bank.horizontal_position,
        min_floor=elevator_bank.min_floor,
        max_floor=elevator_bank.max_floor,
        floor_requests=elevator_bank.floor_requests,
    )


def build_person_snapshot(person: PersonProtocol) -> PersonSnapshot:
    """Build a snapshot for a single person"""
    return PersonSnapshot(
        person_id=person.person_id,
        current_floor_num=person.current_floor_num,
        current_vertical_position=person.current_vertical_position,
        current_horizontal_position=person.current_horizontal_position,
        destination_floor_num=person.destination_floor_num,
        destination_horizontal_position=person.destination_horizontal_position,
        state=person.state,
        waiting_time=person.waiting_time,
        mad_fraction=person.mad_fraction,
        draw_color=person.draw_color,
    )
