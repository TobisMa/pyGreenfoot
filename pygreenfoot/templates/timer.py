from math import floor
import time
from typing import Dict, Hashable


class Timer:
    
    __slots__ = ("__tags", )
    
    def __init__(self) -> None:
        self.__tags: Dict[Hashable, int] = {}
        
    def mark(self, tag: Hashable = None) -> None:
        """Sets a timer (in nanoseconds) on tag. A tag does not need to be provided.

        Args:
            tag (Hashable, optional): the tag to set the timer on. If already set, resets the timer. Defaults to None.
        """
        self.__tags[tag] = time.perf_counter_ns()
        
    def elapsed_ns(self, tag: Hashable = None) -> int:
        """Return the elapsed time on the given tag (in nanoseconds)

        Args:
            tag (Hashable, optional): the tag to look for. Defaults to None.

        Returns:
            int: the elapsed time in nanoseconds
        """
        current_time = time.perf_counter_ns()
        return current_time - self.__tags[tag]