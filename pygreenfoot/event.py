from enum import Enum, auto
from typing import Optional

import pygame


class EventType(Enum):
    
    
    QUIT = auto()
    KEYDOWN = auto()
    KEYUP = auto()
    WINDOW_RESIZED = auto()
    
    @classmethod
    def get_by_number(cls, event: int) -> Optional["EventType"]:
        return {
            pygame.QUIT: EventType.QUIT,
            pygame.KEYDOWN: EventType.KEYDOWN,
            pygame.KEYUP: EventType.KEYUP,
            pygame.WINDOWRESIZED: EventType.WINDOW_RESIZED,
        }.get(event)


class Event():
    def __init__(self, event: pygame.event.Event) -> None:
        for name in dir(event):
            if name == "type" or name.startswith("_"):
                continue
            setattr(self, name, getattr(event, name))
        setattr(self, "_orig_type", getattr(event, "type"))
    
    def __repr__(self) -> str:
        return "<Event(type=%s)>" % (self.type,)
    
    @property
    def type(self) -> Optional[EventType]:
        return EventType.get_by_number(self.orig_type)
        
    @property
    def orig_type(self) -> int:
        return self._orig_type   # type: ignore
