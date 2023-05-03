from abc import abstractmethod
import functools
from typing import Any, Optional
from pygreenfoot import Actor, Image
from pygreenfoot.application import Application
from pygreenfoot.math_helper import FULL_DEGREES_ANGLE


def _screen_update(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        res = f(*args, **kwargs)
        Application.get_app().update(False)
        return res
    return wrapper

class InitActor(Actor):
    
    """
    The InitActor class provides an actor for teaching. 
    It provides an init method to put your code in and 
    executes this method excactly once. This actor refreshes the screen
    as soon as this actor caused a screen change as opposed to the normal
    actors.
    
    
    This counter works like an actor and needs to be added to the active world to be visible
    """

    __slots__ = ("__iter",)
    __screen_update_functions = ["set_image", "remove_touching", "set_position", "move"]
    
    def __init__(self, rotation: int = 0, image: Optional[Image] = None) -> None:
        Actor.__init__(self, rotation, image)
        self.__iter: int = 0

        for m in self.__screen_update_functions:
            setattr(self, m, _screen_update(getattr(self, m)))

    @abstractmethod
    def init(self) -> None:
        raise NotImplementedError("subclasses of InitActor must override the init method")
    
    def act(self) -> None:
        if self.__iter == 1:
            self.init()
        if self.__iter <= 2:
            self.__iter += 1

    def update_screen(self) -> None:
        """
        Updates the screen
        """
        Application.get_app().update(False)
