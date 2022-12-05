from abc import ABCMeta
from typing import TYPE_CHECKING, DefaultDict, Iterable, Iterator, Set
from vectormath import Vector2Array

from pygreenfoot.gameObject import GameObject


class Scene(metaclass=ABCMeta):
    
    __slots__ = ("__size", "world_bounding", "__field_size", "__objects")
    
    def __init__(self, width: int, height: int, field_size: int, world_bounding: bool = True) -> None:
        self.__size = Vector2Array(width, height)
        self.__field_size = field_size
        self.world_bounding = world_bounding
        self.__objects = DefaultDict(set)
        
    def add_to_scene(self, game_object: "GameObject") -> None:
        if not isinstance(game_object, GameObject):
            raise TypeError("Only subclasses of GameObject")
        self.__objects[type(game_object)].add(game_object)
        game_object.on_scene_add(self)
        
    @property
    def width(self) -> int:
        return int(self.__size.x)
    
    @property
    def height(self) -> int:
        return int(self.__size.y)
    
    @property
    def field_size(self) -> int:
        return self.__field_size