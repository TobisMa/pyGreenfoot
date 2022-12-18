from math import cos, degrees, atan2, radians, sin
import os
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Generator, Optional, Tuple, Type, Union

import pygame

from .math_helper import FULL_DEGREES_ANGLE, limit_value
from .image import Image

if TYPE_CHECKING:
    from .world import World
    from .application import Application

class Actor(metaclass=ABCMeta):
    
    __slots__ = ("__id", "__image", "__pos", "__rot", "__size", "__app")
    __game_object_count = 0
    
    def __init__(self, x: int = 0, y: int = 0, rotation: int = 0) -> None:
        from .application import Application  # prevent circular import
        self.__id = self.__game_object_count
        Actor.__game_object_count += 1
        self.__image: Image = Image(pygame.Surface((10, 10)))
        self.__pos = [x, y]
        self.__rot = rotation % FULL_DEGREES_ANGLE
        self.__app: "Application" = Application.get_app()
        
    def on_world_add(self, world: "World") -> None:
        """Called when object is added to scene

        Args:
            scene (Scene): the scene the object is added to
        """
        pass
    
    def on_world_remove(self) -> None:
        """
        TODO making comment
        """
        pass
    
    def __hash__(self) -> int:
        return self.__id
    
    @abstractmethod
    def act(self) -> None:
        """
        Method executed once per frame when the/a world with this actor is currently set
        """
        raise NotImplementedError("act method needs to be implemented and may not be from this class")
    
    def get_world(self) -> "World":
        """Get the current set world

        Returns:
            World: thw world which is currently loaded
        """
        from pygreenfoot.application import Application
        return self.__app.current_world
    
    # TODO property or function     
    @property
    def image(self) -> "Image":
        return self.__image
    
    @image.setter
    def image(self, img: Union["Image", str]) -> None:
        self.set_image(img if isinstance(img, str) else img._surface)
    
    def set_image(self, filename_or_image: Union[str, pygame.surface.Surface]) -> None:  # type: ignore
        if isinstance(filename_or_image, str):
            path = os.path.join("images", filename_or_image)
            if not os.access(path, os.F_OK):
                raise FileNotFoundError("File \"" + path + "\" does not exist")
            filename_or_image: pygame.surface.Surface = pygame.image.load(path)
        
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
        try:
            world = self.get_world()
        except ValueError:
            pass
        else:
            if world.world_bounding:
                self.__pos[0] = limit_value(self.__pos[0], 0, world.width - 1)
                self.__pos[1] = limit_value(self.__pos[1], 0, world.height - 1)
        
    @property
    def rot(self) -> float:
        return self.__rot

    @rot.setter
    def rot(self, value: float) -> None:
        self.__rot = value % FULL_DEGREES_ANGLE
        if self.__image is not None:
            self.__image._set_rot(self.__rot)
        
    def repaint(self) -> None:
        world = self.get_world()
        if self.image is not None:
            rel_pos = self.image._rel_pos
            pos = [
                self.x * world.cell_size + max(0, (world.cell_size - self.image.width)) + rel_pos[0],
                self.y * world.cell_size + max(0, (world.cell_size - self.image.height)) + rel_pos[1]
                
            ]
            screen = world._surface
            screen.blit(self.image._surface, pos)
    
    @property
    def _rect(self) -> pygame.Rect:
        world = self.get_world()
        return pygame.Rect(self.x * world.cell_size, self.y * world.cell_size, self.image.width, self.image.height)
    
    def get_intersecting_actors(self, type_: Optional[Type["Actor"]]) -> Generator["Actor", None, None]:
        actors = self.get_world().get_actors_generator(type_)
        for a in actors:
            if a._rect.colliderect(self._rect):
                yield a
    
    def get_actors_in_range(self, radius: int, type_: Optional[Type["Actor"]] = None) -> Generator["Actor", None, None]:
        actors = self.get_world().get_actors_generator(type_)
        for a in actors:
            dx = a.x - self.x
            dx *= dx
            dy = a.y - self.y
            dy *= dy
            if dx + dy <= radius ** 2:
                yield a
                
    def get_actors_at_offset(self, dx: int, dy: int, type_: Optional[Type["Actor"]]) -> Generator["Actor", None, None]:
        yield from self.get_world().get_objects_at_generator(self.x + dx, self.y + dy, type_)
    
    def get_neighbours(self, cells: int, diagonal: bool = False, type_: Optional[Type["Actor"]] = None) -> Generator["Actor", None, None]:
        if diagonal:
            yield from self.get_actors_in_range(cells * self.get_world().cell_size, type_)
        else:
            actors = self.get_world().get_actors(type_)
            for a in actors:
                if abs(a.x - self.x) <= cells or abs(a.y - self.y) <= cells:
                    yield a
    
    def is_at_edge(self) -> bool:
        return not self.get_world()._rect.contains(self._rect)
    
    def intersects(self, actor: "Actor") -> bool:
        return bool(actor._rect.colliderect(self._rect))
    
    def is_touching(self, type_: Type["Actor"]) -> bool:
        actors = self.get_world().get_actors_generator(type_)
        for a in actors:
            if a == self:
                continue
            elif self.intersects(a):
                return True
        return False
    
    def remove_touching(self, type_: Type["Actor"], fail_silently: bool = False) -> None:
        world = self.get_world()
        actors = world.get_actors_generator(type_)
        remove = None
        for a in actors:
            if a == self:
                continue
            elif self.intersects(a):
                remove = a
                break
        
        if remove is not None:
            world.remove_from_world(remove)
        elif not fail_silently:
            raise RuntimeError("Not touching ")
        
    def turn_towards(self, x: int, y: int) -> None:
        # TODO check math
        self.rot = degrees(atan2(y - self.y, x - self.x))
        
    def set_position(self, x: int, y: int) -> None:
        self.__pos = [x, y]
        self.__check_boundary()
    
    def move(self, steps: int = 1) -> None:
        self.x += round(steps * cos(self.rot))
        self.y += round(steps * sin(self.rot))