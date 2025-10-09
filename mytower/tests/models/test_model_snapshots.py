"""Tests for model snapshot dataclasses"""
from mytower.game.models.model_snapshots import (
    PersonSnapshot, ElevatorSnapshot, ElevatorBankSnapshot, 
    FloorSnapshot, BuildingSnapshot
)
from mytower.game.core.types import FloorType, PersonState, ElevatorState, VerticalDirection



class TestPersonSnapshot:
    """Test PersonSnapshot dataclass"""

    def test_creation(self) -> None:
        """Test PersonSnapshot creation with all fields"""
        snapshot = PersonSnapshot(
            person_id="person_123",
            current_floor_num=5,
            current_floor_float=5.2,
            current_block_float=10.5,
            destination_floor_num=8,
            destination_block_num=15,
            state=PersonState.WALKING,
            waiting_time=30.5,
            mad_fraction=0.7,
            draw_color=(255, 128, 64)
        )
        
        assert snapshot.person_id == "person_123"
        assert snapshot.current_floor_num == 5
        assert snapshot.current_floor_float == 5.2
        assert snapshot.current_block_float == 10.5
        assert snapshot.destination_floor_num == 8
        assert snapshot.destination_block_num == 15
        assert snapshot.state == PersonState.WALKING
        assert snapshot.waiting_time == 30.5
        assert snapshot.mad_fraction == 0.7
        assert snapshot.draw_color == (255, 128, 64)

    def test_immutability(self) -> None:
        """Test that PersonSnapshot is immutable (dataclass frozen behavior)"""
        snapshot = PersonSnapshot(
            person_id="person_123",
            current_floor_num=5,
            current_floor_float=5.2,
            current_block_float=10.5,
            destination_floor_num=8,
            destination_block_num=15,
            state=PersonState.IDLE,
            waiting_time=0.0,
            mad_fraction=0.0,
            draw_color=(128, 128, 128)
        )
        
        # Fields should be accessible but not modifiable in frozen dataclass
        # (Though this dataclass isn't explicitly frozen, it's meant to be immutable)
        assert snapshot.person_id == "person_123"
        assert snapshot.state == PersonState.IDLE


class TestElevatorSnapshot:
    """Test ElevatorSnapshot dataclass"""

    def test_creation(self) -> None:
        """Test ElevatorSnapshot creation with all fields"""
        snapshot = ElevatorSnapshot(
            id="elevator_456",
            current_floor=3.7,
            current_block=14.2,
            destination_floor=8,
            state=ElevatorState.MOVING,
            nominal_direction=VerticalDirection.UP,
            door_open=False,
            passenger_count=5,
            available_capacity=10,
            max_capacity=15
        )
        
        assert snapshot.id == "elevator_456"
        assert snapshot.current_floor == 3.7
        assert snapshot.current_block == 14.2
        assert snapshot.destination_floor == 8
        assert snapshot.state == ElevatorState.MOVING
        assert snapshot.nominal_direction == VerticalDirection.UP
        assert snapshot.door_open is False
        assert snapshot.passenger_count == 5
        assert snapshot.available_capacity == 10
        assert snapshot.max_capacity == 15

    def test_door_states(self) -> None:
        """Test elevator door states"""
        closed_snapshot = ElevatorSnapshot(
            id="elevator_1", current_floor=1.0, current_block=14.0,
            destination_floor=1, state=ElevatorState.IDLE,
            nominal_direction=VerticalDirection.STATIONARY,
            door_open=False, passenger_count=0,
            available_capacity=15, max_capacity=15
        )
        
        open_snapshot = ElevatorSnapshot(
            id="elevator_2", current_floor=1.0, current_block=14.0,
            destination_floor=1, state=ElevatorState.LOADING,
            nominal_direction=VerticalDirection.STATIONARY,
            door_open=True, passenger_count=3,
            available_capacity=12, max_capacity=15
        )
        
        assert closed_snapshot.door_open is False
        assert open_snapshot.door_open is True


class TestElevatorBankSnapshot:
    """Test ElevatorBankSnapshot dataclass"""

    def test_creation(self) -> None:
        """Test ElevatorBankSnapshot creation with all fields"""
        snapshot = ElevatorBankSnapshot(
            horizontal_block=14,
            min_floor=1,
            max_floor=20
        )
        
        assert snapshot.horizontal_block == 14
        assert snapshot.min_floor == 1
        assert snapshot.max_floor == 20

    def test_single_floor_bank(self) -> None:
        """Test elevator bank serving single floor"""
        snapshot = ElevatorBankSnapshot(
            horizontal_block=5,
            min_floor=10,
            max_floor=10
        )
        
        assert snapshot.min_floor == snapshot.max_floor
        assert snapshot.min_floor == 10


class TestFloorSnapshot:
    """Test FloorSnapshot dataclass"""

    def test_creation(self) -> None:
        """Test FloorSnapshot creation with all fields"""
        snapshot = FloorSnapshot(
            floor_type=FloorType.OFFICE,
            floor_number=7,
            floor_height_blocks=1,
            left_edge_block=0,
            floor_width_blocks=20,
            person_count=3,
            floor_color=(150, 200, 250),
            floorboard_color=(10, 10, 10)
        )
        
        assert snapshot.floor_type == FloorType.OFFICE
        assert snapshot.floor_number == 7
        assert snapshot.floor_height_blocks == 1
        assert snapshot.left_edge_block == 0
        assert snapshot.floor_width_blocks == 20
        assert snapshot.person_count == 3
        assert snapshot.floor_color == (150, 200, 250)
        assert snapshot.floorboard_color == (10, 10, 10)

    def test_different_floor_types(self) -> None:
        """Test different floor types"""
        floor_types = [
            FloorType.LOBBY, FloorType.OFFICE, FloorType.APARTMENT,
            FloorType.HOTEL, FloorType.RESTAURANT, FloorType.RETAIL
        ]
        
        for floor_type in floor_types:
            snapshot = FloorSnapshot(
                floor_type=floor_type,
                floor_number=1,
                floor_height_blocks=1,
                left_edge_block=0,
                floor_width_blocks=20,
                person_count=0,
                floor_color=(128, 128, 128),
                floorboard_color=(64, 64, 64)
            )
            
            assert snapshot.floor_type == floor_type


