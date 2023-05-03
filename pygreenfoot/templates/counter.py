from turtle import st

from pygreenfoot import Actor, Font, Color


class Counter(Actor):
    
    """
    A counter where you can use a prefix before the count.
    This counter works like an actor and needs to be added to the active world to be visible.
    """
    
    __slots__ = ("prefix", "__value", "__needs_update")
    
    def __init__(self, prefix: str = "", start_value: int = 0, rotation: int = 0):
        Actor.__init__(self, rotation)
        self.prefix: str = prefix
        self.__needs_update = True
        self.__value: int = start_value
        
    @property
    def value(self) -> int:
        return self.__value
    
    @value.setter
    def value(self, value: int) -> None:
        self.__needs_update = True
        self.__value = value
        
    def act(self) -> None:
        if self.__needs_update:
            display = self.prefix + str(self.value)
            f = Font(Font.get_default_font())
            twidth, theight = f._text_size(display)
            img = self.get_image()
            img.scale(twidth + 10, theight + 10)
            img.color = Color.WHITE
            img.fill_with_color()
            img.color = Color.BLACK
            img.draw_rect(0, 0, twidth + 9, theight + 9)
            img.draw_text(display, 5, 5, f)
        
    
    
        