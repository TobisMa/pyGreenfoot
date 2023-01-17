from typing import Tuple

import pygame

__all__ = ("Color",)

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
    
    BLACK: "Color"
    RED: "Color"
    GREEN: "Color"
    BLUE: "Color"
    YELLOW: "Color"
    VIOLET: "Color"
    CYAN: "Color"
    WHITE: "Color"
    GRAY: "Color"

Color.BLACK = Color(0, 0, 0)
Color.RED = Color(255, 0, 0)
Color.GREEN = Color(0, 255, 0)
Color.BLUE = Color(0, 0, 255)
Color.YELLOW = Color(255, 255, 0)
Color.VIOLET = Color(255, 0, 255)
Color.CYAN = Color(0, 255, 255)
Color.WHITE = Color(255, 255, 255)
Color.GRAY = Color(128, 128, 128)
