import os
from typing import Optional, Tuple, Union

import pygame

from pygreenfoot import get_resource_path

from .color import Color
from .font import Font
from .math_helper import limit_value


class Image:
    
    """
    pygreenfoot's class to handle generally handle images
    """
    
    __slots__ = ("__base_image", "color", "__rot_image", "__rot")
    __hidden_color: Optional[pygame.color.Color] = pygame.color.Color(1, 1, 1)
    
    def __init__(self, image: Union["Image", pygame.surface.Surface]) -> None:
        self.__base_image: pygame.surface.Surface = image.__base_image.copy() if isinstance(image, Image) else image.copy()
        self.__rot_image: pygame.surface.Surface = self.__base_image.copy()  # type: ignore
        self.__rot = 0
        self.color: Color = Color(0, 0, 0)
        
    @property
    def width(self) -> int:
        """
        The width of the image in px
        """
        return self.__base_image.get_width()
    
    @property
    def height(self) -> int:
        """
        The height of the image in px
        """
        return self.__base_image.get_height()
    
    def draw_image(self, image: "Image", x: int, y: int) -> None:
        """
        Draws another Image object onto this one

        Args:
            image (Image): the other image
            x (int): the x position of the upper left corner where to put the image
            y (int): the y position of the upper left corner where to put the image
        """
        self.__base_image.blit(image.__base_image, (x, y))
        
    def draw_line(self, x1: int, y1: int, x2: int, y2: int, width: int = 1) -> None:
        """
        Draws a line on the image from (x1, y1) to (x2, y2)

        Args:
            x1 (int): 1st x-coordinate
            y1 (int): 1st y-coordinate
            x2 (int): 2nd x-coordinate
            y2 (int): 2nd y-coordinate
            width (int, optional): the line width. Defaults to 1.
        """
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
        """
        Fills the canvas with a color. When using `get_hidden_color` this function is equal to `clear`

        Args:
            color (Color, optional): the color to use for clearing the canvas. Defaults to ....
        """
        if color is ...:
            color = self.color
        pygame.draw.rect(self.__base_image, color._pygame, [0, 0, self.width, self.height])
        
    def clear(self) -> None:
        """
        Clears the canvas by setting transparent color
        """
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
        """
        The transparency of the image by the alpha value. This value is from 0 to 255. 0 is fully transparent

        Returns:
            int: the alpha value
        """
        alpha = self.__base_image.get_alpha()
        return 255 if alpha is None else alpha
    
    @alpha.setter
    def alpha(self, alpha: int) -> None:
        self.__base_image.set_alpha(limit_value(alpha, 0, 255))
        
    @staticmethod
    def from_filename(filename: str) -> "Image":
        """
        Create an Image object from an image file

        Args:
            filename (str): the filename/resource path

        Returns:
            Image: the image object
        """
        path = get_resource_path(filename, "image")
        image = pygame.image.load(path)
        return Image(image)
    
    @staticmethod
    def get_empty(width: int, height: int) -> "Image":
        """
        Getting an empty image object

        Args:
            width (int): the width of the empty image
            height (int): the height of the empty image

        Returns:
            Image: the new empty image
        """
        return Image(pygame.Surface((width, height)))
    
    def scale(self, width: int, height: int) -> None:
        """
        Scale the image to a custom size

        Args:
            width (int): the new width
            height (int): the new height
        """
        self.__base_image = pygame.transform.smoothscale(self.__base_image, (width, height))
        
    def copy(self) -> "Image":
        """
        Copy the image object

        Returns:
            Image: the copy
        """
        image = Image(self.__base_image)
        return image
    
    def _set_rot(self, angle: float) -> None:
        """
        Sets the rotation of the image

        Args:
            angle (float): the angle of the rotation in degrees
        """
        self.__rot = angle % 360
        
        if angle == 0:
            self.__rot_image = self.__base_image.copy()
            return
        self.__rot_image = pygame.transform.rotate(self.__base_image, -angle)
    
    @property
    def _surface(self) -> pygame.surface.Surface:
        """
        The image surface for pygame
        """
        return self.__rot_image
    
    @property
    def _rel_pos(self) -> Tuple[int, int]:
        p = pygame.math.Vector2(self.__base_image.get_rect().size)
        p = (p - pygame.math.Vector2(self.__rot_image.get_rect().size))
        return int(p.x), int(p.y)

    @staticmethod
    def set_hidden_color(color: Optional[pygame.color.Color] = None) -> None:
        """
        Set the color used for hiding pixels in the images. This should be set before calling functions using images

        Args:
            color (Optional[pygame.color.Color], optional): the color to use. Defaults to None.
        """
        Image.__hidden_color = color
        
    @staticmethod
    def get_hidden_color() -> Optional[pygame.color.Color]:
        """
        The used hidden color
        NOTE: this color cannot be used in images for drawing or similar because it is hidden as the name implies

        Returns:
            Optional[pygame.color.Color]: the current hidden color used for transparency
        """
        return Image.__hidden_color
    
    def get_color_at(self, x: int, y: int) -> Color:
        """
        Get the color at one particular point in the image

        Args:
            x (int): the x coordinate
            y (int): the y coordinate

        Raises:
            ValueError: if the coordinate is outside of the image

        Returns:
            Color: the color at the specified point
        """
        if x < 0 or x > self.width or y < 0 or y > self.height:
            raise ValueError("Pixel coordinates out of image range")
        return Color.from_pygame_color(self.__base_image.get_at((x, y)))  # type: ignore
    
    def set_color_at(self, x: int, y: int) -> None:
        """
        Set a color at one particular point

        Args:
            x (int): the x coordinate
            y (int): the y coordinate
        """
        self.__base_image.set_at((x, y), self.color._pygame)
        self._set_rot(self.__rot)
        
    def mirror(self, horizontal: bool = False, vertical: bool = False, negate_rotation: bool = False) -> "Image":
        """
        Mirror the image into a new Image object

        Args:
            horizontal (bool, optional): Whether to mirrot horizontally. Defaults to False.
            vertical (bool, optional): Whether to mirrot vertically. Defaults to False.
            negate_rotation (bool, optional): Whether to "mirror" rotation as well. Defaults to False.

        Returns:
            Image: _description_
        """
        new_img = pygame.transform.flip(self.__base_image, vertical, horizontal)
        res_img = Image(new_img)
        if negate_rotation:
            res_img._set_rot(-self.__rot)
        else:
            res_img._set_rot(self.__rot)
        return res_img
    
    @classmethod
    def text_label(cls, text: str, font: Font, foreground: Color, background: Color, outline: Optional[Color] = None, margin: int = 5) -> "Image":        
        """
        Create an text label image object

        Args:
            text (str): the text on the label
            font (Font): the font of the text
            foreground (Color): the foreground color
            background (Color): the background color
            outline (Optional[Color], optional): Whether to outline the boundaries of the text label. Defaults to None.
            margin (int, optional): the margin of the outline. Defaults to 5.

        Returns:
            Image: _description_
        """
        text_size = font._text_size(text)
        text_obj = font.get_text(text, foreground)

        surf = pygame.Surface(text_size)
        surf.fill(background._pygame)
        surf.blit(text_obj._surface, (margin, margin))
        
        if outline:
            pygame.draw.rect(surf, outline._pygame, [0, 0, text_size[0] + margin, text_size[1] + margin], 1)
        
        return Image(surf)
        