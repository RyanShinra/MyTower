
# This is here for historical purposes. I'll probably delete it in a commit or two



class TestElevator: 

    # def test_initial_state(self, elevator: Elevator) -> None:
    #     """Test that elevator initializes with correct values"""
    #     assert elevator.state == ElevatorState.IDLE
    #     assert elevator.current_floor_int == 1
    #     assert elevator.min_floor == 1
    #     assert elevator.max_floor == 10
    #     assert elevator.avail_capacity == 15
    #     assert elevator.is_empty

    # def test_set_destination_floor_up(self, elevator: Elevator) -> None:
    #     """Test setting destination floor and direction updates"""
    #     # The elevator defaults to floor 1
    #     elevator.set_destination_floor(5)
    #     assert elevator.destination_floor == 5
    #     assert elevator.nominal_direction == VerticalDirection.UP

    # def test_set_destination_floor_down(self, elevator: Elevator) -> None:
    #     elevator.testing_set_current_floor(4)
    #     elevator.set_destination_floor(2)
    #     assert elevator.destination_floor == 2
    #     assert elevator.nominal_direction == VerticalDirection.DOWN

    # def test_set_destination_floor_same_floor(self, elevator: Elevator) -> None:
    #     # Setup: The elevator defaults to floor 1, this will change the state of nominal_direction
    #     elevator.set_destination_floor(3)
    #     assert elevator.nominal_direction == VerticalDirection.UP

    #     # Test destination on same floor
    #     elevator.testing_set_current_floor(2)
    #     elevator.set_destination_floor(2)  # Already on floor 2
    #     assert elevator.nominal_direction == VerticalDirection.STATIONARY

    # def test_set_invalid_destination_floor(self, elevator: Elevator) -> None:
    #     """Test that setting invalid destination floor raises ValueError"""
    #     with pytest.raises(ValueError):
    #         elevator.set_destination_floor(15)  # Above max floor

    #     with pytest.raises(ValueError):
    #         elevator.set_destination_floor(0)  # Below min floor

    # def test_update_idle_stays_idle(self, elevator: Elevator) -> None:
    #     """Test transition from IDLE to MOVING state"""
    #     # Set up conditions for transition
    #     elevator.testing_set_state(ElevatorState.IDLE)
    #     elevator.set_destination_floor(5)  # Set a destination above current floor

    #     # Update the elevator
    #     elevator.update(1.0)

    #     # Check if state transitioned correctly
    #     assert elevator.state == ElevatorState.IDLE

    # def test_update_ready_to_move_to_moving(self, elevator: Elevator) -> None:
    #     """Test transition from IDLE to MOVING state"""
    #     # Set up conditions for transition
    #     elevator.testing_set_state(ElevatorState.READY_TO_MOVE)
    #     elevator.set_destination_floor(5)  # Set a destination above current floor

    #     # Update the elevator
    #     elevator.update(1.0)

    #     # Check if state transitioned correctly
    #     assert elevator.state == ElevatorState.MOVING
        
    # def test_update_ready_to_move_to_still_not_moving(self, elevator: Elevator) -> None:
    #     """Test transition from IDLE to MOVING state"""
    #     # Set up conditions for transition
    #     elevator.testing_set_state(ElevatorState.READY_TO_MOVE)
    #     elevator.set_destination_floor(1)  # Set a destination at same floor

    #     # Update the elevator
    #     elevator.update(1.0)

    #     # Check if state transitioned correctly
    #     assert elevator.state == ElevatorState.IDLE

    # def test_update_moving_to_arrived(self, elevator: Elevator) -> None:
    #     """Test transition from MOVING to ARRIVED state when reaching destination"""
    #     # Set up conditions for transition
    #     elevator.testing_set_state(ElevatorState.MOVING)
    #     elevator.set_destination_floor(2)  # Set a destination
    #     elevator.testing_set_current_floor(1.9)  # Almost at destination
    #     elevator.testing_set_motion_direction(VerticalDirection.UP)

    #     # Update the elevator - should reach destination
    #     elevator.update(0.2)

    #     # Check if state transitioned correctly
    #     assert elevator.state == ElevatorState.ARRIVED

    # def test_passengers_who_want_off_current_floor(
    #     self, elevator: Elevator, mock_person_factory: Callable[[int], MagicMock]
    # ) -> None:
    #     """Test filtering passengers by destination floor"""
    #     # Elevator starts on floor one (see test_initial_state above)
    #     passenger_current_floor: Person = mock_person_factory(1)
    #     passenger_another_floor: Person = mock_person_factory(5)

    #     elevator.testing_set_passengers([passenger_another_floor, passenger_current_floor])
    #     who_wants_off: List[Person] = elevator.passengers_who_want_off()

    #     assert len(who_wants_off) == 1
    #     assert who_wants_off[0] == passenger_current_floor

    # @pytest.mark.parametrize(
    #     "current_floor,direction,expected_floors",
    #     [
    #         (3, VerticalDirection.UP, [5, 7]),
    #         (5, VerticalDirection.DOWN, [3, 1]),
    #         (2, VerticalDirection.STATIONARY, []),
    #         (1, VerticalDirection.DOWN, []),  # At min floor going down
    #         (7, VerticalDirection.UP, []),  # At max floor going up
    #         (4, VerticalDirection.UP, [5, 7]),  # From middle floor
    #     ],
    # )
    # def test_get_passenger_destinations_by_direction(
    #     self,
    #     elevator: Elevator,
    #     mock_person_factory: Callable[[int], MagicMock],
    #     current_floor: int,
    #     direction: VerticalDirection,
    #     expected_floors: List[int],
    # ) -> None:
    #     """Test getting sorted destinations in the direction of 'direction' """
    #     elevator.testing_set_current_floor(current_floor)
    #     dest_floors: List[int] = [1, 3, 5, 7]

    #     passengers: List[Person] = [mock_person_factory(floor) for floor in dest_floors]
    #     elevator.testing_set_passengers(passengers)

    #     actual_floors: List[int] = elevator.get_passenger_destinations_in_direction(current_floor, direction)
    #     assert expected_floors == actual_floors

    # def test_passengers_boarding(self, elevator: Elevator, mock_elevator_bank: MagicMock) -> None:
    #     """Test passengers boarding the elevator"""
    #     # Create a mock person
    #     mock_person = MagicMock()
    #     mock_person.destination_floor = 5

    #     # Setup elevator bank to return our mock person
    #     mock_elevator_bank.try_dequeue_waiting_passenger.return_value = mock_person

    #     # Set elevator to loading state and update
    #     elevator.testing_set_state(ElevatorState.LOADING)
    #     elevator.testing_set_nominal_direction(VerticalDirection.UP)
    #     elevator.update(1.1)  # Time > passenger_loading_time

    #     # Check that the passenger was added
    #     current_passengers: Final[List[Person]] = elevator.testing_get_passengers()
    #     assert len(current_passengers) == 1
    #     assert current_passengers[0] == mock_person

    #     # Check that elevator asked bank for passenger with correct params
    #     mock_elevator_bank.try_dequeue_waiting_passenger.assert_called_with(
    #         elevator.current_floor_int, VerticalDirection.UP
    #     )

    pass