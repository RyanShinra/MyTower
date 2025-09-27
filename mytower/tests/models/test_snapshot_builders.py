from unittest.mock import MagicMock
import pytest

from mytower.game.models.snapshot_builders import (
    build_floor_snapshot, build_elevator_snapshot, 
    build_elevator_bank_snapshot, build_person_snapshot
)
from mytower.game.entities.floor import Floor
from mytower.game.entities.elevator import Elevator
from mytower.game.entities.elevator_bank import ElevatorBank
from mytower.game.entities.person import PersonProtocol
from mytower.game.core.types import FloorType, PersonState, ElevatorState, VerticalDirection


class TestBuildFloorSnapshot:
    """Test build_floor_snapshot function"""

    def test_build_floor_snapshot(self) -> None:
        """Test building floor snapshot from floor entity"""
        mock_floor = MagicMock(spec=Floor)
        mock_floor.floor_type = FloorType.OFFICE
        mock_floor.floor_num = 5
        mock_floor.height = 1
        mock_floor.left_edge = 0
        mock_floor.width = 20
        mock_floor.color = (150, 200, 250)
        mock_floor.floorboard_color = (10, 10, 10)
        mock_floor.number_of_people = 3
        
        snapshot = build_floor_snapshot(mock_floor)
        
        assert snapshot.floor_type == FloorType.OFFICE
        assert snapshot.floor_number == 5
        assert snapshot.floor_height_blocks == 1
        assert snapshot.left_edge_block == 0
        assert snapshot.floor_width_blocks == 20
        assert snapshot.floor_color == (150, 200, 250)
        assert snapshot.floorboard_color == (10, 10, 10)
        assert snapshot.person_count == 3

    def test_build_floor_snapshot_different_types(self) -> None:
        """Test building snapshots for different floor types"""
        floor_types = [FloorType.LOBBY, FloorType.APARTMENT, FloorType.HOTEL]
        
        for floor_type in floor_types:
            mock_floor = MagicMock(spec=Floor)
            mock_floor.floor_type = floor_type
            mock_floor.floor_num = 1
            mock_floor.height = 1
            mock_floor.left_edge = 0
            mock_floor.width = 20
            mock_floor.color = (128, 128, 128)
            mock_floor.floorboard_color = (64, 64, 64)
            mock_floor.number_of_people = 0
            
            snapshot = build_floor_snapshot(mock_floor)
            
            assert snapshot.floor_type == floor_type


class TestBuildElevatorSnapshot:
    """Test build_elevator_snapshot function"""

    def test_build_elevator_snapshot(self) -> None:
        """Test building elevator snapshot from elevator entity"""
        mock_elevator = MagicMock(spec=Elevator)
        mock_elevator.elevator_id = "elevator_123"
        mock_elevator.fractional_floor = 3.7
        mock_elevator.current_block_float = 14.2
        mock_elevator.destination_floor = 8
        mock_elevator.state = ElevatorState.MOVING
        mock_elevator.nominal_direction = VerticalDirection.UP
        mock_elevator.door_open = False
        mock_elevator.passenger_count = 5
        mock_elevator.avail_capacity = 10
        mock_elevator.max_capacity = 15
        
        snapshot = build_elevator_snapshot(mock_elevator)
        
        assert snapshot.id == "elevator_123"
        assert snapshot.current_floor == 3.7
        assert snapshot.current_block == 14.2
        assert snapshot.destination_floor == 8
        assert snapshot.state == ElevatorState.MOVING
        assert snapshot.nominal_direction == VerticalDirection.UP
        assert snapshot.door_open is False
        assert snapshot.passenger_count == 5
        assert snapshot.available_capacity == 10
        assert snapshot.max_capacity == 15

    def test_build_elevator_snapshot_different_states(self) -> None:
        """Test building snapshots for different elevator states"""
        states = [ElevatorState.IDLE, ElevatorState.LOADING, ElevatorState.ARRIVED]
        
        for state in states:
            mock_elevator = MagicMock(spec=Elevator)
            mock_elevator.elevator_id = f"elevator_{state.value}"
            mock_elevator.fractional_floor = 1.0
            mock_elevator.current_block_float = 14.0
            mock_elevator.destination_floor = 1
            mock_elevator.state = state
            mock_elevator.nominal_direction = VerticalDirection.STATIONARY
            mock_elevator.door_open = (state == ElevatorState.LOADING)
            mock_elevator.passenger_count = 0
            mock_elevator.avail_capacity = 15
            mock_elevator.max_capacity = 15
            
            snapshot = build_elevator_snapshot(mock_elevator)
            
            assert snapshot.state == state
            assert snapshot.door_open == (state == ElevatorState.LOADING)


