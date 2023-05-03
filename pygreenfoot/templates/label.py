from typing import Any, Optional
from pygreenfoot.actor import Actor
from pygreenfoot.color import Color
from pygreenfoot.font import Font, Text
from pygreenfoot.image import Image
from pygreenfoot.world import World


class Label(Actor):
    
    """
    Useful to put text on the screen which behaves like an actor. When the text is larger than the image the text will be clipped
    The image will be set to the world's cell size on world add.
    """
    
    __slots__ = ("__text", "__font", "__background_color", "__needs_update")
    
    def __init__(self, text: Any, font: Font, rotation: int = 0, image: Optional[Image] = None):
        Actor.__init__(self, rotation, image)
        self.__text: str = str(text)
        self.__font: Font = font
        self.__background_color: Optional[Color] = None
        self.__needs_update = True
    
    @property
    def text(self) -> str:
        return self.__text
    
    @text.setter
    def text(self, value: Any) -> None:
        self.__needs_update = True
        self.__text = str(value)
        
    @property
    def font(self) -> Font:
        self.__needs_update
        return self.__font
    
    @property
    def background_color(self) -> Optional[Color]:
        return self.__background_color
    
    @background_color.setter
    def background_color(self, value: Optional[Color]) -> None:
        self.__background_color = value
        self.__needs_update = True
        
    def on_world_add(self, world: World) -> None:
        self.get_image().scale(world.cell_size, world.cell_size)
        self.__needs_update = True
    
    def act(self):
        if self.__needs_update:
            image = self.get_image()
            image.clear()
            if self.__background_color:
                image.fill_with_color(self.__background_color)
            image.draw_text(self.text, 0, 0, self.__font)
            self.set_image(image)
    
