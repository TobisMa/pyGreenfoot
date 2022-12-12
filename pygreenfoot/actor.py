from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pygreenfoot.world import World

from pygreenfoot.transform import Transform


class Actor(Transform, metaclass=ABCMeta):
    
    __slots__ = ("__id", )
    __game_object_count = 0
    
    def __init__(self) -> None:
        Transform.__init__(self)
        self.__id = self.__game_object_count
        Actor.__game_object_count += 1
        
    def on_world_add(self, world: "World") -> None:
        """Called when object is added to scene

        Args:
            scene (Scene): the scene the object is added to
        """
        pass
    
    def __hash__(self) -> int:
        return self.__id
    
    @abstractmethod
    def act(self) -> None:
        """
        Method executed once per frame when the/a world with this actor is currently set
        """
        raise NotImplementedError("act method needs to be implemented")
    
    def get_world(self) -> "World":
        """Get the current set world

        Returns:
            World: thw world which is currently loaded
        """
        from pygreenfoot.application import Application
        return Application().current_world