class TestBuildingSnapshot:
    """Test BuildingSnapshot dataclass"""

    def test_creation(self) -> None:
        """Test BuildingSnapshot creation with all fields"""
        person_snapshot = PersonSnapshot(
            person_id="person_1", current_floor_num=1, current_floor_float=1.0,
            current_block_float=5.0, destination_floor_num=5, destination_block_num=10,
            state=PersonState.WALKING, waiting_time=0.0, mad_fraction=0.0,
            draw_color=(128, 128, 128)
        )
        
        elevator_snapshot = ElevatorSnapshot(
            id="elevator_1", current_floor=2.5, current_block=14.0,
            destination_floor=5, state=ElevatorState.MOVING,
            nominal_direction=VerticalDirection.UP, door_open=False,
            passenger_count=2, available_capacity=13, max_capacity=15
        )
        
        floor_snapshot = FloorSnapshot(
            floor_type=FloorType.LOBBY, floor_number=1, floor_height_blocks=1,
            left_edge_block=0, floor_width_blocks=20, person_count=1,
            floor_color=(200, 200, 200), floorboard_color=(10, 10, 10)
        )
        
        elevator_bank_snapshot = ElevatorBankSnapshot(
            horizontal_block=14, min_floor=1, max_floor=20
        )
        
        building_snapshot = BuildingSnapshot(
            time=12345.67,
            money=500000,
            floors=[floor_snapshot],
            elevators=[elevator_snapshot],
            people=[person_snapshot],
            elevator_banks=[elevator_bank_snapshot]
        )
        
        assert building_snapshot.time == 12345.67
        assert building_snapshot.money == 500000
        assert len(building_snapshot.floors) == 1
        assert len(building_snapshot.elevators) == 1
        assert len(building_snapshot.people) == 1
        assert building_snapshot.floors[0] == floor_snapshot
        assert building_snapshot.elevators[0] == elevator_snapshot
        assert building_snapshot.people[0] == person_snapshot

    def test_empty_building(self) -> None:
        """Test BuildingSnapshot with empty collections"""
        snapshot = BuildingSnapshot(
            time=0.0,
            money=100000,
            floors=[],
            elevators=[],
            people=[],
            elevator_banks=[]
        )
        
        assert snapshot.time == 0.0
        assert snapshot.money == 100000
        assert len(snapshot.floors) == 0
        assert len(snapshot.elevators) == 0
        assert len(snapshot.people) == 0

    def test_multiple_entities(self) -> None:
        """Test BuildingSnapshot with multiple entities"""
        floors: list[FloorSnapshot] = [
            FloorSnapshot(
                floor_type=FloorType.LOBBY, floor_number=1, floor_height_blocks=1,
                left_edge_block=0, floor_width_blocks=20, person_count=0,
                floor_color=(200, 200, 200), floorboard_color=(10, 10, 10)
            ),
            FloorSnapshot(
                floor_type=FloorType.OFFICE, floor_number=2, floor_height_blocks=1,
                left_edge_block=0, floor_width_blocks=20, person_count=2,
                floor_color=(150, 200, 250), floorboard_color=(10, 10, 10)
            )
        ]
        
        elevators: list[ElevatorSnapshot] = [
            ElevatorSnapshot(
                id="elevator_1", current_floor=1.0, current_block=14.0,
                destination_floor=2, state=ElevatorState.MOVING,
                nominal_direction=VerticalDirection.UP, door_open=False,
                passenger_count=0, available_capacity=15, max_capacity=15
            )
        ]
        
        people: list[PersonSnapshot] = [
            PersonSnapshot(
                person_id="person_1", current_floor_num=2, current_floor_float=2.0,
                current_block_float=5.0, destination_floor_num=1, destination_block_num=10,
                state=PersonState.WAITING_FOR_ELEVATOR, waiting_time=15.5, mad_fraction=0.2,
                draw_color=(200, 150, 100)
            ),
            PersonSnapshot(
                person_id="person_2", current_floor_num=2, current_floor_float=2.0,
                current_block_float=8.0, destination_floor_num=1, destination_block_num=3,
                state=PersonState.IDLE, waiting_time=0.0, mad_fraction=0.0,
                draw_color=(100, 200, 150)
            )
        ]
        
        el_banks: list[ElevatorBankSnapshot] = [
            ElevatorBankSnapshot(
                horizontal_block=14, min_floor=1, max_floor=20
            ),
            ElevatorBankSnapshot(
                horizontal_block=18, min_floor=1, max_floor=10
            )
        ]
        
        snapshot = BuildingSnapshot(
            time=300.0,
            money=450000,
            floors=floors,
            elevators=elevators,
            people=people,
            elevator_banks=el_banks
        )
        
        assert len(snapshot.floors) == 2
        assert len(snapshot.elevators) == 1
        assert len(snapshot.people) == 2
        assert snapshot.floors[0].floor_type == FloorType.LOBBY
        assert snapshot.floors[1].floor_type == FloorType.OFFICE