class TestBuildElevatorBankSnapshot:
    """Test build_elevator_bank_snapshot function"""

    def test_build_elevator_bank_snapshot(self) -> None:
        """Test building elevator bank snapshot from elevator bank entity"""
        mock_bank = MagicMock(spec=ElevatorBank)
        mock_bank.horizontal_block = 14
        mock_bank.min_floor = 1
        mock_bank.max_floor = 20
        
        snapshot = build_elevator_bank_snapshot(mock_bank)
        
        assert snapshot.horizontal_block == 14
        assert snapshot.min_floor == 1
        assert snapshot.max_floor == 20

    def test_build_elevator_bank_snapshot_different_ranges(self) -> None:
        """Test building snapshots for different floor ranges"""
        test_cases = [
            (5, 1, 10),     # Small building
            (10, 5, 25),    # Mid-range
            (3, 15, 15),    # Single floor
        ]
        
        for h_block, min_floor, max_floor in test_cases:
            mock_bank = MagicMock(spec=ElevatorBank)
            mock_bank.horizontal_block = h_block
            mock_bank.min_floor = min_floor
            mock_bank.max_floor = max_floor
            
            snapshot = build_elevator_bank_snapshot(mock_bank)
            
            assert snapshot.horizontal_block == h_block
            assert snapshot.min_floor == min_floor
            assert snapshot.max_floor == max_floor


class TestBuildPersonSnapshot:
    """Test build_person_snapshot function"""

    def test_build_person_snapshot(self) -> None:
        """Test building person snapshot from person entity"""
        mock_person = MagicMock(spec=PersonProtocol)
        mock_person.person_id = "person_456"
        mock_person.current_floor_num = 3
        mock_person.current_floor_float = 3.0
        mock_person.current_block_float = 8.5
        mock_person.destination_floor_num = 7
        mock_person.destination_block_num = 12
        mock_person.state = PersonState.WALKING
        mock_person.waiting_time = 25.3
        mock_person.mad_fraction = 0.4
        mock_person.draw_color = (255, 128, 64)
        
        snapshot = build_person_snapshot(mock_person)
        
        assert snapshot.person_id == "person_456"
        assert snapshot.current_floor_num == 3
        assert snapshot.current_floor_float == 3.0
        assert snapshot.current_block_float == 8.5
        assert snapshot.destination_floor_num == 7
        assert snapshot.destination_block_num == 12
        assert snapshot.state == PersonState.WALKING
        assert snapshot.waiting_time == 25.3
        assert snapshot.mad_fraction == 0.4
        assert snapshot.draw_color == (255, 128, 64)

    def test_build_person_snapshot_different_states(self) -> None:
        """Test building snapshots for different person states"""
        states = [PersonState.IDLE, PersonState.WAITING_FOR_ELEVATOR, PersonState.IN_ELEVATOR]
        
        for state in states:
            mock_person = MagicMock(spec=PersonProtocol)
            mock_person.person_id = f"person_{state.value}"
            mock_person.current_floor_num = 1
            mock_person.current_floor_float = 1.0
            mock_person.current_block_float = 5.0
            mock_person.destination_floor_num = 5
            mock_person.destination_block_num = 10
            mock_person.state = state
            mock_person.waiting_time = 0.0 if state == PersonState.IDLE else 30.0
            mock_person.mad_fraction = 0.0 if state == PersonState.IDLE else 0.5
            mock_person.draw_color = (128, 128, 128)
            
            snapshot = build_person_snapshot(mock_person)
            
            assert snapshot.state == state
            assert snapshot.person_id == f"person_{state.value}"

    def test_build_person_snapshot_mad_fraction_range(self) -> None:
        """Test building snapshots with different mad fraction values"""
        mad_fractions = [0.0, 0.25, 0.5, 0.75, 1.0]
        
        for mad_fraction in mad_fractions:
            mock_person = MagicMock(spec=PersonProtocol)
            mock_person.person_id = "person_test"
            mock_person.current_floor_num = 1
            mock_person.current_floor_float = 1.0
            mock_person.current_block_float = 5.0
            mock_person.destination_floor_num = 2
            mock_person.destination_block_num = 10
            mock_person.state = PersonState.WAITING_FOR_ELEVATOR
            mock_person.waiting_time = mad_fraction * 100  # Correlate waiting time with madness
            mock_person.mad_fraction = mad_fraction
            mock_person.draw_color = (int(255 * mad_fraction), 128, 128)  # Redder when angrier
            
            snapshot = build_person_snapshot(mock_person)
            
            assert snapshot.mad_fraction == mad_fraction
            assert snapshot.waiting_time == mad_fraction * 100

    def test_build_person_snapshot_color_variations(self) -> None:
        """Test building snapshots with different draw colors"""
        colors = [
            (255, 0, 0),      # Red
            (0, 255, 0),      # Green
            (0, 0, 255),      # Blue
            (255, 255, 0),    # Yellow
            (128, 64, 192),   # Purple-ish
        ]
        
        for color in colors:
            mock_person = MagicMock(spec=PersonProtocol)
            mock_person.person_id = "person_test"
            mock_person.current_floor_num = 1
            mock_person.current_floor_float = 1.0
            mock_person.current_block_float = 5.0
            mock_person.destination_floor_num = 2
            mock_person.destination_block_num = 10
            mock_person.state = PersonState.IDLE
            mock_person.waiting_time = 0.0
            mock_person.mad_fraction = 0.0
            mock_person.draw_color = color
            
            snapshot = build_person_snapshot(mock_person)
            
            assert snapshot.draw_color == color


