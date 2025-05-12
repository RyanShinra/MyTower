import pytest
from unittest.mock import MagicMock # , # patch
from game.elevator import Elevator, ElevatorState
from game.types import VerticalDirection
from game.logger import LoggerProvider

class TestElevator:
    @pytest.fixture
    def mock_logger_provider(self) -> MagicMock:
        provider = MagicMock(spec=LoggerProvider)
        mock_logger = MagicMock()
        provider.get_logger.return_value = mock_logger
        return provider
        
    @pytest.fixture
    def mock_elevator_bank(self) -> MagicMock:
        mock_bank = MagicMock()
        mock_bank.horizontal_block = 5
        return mock_bank
        
    @pytest.fixture
    def mock_config(self) -> MagicMock:
        config = MagicMock()
        config.max_speed = 0.75
        config.max_capacity = 15
        config.passenger_loading_time = 1.0
        config.idle_log_timeout = 0.5
        config.moving_log_timeout = 0.5
        config.idle_wait_timeout = 0.5
        return config
        
    @pytest.fixture
    def mock_cosmetics_config(self) -> MagicMock:
        config = MagicMock()
        config.shaft_color = (100, 100, 100)
        config.shaft_overhead = (24, 24, 24)
        config.closed_color = (50, 50, 200)
        config.open_color = (200, 200, 50)
        return config
        
    @pytest.fixture
    def elevator(self, mock_logger_provider: MagicMock, mock_elevator_bank: MagicMock, mock_config: MagicMock, mock_cosmetics_config: MagicMock) -> Elevator:
        return Elevator(
            mock_logger_provider,
            mock_elevator_bank,
            h_cell=5,
            min_floor=1,
            max_floor=10,
            config=mock_config,
            cosmetics_config=mock_cosmetics_config
        )
    
    def test_initial_state(self, elevator: Elevator) -> None:
        """Test that elevator initializes with correct values"""
        assert elevator.state == ElevatorState.IDLE
        assert elevator.current_floor_int == 1
        assert elevator.min_floor == 1
        assert elevator.max_floor == 10
        assert elevator.avail_capacity == 15
        assert elevator.is_empty == True
        
    def test_set_destination_floor(self, elevator: Elevator) -> None:
        """Test setting destination floor and direction updates"""
        elevator.set_destination_floor(5)
        assert elevator.destination_floor == 5
        assert elevator.nominal_direction == VerticalDirection.UP
        
        elevator.set_destination_floor(2)
        assert elevator.destination_floor == 2
        assert elevator.nominal_direction == VerticalDirection.DOWN
        
        # Test destination on same floor
        elevator.set_destination_floor(2)  # Already on floor 2
        assert elevator.nominal_direction == VerticalDirection.STATIONARY
        
    def test_set_invalid_destination_floor(self, elevator: Elevator) -> None:
        """Test that setting invalid destination floor raises ValueError"""
        with pytest.raises(ValueError):
            elevator.set_destination_floor(15)  # Above max floor
            
        with pytest.raises(ValueError):
            elevator.set_destination_floor(0)   # Below min floor