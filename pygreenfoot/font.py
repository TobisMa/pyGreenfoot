from typing import Any, Mapping, Tuple, Union
import pygame

from .color import Color

FONTS = pygame.font.get_fonts()

FontType = Union[
    Union[
        Tuple[int, str],
        Tuple[int, str, bool],
        Tuple[int, str, bool, bool],
        Tuple[int, str, bool, bool, bool],
    ],
    "Font"
]


class Font:
    
    """
    pygreenfoot's class for fonts
    """
    
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
        """
        The font's name
        """
        return self.__fontname
    
    @property
    def size(self) -> int:
        """
        The font's size
        """
        return self.__size
    
    @property
    def italic(self) -> bool:
        """
        if the font is italic
        """
        return self.__font.get_italic()
    
    @italic.setter
    def italic(self, value: bool) -> None:
        self.__font.set_italic(value)
    
    @property
    def bold(self) -> bool:
        """
        if the font is bold
        """
        return self.__font.get_bold()
    
    @bold.setter
    def bold(self, value: bool) -> None:
        self.__font.set_bold(value)
        
    @property
    def underline(self) -> bool:
        """
        if the font is underlined
        """
        return self.__font.get_underline()
    
    @underline.setter
    def underline(self, value: bool) -> None:
        self.__font.set_underline(value)
        
    def copy(self) -> "Font":
        """
        Copies the font by instantiating a Font object with the same properties 

        Returns:
            Font: the new font
        """
        return Font(self.__fontname, self.size, self.bold, self.italic, self.underline)
    
    def get_text(self, text: str, color: Color = Color.BLACK, antialias: bool = True) -> "Text":
        """
        Returns a pygreenfoot.Text object by using this font

        Args:
            text (str): the displayed text
            color (Color, optional): the color of the text. Defaults to Color.BLACK.
            antialias (bool, optional): Shall the text be antialiased. Defaults to True.

        Returns:
            Text: the Text object using above properties
        """
        return Text(self, text, color, antialias)
    
    @property
    def _pygame(self) -> pygame.font.Font:
        """
        The pygame font object of this font
        """
        return self.__font
        
    @staticmethod
    def get_default_font() -> str:
        """
        Returns the systems default font
        """
        return pygame.font.get_default_font()
    
    def _text_size(self, text: str) -> Tuple[int, int]:
        """
        Returns the measurement of text using this font in px

        Args:
            text (str): the text

        Returns:
            Tuple[int, int]: the size of the text in (width, height)
        """
        return self.__font.size(text)
    

class Text:
    
    """
    Class to easily have rendered text on screen with a font and other settings.
    """
    
    __slots__ = ("__display_text", "font", "color", "__surface", "antialias")
    
    def __init__(self, font: Union[
        Union[
            Tuple[int, str, bool, bool, bool],
            Tuple[int, str, bool, bool],
            Tuple[int, str, bool],
            Tuple[int, str],
        ],
        "Font"
    ], display_text: Any, color: Color, antialias: bool = True) -> None:
        self.font: Font = font if isinstance(font, Font) else Font(*font)  # type: ignore
        self.color: Color = color
        self.antialias: bool = antialias
        self.__display_text: str = str(display_text)
        self.__surface: pygame.surface.Surface = self.font._pygame.render(display_text, True, color._pygame)
        
    @property
    def display_text(self) -> str:
        """
        The text which will be shown
        """
        return self.__display_text
    
    @display_text.setter
    def display_text(self, value: Any) -> None:
        self.__display_text = str(value)
        self.__surface: pygame.surface.Surface = self.font._pygame.render(self.__display_text, True, self.color._pygame)
    
    @property
    def _surface(self) -> pygame.surface.Surface:
        """
        The surface with the text on
        """
        return self.__surface
