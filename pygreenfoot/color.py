from typing import Tuple

import pygame

__all__ = ("Color", "BLUE", "GREEN", "RED", "BLACK", "YELLOW", "VIOLET", "CYAN", "WHITE")

class Color:
    def __init__(self, r: int, g: int, b: int):
        self.r = r
        self.g = g
        self.b = b
        
    @property
    def _pygame(self) -> Tuple[int, int, int]:
        return self.r, self.g, self.b
    
    @staticmethod
    def from_pygame_color(color: pygame.Color) -> "Color":
        return Color(color.r, color.g, color.b)


BLACK = Color(0, 0, 0)
RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
YELLOW = Color(255, 255, 0)
VIOLET = Color(255, 0, 255)
CYAN = Color(0, 255, 255)
WHITE = Color(255, 255, 255)
GRAY = Color(128, 128, 128)
