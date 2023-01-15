import builtins
import os
from typing import Type

# block message of pygame
__orig_print = print
builtins.print = lambda *args, **kwargs : None
import pygame
builtins.print = __orig_print


def get_world(module_str: str) -> Type:
    importstr = "from " + '.'.join(module_str.split(".")[:-1]) + " import " + module_str.split(".")[-1]
    exec(importstr)
    return eval(module_str.split(".")[-1])


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
from .font import Text, Font

__version__ = "1.0.0"

# check for folder
if not os.access("./images", os.F_OK):
    os.mkdir("./images", 0o444)

if not os.access("./sounds", os.F_OK):
    os.mkdir("./sounds", 0o444)
    
