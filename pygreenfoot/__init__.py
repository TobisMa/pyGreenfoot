import pygame
from .application import Application
from .actor import Actor
from .world import World
from . import keys
from .pygreenfoot import PyGreenfoot

# assigning the values to the key elements in keys
__keys = {k for k in dir(pygame.constants) if k.startswith("K_")}
for __k in __keys:
    setattr(keys, __k, getattr(pygame.constants, __k))
