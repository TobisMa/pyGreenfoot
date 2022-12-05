import os
from typing import Iterator, Optional, Set, Type, Generator

import pygame
from pygreenfoot.event import Event

from pygreenfoot.scene import Scene

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()

class Application:
    
    __slots__ = ("__scene", "__screen", "__scenes", "__running", "__handled_events")
    
    __instance: "Application" = None
    __pygame_info = pygame.display.Info()
    __sw = __pygame_info.current_w
    __sh = __pygame_info.current_h
    
    def __new__(cls) -> "Application":
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance
    
    def __init__(self) -> None:
        self.__handled_events: bool = False 
        self.__running: bool = False
        self.__scene: Optional[Scene] = None
        self.__scenes: Set[Type[Scene]] = set() 
        self.__screen: pygame.Surface = None
        
    def start(self) -> None:
        if self.__scene is None:
            raise RuntimeError("Scene has to be set before running the application")
        self.__running = True
        self.__update_screen()
        
    def stop(self) -> None:
        self.__running = False
        
    def __update_screen(self) -> None:
        self.__screen = pygame.display.set_mode((Application.__sw // 2, Application.__sh // 2), pygame.RESIZABLE)
        
        
    @property
    def current_scene(self) -> Scene:
        if self.__scene is None:
            raise ValueError("No scene set")
        return self.__scene

    @current_scene.setter
    def current_scene(self, scene: Scene) -> None:
        if scene is None:
            raise RuntimeError("scene cannot be set to None")
        self.__scene = scene
        self.__update_screen()
        
    @property
    def scenes(self) -> Iterator[Type[Scene]]:
        return iter(self.__scenes)
    
    def add_scene(self, scene: Type[Scene]) -> None:
        self.__scenes.add(scene)
        
    def is_running(self) -> bool:
        return self.__running
    
    def __handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.__running = False
                
        self.__handled_events = True
                
    def get_events(self) -> Generator[Event, None, None]:
        for event in pygame.event.get():
            e = Event(event)
            if e.type is None:
                print(event)
            yield e
        self.__handled_events = True
        
        
    def update(self) -> None:
        if not self.__handled_events:
            self.__handle_events()
        self.__handled_events = False
        pygame.display.update()
        
    def __del__(self) -> None:
        pygame.quit()