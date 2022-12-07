from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pygreenfoot.scene import Scene

from pygreenfoot.transform import Transform


class GameObject(Transform, metaclass=ABCMeta):
    
    __slots__ = ("__id")
    __game_object_count = 0
    
    def __init__(self) -> None:
        Transform.__init__(self)
        self.__id = self.__game_object_count
        GameObject.__game_object_count += 1
        
    def on_scene_add(self, scene: "Scene") -> None:
        """Called when object is added to scene

        Args:
            scene (Scene): the scene the object is added to
        """
        pass
    
    def __hash__(self) -> int:
        return self.__id
    
    @abstractmethod
    def act(self) -> None:
        raise NotImplementedError("act method needs to be implemented")