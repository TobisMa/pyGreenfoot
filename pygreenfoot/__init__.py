import pygame
from .application import Application
from .gameObject import GameObject
from .scene import Scene
from . import keys
from .event import Event, EventType

# assigning the values to the key elements in keys
__keys = {k for k in dir(pygame.constants) if k.startswith("K_")}
for __k in __keys:
    setattr(keys, __k, getattr(pygame.constants, __k))
