from typing import Any, Tuple, Union, Dict
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
    "Font",
]


class Font:

    """
    pygreenfoot's class for fonts
    """

    __slots__ = ("__font", "__fontname", "__size")
    pygame_fonts: Dict[Tuple[str, int, bool, bool, bool, bool], pygame.font.Font] = {}

    def __init__(
        self,
        name: str,
        size: int = 11,
        bold: bool = False,
        italic: bool = False,
        underline: bool = False,
        strike_through: bool = False,
    ) -> None:
        self.__font: pygame.font.Font = Font.get_pygame_font(name, size)
        self.__fontname: str = name
        self.__size = size
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.strike_through = strike_through

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
        # self.__font.set_italic(value)
        self.__font = Font.get_pygame_font(
            self.__fontname,
            self.__size,
            self.bold,
            value,
            self.underline,
            self.strike_through,
        )

    @property
    def bold(self) -> bool:
        """
        if the font is bold
        """
        return self.__font.get_bold()

    @bold.setter
    def bold(self, value: bool) -> None:
        # self.__font.set_bold(value)
        self.__font = Font.get_pygame_font(
            self.__fontname,
            self.__size,
            value,
            self.italic,
            self.underline,
            self.strike_through,
        )

    @property
    def underline(self) -> bool:
        """
        if the font is underlined
        """
        return self.__font.get_underline()

    @underline.setter
    def underline(self, value: bool) -> None:
        # self.__font.set_underline(value)
        self.__font = Font.get_pygame_font(
            self.__fontname,
            self.__size,
            self.bold,
            self.italic,
            value,
            self.strike_through,
        )

    @property
    def strike_through(self) -> bool:
        """
        if the font is stroken-through
        """
        return self.__font.get_strikethrough()

    @strike_through.setter
    def strike_through(self, value: bool) -> None:
        # self.__font.set_strikethrough(value)
        self.__font = Font.get_pygame_font(
            self.__fontname,
            self.__size,
            self.bold,
            self.italic,
            self.underline,
            value,
        )

    def copy(self) -> "Font":
        """
        Copies the font by instantiating a Font object with the same properties

        Returns:
            Font: the new font
        """
        return Font(
            self.__fontname,
            self.size,
            self.bold,
            self.italic,
            self.underline,
            self.strike_through,
        )

    def get_text(
        self, text: str, color: Color = Color.BLACK, antialias: bool = True
    ) -> "Text":
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

    def _text_size(self, text: str) -> Tuple[int, int]:
        """
        Returns the measurement of text using this font in px

        Args:
            text (str): the text

        Returns:
            Tuple[int, int]: the size of the text in (width, height)
        """
        return self.__font.size(text)

    @staticmethod
    def get_default_font() -> str:
        """
        Returns the systems default font
        """
        return pygame.font.get_default_font()

    @staticmethod
    def get_pygame_font(
        name: str,
        size: int,
        bold: bool = False,
        italic: bool = False,
        underline: bool = False,
        strike_through: bool = False,
    ) -> pygame.font.Font:
        """
        Returns the pygame font with the according properties

        Args:
            name (str): font name
            size (int): font size
            bold (bool): bold font? Defaults to False.
            italic (bool): italic font? Defaults to False.
            underline (bool): underlined font? Defaults to False.

        Returns:
            pygame.font.Font: the pygame font with the according sizes
        """
        properties = (name, size, bold, italic, underline, strike_through)

        if Font.pygame_fonts.get(properties) is None:
            f = pygame.font.Font(name, size)
            f.set_bold(bold)
            f.set_italic(italic)
            f.set_underline(underline)
            f.set_strikethrough(strike_through)
            Font.pygame_fonts[properties] = f
            return f
        return Font.pygame_fonts[properties]


class Text:

    """
    Class to easily have rendered text on screen with a font and other settings.
    """

    __slots__ = (
        "__display_text",
        "__font",
        "color",
        "__surface",
        "antialias",
        "__update",
    )

    def __init__(
        self,
        font: Union[
            Union[
                Tuple[int, str, bool, bool, bool],
                Tuple[int, str, bool, bool],
                Tuple[int, str, bool],
                Tuple[int, str],
            ],
            "Font",
        ],
        display_text: Any,
        color: Color,
        antialias: bool = True,
    ) -> None:
        self.__font: Font = font if isinstance(font, Font) else Font(*font)  # type: ignore
        self.color: Color = color
        self.antialias: bool = antialias
        self.__display_text: str = str(display_text)
        self.__surface: pygame.surface.Surface = self.font._pygame.render(
            display_text, True, color._pygame
        )
        self.__update = False

    @property
    def font(self) -> Font:
        self.__update = True
        return self.__font

    @font.setter
    def font(self, f: Font) -> None:
        self.__update = True
        self.__font = f

    @property
    def display_text(self) -> str:
        """
        The text which will be shown
        """
        return self.__display_text

    @display_text.setter
    def display_text(self, value: Any) -> None:
        self.__display_text = str(value)
        self.__update = True

    @property
    def _surface(self) -> pygame.surface.Surface:
        """
        The surface with the text on
        """
        if self.__update:
            self.__surface = self.font._pygame.render(
                self.__display_text, True, self.color._pygame
            )
        return self.__surface
