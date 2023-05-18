import os
from typing import Optional, Tuple, Union

import pygame

from .color import Color
from .font import Font
from .math_helper import limit_value


class Image:
    
    __slots__ = ("__base_image", "color", "__rot_image", "__rot")
    __hidden_color: Optional[pygame.color.Color] = pygame.color.Color(1, 1, 1)
    
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
                  font: Optional[Union[pygame.font.Font, Font, str]] = None, font_size: int = 26, 
                  bold: bool = False, italic: bool = False) -> None:
        if font is None:
            font_obj = pygame.font.SysFont(pygame.font.get_default_font(), font_size, bold, italic)
        elif isinstance(font, str):
            font_obj = pygame.font.SysFont(font, font_size, bold, italic)
        elif isinstance(font, Font):
            font_obj = font._pygame
        else:
            font_obj = font
            
        rendered_text = font_obj.render(text, True, self.color._pygame)
        self.__base_image.blit(rendered_text, (x, y))
        self._set_rot(self.__rot)
        
    @property
    def alpha(self) -> int:
        alpha = self.__base_image.get_alpha()
        return 255 if alpha is None else alpha
    
    @alpha.setter
    def alpha(self, alpha: int) -> None:
        self.__base_image.set_alpha(limit_value(alpha, 0, 255))
        
    @staticmethod
    def from_filename(filename: str) -> "Image":
        from pygreenfoot import Application
        path = os.path.join(Application.get_app().image_folder, filename)
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
            self.__rot_image = self.__base_image.copy()
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
    
    def get_color_at(self, x: int, y: int) -> Color:
        if x < 0 or x > self.width or y < 0 or y > self.height:
            raise ValueError("Pixel coordinates out of image range")
        return Color.from_pygame_color(self.__base_image.get_at((x, y)))  # type: ignore
    
    def set_color_at(self, x: int, y: int) -> None:
        self.__base_image.set_at((x, y), self.color._pygame)
        self._set_rot(self.__rot)
        
    def mirror(self, horizontal: bool = False, vertical: bool = False, negate_rotation: bool = False) -> "Image":
        new_img = pygame.transform.flip(self.__base_image, vertical, horizontal)
        res_img = Image(new_img)
        if negate_rotation:
            res_img._set_rot(-self.__rot)
        else:
            res_img._set_rot(self.__rot)
        return res_img
    
    @classmethod
    def text_label(cls, text: str, font: Font, foreground: Color, background: Color, outline: Optional[Color] = None, margin: int = 5) -> "Image":        
        text_size = font._text_size(text)
        text_obj = font.get_text(text, foreground)

        surf = pygame.Surface(text_size)
        surf.fill(background._pygame)
        surf.blit(text_obj._surface, (margin, margin))
        
        if outline:
            pygame.draw.rect(surf, outline._pygame, [0, 0, text_size[0] + margin, text_size[1] + margin], 1)
        
        return Image(surf)
        