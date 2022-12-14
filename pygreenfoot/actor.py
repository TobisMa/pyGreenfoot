import os
import pygame
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Optional, Union
from .math_helper import FULL_DEGREES_ANGLE


if TYPE_CHECKING:
    from pygreenfoot.world import World

class Actor(metaclass=ABCMeta):
    
    __slots__ = ("__id", "__image", "__pos", "__rot", "__size", "__pos_delta")
    __game_object_count = 0
    
    def __init__(self, x: int = 0, y: int = 0, rotation: int = 0) -> None:
        self.__id = self.__game_object_count
        Actor.__game_object_count += 1
        self.__image: Optional[pygame.Surface] = None
        self.__pos = [x, y]
        self.__size = [0, 0]
        self.__rot = rotation % FULL_DEGREES_ANGLE
        self.__pos_delta = [0, 0]
        
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
    
    @property
    def image(self) -> Optional[pygame.Surface]:
        return self.__image
    
    @image.setter
    def image(self, img) -> None:
        self.set_image(img)
    
    def set_image(self, filename_or_image: Union[str, pygame.Surface]) -> None:  # type: ignore
        if isinstance(filename_or_image, str):
            filename_or_image = os.path.join("images", filename_or_image)
            if not os.access(filename_or_image, os.F_OK):
                raise FileNotFoundError("File \"" + filename_or_image + "\" does not exist")
            filename_or_image: pygame.Surface = pygame.image.load(filename_or_image)
        
        else:
            filename_or_image = pygame.Surface((self.x, self.y), surface=filename_or_image)
        
        # filename_or_image = pygame.transform.smoothscale(filename_or_image, (self.width, self.height))
        filename_or_image = pygame.transform.rotate(filename_or_image, self.rot)
        self.__image = filename_or_image
        
    @property
    def x(self) -> int:
        """
        x-coordinate of the object using transform
        """
        return self.__pos[0]
    
    @x.setter
    def x(self, value: int) -> None:  # sourcery skip: remove-unnecessary-cast
        self.__pos[0] = int(value)
    
    @property
    def y(self) -> int:
        """
        y-coordinate of the object using transform
        """
        return self.__pos[1]
    
    @y.setter
    def y(self, value: int) -> None:  # sourcery skip: remove-unnecessary-cast
        self.__pos[1] = int(value)
        
    @property
    def rot(self) -> float:
        return self.__rot

    @rot.setter
    def rot(self, value: float) -> None:
        if self.__image is not None:
            pygame.transform.rotate(self.__image, value)
        self.__rot = value % FULL_DEGREES_ANGLE
        
    @property
    def width(self) -> int:
        return self.__size[0]
    
    @width.setter
    def width(self, value: int) -> None:
        self.set_size(value, self.height)
    
    @property
    def height(self) -> int:
        return self.__size[1]
    
    @height.setter
    def height(self, value: int) -> None:
        self.set_size(self.width, value)
        
    def set_size(self, width: int, height: int) -> None:
        # sourcery skip: remove-unnecessary-cast
        self.__size = [int(width), int(height)]
        if self.image is not None:
            self.__pos_delta = [x // 2 for x in self.__size]
            self.__image = pygame.transform.smooth_scale(self.image, self.__size)
        
    def repaint(self, screen: pygame.Surface) -> None:
        if self.__image:
            pos = [
                self.__pos_delta[0] + self.x,
                self.__pos_delta[1] + self.y
            ]
            screen.blit(self.__image, pos)
    