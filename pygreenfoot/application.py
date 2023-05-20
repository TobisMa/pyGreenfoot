import os
import sys
import threading
from typing import Any, Callable, DefaultDict, Dict, List, Optional, Tuple, Type, TypeVar, Union

import pygame
from pygreenfoot import get_module_str_import
from pygreenfoot.color import Color

from pygreenfoot.inheritance_tree import create_inheritance_tree

from .__types import _Key
from .mouse_info import MouseInfo
from .sound import Sound
from .world import World
from .math_helper import limit_value
from configparser import ConfigParser

os.environ['SDL_VIDEO_CENTERED'] = '1'
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
    result = pygame.SRCALPHA
    result = result | _pygame_screen_modes[value.upper()]
    return result

_pygame_screen_modes = {
    "RESIZABLE": pygame.RESIZABLE,
    "FULLSCREEN": pygame.FULLSCREEN,
    "BORDERLESS": pygame.NOFRAME,
    "FIXED": 0  # NOTE: apparently, no constant for the default exists
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
    "firstWorld": str
}


class Application:
    
    __slots__ = ("__screen", "__world", "__running", "__keys", "__mouse_in_window", "__size",
                 "__mouse_down", "__clock", "__fps_limit", "__mouse_wheel", "__scrollbar",
                 "__delta_size", "__delta_move", "show_scrollbar", "__scrollbar_rects",
                 "__maximized", "__window_exposed", "__config", "scrollbar_color")
    
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
        "windowMode": pygame.RESIZABLE | pygame.SRCALPHA,
        "windowStartUpMode": pygame.RESIZABLE | pygame.SRCALPHA,
        "firstWorld": None,
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
        self.__scrollbar_rects: Tuple[pygame.rect.Rect, pygame.rect.Rect] = (pygame.rect.Rect(0, 0, 0, 10), pygame.rect.Rect(0, 0, 10, 0))
        self.__size: Tuple[int, int] = (0, 0)
        self.__maximized: bool = False
        self.__window_exposed: int = 0
        self.__config = Application.DEFAULT_CONFIG
        
    def start(self) -> None:
        """Initialize the application

        Raises:
            RuntimeError: When no starting scene is given
        """
        if self.__world is None:
            raise RuntimeError("Scene has to be set before running the application")
        self.__running = True
        self.__update_screen()
        self.__handle_events()
        
    def stop(self) -> None:
        """
        Stops the application and clean ups pygame
        """
        self.__running = False
        pygame.quit()
        
    def __update_screen(self) -> None:
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

        self.__screen = pygame.display.set_mode((w, h), self.__config["windowMode"])  # type: ignore
        
        if not self.__maximized:
            self.__size = self.__screen.get_size()
            
        self.__calc_scrollbars()
            
    def __calc_scrollbars(self) -> None:
        if self.current_world:
            world_surface = self.current_world._surface
            screen = self.__screen
            self.__scrollbar = (
                screen.get_width() < world_surface.get_width() and self.show_scrollbar[0],
                screen.get_height() < world_surface.get_height() and self.show_scrollbar[1]
            )
        
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
        """The fps limit for the game

        Returns:
            int: the current set limit
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
            
            elif event.type != pygame.MOUSEMOTION:
                print(event)
      
    def update(self, act_cycle: bool = True) -> None:
        """
        Needs to be called once for frame
        Handles the pygame events (and thus, prevents pygame from freezing) as well as updating screen
        """
        self.__handle_events()
        
        if act_cycle:
            self.current_world._calc_frame()
        else:
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
            pygame.draw.rect(self.__screen, self.scrollbar_color._pygame, self.__scrollbar_rects[0], border_radius=3)
        
        if self.__scrollbar[1] and self.show_scrollbar[1]:
            pygame.draw.rect(self.__screen, self.scrollbar_color._pygame, self.__scrollbar_rects[1], border_radius=3)            
        
        pygame.display.update()
        
        self.__clock.tick(self.__fps_limit)
        
        self.__screen.fill([0] * 3)
        
    def __make_scrollbars(self) -> None:
        world_surface = self.current_world._surface
        screen_width, screen_height = self.__size
        self.__make_scrollbar_x(world_surface, screen_width)
        self.__make_scrollbar_y(world_surface, screen_height)
        
    def __make_scrollbar_x(self, world_surf: pygame.surface.Surface, screen_width: int) -> None:
        if self.__scrollbar[0] and self.show_scrollbar[0]:
            vr = self.__scrollbar_rects[0]
            fraction_width = screen_width / (world_surf.get_width() + screen_width)
            
            if fraction_width >= 1:
                return
            
            vr.y = self.__screen.get_height() - 3 - vr.height
            vr.width = int(fraction_width * screen_width)
            
            xmax = screen_width - vr.width
            vr.x = limit_value(vr.x, 0, xmax)
            
            self.__delta_move.x = -vr.x / xmax * (world_surf.get_width() - screen_width)
            
    
    def __make_scrollbar_y(self, world_surf: pygame.surface.Surface, screen_height: int) -> None:
        if self.__scrollbar[1] and self.show_scrollbar[1]:
            hr = self.__scrollbar_rects[1]
            fraction_height = screen_height / (world_surf.get_height() + screen_height)
            
            if fraction_height >= 1:
                return
            
            hr.x = self.__screen.get_width() - 3 - hr.width
            hr.height = int(fraction_height * screen_height)
            
            ymax = screen_height - hr.height
            hr.y = limit_value(hr.y, 0, ymax)
            
            self.__delta_move.y = -hr.y / ymax * (world_surf.get_height() - screen_height)
    
                    
    def get_key_states(self, *keys: int) -> Tuple[bool, ...]:
        """Return a series of boolean indictating if the given key at index is pressed (True) or released (False)

        Args:
            *keys: a series of keys value args

        Returns:
            Tuple[bool, ...]: a tuple with the same length as the input data
        """
        return tuple(self.__keys[k] for k in keys)
    
    def get_mouse_states(self) -> "MouseInfo":
        return MouseInfo(self.__mouse_wheel)
    
    def read_config(self) -> None:
        def _unknown_key(value):
            raise TypeError("Key is unknown")
        cnf_file: str = os.path.join(".", Application.CONFIG_FILENAME)
        if not os.access(cnf_file, os.R_OK):
            print("WARNING: No readable config file found")
            return
        parsed = {}
        print("Reading config")
        with open(cnf_file, "r") as f:
            for line in f:
                line = line.lstrip().rstrip("\n")
                if line.startswith("#"): continue
                if Application.CONFIG_DELIMITER not in line:
                    print("WARNING: No `=` in config file line")
                    continue
                key, attr = line.split(Application.CONFIG_DELIMITER)
                print("Parse key: %s" % key)
                try:
                    v = _config_key_converter.get(key, _unknown_key)(attr)
                except TypeError as e:
                    print("ERROR: %r: %s" %(key, e.args))
                else:
                    parsed[key] = v
        self.__config.update(parsed)
        
    @property
    def image_folder(self) -> str:
        return self.__config["imageResourceFolder"]
    
    @property
    def sound_folder(self) -> str:
        return self.__config["soundResourceFolder"]
    
    @property
    def default_world_speed(self) -> float:
        return self.__config["defaultWorldSpeed"]
    
    @staticmethod
    def get_app() -> "Application":
        if Application.__instance is None:
            Application.__instance = Application()
        return Application.__instance
    
    def setup_folder(self):
        # check for folder
        if not os.access(self.__config["imageResourceFolder"], os.F_OK):
            os.makedirs(self.__config["imageResourceFolder"], 0o444)

        if not os.access(self.__config["soundResourceFolder"], os.F_OK):
            os.mkdir(self.__config["soundResourceFolder"], 0o444)
            
    @staticmethod
    def main(first_world: Optional[Type[FirstWorld]] = None) -> None:
        app = Application.get_app()
        app.read_config()
        app.setup_folder()
        
        if app.__config.get("fpsLimit"):
            app.__fps_limit = app.__config["fpsLimit"]
        
        if first_world is None:
            first_world_str = app.__config["firstWorld"]
            try:
                world = get_module_str_import(first_world_str)
            except ImportError:
                print("World entry %r in pygreenfoot.config is invalid or does not exist" % first_world_str, file=sys.stderr)
            else:
                if not issubclass(world, World):
                    print("world entry %r in pygreenfoot.config does not inherit from pygreenfoot.World" % first_world_str, file=sys.stderr)
                    exit(-1)
                first_world = world # type: ignore
        
        app.current_world = first_world() # type: ignore
        
        if app.__config["generateDiagram"]:
            t = threading.Thread(
                target=create_inheritance_tree,
                kwargs={
                    "ignore": [
                        app.__config["imageResourceFolder"],
                        app.__config["soundResourceFolder"]
                    ],
                    "output_dir": app.__config["diagramFolder"],
                    "output_file": app.__config["diagramFilename"],
                    "temp_file": app.__config["tempPlantumlFile"],
                    "generate_image": app.__config["generateImage"]
                }
            )
            t.start()
            
        try:
            app.start()
            while app.is_running():
                app.update()
            
            app.quit()
            
        finally:
            if app.__config["generateDiagram"]:
                t.join()  # type: ignore
    
    def is_mouse_in_window(self) -> bool:
        return self.__mouse_in_window
    
    def quit(self) -> None:
        Sound.stop_all()
        self.stop()
        exit(0)
        
    def move_world(self, delta_x: int = 0, delta_y: int = 0) -> None:
        self.__scrollbar_rects[0].x += delta_x
        self.__scrollbar_rects[1].y += delta_y
        
    def set_world_position(self, x: int = 0, y: int = 0) -> None:
        self.__scrollbar_rects[0].x = x
        self.__scrollbar_rects[0].y = y
        
    @property
    def delta_pos(self) -> Tuple[int, int]:
        diff = self.__delta_move + self.__delta_size
        return (int(diff[0]), int(diff[1]))
