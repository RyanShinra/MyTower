import gc
import time
from dataclasses import dataclass
from typing import Callable


@dataclass
class GCStats:
    """Snapshot of garbage collection statistics"""
    gen0_collections: int
    gen1_collections: int
    gen2_collections: int
    gen0_objects: int
    gen1_objects: int
    gen2_objects: int
    timestamp: float


class GCProfiler:
    """Monitor GC behavior during rendering loops"""
    
    def __init__(self) -> None:
        self._start_stats: GCStats | None = None
        self._end_stats: GCStats | None = None
    
    def start(self) -> None:
        """Begin profiling session"""
        gc.collect()  # Clear baseline
        self._start_stats = self._capture_stats()
    
    def stop(self) -> None:
        """End profiling session"""
        self._end_stats = self._capture_stats()
    
    def _capture_stats(self) -> GCStats:
        """Capture current GC state"""
        counts = gc.get_count()
        stats = gc.get_stats()
        
        return GCStats(
            gen0_collections=gc.get_stats()[0]['collections'],
            gen1_collections=gc.get_stats()[1]['collections'],
            gen2_collections=gc.get_stats()[2]['collections'],
            gen0_objects=counts[0],
            gen1_objects=counts[1],
            gen2_objects=counts[2],
            timestamp=time.time()
        )
    
    def report(self) -> str:
        """Generate human-readable report"""
        if not self._start_stats or not self._end_stats:
            return "Profiler not run"
        
        duration = self._end_stats.timestamp - self._start_stats.timestamp
        gen0_delta = self._end_stats.gen0_collections - self._start_stats.gen0_collections
        gen1_delta = self._end_stats.gen1_collections - self._start_stats.gen1_collections
        gen2_delta = self._end_stats.gen2_collections - self._start_stats.gen2_collections
        
        return f"""
GC Profile ({duration:.2f}s):
  Gen 0: {gen0_delta} collections ({gen0_delta/duration:.1f}/sec)
  Gen 1: {gen1_delta} collections ({gen1_delta/duration:.1f}/sec)
  Gen 2: {gen2_delta} collections ({gen2_delta/duration:.1f}/sec)
  
  Current objects:
    Gen 0: {self._end_stats.gen0_objects}
    Gen 1: {self._end_stats.gen1_objects}
    Gen 2: {self._end_stats.gen2_objects}
"""


def profile_function(func: Callable[[], None], iterations: int = 1000) -> str:
    """Profile a function's GC behavior"""
    profiler = GCProfiler()
    profiler.start()
    
    for _ in range(iterations):
        func()
    
    profiler.stop()
    return profiler.report()
