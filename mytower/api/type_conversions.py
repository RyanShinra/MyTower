from mytower.api.graphql_types import BuildingSnapshotGQL, ElevatorSnapshotGQL, FloorSnapshotGQL, PersonSnapshotGQL
from mytower.game.models.model_snapshots import BuildingSnapshot, ElevatorSnapshot, FloorSnapshot, PersonSnapshot


def convert_building_snapshot(snapshot: BuildingSnapshot) -> BuildingSnapshotGQL:
    return BuildingSnapshotGQL(
        time=snapshot.time,
        money=snapshot.money,
        floors=[convert_floor_snapshot(f) for f in snapshot.floors],
        elevators=[convert_elevator_snapshot(e) for e in snapshot.elevators],
        people=[convert_person_snapshot(p) for p in snapshot.people]
    )

def convert_person_snapshot(person: PersonSnapshot) -> PersonSnapshotGQL:
    return PersonSnapshotGQL(
        person_id=person.person_id,
        current_floor_num=person.current_floor_num,
        current_block_float=person.current_block_float,
        destination_floor_num=person.destination_floor_num,
        destination_block_num=person.destination_block_num,
        state=person.state.value,  # Enum to string
        waiting_time=person.waiting_time,
        mad_fraction=person.mad_fraction
    )

def convert_elevator_snapshot(elevator: ElevatorSnapshot) -> ElevatorSnapshotGQL:
    return ElevatorSnapshotGQL(
        id=elevator.id,
        current_floor=elevator.current_floor,
        current_block=elevator.current_block,
        destination_floor=elevator.destination_floor,
        state=elevator.state.value,  # Enum to string
        door_open=elevator.door_open,
        passenger_count=elevator.passenger_count,
        available_capacity=elevator.available_capacity,
        max_capacity=elevator.max_capacity
    )

def convert_floor_snapshot(floor: FloorSnapshot) -> FloorSnapshotGQL:
    return FloorSnapshotGQL(
        floor_number=floor.floor_number,
        floor_type=floor.floor_type.value,  # Enum to string
        floor_height_blocks=floor.floor_height_blocks,
        person_count=floor.person_count
    )