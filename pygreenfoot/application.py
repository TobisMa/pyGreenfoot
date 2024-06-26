import os
import sys
import threading
from typing import (
    Any,
    Callable,
    DefaultDict,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

import pygame
from pygreenfoot import get_module_str_import, get_resource_path
from pygreenfoot.color import Color
from pygreenfoot.image import Image

from pygreenfoot.inheritance_tree import create_inheritance_tree

from .__types import _Key
from .mouse_info import MouseInfo
from .sound import Sound
from .world import World
from .math_helper import limit_value


os.environ["SDL_VIDEO_CENTERED"] = "1"
pygame.init()

FirstWorld = TypeVar("FirstWorld", bound=World)


def bool_(value: str) -> Union[str, bool]:
    if value.lower() == "true":
        return True
    elif value.lower() == "false":
        return False
    raise TypeError("Invalid boolean value '%s'" % value)


def signed_int(value: str) -> int:
    v = int(value)
    if v < 0:
        raise TypeError("Negative integer value '%s'")
    return v


def none_value(value) -> bool:
    return value.lower() in ("none", "null", "unset")


def optional_signed_int(value: str) -> Optional[int]:
    return None if none_value(value) else signed_int(value)


def signed_float(value) -> float:
    v = float(value)
    if v < 0:
        raise TypeError("Negative integer value '%s'")
    return v


def window_mode(value):
    return _pygame_screen_modes[value.upper()]


_pygame_screen_modes = {
    "RESIZABLE": pygame.RESIZABLE,
    "FULLSCREEN": pygame.FULLSCREEN,
    "BORDERLESS": pygame.NOFRAME,
    "FIXED": 0,  # NOTE: apparently, no constant for the default exists
}

_config_key_converter: Dict[str, Callable[[str], Any]] = {
    "generateDiagram": bool_,
    "generateImage": bool_,
    "tempPlantumlFile": bool_,
    "diagramFilename": str,
    "diagramFolder": str,
    "imageResourceFolder": str,
    "soundResourceFolder": str,
    "fpsLimit": signed_int,
    "defaultWorldSpeed": signed_float,
    "windowWidth": optional_signed_int,
    "windowHeight": optional_signed_int,
    "windowMode": window_mode,
    "windowModeStartUp": window_mode,
    "firstWorld": str,
    "title": str,
    "icon": str,
    "vsync": bool_
}


class Application:
    __slots__ = (
        "__screen",
        "__world",
        "__running",
        "__keys",
        "__mouse_in_window",
        "__size",
        "__mouse_down",
        "__clock",
        "__fps_limit",
        "__mouse_wheel",
        "__scrollbar",
        "__delta_size",
        "__delta_move",
        "show_scrollbar",
        "__scrollbar_rects",
        "__maximized",
        "__window_exposed",
        "__config",
        "scrollbar_color",
    )

    __instance: Optional["Application"] = None
    __pygame_info = pygame.display.Info()
    __sw = __pygame_info.current_w
    __sh = __pygame_info.current_h

    DEFAULT_CONFIG = {
        "generateDiagram": True,
        "generateImage": True,
        "tempPlantumlFile": False,
        "diagramFilename": "diagram",
        "diagramFolder": "_structure",
        "fpsLimit": 60,
        "imageResourceFolder": "images",
        "soundResourceFolder": "sounds",
        "defaultWorldSpeed": 0,
        "windowWidth": None,
        "windowHeight": None,
        "windowMode": pygame.RESIZABLE,
        "windowStartUpMode": pygame.SRCALPHA,
        "firstWorld": None,
        "title": "PyGreenfoot Game",
        "icon": "wizard.png",
        "vsync": False
    }
    CONFIG_FILENAME = "pygreenfoot.config"
    CONFIG_DELIMITER = "="

    def __new__(cls) -> "Application":
        if Application.__instance is None:
            Application.__instance = super().__new__(cls)
            return Application.__instance
        raise RuntimeError("No new instances of Application are allowed")

    def __init__(self) -> None:
        self.__running: bool = False
        self.__world: Optional[World] = None
        self.__screen: pygame.surface.Surface = None  # type: ignore
        self.__clock = pygame.time.Clock()
        self.__fps_limit = 60
        self.__keys: DefaultDict[_Key, bool] = DefaultDict(bool)
        self.__mouse_wheel: int = 0
        self.__mouse_in_window: bool = pygame.mouse.get_focused()
        self.__delta_size: pygame.math.Vector2 = pygame.math.Vector2()
        self.__delta_move: pygame.math.Vector2 = pygame.math.Vector2()
        self.__mouse_down: Optional[int] = None
        self.scrollbar_color: Color = Color(128, 128, 128)
        self.show_scrollbar: List[bool] = [True, True]
        self.__scrollbar: Tuple[bool, bool] = (False, False)
        self.__scrollbar_rects: Tuple[pygame.rect.Rect, pygame.rect.Rect] = (
            pygame.rect.Rect(0, 0, 0, 10),
            pygame.rect.Rect(0, 0, 10, 0),
        )
        self.__size: Tuple[int, int] = (0, 0)
        self.__maximized: bool = False
        self.__window_exposed: int = 0
        self.__config = Application.DEFAULT_CONFIG

    def start(self) -> None:
        """Initialize the application

        Raises:
            RuntimeError: When no starting world is given
        """
        if self.__world is None:
            raise RuntimeError("Scene has to be set before running the application")
        self.__running = True
        self.__update_screen()
        self.__handle_events()

    def stop(self, stop_sounds: bool = True) -> None:
        """
        Stops the application and clean ups pygame. This forces no exit of the python process.
        Everthing after the main function will be executed
        """
        self.__running = False
        if stop_sounds:
            Sound.stop_all()
        pygame.quit()

    def __update_screen(self) -> None:
        """
        Updates the screen and reconfigures the scrollbars
        """
        world = self.current_world
        aw = world.width * world.cell_size if world else Application.__sw // 2
        ah = world.height * world.cell_size if world else Application.__sh // 2

        if self.__config.get("windowWidth"):
            w = self.__config["windowWidth"]
        else:
            w = min(aw, Application.__sw)

        if self.__config.get("windowHeight"):
            h = self.__config["windowHeight"]
        else:
            h = min(ah, Application.__sh - 50)

        self.__screen = pygame.display.set_mode((w, h), self.__config["windowMode"] | pygame.SRCALPHA, vsync=self.__config["vsync"])  # type: ignore

        if not self.__maximized:
            self.__size = self.__screen.get_size()

        self.__calc_scrollbars()

    def __calc_scrollbars(self) -> None:
        """
        Recalculates if scrollbars are needed
        """
        if self.current_world:
            world_surface = self.current_world._surface
            screen_width, screen_height = self.__screen.get_size()

            self.__scrollbar = (
                screen_width < world_surface.get_width(),
                screen_height < world_surface.get_height(),
            )

            if self.__maximized:
                # fixing world position if scrollbars get lost on resize
                if not self.__scrollbar[0]:
                    self.__scrollbar_rects[0].x = 0
                    self.__make_scrollbar_x(world_surface, screen_width, True)
                if not self.__scrollbar[1]:
                    self.__scrollbar_rects[1].y = 0
                    self.__make_scrollbar_x(world_surface, screen_height, True)

    @property
    def current_world(self) -> World:
        """the world which is displayed in the window

        Raises:
            ValueError: if current world is None (only before setting this for once)

        Returns:
            World: the world currently being simulated
        """
        if self.__world is None:
            raise ValueError("No scene set")
        return self.__world

    @current_world.setter
    def current_world(self, world: World) -> None:
        if world is None:
            raise RuntimeError("world cannot be set to None")
        elif not isinstance(world, World):
            raise RuntimeError("world instance has to inherit from World")

        self.__world = world
        self.__update_screen()

    @property
    def fps(self) -> int:
        """The fps limit for the game.
        This value can be configured in the `pygreenfoot.config`
        file for initial setup or later through accessing this property.
        The value defaults to 60.

        Returns:
            int: the current set fps limit
        """
        return self.__fps_limit

    @fps.setter
    def fps(self, fps_limit: int) -> None:
        if fps_limit <= 0:
            raise ValueError("fps limit must be greater than 0")
        self.__fps_limit = fps_limit

    def is_running(self) -> bool:
        """An boolean indicating if the application is simulating a world

        Returns:
            bool: True if the application is running, otherwise False
        """
        return self.__running

    def __handle_events(self) -> None:
        """
        Handle close, key and mouse events as needed to provide data to the user
        """
        self.__mouse_wheel = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()

            elif event.type == pygame.KEYDOWN:
                self.__keys[event.key] = True

            elif event.type == pygame.KEYUP:
                self.__keys[event.key] = False

            elif event.type == pygame.MOUSEWHEEL:
                self.__mouse_wheel += event.y

            elif event.type == pygame.WINDOWENTER:
                self.__mouse_in_window = True

            elif event.type == pygame.WINDOWLEAVE:
                self.__mouse_in_window = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                sr = self.__scrollbar_rects
                if sr is None:
                    continue

                pos: Tuple[int, int] = event.pos
                if sr[0].collidepoint(pos):
                    self.__mouse_down = 0
                elif sr[1].collidepoint(pos):
                    self.__mouse_down = 1

            elif self.__mouse_down is not None and event.type == pygame.MOUSEMOTION:
                index = self.__mouse_down
                if index == 0:
                    self.__scrollbar_rects[0].x += event.rel[0]
                elif index == 1:
                    self.__scrollbar_rects[1].y += event.rel[1]

            elif event.type == pygame.MOUSEBUTTONUP:
                self.__mouse_down = None

            elif event.type == pygame.ACTIVEEVENT:
                if getattr(event, "gain", -1) == 0 and self.__mouse_down is not None:
                    self.__mouse_down = None

            elif event.type == pygame.WINDOWSIZECHANGED:
                self.__size = (event.x, event.y)
                self.__calc_scrollbars()

            elif event.type == pygame.WINDOWMAXIMIZED:
                self.__maximized = True
                self.__calc_scrollbars()

            elif event.type == pygame.WINDOWMINIMIZED:
                self.__maximized = False

            elif event.type == pygame.WINDOWEXPOSED or self.__window_exposed:
                self.__window_exposed += 1

    def update(self, act_cycle: bool = True) -> None:
        """
        Needs to be called once for frame
        Handles the pygame events (and thus, prevents pygame from freezing) as well as updates the screen
        """
        self.__handle_events()

        if act_cycle:
            self.current_world._calc_frame()
        elif self.current_world._check_world_time():
            self.current_world.repaint()

        if not self.__running:
            return

        world_surf = self.current_world._surface
        self.__delta_size = pygame.math.Vector2(
            max(0, self.__screen.get_width() - world_surf.get_width()) // 2,
            max(0, self.__screen.get_height() - world_surf.get_height()) // 2,
        )
        self.__make_scrollbars()
        diff = self.__delta_move + self.__delta_size

        self.__screen.blit(world_surf, diff)

        if self.__scrollbar[0] and self.show_scrollbar[0]:
            pygame.draw.rect(
                self.__screen,
                self.scrollbar_color._pygame,
                self.__scrollbar_rects[0],
                border_radius=3,
            )

        if self.__scrollbar[1] and self.show_scrollbar[1]:
            pygame.draw.rect(
                self.__screen,
                self.scrollbar_color._pygame,
                self.__scrollbar_rects[1],
                border_radius=3,
            )

        pygame.display.update()

        self.__clock.tick(self.__fps_limit)

        self.__screen.fill([0] * 3)

    def __make_scrollbars(self, force=False) -> None:
        """
        Bundle method to call make_scrollbar functions
        """
        world_surface = self.current_world._surface
        screen_width, screen_height = self.__size
        self.__make_scrollbar_x(world_surface, screen_width, force)
        self.__make_scrollbar_y(world_surface, screen_height, force)

    def __make_scrollbar_x(
        self, world_surf: pygame.surface.Surface, screen_width: int, force=False
    ) -> None:
        """
        Calculates position of the world surfaces and the horizontal scrollbar

        Args:
            world_surf (pygame.surface.Surface): the surfaces of the world
            screen_width (int): the screen width
        """
        if self.__scrollbar[0] or force:
            vr = self.__scrollbar_rects[0]
            fraction_width = screen_width / (world_surf.get_width() + screen_width)

            if fraction_width >= 1:
                return

            vr.y = self.__screen.get_height() - 3 - vr.height
            vr.width = int(fraction_width * screen_width)

            xmax = screen_width - vr.width
            vr.x = limit_value(vr.x, 0, xmax)

            self.__delta_move.x = -vr.x / xmax * (world_surf.get_width() - screen_width)

    def __make_scrollbar_y(
        self, world_surf: pygame.surface.Surface, screen_height: int, force=False
    ) -> None:
        """
        Calculates the position of the world surfaces and the vertical scrollbar

        Args:
            world_surf (pygame.surface.Surface): the surface of the world
            screen_height (int): the height of the screen
        """
        if self.__scrollbar[1] or force:
            hr = self.__scrollbar_rects[1]
            fraction_height = screen_height / (world_surf.get_height() + screen_height)

            if fraction_height >= 1:
                return

            hr.x = self.__screen.get_width() - 3 - hr.width
            hr.height = int(fraction_height * screen_height)

            ymax = screen_height - hr.height
            hr.y = limit_value(hr.y, 0, ymax)

            self.__delta_move.y = (
                -hr.y / ymax * (world_surf.get_height() - screen_height)
            )

    def get_key_states(self, *keys: int) -> Tuple[bool, ...]:
        """Return a series of boolean indictating if the given key at index is pressed (True) or released (False)

        Args:
            *keys: a series of keys value args

        Returns:
            Tuple[bool, ...]: a tuple with the same length as the input data
        """
        return tuple(self.__keys[k] for k in keys)

    def get_mouse_states(self) -> "MouseInfo":
        """
        Returns the mouse state in a MouseInfo object

        Returns:
            MouseInfo: the mouse info object with the mouse states
        """
        return MouseInfo(self.__mouse_wheel)

    def read_config(self) -> None:
        """
        Parses the config file if provided
        """

        def _unknown_key(value):
            raise TypeError("Key is unknown")

        cnf_file: str = os.path.join(".", Application.CONFIG_FILENAME)
        if not os.access(cnf_file, os.R_OK):
            print("INFO: No readable config file found")
            return
        parsed = {}
        print("Reading config")
        with open(cnf_file, "r") as f:
            for line in f:
                line = line.lstrip().rstrip("\n")
                if line.startswith("#"):
                    continue
                if Application.CONFIG_DELIMITER not in line:
                    print("WARNING: No `=` in config file line")
                    continue
                key, attr = line.split(Application.CONFIG_DELIMITER)
                print("Parse key: %s" % key)
                try:
                    v = _config_key_converter.get(key, _unknown_key)(attr)
                except TypeError as e:
                    print("ERROR: %r: %s" % (key, e.args))
                else:
                    parsed[key] = v
        self.__config.update(parsed)

    @property
    def image_folder(self) -> str:
        """
        Returns the relative path to the image folder in the cwd
        """
        return self.__config["imageResourceFolder"]

    @property
    def sound_folder(self) -> str:
        """
        Returns the relative path to the sound folder in the cwd
        """
        return self.__config["soundResourceFolder"]

    @property
    def default_world_speed(self) -> float:
        """
        Returns the world speed initially used if not other specified in your world's constructor

        Returns:
            float: the world speed.
        """
        return self.__config["defaultWorldSpeed"]

    @staticmethod
    def get_app() -> "Application":
        """
        Static method to get the application object

        Returns:
            Application: the application
        """
        if Application.__instance is None:
            Application.__instance = Application()
        return Application.__instance

    def setup_folder(self):
        """
        Creates the resource folders if necessary.
        """
        # check for folder
        if not os.access(self.__config["imageResourceFolder"], os.F_OK):
            os.makedirs(self.__config["imageResourceFolder"], 0o444)

        if not os.access(self.__config["soundResourceFolder"], os.F_OK):
            os.mkdir(self.__config["soundResourceFolder"], 0o444)

    def apply_config(self) -> None:
        """
        Applies other config keys like fps limit or window caption
        """
        self.setup_folder()
        self.__fps_limit = self.__config["fpsLimit"]
        pygame.display.set_caption(
            self.__config["title"],
        )
        pygame.display.set_icon(
            Image.from_filename(
                get_resource_path(self.__config["icon"], "image")
            )._surface
        )

    @staticmethod
    def main(first_world: Optional[Type[FirstWorld]] = None) -> None:
        """
        Function called to start the pygreenfoot program

        Args:
            first_world (Optional[Type[FirstWorld]]): The first world to start the game with as type (no parentheses). Defaults to None and looks in the `pygreenfoot.config` file for `firstWorld`.
        """
        app = Application.get_app()
        app.read_config()
        app.apply_config()

        if first_world is None:
            first_world_str = app.__config["firstWorld"]
            try:
                world = get_module_str_import(first_world_str)
            except ImportError:
                print(
                    "World entry %r in pygreenfoot.config is invalid or does not exist"
                    % first_world_str,
                    file=sys.stderr,
                )
            else:
                if not issubclass(world, World):
                    print(
                        "world entry %r in pygreenfoot.config does not inherit from pygreenfoot.World"
                        % first_world_str,
                        file=sys.stderr,
                    )
                    exit(-1)
                first_world = world  # type: ignore

        app.current_world = first_world()  # type: ignore

        if app.__config["generateDiagram"]:
            t = threading.Thread(
                target=create_inheritance_tree,
                kwargs={
                    "ignore": [
                        app.__config["imageResourceFolder"],
                        app.__config["soundResourceFolder"],
                    ],
                    "output_dir": app.__config["diagramFolder"],
                    "output_file": app.__config["diagramFilename"],
                    "temp_file": app.__config["tempPlantumlFile"],
                    "generate_image": app.__config["generateImage"],
                },
            )
            t.start()

        try:
            app.start()
            while app.is_running():
                app.update()

            app.quit()

        except pygame.error as e:
            if app.is_running():
                raise e

        finally:
            if app.__config["generateDiagram"]:
                t.join()  # type: ignore

    def is_mouse_in_window(self) -> bool:
        """
        Check if the mouse is in the winow

        Returns:
            bool: True if the mouse is in the winow else False
        """
        return self.__mouse_in_window

    def quit(self) -> None:
        """
        Quits the game/application and forces exit of the python process. Use `app.stop()` when the python process shall continue.
        """
        self.stop(stop_sounds=True)
        exit(0)

    def move_world(self, delta_x: int = 0, delta_y: int = 0) -> None:
        """
        Moves the world in px by moving the scrollbars by (delta_x, delta_y). Boundaries are automatically applied

        Args:
            delta_x (int, optional): the delta movement in the x direction. Defaults to 0.
            delta_y (int, optional): the delta movement in the y direction. Negative values move the world up. Defaults to 0.
        """
        self.__scrollbar_rects[0].x += delta_x
        self.__scrollbar_rects[1].y += delta_y

    def set_world_position(self, x: int = 0, y: int = 0) -> None:
        """
        Sets the world position by setting the scrollbars Boundaries are applied automatically

        Args:
            x (int, optional): the x position of the world. Defaults to 0.
            y (int, optional): the y position of the world. Defaults to 0.
        """
        self.__scrollbar_rects[0].x = x
        self.__scrollbar_rects[1].y = y

    @property
    def delta_pos(self) -> Tuple[int, int]:
        """
        The delta position of the worlds current position

        Returns:
            Tuple[int, int]: the moved position of the world in px
        """
        diff = self.__delta_move + self.__delta_size
        return int(diff[0]), int(diff[1])
