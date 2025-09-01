
from __future__ import annotations
from mytower.game.models.model_snapshots import ElevatorSnapshot, FloorSnapshot, PersonSnapshot
from typing import TYPE_CHECKING

from mytower.game.person import PersonProtocol

if TYPE_CHECKING:
    from mytower.game.floor import Floor
    from mytower.game.elevator import Elevator

def build_floor_snapshot(floor: Floor) -> FloorSnapshot:
    """Build a snapshot for a single floor"""
    return FloorSnapshot(
        floor_number=floor.floor_num,
        floor_type=floor.floor_type,
        person_count=0  # TODO: Implement once we have floors contain people
    )
    
def build_elevator_snapshot(elevator: Elevator) -> ElevatorSnapshot:
    """Build a snapshot for a single elevator"""
    return ElevatorSnapshot(
        id=elevator.elevator_id,
        current_floor=elevator.fractional_floor,
        destination_floor=elevator.destination_floor,
        state=elevator.state,
        nominal_direction=elevator.nominal_direction,
        door_open=elevator.door_open,
        passenger_count=elevator.passenger_count,
        available_capacity=elevator.avail_capacity,
        max_capacity=elevator.max_capacity,
    )
    
def build_person_snapshot(person: PersonProtocol) -> PersonSnapshot:
    """Build a snapshot for a single person"""
    return PersonSnapshot(
        id=person.person_id,
        current_floor=person.current_floor,
        current_block=person.current_block,
        destination_floor=person.destination_floor,
        destination_block=person.destination_block,
        state=person.state,
        waiting_time=person.waiting_time
    )