from typing import Tuple


class Color:
    def __init__(self, r: int, g: int, b: int):
        self.r = r
        self.g = g
        self.b = b
        
    @property
    def _pygame(self) -> Tuple[int, int, int]:
        return self.r, self.g, self.b