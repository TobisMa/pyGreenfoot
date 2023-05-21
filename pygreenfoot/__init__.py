import builtins
from functools import cache
import os
from typing import Type
from importlib_resources import files 

# block message of pygame
__orig_print = print
builtins.print = lambda *args, **kwargs : None
import pygame
builtins.print = __orig_print


def get_module_str_import(module_str: str) -> Type:
    importstr = "from " + '.'.join(module_str.split(".")[:-1]) + " import " + module_str.split(".")[-1]
    exec(importstr)
    return eval(module_str.split(".")[-1])


@cache
def get_resource_path(file: str, type_: str) -> str:
    """
    Returns the path to the resource file

    Args:
        file (str): the filename (may include folders)
        type_ (str): the resource type. If it is something else than 'image' or 'sound' this 
        function assumes in the cwd exists an folder of type_ in which the resource is to be found

    Raises:
        FileNotFoundError: If the resource path does not exist

    Returns:
        str: the relative path to the resource from the cwd or absolute posix path to the packages resources
    """
    if type_ == "image":
        folder = Application.get_app().image_folder
        subfolder = "images"
    elif type_ == "sound":
        folder = Application.get_app().sound_folder
        subfolder = "sounds"
    else:
        folder = type_
        subfolder = None
        
    path = os.path.join(folder, file)
    if os.access(path, os.R_OK):
        return path
    
    if subfolder is not None:
        path = files("pygreenfoot").joinpath(subfolder).joinpath(file).as_posix()  # TODO test on other platforms than windows
        if os.access(path, os.R_OK):
            return path
    
    raise FileNotFoundError("Resource not found %r with assumed type %s" % (file, type_))


from . import keys

# assigning the values to the key elements in keys
__keys = {k for k in dir(pygame.constants) if k.startswith("K_")}
for __k in __keys:
    setattr(keys, __k, getattr(pygame.constants, __k))

from .actor import Actor
from .application import Application
from .color import Color
from .image import Image
from .pygreenfoot import PyGreenfoot
from .sound import Sound
from .world import World
from .font import Text, Font

__version__ = "1.0.0"
