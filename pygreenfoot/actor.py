from asyncio import get_child_watcher
import math
import os
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Optional, Union

import pygame

from .math_helper import FULL_DEGREES_ANGLE, limit_value
from .image import Image

if TYPE_CHECKING:
    from pygreenfoot.world import World

class Actor(metaclass=ABCMeta):
    
    __slots__ = ("__id", "__image", "__pos", "__rot", "__size")
    __game_object_count = 0
    
    def __init__(self, x: int = 0, y: int = 0, rotation: int = 0) -> None:
        self.__id = self.__game_object_count
        Actor.__game_object_count += 1
        self.__image: Optional[Image] = Image(pygame.Surface((1,1)))
        self.__pos = [x, y]
        self.__rot = rotation % FULL_DEGREES_ANGLE
        
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
        return Application.get_app().current_world
    
    @property
    def image(self) -> "Image":
        return self.__image
    
    @image.setter
    def image(self, img: Union["Image", str]) -> None:
        self.set_image(img if isinstance(img, str) else img._surface)
    
    def set_image(self, filename_or_image: Union[str, pygame.Surface]) -> None:  # type: ignore
        if isinstance(filename_or_image, str):
            path = os.path.join("images", filename_or_image)
            if not os.access(path, os.F_OK):
                raise FileNotFoundError("File \"" + path + "\" does not exist")
            filename_or_image: pygame.Surface = pygame.image.load(path)
        
        else:
            filename_or_image = pygame.Surface((self.x, self.y), surface=filename_or_image)
        
        filename_or_image = pygame.transform.rotate(filename_or_image, self.rot)
        image = Image(filename_or_image)
        self.__image = image
        
    @property
    def x(self) -> int:
        """
        x-coordinate of the object using transform
        """
        return self.__pos[0]
    
    @x.setter
    def x(self, value: int) -> None:  # sourcery skip: remove-unnecessary-cast
        self.__pos[0] = int(value)
        self.__check_boundary()
    
    @property
    def y(self) -> int:
        """
        y-coordinate of the object using transform
        """
        return self.__pos[1]
    
    @y.setter
    def y(self, value: int) -> None:  # sourcery skip: remove-unnecessary-cast
        self.__pos[1] = int(value)
        self.__check_boundary()
        
    def __check_boundary(self) -> None:
        world = self.get_world()
        if world.world_bounding:
            self.__pos[0] = limit_value(self.__pos[0], 0, world.width - 1)
            self.__pos[1] = limit_value(self.__pos[1], 0, world.height - 1)
        
    @property
    def rot(self) -> float:
        return self.__rot

    @rot.setter
    def rot(self, value: float) -> None:
        if self.__image is not None:
            pygame.transform.rotate(self.__image, value)
        self.__rot = value % FULL_DEGREES_ANGLE
        
    def repaint(self, screen: pygame.Surface, world: "World") -> None:
        if self.image is not None:
            pos = [
                max(0, world.cell_size - self.image.width) // 2 + self.x * world.cell_size,
                max(0, world.cell_size - self.image.height) // 2 + self.y * world.cell_size
            ]
            screen.blit(self.image._surface, pos)
    