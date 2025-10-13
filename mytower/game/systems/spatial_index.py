from collections import defaultdict
from typing import Dict, List

class FloorSpatialIndex:
    """Fast lookup: which people are on which floor"""
    def __init__(self):
        self._people_by_floor: Dict[int, List[PersonAgent]] = defaultdict(list)
    
    def update(self, people: List[PersonAgent]) -> None:
        """Rebuild index (cheap - just sorting pointers)"""
        self._people_by_floor.clear()
        for p in people:
            self._people_by_floor[p.current_floor].append(p)
    
    def get_people_on_floor(self, floor: int) -> List[PersonAgent]:
        """O(1) lookup instead of O(n) scan"""
        return self._people_by_floor[floor]
