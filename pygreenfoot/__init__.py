import builtins
import importlib
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

__version__ = "1.0.0"

# check for folder
if not os.access("./images", os.F_OK):
    os.mkdir("./images", 0o444)

if not os.access("./sounds", os.F_OK):
    os.mkdir("./sounds", 0o444)
    
    

try:
    config_file = open("config.pygreenfoot", "r")
except FileNotFoundError:
    with open("config.pygreenfoot", "w") as f:
        f.write("run_main=False\nstart_world=")

    cnf = {
        "run_main": False,
        "start_world": None
    }

else:
    data = config_file.read()
    config_file.close()

    cnf = {}
    attr, value = 0, 0
    for line in data.split("\n"):
        line.strip()
        if "=" not in line or not line:
            continue

        attr, value = line.split("=")
        if attr == "run_main":
            cnf["run_main"] = eval(value)
        elif attr == "start_world":
            cnf["start_world"] = None if value in ["None", ""] else value

    del attr, value

# app = Application.get_app()
# start_world = None
# if cnf["start_world"] is not None:
#     start_world = get_world(cnf["start_world"])
#     if cnf["run_main"]:
#         Application.main(start_world())

# elif cnf["run_main"]:
#     print(cnf)
#     raise ValueError("When the main function shall be run by this module a start world has to be given as well")
# del cnf, start_world, app

# generate default script
filenames = ["run.py", "start.py", "scenario.py"]
filename = "main.py"
while os.access(filename, os.F_OK):
    filename = filenames.pop(0)
    
start_world = "" if cnf["start_world"] is None else cnf["start_world"].split(".")[-1]
importstr = "" if cnf["start_world"] is None else "from " + '.'.join(cnf["start_world"].split(".")[:-1]) + " import " + cnf["start_world"].split(".")[-1]
with open(filename, "w") as f:
    f.write(f"from pygreenfoot import Application\n{importstr}\nif __name__ == '__main__':\tApplication.main({start_world}())")

del pygame, os, builtins