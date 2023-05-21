from typing import Tuple

import pygame

from .__types import _MouseButtonStates


class MouseInfo:
    
    __slots__ =  ("__mouse_wheel", "__app")
        
    def __init__(self, mouse_wheel: int) -> None:
        from .application import Application
        self.__mouse_wheel = mouse_wheel
        self.__app: Application = Application.get_app()
        
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
        """
        Returns the pressed state of the left button, middle wheel and right button

        Returns:
            _MouseButtonStates: the mouse button states in a 3-length-tuple
        """
        if self.__app.is_running():
            return pygame.mouse.get_pressed(num_buttons=3)  # type: ignore
        return 0, 0, 0
        
    @property
    def pos(self) -> Tuple[int, int]:
        """
        The position of the cursor or the position of the cursor before it left the window.

        Returns:
            Tuple[int, int]: (x, y)
        """
        x, y = pygame.mouse.get_pos()
        return x, y
    
    @property
    def mouse_in_window(self) -> bool:
        return self.__app.is_mouse_in_window()
