import pygame

from . import keys

# assigning the values to the key elements in keys
__keys = {k for k in dir(pygame.constants) if k.startswith("K_")}
for __k in __keys:
    setattr(keys, __k, getattr(pygame.constants, __k))

from .actor import Actor
from .application import Application
from .color import *
from .image import Image
from .pygreenfoot import PyGreenfoot
from .sound import Sound
from .world import World

__version__ = "1.0.0"

del pygame