# game/entities/person_batch_updater.py
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

from __future__ import annotations  # Defer type evaluation

from typing import List
from mytower.game.entities.person import PersonProtocol
from mytower.game.entities.person import PersonState


class PersonBatchUpdater:
    """
    Batch update person positions to reduce method call overhead.
    
    Still OOP for logic, but batched for performance.
    """
    
    def update_walking_people(self, people: List[PersonProtocol], dt: float) -> None:
        """Update all walking people in one pass"""
        # Filter once
        walking = [p for p in people if p.state == PersonState.WALKING_TO_ELEVATOR]
        
        # Update in batch (reduces interpreter overhead)
        for person in walking:
            person.position += person.velocity * dt
            
            if person.reached_elevator():
                person.transition_to_waiting()
    
    def update_waiting_people(self, people: List[PersonProtocol], dt: float) -> None:
        """Check elevator arrivals for all waiting people"""
        # Group by floor first (spatial optimization)
        by_floor: dict[int, List[PersonProtocol]] = {}
        for p in people:
            if p.state == PersonState.WAITING_FOR_ELEVATOR:
                by_floor.setdefault(p.current_floor, []).append(p)
        
        # Process floor-by-floor (cache-friendlier)
        for floor, waiting_group in by_floor.items():
            # Check elevator arrivals once per floor, not per person
            pass  # ...existing code...
    
    def update_all(self, people: List[PersonAgent], dt: float) -> None:
        """Process people in state groups to reduce branching"""
        # Group by state once
        by_state: dict[PersonState, List[PersonAgent]] = {}
        for p in people:
            by_state.setdefault(p.state, []).append(p)
        
        # Update each group with specialized logic
        self._update_walking_batch(by_state.get(PersonState.WALKING_TO_ELEVATOR, []), dt)
        self._update_waiting_batch(by_state.get(PersonState.WAITING_FOR_ELEVATOR, []), dt)