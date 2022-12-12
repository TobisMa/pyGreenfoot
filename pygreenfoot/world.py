from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, DefaultDict, Iterable, Iterator, List, Set, Type
from vectormath import Vector2Array

from pygreenfoot.actor import Actor


class World(metaclass=ABCMeta):
    
    __slots__ = ("__size", "world_bounding", "__field_size", "__objects", "__existing_object_types", \
        "__render_order")
    
    
    def __init__(self, width: int, height: int, field_size: int, world_bounding: bool = True) -> None:
        self.__size = Vector2Array(width, height)
        self.__field_size = field_size
        self.world_bounding = world_bounding
        self.__render_order: List[Type[Actor]] = []
        self.__objects: DefaultDict[Type[Actor], Set[Actor]] = DefaultDict(set)
        self.__existing_object_types = set()
        
    def add_to_world(self, game_object: "Actor") -> None:
        """Adds an actor to this world instance

        Args:
            actor (Actor): The actor which will be added to this world instance

        Raises:
            TypeError: if the passed argument is not inheriting from pygreenfoot.Actor
        """
        if not isinstance(game_object, Actor):
            raise TypeError("Only subclasses of Actor can be added to world")
        self.__objects[type(game_object)].add(game_object)
        self.__existing_object_types.add(type(game_object))
        game_object.on_world_add(self)
        
    @property
    def width(self) -> int:
        return int(self.__size.x)
    
    @property
    def height(self) -> int:
        return int(self.__size.y)
    
    @property
    def field_size(self) -> int:
        return self.__field_size
    
    def _calc_frame(self) -> None:
        self.act()
        done: Set[Type[Actor]] = set()
        for object_type in self.__render_order:
            done.add(object_type)
            for game_object in self.__objects[object_type]:
                game_object.act()
        
        for object_type in set(self.__objects) - done:
            done.add(object_type)
            for game_object in self.__objects[object_type]:
                game_object.act()
            
    
    @abstractmethod
    def act(self) -> None:
        raise NotImplementedError("act method needs to be implemented")
    
    
    @classmethod
    def set_render_order(cls, render_order: Iterable) -> None:
        cls.__render_order = list(render_order)
        
    @classmethod
    def get_render_order(cls) -> List[Type[Actor]]:
        return cls.__render_order
    