
from __future__ import annotations
from mytower.game.entities.elevator_bank import ElevatorBank
from mytower.game.models.model_snapshots import ElevatorBankSnapshot, ElevatorSnapshot, FloorSnapshot, PersonSnapshot
from typing import TYPE_CHECKING

from mytower.game.entities.person import PersonProtocol

if TYPE_CHECKING:
    from mytower.game.entities.floor import Floor
    from mytower.game.entities.elevator import Elevator



def build_floor_snapshot(floor: Floor) -> FloorSnapshot:
    """Build a snapshot for a single floor"""
    return FloorSnapshot(
        floor_type=floor.floor_type,
        floor_number=floor.floor_num,
        floor_height_blocks=floor.height,
        left_edge_block=floor.left_edge,
        floor_width_blocks=floor.width,
        floor_color=floor.color,
        floorboard_color=floor.floorboard_color,
        person_count=floor.number_of_people
    )

def build_elevator_snapshot(elevator: Elevator) -> ElevatorSnapshot:
    """Build a snapshot for a single elevator"""
    return ElevatorSnapshot(
        id=elevator.elevator_id,
        current_floor=elevator.fractional_floor,
        current_block=elevator.current_block_float,
        destination_floor=elevator.destination_floor,
        state=elevator.state,
        nominal_direction=elevator.nominal_direction,
        door_open=elevator.door_open,
        passenger_count=elevator.passenger_count,
        available_capacity=elevator.avail_capacity,
        max_capacity=elevator.max_capacity,
    )

def build_elevator_bank_snapshot(elevator_bank: ElevatorBank) -> ElevatorBankSnapshot:
    """Build a snapshot for a single elevator bank"""
    return ElevatorBankSnapshot(
        id=elevator_bank.elevator_bank_id,
        horizontal_block=elevator_bank.horizontal_block,
        min_floor=elevator_bank.min_floor,
        max_floor=elevator_bank.max_floor,
    )

def build_person_snapshot(person: PersonProtocol) -> PersonSnapshot:
    """Build a snapshot for a single person"""
    return PersonSnapshot(
        person_id=person.person_id,
        current_floor_num=person.current_floor_num,
        current_floor_float=person.current_floor_float,
        current_block_float=person.current_block_float,
        destination_floor_num=person.destination_floor_num,
        destination_block_float=person.destination_block_num,
        state=person.state,
        waiting_time=person.waiting_time,
        mad_fraction=person.mad_fraction,
        draw_color=person.draw_color,
    )
