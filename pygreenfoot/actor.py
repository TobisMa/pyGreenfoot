import os
from abc import ABCMeta, abstractmethod
from math import atan2, cos, degrees, sin
from typing import TYPE_CHECKING, Generator, List, Optional, Tuple, Type, Union

import pygame

from .image import Image
from .math_helper import FULL_DEGREES_ANGLE, limit_value

if TYPE_CHECKING:
    from .application import Application
    from .world import World

class Actor(metaclass=ABCMeta):
    
    __slots__ = ("__id", "__image", "__pos", "__rot", "__size", "__app")
    __game_object_count = 0
    
    def __init__(self, rotation: int = 0) -> None:
        """Construct an Actor. The object will have a default image.

        Args:
            rotation (int, optional): the initial rotation of the Actor. Defaults to 0.
        """
        from .application import Application  # prevent circular import
        self.__id = self.__game_object_count
        Actor.__game_object_count += 1
        self.__image: Image = Image(pygame.Surface((10, 10)))
        self.__pos: List[int] = [x, y]
        self.__rot = rotation % FULL_DEGREES_ANGLE
        self.__app: "Application" = Application.get_app()
        
    def on_world_add(self, world: "World") -> None:
        """Called when this actor is added to a world.

        Args:
            world (World): the world this actor is added to
        """
        pass
    
    def on_world_remove(self) -> None:
        """
        Called when this actor is removed from the world it was added to
        """
        pass
    
    def __hash__(self) -> int:
        return self.__id
    
    @abstractmethod
    def act(self) -> None:
        """
        Method executed once per frame when the/a world with this actor is currently set on the application
        This method must be implemented in subclasses.
        """
        raise NotImplementedError("act method needs to be implemented and may not be from this class")
    
    def get_world(self) -> "World":
        """Get the current active world

        Returns:
            World: the world which is currently active
        """
        return self.__app.current_world
    
    # TODO property or function     
    @property
    def image(self) -> "Image":
        """
        the image representing the actor (without rotation)
        """
        return self.__image
    
    @image.setter
    def image(self, img: Union["Image", str]) -> None:
        self.set_image(img if isinstance(img, str) else img._surface)
    
    def set_image(self, filename_or_image: Union[str, pygame.surface.Surface]) -> None:  # type: ignore
        """Set the image of the actor

        Args:
            filename_or_image (Union[str, pygame.surface.Surface]): a string to the image file (default directory: 'images') or an Surfaces object from pygame

        Raises:
            FileNotFoundError: if the given argument is a string, but an invalid filename
        """
        if isinstance(filename_or_image, str):
            path = os.path.join("images", filename_or_image)
            if not os.access(path, os.F_OK):
                raise FileNotFoundError("File \"" + path + "\" does not exist")
            filename_or_image: pygame.surface.Surface = pygame.image.load(path)
        
        else:
            filename_or_image = pygame.Surface((self.x, self.y), surface=filename_or_image)
        
        filename_or_image = pygame.transform.rotate(filename_or_image, self.rotation)
        image = Image(filename_or_image)
        self.__image = image
        
    @property
    def x(self) -> int:
        """
        x-coordinate of the object using transform
        """
        self.__check_boundary()
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
        self.__check_boundary()
        return self.__pos[1]
    
    @y.setter
    def y(self, value: int) -> None:  # sourcery skip: remove-unnecessary-cast
        self.__pos[1] = int(value)
        self.__check_boundary()
        
        
    def __check_boundary(self) -> None:
        try:
            world = self.get_world()
        except ValueError:
            return
        
        if world.world_bounding:
            self.__pos[0] = limit_value(self.__pos[0], 0, world.width - 1)
            self.__pos[1] = limit_value(self.__pos[1], 0, world.height - 1)
        
    @property
    def rotation(self) -> float:
        """
        the rotation of the actor
        """
        return self.__rot

    @rotation.setter
    def rotation(self, value: float) -> None:
        self.__rot = value % FULL_DEGREES_ANGLE
        if self.__image is not None:
            self.__image._set_rot(self.__rot)
        
    def repaint(self) -> None:
        """
        draws the actor anew in the world
        """
        self.__check_boundary()
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
    
    
    def get_intersecting_actors(self, type_: Optional[Type["Actor"]]) -> List["Actor"]:
        """this method returns the same as `get_intersecting_actors_generator` as a list. 
        This method has to be used if actors are getting removed during iteration.
        
        Returns:
            type_: all the intersecting actors of type type_
        """
        return list(self.get_intersecting_actors_generator(type_))

    def get_intersecting_actors_generator(self, type_: Optional[Type["Actor"]]) -> Generator["Actor", None, None]:
        """Returns a generator object to iterate over all actors intersecting this one.
        The rectangular representation of the actors will be used for collision detection 

        Yields:
            Actor: an intersecting actor of type type_
        """
        actors = self.get_world().get_actors_generator(type_)
        for a in actors:
            if a._rect.colliderect(self._rect):
                yield a
    
    def get_actors_in_range(self, radius: int, type_: Optional[Type["Actor"]] = None) -> List["Actor"]:
        """Returns a list of all actors within range of this one of type type_. None is treated as wildcard"""
        return list(self.get_actors_in_range_generator(radius, type_))
        
    def get_actors_in_range_generator(self, radius: int, type_: Optional[Type["Actor"]] = None) -> Generator["Actor", None, None]:
        """A generator iterating over all actors of type type_ within radius. None is treated as wildcard

        Yields:
            Actor: all actors of type type_ within radius
        """
        actors = self.get_world().get_actors_generator(type_)
        for a in actors:
            dx = a.x - self.x
            dx *= dx
            dy = a.y - self.y
            dy *= dy
            if dx + dy <= radius ** 2:
                yield a
    
    def get_actors_at_offset(self, dx: int, dy: int, type_: Optional[Type["Actor"]]) -> List["Actor"]:
        """
        Returns the same as get_actors_at_offset_generator but converted to a list
        """
        return list(self.get_actors_at_offset_generator(dx, dy, type_))        
    
    def get_actors_at_offset_generator(self, dx: int, dy: int, type_: Optional[Type["Actor"]]) -> Generator["Actor", None, None]:
        """Returns all objects at the relative offset (dx, dy) of this actor's coordinates.

        Yields:
            Actor: an actor which is at that relative offset
        """
        yield from self.get_world().get_objects_at_generator(self.x + dx, self.y + dy, type_)
    
    def get_neighbours(self, cells: int, diagonal: bool = False, type_: Optional[Type["Actor"]] = None) -> List["Actor"]:
        """Returns the same as get_neighbours_generator but as a list instead of a generator object

        Returns:
            List[Actor]: all actors considered as neighbours
        """
        return list(self.get_neighbours_generator(cells, diagonal, type_))
    
    def get_neighbours_generator(self, cells: int, diagonal: bool = False, type_: Optional[Type["Actor"]] = None) -> Generator["Actor", None, None]:
        """Returns all actors considered to be neighbours. if diagonal=True it will be the same as get_actors_in_range(cells, type_)
        if diagonal is False it will consider an actor as neighbours if either x or y have the same value and the absolute difference between
        x or y is less than or equals the specified cells

        Yields:
            Actor: actors considered to be neighbours
        """
        if diagonal:
            yield from self.get_actors_in_range(cells * self.get_world().cell_size, type_)
        else:
            actors = self.get_world().get_actors(type_)
            for a in actors:
                if abs(a.x - self.x) <= cells or abs(a.y - self.y) <= cells:
                    yield a
    
    # TODO "AT EDGE"
    def is_at_edge(self) -> bool:
        """if the actor is outside of the world. Only possible if actors are not bound to the world

        Returns:
            bool: True if the actor is outside of the world
        """
        return not self.get_world()._rect.contains(self._rect)
    
    def intersects(self, actor: "Actor") -> bool:
        """Checks for graphical intersection between two actors. Rotation is not considered

        Args:
            actor (Actor): the other actor

        Returns:
            bool: True if the actors intersect each other, False otherwise.
        """
        return bool(actor._rect.colliderect(self._rect))
    
    def is_touching(self, type_: Type["Actor"]) -> bool:
        """Checks if the actor touches an actor of given type type_

        Args:
            type_ (Type[Actor]): the type of the other actor

        Returns:
            bool: True if at least one actor of the given type_ was found.
        """
        actors = self.get_world().get_actors_generator(type_)
        for a in actors:
            if a == self:
                continue
            elif self.intersects(a):
                return True
        return False
    
    def remove_touching(self, type_: Type["Actor"], fail_silently: bool = False) -> None:
        """Removes the first found actor of type type_ which is being touched by this actor

        Args:
            type_ (Type[Actor): the type the other actor shall have
            fail_silently (bool, optional): If set to True, no error will be raised in case no actor of type_ is touched. Defaults to False.

        Raises:
            RuntimeError: _description_
        """
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
            raise RuntimeError("Not touching an actor of type %s" % type_.__name__)
        
    def turn_towards(self, x: int, y: int) -> None:
        """Turns the actor towards the given coordinates

        Args:
            x (int): x coordinate of the direction
            y (int): y coordinate of the direction
        """
        self.rotation = degrees(atan2(y - self.y, x - self.x))
        
    def set_position(self, x: int, y: int) -> None:
        """Sets the position of the actor to (x, y)

        Args:
            x (int): the new x coordinate
            y (int): the new y coordinate
        """
        self.__pos = [x, y]
        self.__check_boundary()
    
    def move(self, steps: int = 1) -> None:
        """Move into the direction the actor is currently facing

        Args:
            steps (int, optional): the amount of cells the actor shall go. In case of a rotation like 30° the steps will be rounded. Defaults to 1.
        """
        self.x += round(steps * cos(self.rotation))
        self.y += round(steps * sin(self.rotation))