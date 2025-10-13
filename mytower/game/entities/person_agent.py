# game/person_agent.py
# This file is part of MyTower.
#
# MyTower is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MyTower is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of

# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MyTower. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Optional as Opt

from mytower.game.core.units import Blocks
from mytower.game.core.types import VerticalDirection

if TYPE_CHECKING:
    from mytower.game.entities.elevator import Elevator

"""
This is a preliminary design for a Person Agent designed by claude. I'll need to review it before we do anything with it.
"""

class PersonState(Enum):
    """Finite state machine for person behavior"""
    IDLE = auto()               # At home/office, not moving
    WALKING_TO_ELEVATOR = auto()  # Moving to elevator bank
    WAITING_FOR_ELEVATOR = auto() # Queued at elevator bank
    RIDING_ELEVATOR = auto()      # Inside elevator
    WALKING_TO_DESTINATION = auto()  # Moving to final location on floor
    ARRIVED = auto()             # Reached destination


@dataclass(frozen=True, slots=True)
class CachedPath:
    """Pre-computed path for routine travel"""
    origin_floor: int
    destination_floor: int
    elevator_bank_x: Blocks  # Which elevator bank to use
    walk_time: float         # Time to walk to elevator
    
    # Could add: alternate_routes for elevator outages


class PersonAgent:
    """
    Agent-based person with goal-directed behavior.
    
    Design philosophy:
    - Fixed daily routine (home → office, office → home)
    - Cached paths for common routes
    - Simple state machine (not every decision every frame)
    - Batch updates where possible
    """
    
    def __init__(
        self,
        person_id: str,
        home_floor: int,
        work_floor: int,
        work_schedule: tuple[float, float],  # (start_time, end_time)
    ):
        self._person_id = person_id
        self._home_floor = home_floor
        self._work_floor = work_floor
        self._work_schedule = work_schedule
        
        # State
        self._state = PersonState.IDLE
        self._current_floor = home_floor
        self._current_elevator: Opt[Elevator] = None
        
        # Pre-computed paths (cache, not recomputed every frame)
        self._path_to_work: Opt[CachedPath] = None
        self._path_to_home: Opt[CachedPath] = None
        
        # Timing
        self._state_timer = 0.0
        self._next_decision_time = 0.0  # Only make decisions at intervals
    
    def update(self, dt: float, current_time: float) -> None:
        """Update person state - only makes decisions at intervals"""
        
        # Optimization: Don't process every frame
        if current_time < self._next_decision_time:
            self._state_timer += dt
            return
        
        self._next_decision_time = current_time + 1.0  # Decide once per second
        
        match self._state:
            case PersonState.IDLE:
                self._update_idle(current_time)
            case PersonState.WALKING_TO_ELEVATOR:
                self._update_walking_to_elevator(dt)
            case PersonState.WAITING_FOR_ELEVATOR:
                pass  # Handled by elevator system
            case PersonState.RIDING_ELEVATOR:
                pass  # Handled by elevator
            case PersonState.WALKING_TO_DESTINATION:
                self._update_walking_to_destination(dt)
            case PersonState.ARRIVED:
                pass  # Idle at destination
    
    def _update_idle(self, current_time: float) -> None:
        """Check if it's time to go somewhere"""
        start_work, end_work = self._work_schedule
        
        if start_work <= current_time < end_work:
            if self._current_floor != self._work_floor:
                self._begin_journey_to_work()
        else:
            if self._current_floor != self._home_floor:
                self._begin_journey_to_home()
    
    def _begin_journey_to_work(self) -> None:
        """Start going to work - uses cached path"""
        if not self._path_to_work:
            # First time - compute and cache path
            self._path_to_work = self._compute_path(
                self._current_floor, 
                self._work_floor
            )
        
        self._state = PersonState.WALKING_TO_ELEVATOR
        # ...existing code...
    
    def _compute_path(self, from_floor: int, to_floor: int) -> CachedPath:
        """Compute path once, cache for reuse"""
        # Simple heuristic: use nearest elevator bank
        # In real game, consider: distance, wait times, outages
        return CachedPath(
            origin_floor=from_floor,
            destination_floor=to_floor,
            elevator_bank_x=Blocks(10.0),  # Placeholder
            walk_time=5.0
        )
    
    # ...existing code...