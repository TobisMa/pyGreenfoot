import pygame
from typing import Tuple

from .__types import _MouseButtonStates


class MouseInfo:
    
    __slots__ =  ("__mouse_wheel",)
        
    def __init__(self, mouse_wheel: int) -> None:
        self.__mouse_wheel = mouse_wheel
        
    @property
    def mouse_wheel(self) -> int:
        """an integer indicating the amount of the mouse wheel moves were made.
        Negative values mean downwards, positive values mean upwards

        Returns:
            int: how far the mouse wheel was moved between the last and current frame
        """
        return self.__mouse_wheel
    
    @property
    def buttons(self) -> _MouseButtonStates:
        from .application import Application
        if Application.get_app().is_running():
            return pygame.mouse.get_pressed(num_buttons=3)  # type: ignore
        return 0, 0, 0
        
    @property
    def pos(self) -> Tuple[int, int]:
        x, y = pygame.mouse.get_pos()
        return x, y