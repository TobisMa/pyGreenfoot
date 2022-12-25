from typing import Tuple

import pygame

from . import keys
from .__types import _Key, _MouseButton
from .application import Application


class PyGreenfoot:
    @staticmethod
    def is_key_pressed(key: _Key) -> bool:  # sourcery skip: low-code-quality
        """Is the given key pressed?

        Args:
            key (_Key): the key to check for. can be either a specific string or a pygreenfoot.keys constant

        Returns:
            bool: True if the given key is pressed, otherwise False
        """
        app = Application.get_app()
        if isinstance(key, str):
            if len(key) == 1:
                if key.isdigit() or key.islower():
                    key = getattr(keys, "K_" + key)
                elif key.isupper():
                    shift = any(app.get_key_states(keys.K_LSHIFT, keys.K_RSHIFT))
                    return shift and app.get_key_states(getattr(keys, "K_" + key.lower()))[0]
                elif key == ".":
                    return app.get_key_states(keys.K_PERIOD)[0]
                elif key == ",":
                    return app.get_key_states(keys.K_COMMA)[0]
                elif key == "-":
                    return app.get_key_states(keys.K_MINUS)[0]
                elif key == "#":
                    return app.get_key_states(keys.K_HASH)[0]
                elif key == "<":
                    return app.get_key_states(keys.K_LESS)[0]
                elif key == "^":
                    return app.get_key_states(keys.K_CARET)[0]
            else:
                if len(key) in range(2, 4) and key.startswith(("f", "F")):
                    return app.get_key_states(getattr(keys, "K_" + key.upper()))[0]
                
                key = key.lower()
                if key == "space":
                    return app.get_key_states(keys.K_SPACE)[0]
                elif key == "shift":
                    return any(app.get_key_states(keys.K_LSHIFT, keys.K_RSHIFT))
                elif key == "escape":
                    return app.get_key_states(keys.K_ESCAPE)[0]
                elif key == "enter":
                    return app.get_key_states(keys.K_RETURN)[0]
                elif key in ("ctrl", "strg"):
                    return any(app.get_key_states(keys.K_LCTRL, keys.K_RCTRL))
                elif key == "left":
                    return app.get_key_states(keys.K_LEFT)[0]
                elif key == "right":
                    return app.get_key_states(keys.K_RIGHT)[0]
                elif key == "up":
                    return app.get_key_states(keys.K_UP)[0]
                elif key == "down":
                    return app.get_key_states(keys.K_DOWN)[0]
                elif key == "meta":
                    return any(app.get_key_states(keys.K_LMETA, keys.K_RMETA))
                elif key == "alt":
                    return app.get_key_states(keys.K_LALT)[0]
                elif key == "alt gr":
                    return app.get_key_states(keys.K_RALT)[0]
                elif key == "backspace":
                    return app.get_key_states(keys.K_BACKSPACE)[0]
                elif key == "delete":
                    return app.get_key_states(keys.K_DELETE)[0]
                elif key == "insert":
                    return app.get_key_states(keys.K_INSERT)[0]
                elif key == "tab":
                    return app.get_key_states(keys.K_TAB)[0]
                elif key == "print":
                    return app.get_key_states(keys.K_PRINT)[0]
                
            if not isinstance(key, int):
                raise ValueError("invalid key: %s" % key)
        
        return app.get_key_states(key)[0]
    
    @staticmethod
    def is_mouse_button_pressed(button: _MouseButton) -> bool:
        """Returns if the given mouse button is pressed.
        Existing values are 1 (left), 2 (mouse wheel click), 3 (right).

        Args:
            button (_MouseButton): A Mousebutton value 1, 2 or 3.

        Raises:
            ValueError: if the given mouse button is not existing

        Returns:
            bool: True if the given mouse button is pressed, otherwise False.
        """
        button -= 1
        if button not in range(3):
            raise ValueError("The only valid mouse buttons are: 1, 2, 3")
        app = Application.get_app()
        states = app.get_mouse_states()
        buttons = states.buttons
        return buttons[button] != 0
    
    @staticmethod
    def get_mouse_wheel() -> int:
        """How far the mouse wheel was moved between the current and last frame.
        Negative values mean the mouse wheel was moved downwards, positive values 
        mean the mouse wheel was moved upwards

        Returns:
            int: an integer indicating whether the mouse wheel was moved and how far
        """
        return Application.get_app().get_mouse_states().mouse_wheel
    
    @staticmethod
    def get_mouse_position() -> Tuple[int, int]:
        """Return the mouse position (in cells). This function might return odd numbers if the cursor has left the window.
        To ensure that the mouse position is correct you can check that using PyGreenfoot.is_mouse_in_window().

        Returns:
            Tuple[int, int]: the coordinates of the mouse cursor in the form (x, y)
        """
        app = Application.get_app()
        pos = pygame.mouse.get_pos()
        dp = app.delta_pos
        pos = (pos[0] - dp[0], pos[1] - dp[1])
        return pos[0] // app.current_world.cell_size, pos[1] // app.current_world.cell_size
    
    @staticmethod
    def is_mouse_in_window() -> bool:
        """Checks whether the mouse is within the window or not.

        Returns:
            bool: True if the mouse is hovering over the window, otherwise False.
        """
        return Application.get_app().is_mouse_in_window()
    
    @staticmethod
    def set_game_frames(fps: int) -> None:
        """sets the fps limit for the application

        Args:
            fps (int): the new limit (defaults to 60)
        """
        Application.get_app().fps = fps
        