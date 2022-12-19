import os
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from functools import cached_property
from time import time
from typing import (DefaultDict, Dict, Generator, Iterable, List, Optional,
                    Set, Tuple, Type, Union)

import pygame

from . import keys
from .actor import Actor
from .color import WHITE, Color
from .image import Image


class World(metaclass=ABCMeta):
    
    __slots__ = ("__size", "world_bounding", "__cell_size", "__objects", "__texts",
                 "__existing_object_types", "__act_order", "__paint_order", "__world_speed"
                 "__background", "__canvas", "__half_cell", "__app", "running", "__last_time")
    
    
    def __init__(self, width: int, height: int, cell_size: int, world_bounding: bool = True) -> None:
        from .application import Application
        self.__size = (width, height)
        self.__cell_size: int = cell_size
        self.world_bounding: bool = world_bounding
        self.__act_order: List[Type[Actor]] = []
        self.__paint_order: List[Type[Actor]] = []
        self.__objects: DefaultDict[Type[Actor], Set[Actor]] = defaultdict(set)
        self.__existing_object_types = set()
        self.__background: Optional[Image] = None
        self.__canvas: pygame.surface.Surface = pygame.Surface((width * cell_size, height * cell_size))
        self.__half_cell: int = self.__cell_size // 2
        self.__app = Application.get_app()
        self.__texts: Dict[Tuple[int, int], Tuple[pygame.surface.Surface, Tuple[int, int], str]] = {}
        self.running = True
        self.world_speed = 0
        self.__last_time = time()
        
    def add_to_world(self, game_object: "Actor", x: int, y: int) -> None:
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
        game_object.set_position(x, y)
        game_object.on_world_add(self)
        
    @cached_property
    def width(self) -> int:
        """width of this world instance

        Returns:
            int: the world width in cells
        """
        return int(self.__size[0])
    
    @cached_property
    def height(self) -> int:
        """height of this world instance

        Returns:
            int: the world height in cells
        """
        return int(self.__size[1])
    
    @cached_property
    def cell_size(self) -> int:
        """how large one cell (always quadratic) is in pixel

        Returns:
            int: the width and height of the cell
        """
        return self.__cell_size
    
    def _calc_frame(self, screen: pygame.surface.Surface) -> None:
        cur_time = time()
        if cur_time - self.__last_time <= self.world_speed:
            return
        
        elif self.running:
            self.__act_cycle()
            self.repaint()
            screen.blit(self.__canvas, (0, 0))
            
        elif not self.running and self.__app.get_key_states(keys.K_SPACE)[0]:
            self.running = True
        
        self.__last_time = time()
                
    def repaint(self) -> None:
        if self.__background is not None:
            self.__canvas.blit(self.__background._surface, (0, 0))
            
        done: Set[Type[Actor]] = set()
        for object_type in self.__paint_order:
            done.add(object_type)
            for game_object in self.__objects[object_type]:
                game_object.repaint()
        
        for object_type in set(self.__objects) - done:
            done.add(object_type)
            for game_object in self.__objects[object_type]:
                game_object.repaint()
        
        for text_surface, pos, _ in self.__texts.values():
            self.__canvas.blit(text_surface, pos)
                
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
    
    def set_background(self, filename_or_image: Union[str, pygame.Surface]) -> None:
        if isinstance(filename_or_image, str):
            path = os.path.join("images", filename_or_image)
            if not os.access(path, os.F_OK):
                raise FileNotFoundError("File \"" + path + "\" not found")

            image: pygame.surface.Surface = pygame.image.load(path)
            
        else:
            image: pygame.surface.Surface = filename_or_image
        
        bg = pygame.Surface((self.width * self.cell_size, self.height * self.cell_size))
        wr = range(0, self.cell_size * self.width + self.cell_size, self.cell_size)
        hr = range(0, self.cell_size * self.height + self.cell_size, self.cell_size)
        
        for x in wr:
            for y in hr:
                bg.blit(image.copy(), (x, y))
        
        self.__background = Image(bg)
        
    def get_background_image(self) -> Image:
        if self.__background is None:
            s = pygame.Surface((self.__cell_size * self.width, self.__cell_size * self.height))
            s.fill(WHITE._pygame)
            return Image(s)
        return self.__background
            
    def get_color_at(self, x: int, y: int) -> Color:
        return Color.from_pygame_color(
            self.__canvas.get_at(  # type: ignore
                (x * self.__cell_size + self.__half_cell, y * self.__cell_size + self.__half_cell)
            )
        )
    
    def get_actors(self, type_: Optional[Type[Actor]] = None) -> List[Actor]:
        return list(self.get_actors_generator(type_))
        
    def get_actors_generator(self, type_: Optional[Type[Actor]] = None) -> Generator[Actor, None, None]:
        if type_ is None:
            for actor_set in self.__objects.values():
                yield from actor_set
        else:
            yield from self.__objects[type_]
                
    def get_objects_at(self, x: int, y: int, type_: Optional[Type[Actor]] = None) -> List[Actor]:
        return list(self.get_objects_at_generator(x, y, type_))
    
    def get_objects_at_generator(self, x: int, y: int, type_: Optional[Type[Actor]] = None) -> Generator[Actor, None, None]:        
        area = pygame.Rect(x * self.__cell_size, y * self.__cell_size, self.__cell_size, self.__cell_size)
        if type_ is None:
            for actor_type in self.__objects:
                yield from self.get_objects_at_generator(x, y, actor_type)
        else:
            for actor in self.__objects[type_]:
                if actor._rect.colliderect(area):
                    yield actor
                    
    def remove_from_world(self, *actors: Actor) -> None:
        for actor in actors:
            actor.on_world_remove()
            self.__objects[type(actor)].remove(actor)
                        
    def number_of_actors(self) -> int:
        return sum(len(actor_set) for actor_set in self.__objects.values())

    def show_text(self, text: Optional[str], x: int, y: int) -> None:
        # if self.__texts.get((x, y)) is None:
        if text is None:
            self.__texts.pop((x, y), None)
            return
        
        font = pygame.font.SysFont(pygame.font.get_default_font(), 26)
        width, height = font.size(text)
        px: int = x * self.__cell_size + self.__half_cell - width // 2
        py: int = y * self.__cell_size + self.__half_cell - height // 2
        font_surface: pygame.surface.Surface = font.render(text, True, (0, 0, 0))
        self.__texts[(x, y)] = font_surface, (px, py), text
        
    def get_text_at(self, x: int, y: int) -> Optional[str]:
        value = self.__texts.get((x, y))
        return None if value is None else value[2]
    
    
    @property
    def _rect(self) -> pygame.Rect:
        return pygame.Rect(0, 0, self.width * self.cell_size, self.height * self.cell_size)
    
    @property
    def _surface(self) -> pygame.surface.Surface:
        return self.__canvas