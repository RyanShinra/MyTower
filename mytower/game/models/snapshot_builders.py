from __future__ import annotations
from mytower.game.models.model_snapshots import ElevatorBankSnapshot, ElevatorSnapshot, FloorSnapshot, PersonSnapshot
from typing import TYPE_CHECKING

from mytower.game.entities.entities_protocol import (
    PersonProtocol,
    ElevatorProtocol,
    FloorProtocol,
    ElevatorBankProtocol
)

if TYPE_CHECKING:
    pass  # No longer need concrete imports


def build_floor_snapshot(floor: FloorProtocol) -> FloorSnapshot:
    """Build a snapshot for a single floor"""
    return FloorSnapshot(
        floor_type=floor.floor_type,
        floor_number=floor.floor_num,
        floor_height_blocks=floor.floor_height,
        left_edge_block=floor.left_edge,
        floor_width_blocks=floor.floor_width,
        floor_color=floor.color,
        floorboard_color=floor.floorboard_color,
        person_count=floor.number_of_people
    )

def build_elevator_snapshot(elevator: ElevatorProtocol) -> ElevatorSnapshot:
    """Build a snapshot for a single elevator"""
    return ElevatorSnapshot(
        id=elevator.elevator_id,
        current_floor=elevator.vertical_position,
        current_block=elevator.horizontal_position,
        destination_floor=elevator.destination_floor,
        state=elevator.elevator_state,
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
        horizontal_block=elevator_bank.horizontal_position,
        min_floor=elevator_bank.min_floor,
        max_floor=elevator_bank.max_floor,
    )

def build_person_snapshot(person: PersonProtocol) -> PersonSnapshot:
    """Build a snapshot for a single person"""
    return PersonSnapshot(
        person_id=person.person_id,
        current_floor_num=person.current_floor_num,
        current_floor_float=person.current_vertical_position,
        current_block_float=person.current_horizontal_position,
        destination_floor_num=person.destination_floor_num,
        destination_block_float=person.destination_horizontal_position,
        state=person.state,
        waiting_time=person.waiting_time,
        mad_fraction=person.mad_fraction,
        draw_color=person.draw_color,
    )
