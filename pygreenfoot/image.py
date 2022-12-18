import os
import pygame
from typing import Callable, Optional, Tuple, Union
from functools import wraps as __wraps

from .math_helper import limit_value

from .color import Color


class Image:
    
    __slots__ = ("__base_image", "color", "__rot_image", "__rot")
    __hidden_color: Optional[pygame.color.Color] = pygame.color.Color(0, 0, 0)
    
    def __init__(self, image: Union["Image", pygame.surface.Surface]) -> None:
        self.__base_image: pygame.surface.Surface = image.__base_image.copy() if isinstance(image, Image) else image.copy()
        self.__rot_image: pygame.surface.Surface = self.__base_image.copy()  # type: ignore
        self.__rot = 0
        self.color: Color = Color(0, 0, 0)
        
    @property
    def width(self) -> int:
        return self.__base_image.get_width()
    
    @property
    def height(self) -> int:
        return self.__base_image.get_height()
    
    def draw_image(self, image: "Image", x: int, y: int) -> None:
        self.__base_image.blit(image.__base_image, (x, y))
        
    def draw_line(self, x1: int, y1: int, x2: int, y2: int, width: int = 1) -> None:
        pygame.draw.line(self.__base_image, self.color._pygame, (x1, y1) , (x2, y2), width)
        self._set_rot(self.__rot)
        
    def draw_oval(self, x: int, y: int, width: int, height: int, fill: bool = False) -> None:
        w = 0 if fill else 1
        pygame.draw.ellipse(self.__base_image, self.color._pygame, [x, y, width, height], w)
        
    def draw_rect(self, x: int, y: int, width: int, height: int, fill: bool = False) -> None:
        w = 0 if fill else 1
        pygame.draw.rect(self.__base_image, self.color._pygame, [x, y, width, height], w)
        
    def draw_polygon(self, points: Tuple[Tuple[int, int], ...], fill: bool = False) -> None:
        if len(points) < 3:
            raise ValueError("Polygon needs at least 3 points")
        w = 0 if fill else 1
        pygame.draw.polygon(self.__base_image, self.color._pygame, points, w)
    
    def fill_with_color(self, color: Color = ...) -> None:
        if color is ...:
            color = self.color
        pygame.draw.rect(self.__base_image, color._pygame, [0, 0, self.width, self.height])
        
    def clear(self) -> None:
        surface = pygame.Surface((self.width, self.height))
        if Image.__hidden_color is not None:
            surface.set_colorkey(Image.__hidden_color)
            surface.fill(Image.__hidden_color)
        self.__base_image = surface
        
    def draw_text(self, text: str, x: int, y: int,
                  font: Optional[Union[pygame.font.Font, str]] = None, font_size: int = 26, 
                  bold: bool = False, italic: bool = False) -> None:
        if font is None:
            font_obj = pygame.font.SysFont(pygame.font.get_default_font(), font_size, bold, italic)
        elif isinstance(font, str):
            font_obj = pygame.font.SysFont(font, font_size, bold, italic)
        else:
            font_obj = font
            
        rendered_text = font_obj.render(text, True, self.color._pygame)
        self.__base_image.blit(rendered_text, (x, y))
        
    @property
    def alpha(self) -> int:
        alpha = self.__base_image.get_alpha()
        return 255 if alpha is None else alpha
    
    @alpha.setter
    def alpha(self, alpha: int) -> None:
        self.__base_image.set_alpha(limit_value(alpha, 0, 255))
        
    @staticmethod
    def from_filename(filename: str) -> "Image":
        path = os.path.join("images", filename)
        if not os.access(path, os.F_OK):
            raise FileNotFoundError("File %r does not exist" % path)
        image = pygame.image.load(path)
        return Image(image)
    
    @staticmethod
    def get_empty(width: int, height: int) -> "Image":
        return Image(pygame.Surface((width, height)))
    
    def scale(self, width: int, height: int) -> None:
        self.__base_image = pygame.transform.smoothscale(self.__base_image, (width, height))
        
    def copy(self) -> "Image":
        image = Image(self.__base_image)
        return image
    
    def _set_rot(self, angle: float) -> None:
        self.__rot = angle % 360
        
        # TODO fix rot positioning
        if angle == 0:
            self.__rot_image = self.__base_image.copy() # type: ignore
            return
        self.__rot_image = pygame.transform.rotate(self.__base_image, -angle)
    
    @property
    def _surface(self) -> pygame.surface.Surface:
        return self.__rot_image
    
    @property
    def _rel_pos(self) -> Tuple[int, int]:
        p = pygame.math.Vector2(self.__base_image.get_rect().size)
        p = (p - pygame.math.Vector2(self.__rot_image.get_rect().size))
        return int(p.x), int(p.y)

    @staticmethod
    def set_hidden_color(color: Optional[pygame.color.Color] = None) -> None:
        Image.__hidden_color = color
        
    @staticmethod
    def get_hidden_color() -> Optional[pygame.color.Color]:
        return Image.__hidden_color