from abc import ABCMeta
from collections import defaultdict
from functools import cached_property
from time import time
from typing import (
    DefaultDict,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)

import pygame

from . import get_resource_path, keys
from .actor import Actor
from .color import Color
from .font import Font, Text
from .image import Image
from .__types import _ActorType


class World(metaclass=ABCMeta):
    __slots__ = (
        "__size",
        "world_bounding",
        "__cell_size",
        "__objects",
        "__texts",
        "__existing_object_types",
        "__act_order",
        "__paint_order",
        "__world_speed" "__background",
        "__canvas",
        "__half_cell",
        "__app",
        "running",
        "__last_time",
    )

    DEFAULT_FONT: Font = Font(
        Font.get_default_font(), 26
    )  # pygame.font initialized in __init__.py

    def __init__(
        self, width: int, height: int, cell_size: int, world_bounding: bool = True
    ) -> None:
        from .application import Application

        self.__size = (width, height)
        self.__cell_size: int = cell_size
        self.world_bounding: bool = world_bounding
        self.__act_order: List[Type[Actor]] = []
        self.__paint_order: List[Type[Actor]] = []
        self.__objects: DefaultDict[Type[Actor], Set[Actor]] = defaultdict(set)
        self.__existing_object_types = set()
        self.__background: Optional[Image] = None
        self.__canvas: pygame.surface.Surface = pygame.Surface(
            (width * cell_size, height * cell_size)
        )
        self.__half_cell: int = self.__cell_size // 2
        self.__app = Application.get_app()
        self.__texts: Dict[Tuple[int, int], Tuple[Text, Tuple[int, int]]] = {}
        self.running: bool = True
        self.world_speed: float = self.__app.default_world_speed
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

    def _check_world_time(self) -> bool:
        """
        Returns True if the next frame shall be exexcuted

        Returns:
            bool: True if the next act_cycle shall be exexcuted or False if the world time still needs to be awaited
        """
        return time() >= self.world_speed + self.__last_time

    def _calc_frame(self) -> None:
        """
        Runs the act cylces if necessary
        """
        if self.running and self._check_world_time():
            self.__act_cycle()
            self.repaint()
            self.__last_time = time()

        elif not self.running and self.__app.get_key_states(keys.K_SPACE)[0]:
            self.running = True

    def repaint(self, only_background: bool = False) -> None:
        """
        Redraws the whole world
        """
        if self.__background is not None:
            self.__canvas.blit(self.__background._surface, (0, 0))
        else:
            self.__canvas.fill([0, 0, 0])

        if only_background:
            return

        done: Set[Type[Actor]] = set()
        for object_type in self.__paint_order:
            done.add(object_type)
            for game_object in self.__objects[object_type]:
                game_object.repaint()

        for object_type in set(self.__objects) - done:
            done.add(object_type)
            for game_object in self.__objects[object_type]:
                game_object.repaint()

        for text, pos in self.__texts.values():
            self.__canvas.blit(text._surface, pos)

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

    def act(self) -> None:
        """
        Called once per frame by the main application.
        Subclasses can override this method.
        The default does nothing
        """
        pass

    def set_act_order(self, *act_order: Type[Actor]) -> None:
        """Sets the order in which the actor's act methods are called

        Args:
            act_order (Iterable): an iterable of types of actors to specify in which order they should be drawn.
                It is not possible to influence the draw order of two actors with the same type.
        """
        self.__act_order = list(act_order)

    def get_act_order(self) -> List[Type[Actor]]:
        """Returns the current set act order

        Returns:
            List[Type[Actor]]: the order the objects will be sorted. Types of actors which are not within the returned list will be drawn in an random order.
        """
        return self.__act_order

    def set_paint_order(self, *paint_order: Type[Actor]) -> None:
        """Sets the paint order of actor types. It is not possible to influence the draw order of two actors with the same type

        Args:
            paint_order (Iterable[Type[Actor]]): an iterable of types of actors
        """
        self.__paint_order = list(paint_order)

    def get_paint_order(self) -> List[Type[Actor]]:
        """Returns the paint order

        Returns:
            List[Type[Actor]]: the current paint order. If a type of actor is missing within this list this type of actor will
                be drawn after all listed types at an certain point within each frame
        """
        return self.__paint_order

    def set_background(
        self,
        filename_or_image: Union[str, pygame.Surface],
        scale_to_cell_size: bool = False,
    ) -> None:
        """Set an background image for the world. If the image is too small for the world it will be repeated in vertical
        and horizontal direction until it covers all cells of the world.

        Args:
            filename_or_image (Union[str, pygame.Surface]): a str used as path (default directory is 'images') or an pygame.Surface object
            scale_to_cell_size (bool): scales the image to the cell size if True. Default is False.

        Raises:
            FileNotFoundError: if the argument is a string, but an invalid filename
        """
        if isinstance(filename_or_image, str):
            path = get_resource_path(filename_or_image, "image")

            image: pygame.surface.Surface = pygame.image.load(path)

        else:
            image: pygame.surface.Surface = filename_or_image

        bg = pygame.Surface((self.width * self.cell_size, self.height * self.cell_size))
        wr = range(0, self.cell_size * self.width + self.cell_size, image.get_width())
        hr = range(0, self.cell_size * self.height + self.cell_size, image.get_height())

        for x in wr:
            for y in hr:
                bg.blit(image.copy(), (x, y))

        self.__background = Image(bg)

    def get_background_image(self) -> Image:
        """Returns the rendered background image

        Returns:
            Image: the background image drawn on the surface
        """
        if self.__background is None:
            s = pygame.Surface(
                (self.__cell_size * self.width, self.__cell_size * self.height)
            )
            s.fill(Color.WHITE._pygame)
            return Image(s)
        return self.__background

    def get_color_at(self, x: int, y: int) -> Color:
        """Return the color at the center of the cell (x, y). Objects drawn on the background are considered.

        Args:
            x (int): the x coordinate of the cell
            y (int): the y coordinate of the cell

        Returns:
            Color: the color at the center of the cell
        """
        return Color.from_pygame_color(
            self.__canvas.get_at(  # type: ignore
                (
                    x * self.__cell_size + self.__half_cell,
                    y * self.__cell_size + self.__half_cell,
                )
            )
        )

    def get_actors(self, type_: Optional[Type[_ActorType]] = None) -> List[_ActorType]:
        """Return all actors currently existing in the world

        Args:
            type_ (Optional[Type[Actor]], optional): an argument to filter for a specific type of actors. Defaults to None.

        Returns:
            List[Actor]: the actors having type type_ or all actors within the world in case type_=None
        """
        return list(self.get_actors_generator(type_))

    def get_actors_generator(
        self, type_: Optional[Type[_ActorType]] = None
    ) -> Generator[_ActorType, None, None]:
        """
        the same as get_actors but returns a generator object
        """
        if type_ is None or type_ == Actor:
            for actor_set in self.__objects.values():
                yield from actor_set  # type: ignore
        else:
            bases = self._get_subclasses(type_)
            for base in bases:
                yield from self.__objects[base]  # type: ignore

    def _get_subclasses(self, type_: Type[Actor]) -> Generator[Type[Actor], None, None]:
        """
        Retrieves the subclasses of a given superclass type_

        Args:
            type_ (Type[ActorType_]): common base class of subclasses

        Returns:
            Generator[Type[Actor], None, None]: a generator of all the subclasses having type_ somewhere above them in their inheritance tree
        """
        yield type_
        for subclass in type_.__subclasses__():
            if issubclass(subclass, Actor):
                yield from self._get_subclasses(subclass)

    def get_objects_at(
        self, x: int, y: int, type_: Optional[Type[_ActorType]] = None
    ) -> List[_ActorType]:
        """Return all objects at the position (x, y) having the type type_

        Args:
            x (int): the x coorindate of the actor
            y (int): the y coordinate of the actor
            type_ (Optional[Type[Actor]], optional): the type the actor must have. Defaults to None.

        Returns:
            List[Actor]: a list of all actors at the position (x, y) having the type type_ or just all types if type_ is None
        """
        return list(self.get_objects_at_generator(x, y, type_))

    def get_objects_at_generator(
        self, x: int, y: int, type_: Optional[Type[_ActorType]] = None
    ) -> Generator[_ActorType, None, None]:
        """
        The same as get_objects_at but returns a generator
        """
        area = pygame.Rect(
            x * self.__cell_size,
            y * self.__cell_size,
            self.__cell_size,
            self.__cell_size,
        )
        if type_ is None:
            for actor_type in self.__objects:
                yield from self.get_objects_at_generator(x, y, actor_type)  # type: ignore
        else:
            for actor in self.__objects[type_]:
                if actor._rect.colliderect(area):
                    yield actor  # type: ignore

    def remove_from_world(self, *actors: Actor) -> None:
        """
        Removes the given actor(s) from the world
        """
        for actor in actors:
            actor.on_world_remove()
            self.__objects[type(actor)].remove(actor)

    def number_of_actors(self) -> int:
        """Counts the actors existing currently in this world

        Returns:
            int: the amount of actors in the world
        """
        return sum(len(actor_set) for actor_set in self.__objects.values())

    def show_text(self, text: Optional[Union[str, Text]], x: int, y: int) -> None:
        """Adds the text to the cell (x, y)

        Args:
            text (Optional[str]): the text to be shown at cell (x, y). If the text is None it will be removed
            x (int): the x position of the cell
            y (int): the y position of the cell
        """
        if text is None:
            self.__texts.pop((x, y), None)
            return

        if isinstance(text, str):
            font = World.DEFAULT_FONT
            width, height = font._pygame.size(text)
        else:
            width, height = text.font._pygame.size(text.display_text)

        px: int = x * self.__cell_size + self.__half_cell - width // 2
        py: int = y * self.__cell_size + self.__half_cell - height // 2

        if isinstance(text, str):
            text: Text = font.get_text(text, Color(0, 0, 0), True)  # type: ignore

        self.__texts[(x, y)] = text, (px, py)

    def get_text_at(self, x: int, y: int) -> Optional[str]:
        """Returns the text at the cell (x, y)

        Args:
            x (int): the x position of the cell
            y (int): the y position of the cell

        Returns:
            Optional[str]: the text at the cell or if no text is found, this function will return None
        """
        value = self.__texts.get((x, y))
        return None if value is None else value[0].display_text

    @property
    def _rect(self) -> pygame.Rect:
        """
        pygame.Rect of the world
        """
        return pygame.Rect(
            0, 0, self.width * self.cell_size, self.height * self.cell_size
        )

    @property
    def _surface(self) -> pygame.surface.Surface:
        """
        The pygame's world surface
        """
        return self.__canvas
