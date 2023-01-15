from abc import abstractmethod
from typing import Optional
from pygreenfoot import Actor
from pygreenfoot import Image


class InitActor(Actor):
    
    __slots__ = ("__init",)
    
    def __init__(self, rotation: int = 0, image: Optional[Image] = None) -> None:
        Actor.__init__(self, rotation, image)
        self.__init: bool = False
    
    @abstractmethod
    def init(self) -> None:
        raise NotImplementedError("subclasses of InitActor must override the init method")
    
    def act(self) -> None:
        if not self.__init:
            self.init()
            self.__init = True