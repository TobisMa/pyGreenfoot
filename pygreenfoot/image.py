import os
import pygame
from typing import Optional, Tuple, Union

from .math_helper import limit_value

from .color import Color


class Image:
    
    __slots__ = ("__image", "color")
    
    def __init__(self, image: Union["Image", pygame.Surface]):
        self.__image = image.__image if isinstance(image, Image) else image
        self.color: Color = Color(0, 0, 0)
        
    @property
    def width(self) -> int:
        return self.__image.get_width()
    
    @property
    def height(self) -> int:
        return self.__image.get_height()
    
    def draw_image(self, image: "Image", x: int, y: int) -> None:
        self.__image.blit(image.__image, (x, y))
        
    def draw_line(self, x1: int, y1: int, x2: int, y2: int, width: int = 1) -> None:
        pygame.draw.line(self.__image, self.color._pygame, (x1, y1) , (x2, y2), width)
        
    def draw_oval(self, x: int, y: int, width: int, height: int, fill: bool = False) -> None:
        w = 0 if fill else 1
        pygame.draw.ellipse(self.__image, self.color._pygame, [x, y, width, height], w)
        
    def draw_rect(self, x: int, y: int, width: int, height: int, fill: bool = False) -> None:
        w = 0 if fill else 1
        pygame.draw.rect(self.__image, self.color._pygame, [x, y, width, height], w)
        
    def draw_polygon(self, points: Tuple[Tuple[int, int], ...], fill: bool = False) -> None:
        if len(points) < 3:
            raise ValueError() # TODO
        w = 0 if fill else 1
        pygame.draw.polygon(self.__image, self.color, w)
    
    def fill_with_color(self, color: Color = ...) -> None:
        if color is ...:
            color = self.color
        pygame.draw.rect(self.__image, color._pygame, [0, 0, self.width, self.height])
        
    def clear(self) -> None:
        surface = pygame.Surface((self.width, self.height))
        self.__image = surface
        
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
        self.__image.blit(rendered_text, (x, y))
        
    @property
    def alpha(self) -> int:
        alpha = self.__image.get_alpha()
        return 255 if alpha is None else alpha
    
    @alpha.setter
    def alpha(self, alpha: int) -> None:
        self.__image.set_alpha(limit_value(alpha, 0, 255))
        
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
        pygame.transform.smoothscale(self.__image, (width, height))
        
    def copy(self) -> "Image":
        image = Image(self.__image)
        return image
    
    @property
    def _surface(self) -> pygame.Surface:
        return self.__image
