#test_el_bank_requests.py

from typing import Final

import pytest

from mytower.game.elevator_bank import ElevatorBank
from mytower.game.types import VerticalDirection

# test_el_bank_requests.py
class TestRequestElevator:
    VALID_FLOORS: Final = [1, 5, 10] # bottom, middle, top, keep in sync with the conftest.py
    DIRECTIONS: Final = [VerticalDirection.UP, VerticalDirection.DOWN]
    INVALID_FLOORS: Final =  [-1, 0, 11, 100]
    
    @pytest.mark.parametrize("floor", VALID_FLOORS)
    @pytest.mark.parametrize("direction", DIRECTIONS)
    def test_request_elevator_valid_floor(self, elevator_bank: ElevatorBank, floor: int, direction: VerticalDirection) -> None: 
        """Test that requesting an elevator on valid floors (boundary and middle) stores the request correctly"""
        
        # This should pass w/o raising an exception
        elevator_bank.request_elevator(floor, direction)
        
        requests: Final[set[VerticalDirection]] = elevator_bank.get_requests_for_floor(floor)
        assert direction in requests
        assert len(requests) == 1
        
        for other_floor in range(elevator_bank.min_floor, elevator_bank.max_floor + 1, 1):
            if other_floor == floor:
                continue # Obviously, THIS floor won't be 0 
            assert len(elevator_bank.get_requests_for_floor(other_floor)) == 0 # all the other floors should be empty
         
        
    @pytest.mark.parametrize("floor", VALID_FLOORS)
    @pytest.mark.parametrize("direction", DIRECTIONS)
    def test_request_multiple_directions_same_floor(self, elevator_bank: ElevatorBank, floor: int, direction: VerticalDirection) -> None: 
        """Test that regardless of floor, multiple button presses yield only two (i.e. both) buttons pressed"""
        
        # This should pass w/o raising an exception
        elevator_bank.request_elevator(floor, direction)
        
        # Let's make sure it behaves like a set
        elevator_bank.request_elevator(floor, VerticalDirection.UP)
        elevator_bank.request_elevator(floor, VerticalDirection.DOWN)
        
        assert len(elevator_bank.get_requests_for_floor(floor)) == 2
    
    
    @pytest.mark.parametrize("direction", DIRECTIONS)
    def test_request_same_direction_multiple_floors(self, elevator_bank: ElevatorBank, direction: VerticalDirection) -> None:
        """There should be 1 request on each of the `VALID_FLOORS`, regardless of direction"""
        
        # This should pass w/o raising an exception
        for req_floor in TestRequestElevator.VALID_FLOORS:
            elevator_bank.request_elevator(req_floor, direction)
            
        for tgt_floor in TestRequestElevator.VALID_FLOORS:
            requests: set[VerticalDirection] = elevator_bank.get_requests_for_floor(tgt_floor)
            assert direction in requests
            assert len(requests) == 1
    
    
    @pytest.mark.parametrize("invalid_floor", INVALID_FLOORS)
    @pytest.mark.parametrize("direction", DIRECTIONS)
    def test_request_invalid_floor_raises_error(self, elevator_bank: ElevatorBank, invalid_floor: int, direction: VerticalDirection) -> None:
        """There should be an exception when you request a bogus floor"""
        
        with pytest.raises((ValueError)):  # Not sure which exception it throws
            elevator_bank.request_elevator(invalid_floor, direction)

    def test_request_invalid_direction_raises_error(self, elevator_bank: ElevatorBank, floor: int = 5) -> None:
        with pytest.raises(KeyError):
            elevator_bank.request_elevator(floor, VerticalDirection.STATIONARY)
            
# class TestRequestClearing:
    # Tests for when requests get fulfilled/cleared
    # This might involve some elevator state simulation
    # Let's return to this as an integration test