class TestSnapshotBuilderIntegration:
    """Test integration between different snapshot builders"""

    def test_all_builders_return_correct_types(self) -> None:
        """Test that all builders return the expected snapshot types"""
        # Floor
        mock_floor = MagicMock(spec=Floor)
        mock_floor.floor_type = FloorType.OFFICE
        mock_floor.floor_num = 1
        mock_floor.height = 1
        mock_floor.left_edge = 0
        mock_floor.width = 20
        mock_floor.color = (128, 128, 128)
        mock_floor.floorboard_color = (64, 64, 64)
        mock_floor.number_of_people = 0
        
        floor_snapshot = build_floor_snapshot(mock_floor)
        assert hasattr(floor_snapshot, 'floor_type')
        assert hasattr(floor_snapshot, 'floor_number')
        
        # Elevator
        mock_elevator = MagicMock(spec=Elevator)
        mock_elevator.elevator_id = "elevator_1"
        mock_elevator.fractional_floor = 1.0
        mock_elevator.current_block_float = 14.0
        mock_elevator.destination_floor = 1
        mock_elevator.state = ElevatorState.IDLE
        mock_elevator.nominal_direction = VerticalDirection.STATIONARY
        mock_elevator.door_open = False
        mock_elevator.passenger_count = 0
        mock_elevator.avail_capacity = 15
        mock_elevator.max_capacity = 15
        
        elevator_snapshot = build_elevator_snapshot(mock_elevator)
        assert hasattr(elevator_snapshot, 'id')
        assert hasattr(elevator_snapshot, 'state')
        
        # Bank
        mock_bank = MagicMock(spec=ElevatorBank)
        mock_bank.horizontal_block = 14
        mock_bank.min_floor = 1
        mock_bank.max_floor = 5
        
        bank_snapshot = build_elevator_bank_snapshot(mock_bank)
        assert hasattr(bank_snapshot, 'horizontal_block')
        assert hasattr(bank_snapshot, 'min_floor')
        
        # Person
        mock_person = MagicMock(spec=PersonProtocol)
        mock_person.person_id = "person_1"
        mock_person.current_floor_num = 1
        mock_person.current_floor_float = 1.0
        mock_person.current_block_float = 5.0
        mock_person.destination_floor_num = 2
        mock_person.destination_block_num = 10
        mock_person.state = PersonState.IDLE
        mock_person.waiting_time = 0.0
        mock_person.mad_fraction = 0.0
        mock_person.draw_color = (128, 128, 128)
        
        person_snapshot = build_person_snapshot(mock_person)
        assert hasattr(person_snapshot, 'person_id')
        assert hasattr(person_snapshot, 'state')