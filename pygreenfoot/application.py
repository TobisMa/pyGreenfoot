import os
from typing import DefaultDict, List, Optional, Tuple

import pygame

from .__types import _Key
from .mouse_info import MouseInfo
from .sound import Sound
from .world import World
from .math_helper import limit_value

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()


class Application:
    
    __slots__ = ("__screen", "__world", "__running", "__keys", "__mouse_in_window", "__size",
                 "__mouse_down", "__clock", "__fps_limit", "__mouse_wheel", "__scrollbar",
                 "__delta_size", "__delta_move", "show_scrollbar", "__scrollbar_rects",
                 "__maximized")
    
    __instance: Optional["Application"] = None
    __pygame_info = pygame.display.Info()
    __sw = __pygame_info.current_w
    __sh = __pygame_info.current_h
    
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
        self.show_scrollbar: List[bool] = [True, True]
        self.__scrollbar: Tuple[bool, bool] = (False, False)
        self.__scrollbar_rects: Tuple[pygame.rect.Rect, pygame.rect.Rect] = (pygame.rect.Rect(0, 0, 0, 10), pygame.rect.Rect(0, 0, 10, 0))
        self.__size: Tuple[int, int] = (0, 0)
        self.__maximized: bool = False
        
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
        world = self.current_world
        aw = world.width * world.cell_size if world else Application.__sw // 2
        ah = world.height * world.cell_size if world else Application.__sh // 2
        
        w = min(aw, Application.__sw)
        h = min(ah, Application.__sh - 50)
        
        self.__screen = pygame.display.set_mode((w, h), pygame.RESIZABLE | pygame.SRCALPHA)  # type: ignore
        
        if not self.__maximized:
            self.__size = self.__screen.get_size()
            
        if self.current_world:
            ws = world._surface
            ss = self.__screen
            self.__scrollbar = (
                ss.get_width() < ws.get_width() and self.show_scrollbar[0],
                ss.get_height() < ws.get_height() and self.show_scrollbar[1]
            )
            print(f"{ss=}; {ws=}")
        
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
                
            elif event.type == pygame.WINDOWMAXIMIZED:
                self.__maximized = True
                
            elif event.type == pygame.WINDOWMINIMIZED:
                self.__maximized = False
                        
            elif event.type != pygame.MOUSEMOTION:
                print(event)
                                
    def update(self) -> None:
        """
        Needs to be called once for frame
        Handles the pygame events (and thus, prevents pygame from freezing) as well as updating screen
        """
        self.__handle_events()
        
        if not self.__running:
            return
        
        self.current_world._calc_frame(self.__screen)
        world_surf = self.current_world._surface
        self.__delta_size = pygame.math.Vector2(
            max(0, self.__screen.get_width() - world_surf.get_width()) // 2,
            max(0, self.__screen.get_height() - world_surf.get_height()) // 2,
        )
        self.__make_scrollbars()
        diff = self.__delta_move + self.__delta_size
        
        self.__screen.blit(world_surf, diff)
        
        if self.__scrollbar[0] and self.show_scrollbar[0]:
            pygame.draw.rect(self.__screen, [128, 128, 128], self.__scrollbar_rects[0], border_radius=3)
        
        if self.__scrollbar[1] and self.show_scrollbar[1]:
            pygame.draw.rect(self.__screen, [128, 128, 128], self.__scrollbar_rects[1], border_radius=3)            
        
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
            fraction_width = screen_width / (world_surf.get_width() - screen_width)
            
            # FIXME find real bug
            if fraction_width >= 1:
                return
            
            vr.y = self.__screen.get_height() - 3 - vr.height
            vr.width = int(fraction_width * screen_width)
            
            xmax = screen_width - vr.width
            vr.x = limit_value(vr.x, 0, xmax)
            
            self.__delta_move.x = -vr.x / xmax * (world_surf.get_width() - screen_width)
            
            print(f"{fraction_width=}")
    
    def __make_scrollbar_y(self, world_surf: pygame.surface.Surface, screen_height: int) -> None:
        if self.__scrollbar[1] and self.show_scrollbar[1]:
            hr = self.__scrollbar_rects[1]
            fraction_height = screen_height / (world_surf.get_height() - screen_height)
            
            # FIXME find real bug
            if fraction_height >= 1:
                return
            
            hr.x = self.__screen.get_width() - 3 - hr.width
            hr.height = int(fraction_height * screen_height)
            
            ymax = screen_height - hr.height
            hr.y = limit_value(hr.y, 0, ymax)
            
            self.__delta_move.y = -hr.y / ymax * (world_surf.get_height() - screen_height)

            print(f"{fraction_height=}")
    
        print(self.__delta_move)
                    
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
        app.fps = 15
        app.current_world = first_world
        app.start()
        
        while app.is_running():
            app.update()
        
        app.quit()
    
    def is_mouse_in_window(self) -> bool:
        return self.__mouse_in_window
    
    def quit(self) -> None:
        Sound.stop_all()
        self.stop()
        
    @property
    def delta_pos(self) -> Tuple[int, int]:
        diff = self.__delta_move + self.__delta_size
        return (int(diff[0]), int(diff[1]))