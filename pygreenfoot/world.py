import pygame
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, DefaultDict, Iterable, Iterator, List, Set, Type
from vectormath import Vector2Array

from pygreenfoot.actor import Actor


class World(metaclass=ABCMeta):
    
    __slots__ = ("__size", "world_bounding", "__cell_size", "__objects", 
                 "__existing_object_types", "__act_order", "__paint_order")
    
    
    def __init__(self, width: int, height: int, field_size: int, world_bounding: bool = True) -> None:
        self.__size = Vector2Array(width, height)
        self.__cell_size: int = field_size
        self.world_bounding: bool = world_bounding
        self.__act_order: List[Type[Actor]] = []
        self.__paint_order: List[Type[Actor]] = []
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
        """width of this world instance

        Returns:
            int: the world width in cells
        """
        return int(self.__size.x)
    
    @property
    def height(self) -> int:
        """height of this world instance

        Returns:
            int: the world height in cells
        """
        return int(self.__size.y)
    
    @property
    def cell_size(self) -> int:
        """how large one cell (always quadratic) is in pixel

        Returns:
            int: the width and height of the cell
        """
        return self.__cell_size
    
    def _calc_frame(self, screen: pygame.Surface) -> None:
        self.__act_cycle()
        self.__draw_cycle(screen)
        
    def __draw_cycle(self, screen: pygame.Surface) -> None:
        done: Set[Type[Actor]] = set()
        for object_type in self.__paint_order:
            done.add(object_type)
            for game_object in self.__objects[object_type]:
                game_object.repaint(screen)
        
        for object_type in set(self.__objects) - done:
            done.add(object_type)
            for game_object in self.__objects[object_type]:
                game_object.repaint(screen)
                
                
    def __act_cycle(self) -> None:
        self.act()
        done: Set[Type[Actor]] = set()
        for object_type in self.__act_order:
            done.add(object_type)
            for game_object in self.__objects[object_type]:
                game_object.act()
        
        for object_type in set(self.__objects) - done:
            done.add(object_type)
            for game_object in self.__objects[object_type]:
                game_object.act()
            
    
    @abstractmethod
    def act(self) -> None:
        """Called once per frame by the main application"""
        raise NotImplementedError("act method needs to be implemented")
    
    def set_act_order(self, act_order: Iterable[Type[Actor]]) -> None:
        """Sets the order in which the actor's act methods are called

        Args:
            act_order (Iterable): _description_
        """
        self.__act_order = list(act_order)
        
    def get_act_order(self) -> List[Type[Actor]]:
        return self.__act_order
    
    def set_paint_order(self, paint_order: Iterable[Type[Actor]]) -> None:
        self.__paint_order = list(paint_order)
        
    def get_paint_order(self) -> List[Type[Actor]]:
        return self.__paint_order
    