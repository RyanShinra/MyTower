"""
Test cases for elevator idle state fallback search functionality.

These tests verify that an idle elevator will search ALL floors for ANY requests
when directional searches find nothing, ensuring elevators don't stay idle
when passengers are waiting elsewhere in the building.
"""

import pytest
from mytower.game.core.types import ElevatorState, VerticalDirection
from mytower.game.core.units import Blocks, Time
from mytower.game.entities.elevator_bank import ElevatorBank
from mytower.game.entities.elevator import Elevator
from mytower.game.entities.building import Building
from mytower.game.core.config import GameConfig
from mytower.game.utilities.logger import LoggerProvider


class TestIdleElevatorFallbackSearch:
    """Test that idle elevators find requests on distant floors using fallback search"""

    @pytest.fixture
    def setup(self):
        """Create test fixtures"""
        logger_provider = LoggerProvider(log_level=30)  # WARNING level
        config = GameConfig()
        building = Building(logger_provider, width=20)
        
        # Create floors 1-18
        from mytower.game.core.types import FloorType
        for _ in range(18):
            building.add_floor(FloorType.OFFICE)
        
        # Create elevator bank
        bank = ElevatorBank(
            logger_provider=logger_provider,
            building=building,
            horizontal_position=10,
            min_floor=1,
            max_floor=18,
            cosmetics_config=config.elevator_cosmetics
        )
        
        # Create elevator starting at floor 1
        elevator = Elevator(
            logger_provider=logger_provider,
            elevator_bank=bank,
            min_floor=1,
            max_floor=18,
            config=config.elevator,
            cosmetics_config=config.elevator_cosmetics,
            starting_floor=1
        )
        bank.add_elevator(elevator)
        
        return {"bank": bank, "elevator": elevator, "logger_provider": logger_provider}

    def test_idle_elevator_finds_request_below_via_fallback(self, setup):
        """
        Test: Elevator at floor 7 should find UP request at floor 1
        
        Scenario:
        - Elevator is idle at floor 7
        - Floor 1 has an UP request
        - Directional search misses it (searches floors 8-18 for UP, finds nothing)
        - Fallback search should find floor 1
        """
        bank = setup["bank"]
        elevator = setup["elevator"]
        
        # Position elevator at floor 7
        elevator.testing_set_current_vertical_pos(Blocks(7.0))
        elevator.testing_set_state(ElevatorState.IDLE)
        elevator.testing_set_nominal_direction(VerticalDirection.STATIONARY)
        
        # Add request at floor 1 going UP
        bank.request_elevator(1, VerticalDirection.UP)
        
        # Trigger idle update with elapsed timeout
        bank.testing_update_idle_elevator(elevator, elevator.idle_wait_timeout)
        
        # Elevator should transition from IDLE to READY_TO_MOVE
        # and then to MOVING with destination floor 1
        # Let's check the state after the bank processes the ready state
        if elevator.elevator_state == ElevatorState.READY_TO_MOVE:
            bank.testing_update_ready_elevator(elevator)
        
        # Verify elevator has floor 1 as destination
        assert elevator.destination_floor == 1, \
            f"Expected elevator to set destination to floor 1, but got {elevator.destination_floor}"

    def test_idle_elevator_finds_request_above_via_fallback(self, setup):
        """
        Test: Elevator at floor 7 should find DOWN request at floor 12
        
        Scenario:
        - Elevator is idle at floor 7
        - Floor 12 has a DOWN request
        - Directional search misses it (searches floors 8-18 for UP, floors 1-6 for DOWN)
        - Fallback search should find floor 12
        """
        bank = setup["bank"]
        elevator = setup["elevator"]
        
        # Position elevator at floor 7
        elevator.testing_set_current_vertical_pos(Blocks(7.0))
        elevator.testing_set_state(ElevatorState.IDLE)
        elevator.testing_set_nominal_direction(VerticalDirection.STATIONARY)
        
        # Add request at floor 12 going DOWN
        bank.request_elevator(12, VerticalDirection.DOWN)
        
        # Trigger idle update with elapsed timeout
        bank.testing_update_idle_elevator(elevator, elevator.idle_wait_timeout)
        
        # Process ready state if needed
        if elevator.elevator_state == ElevatorState.READY_TO_MOVE:
            bank.testing_update_ready_elevator(elevator)
        
        # Verify elevator has floor 12 as destination
        assert elevator.destination_floor == 12, \
            f"Expected elevator to set destination to floor 12, but got {elevator.destination_floor}"

    def test_idle_elevator_finds_closest_request_via_fallback(self, setup):
        """
        Test: Elevator should choose closest request when multiple requests exist
        
        Scenario:
        - Elevator is idle at floor 7
        - Floor 1 has an UP request
        - Floor 12 has a DOWN request
        - Elevator should choose floor 12 (distance 5) over floor 1 (distance 6)
        """
        bank = setup["bank"]
        elevator = setup["elevator"]
        
        # Position elevator at floor 7
        elevator.testing_set_current_vertical_pos(Blocks(7.0))
        elevator.testing_set_state(ElevatorState.IDLE)
        elevator.testing_set_nominal_direction(VerticalDirection.STATIONARY)
        
        # Add requests at floors 1 and 12
        bank.request_elevator(1, VerticalDirection.UP)
        bank.request_elevator(12, VerticalDirection.DOWN)
        
        # Trigger idle update
        bank.testing_update_idle_elevator(elevator, elevator.idle_wait_timeout)
        
        # Process ready state if needed
        if elevator.elevator_state == ElevatorState.READY_TO_MOVE:
            bank.testing_update_ready_elevator(elevator)
        
        # Verify elevator chose floor 12 (closer)
        assert elevator.destination_floor == 12, \
            f"Expected elevator to set destination to floor 12 (closer), but got {elevator.destination_floor}"

    def test_idle_elevator_stays_idle_when_no_requests(self, setup):
        """
        Test: Elevator should stay idle when no requests exist anywhere
        
        Scenario:
        - Elevator is idle at floor 7
        - No requests on any floor
        - Elevator should remain idle
        """
        bank = setup["bank"]
        elevator = setup["elevator"]
        
        # Position elevator at floor 7
        elevator.testing_set_current_vertical_pos(Blocks(7.0))
        elevator.testing_set_state(ElevatorState.IDLE)
        elevator.testing_set_nominal_direction(VerticalDirection.STATIONARY)
        
        # No requests added
        
        # Trigger idle update
        initial_state = elevator.elevator_state
        bank.testing_update_idle_elevator(elevator, elevator.idle_wait_timeout)
        
        # Elevator should still be idle
        assert elevator.elevator_state == ElevatorState.IDLE or elevator.elevator_state == ElevatorState.READY_TO_MOVE, \
            f"Expected elevator to stay IDLE or transition to READY_TO_MOVE, but got {elevator.elevator_state}"
        
        # If READY_TO_MOVE, process it and check it stays on same floor
        if elevator.elevator_state == ElevatorState.READY_TO_MOVE:
            bank.testing_update_ready_elevator(elevator)
            assert elevator.destination_floor == 7, \
                f"Expected elevator to stay at floor 7, but destination is {elevator.destination_floor}"
