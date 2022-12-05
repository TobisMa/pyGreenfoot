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
    
    def __repr__(self) -> str:
        return "Event(" + str({name: getattr(self, name) for name in dir(self) if not name.startswith("_")}) + ")"
    
    @property
    def type(self) -> Optional[EventType]:
        return EventType.get_by_number(self.orig_type)
        
    @property
    def orig_type(self) -> int:
        return self._orig_type
    
    @classmethod
    def to_event(cls, event: pygame.event.Event) -> "Event":
        res_event = Event()
        for name in dir(event):
            if name == "type" or name.startswith("_"):
                continue
            setattr(res_event, name, getattr(event, name))
        setattr(res_event, "_orig_type", getattr(event, "type"))
        return res_event
