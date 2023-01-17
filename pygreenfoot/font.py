from typing import Any, Tuple, Union
import pygame

from .color import Color

FONTS = pygame.font.get_fonts()


class Font:
    
    __slots__ = ("__font", "__fontname", "__size")
    
    def __init__(self, name: str, size: int = 11, bold: bool = False, italic: bool = False, underline: bool = False) -> None:
        self.__font: pygame.font.Font = pygame.font.Font(name, size)
        self.__fontname: str = name
        self.__size = size
        self.bold = bold
        self.italic = italic
        self.underline = underline
        
    @property
    def font_name(self) -> str:
        return self.__fontname
    
    @property
    def size(self) -> int:
        return self.__size
    
    @property
    def italic(self) -> bool:
        return self.__font.get_italic()
    
    @italic.setter
    def italic(self, value: bool) -> None:
        self.__font.set_italic(value)
    
    @property
    def bold(self) -> bool:
        return self.__font.get_bold()
    
    @bold.setter
    def bold(self, value: bool) -> None:
        self.__font.set_bold(value)
        
    @property
    def underline(self) -> bool:
        return self.__font.get_underline()
    
    @underline.setter
    def underline(self, value: bool) -> None:
        self.__font.set_underline(value)
        
    def copy(self) -> "Font":
        return Font(self.__fontname, self.size, self.bold, self.italic, self.underline)
    
    def get_text(self, text: str, color: Color = Color.BLACK, antialias: bool = True) -> "Text":
        return Text(self, text, color, antialias)
    
    @property
    def _pygame(self) -> pygame.font.Font:
        return self.__font
        
    @staticmethod
    def get_default_font() -> str:
        return pygame.font.get_default_font()
    
    def _text_size(self, text: str) -> Tuple[int, int]:
        return self.__font.size(text)
    

class Text:
    
    __slots__ = ("__display_text", "font", "color", "__surface", "antialias")
    
    def __init__(self, font: Union[Tuple[str, int], Font], display_text: Any, color: Color, antialias: bool = True) -> None:
        self.font: Font = font if isinstance(font, Font) else Font(*font)
        self.color: Color = color
        self.antialias: bool = antialias
        self.__display_text: str = str(display_text)
        self.__surface: pygame.surface.Surface = self.font._pygame.render(display_text, True, color._pygame)
        
    @property
    def display_text(self) -> str:
        return self.__display_text
    
    @display_text.setter
    def display_text(self, value: Any) -> None:
        self.__display_text = str(value)
        self.__surface: pygame.surface.Surface = self.font._pygame.render(self.__display_text, True, self.color._pygame)
    
    @property
    def _surface(self) -> pygame.surface.Surface:
        return self.__surface