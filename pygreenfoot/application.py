import os
from typing import DefaultDict, Optional, Tuple

import pygame

from .__types import _Key, _MouseButtonStates
from .mouse_info import MouseInfo
from .world import World

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()


class Application:
    
    __slots__ = ("__screen", "__world", "__running", "__keys", 
                 "__clock", "__fps_limit", "__mouse_wheel")
    
    __instance: "Application" = None
    __pygame_info = pygame.display.Info()
    __sw = __pygame_info.current_w
    __sh = __pygame_info.current_h
    
    def __new__(cls) -> "Application":
        print("__new__")
        if Application.__instance is None:
            Application.__instance = super().__new__(cls)
            return Application.__instance
        raise RuntimeError("No new instances of Application are allowed")
    
    def __init__(self) -> None:
        self.__running: bool = False
        self.__world: Optional[World] = None
        self.__screen: pygame.Surface = None
        self.__clock = pygame.time.Clock()
        self.__fps_limit = 60
        self.__keys: DefaultDict[_Key, bool] = DefaultDict(bool)
        self.__mouse_wheel: int = 0
        
    def start(self) -> None:
        """Initialize the application

        Raises:
            RuntimeError: When no starting scene is given
        """
        if self.__world is None:
            raise RuntimeError("Scene has to be set before running the application")
        self.__running = True
        self.__update_screen()
        
    def stop(self) -> None:
        """
        Stops the application and clean ups pygame
        """
        self.__running = False
        pygame.quit()
        
    def __update_screen(self) -> None:
        self.__screen = pygame.display.set_mode((Application.__sw // 2, Application.__sh // 2), pygame.RESIZABLE)
        
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
                                
    def update(self) -> None:
        """
        Needs to be called once for frame
        Handles the pygame events (and thus, prevents pygame from freezing) as well as updating screen
        """
        self.__handle_events()
        
        if not self.__running:
            return
        
        self.current_world._calc_frame(self.__screen)

        pygame.display.update()
        
        self.__clock.tick(self.__fps_limit)
        
        self.__screen.fill([0] * 3)  # TODO background image
        
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
    
    @staticmethod
    def get_app() -> "Application":
        if Application.__instance is None:
            Application.__instance = Application()
        return Application.__instance
            
    @staticmethod
    def main(first_world: World) -> None:
        app = Application.get_app()
        app.current_world = first_world
        app.start()
        
        while app.is_running():
            app.update()
        