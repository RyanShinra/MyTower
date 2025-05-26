from typing import Callable, List, cast
from unittest.mock import MagicMock  # , # patch

import pytest

from mytower.game.elevator import Elevator, ElevatorState
from mytower.game.logger import LoggerProvider
from mytower.game.person import Person
from mytower.game.types import VerticalDirection


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

    # @pytest.fixture
    # def mock_person_floor_2(self) -> MagicMock:
    #     person = MagicMock()
    #     person.destination_floor = 2
    #     return person

    # @pytest.fixture
    # def mock_person_floor_5(self) -> MagicMock:
    #     person = MagicMock()
    #     person.destination_floor = 5
    #     return person

    @pytest.fixture
    def mock_person_factory(self) -> Callable[[int], MagicMock]:
        def _person_gen(destination_floor: int) -> MagicMock:
            person: MagicMock = MagicMock(spec=Person)
            cast(Person, person)._dest_floor = destination_floor  # pylint: disable=protected-access # type: ignore[attr-defined]
            return person
        return _person_gen

    @pytest.fixture
    def elevator(
        self,
        mock_logger_provider: MagicMock,
        mock_elevator_bank: MagicMock,
        mock_config: MagicMock,
        mock_cosmetics_config: MagicMock,
    ) -> Elevator:
        return Elevator(
            mock_logger_provider,
            mock_elevator_bank,
            h_cell=5,
            min_floor=1,
            max_floor=10,
            config=mock_config,
            cosmetics_config=mock_cosmetics_config,
        )

    def test_initial_state(self, elevator: Elevator) -> None:
        """Test that elevator initializes with correct values"""
        assert elevator.state == ElevatorState.IDLE
        assert elevator.current_floor_int == 1
        assert elevator.min_floor == 1
        assert elevator.max_floor == 10
        assert elevator.avail_capacity == 15
        assert elevator.is_empty

    def test_set_destination_floor_up(self, elevator: Elevator) -> None:
        """Test setting destination floor and direction updates"""
        # The elevator defaults to floor 1
        elevator.set_destination_floor(5)
        assert elevator.destination_floor == 5
        assert elevator.nominal_direction == VerticalDirection.UP

    def test_set_destination_floor_down(self, elevator: Elevator) -> None:
        elevator.testing_set_current_floor(4)
        elevator.set_destination_floor(2)
        assert elevator.destination_floor == 2
        assert elevator.nominal_direction == VerticalDirection.DOWN

    def test_set_destination_floor_same_floor(self, elevator: Elevator) -> None:
        # Setup: The elevator defaults to floor 1, this will change the state of nominal_direction
        elevator.set_destination_floor(3)
        assert elevator.nominal_direction == VerticalDirection.UP

        # Test destination on same floor
        elevator.testing_set_current_floor(2)
        elevator.set_destination_floor(2)  # Already on floor 2
        assert elevator.nominal_direction == VerticalDirection.STATIONARY

    def test_set_invalid_destination_floor(self, elevator: Elevator) -> None:
        """Test that setting invalid destination floor raises ValueError"""
        with pytest.raises(ValueError):
            elevator.set_destination_floor(15)  # Above max floor

        with pytest.raises(ValueError):
            elevator.set_destination_floor(0)  # Below min floor

    def test_update_idle_to_moving(self, elevator: Elevator) -> None:
        """Test transition from IDLE to MOVING state"""
        # Set up conditions for transition
        elevator.testing_set_state(ElevatorState.IDLE)
        elevator.set_destination_floor(5)  # Set a destination above current floor

        # Update the elevator
        elevator.update(1.0)

        # Check if state transitioned correctly
        assert elevator.state == ElevatorState.MOVING

    def test_update_moving_to_arrived(self, elevator: Elevator) -> None:
        """Test transition from MOVING to ARRIVED state when reaching destination"""
        # Set up conditions for transition
        elevator.testing_set_state(ElevatorState.MOVING)
        elevator.set_destination_floor(2)  # Set a destination
        elevator.testing_set_current_floor(1.9)  # Almost at destination
        elevator.testing_set_motion_direction(VerticalDirection.UP)

        # Update the elevator - should reach destination
        elevator.update(0.2)

        # Check if state transitioned correctly
        assert elevator.state == ElevatorState.ARRIVED

    def test_passengers_who_want_off_current_floor(self, elevator: Elevator) -> None:
        """Test filtering passengers by destination floor"""
        # Elevator starts on floor one (see test_initial_state above)
        passenger_current_floor: Person = cast(Person, MagicMock(spec=Person))
        passenger_current_floor._dest_floor = 1  # pylint: disable=protected-access # type: ignore[attr-defined]

        passenger_another_floor: Person = cast(Person, MagicMock(spec=Person))
        passenger_another_floor._dest_floor = 5  # pylint: disable=protected-access # type: ignore[attr-defined]

        elevator.testing_set_passengers([passenger_another_floor, passenger_current_floor])
        who_wants_off: List[Person] = elevator.passengers_who_want_off()

        assert len(who_wants_off) == 1
        assert who_wants_off[0] == passenger_current_floor

    @pytest.mark.parametrize(
        "current_floor,direction,expected_floors",
        [
            (3, VerticalDirection.UP, [5, 7]),
            (5, VerticalDirection.DOWN, [3, 1]),
            (2, VerticalDirection.STATIONARY, []),
            (1, VerticalDirection.DOWN, []),  # At min floor going down
            (7, VerticalDirection.UP, []),  # At max floor going up
            (4, VerticalDirection.UP, [5, 7]),  # From middle floor
        ],
    )
    def test_get_passenger_destinations_by_direction(
        self,
        elevator: Elevator,
        mock_person_factory: Callable[[int], MagicMock],
        current_floor: int,
        direction: VerticalDirection,
        expected_floors: List[int],
    ) -> None:
        """Test getting sorted destinations in the direction of 'direction' """
        elevator.testing_set_current_floor(current_floor)
        dest_floors: List[int] = [1, 3, 5, 7]

        passengers: List[Person] = [mock_person_factory(floor) for floor in dest_floors]
        elevator.testing_set_passengers(passengers)

        actual_floors: List[int] = elevator.get_passenger_destinations_in_direction(current_floor, direction)
        assert expected_floors == actual_floors
