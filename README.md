# pyGreenfoot

## Install
Either move the `pygreenfoot` folder in the working directory from where the main file gets executed
or use pip: `pip install git+https://github.com/TobisMa/pyGreenfoot`

## How to begin a project
Install the project using the ps1 script for the desired solution or use the `pygreenfoot-v**.zip` file from the release and move the pygreenfoot folder to your python site-packages folder.

### Create a world
wordl.py:
```py
from pygreenfoot import World

class MyWorld(World):
  def __init__(self):
    super(8, 8, 60)
```

### Set the world as entry on the application
```py
from pygreenfoot import Application
from world import MyWorld

if __name__ == "__main__":
  Application.main(MyWorld)  # notice that the class is not instantiated
```

### What to use the world for
Now use the world to add/remove actors. Actors are classes inheriting `pygreenfoot.Actor`. 
For example `actor.py`:
```py
from pygreenfoot import Actor

class MyActor(Actor):
  def __init__(self):
    Actor.__init__(self, rotation=0, image=None)  # those are the default values

  def on_world_add(world):
    print("Added actor to world.")

  def act(self):
    pass # do your cyclic stuff
```
The act methods on worlds and actors are called once per frame and used for whatever you want.
It is also possible to change the current world

Now change the world to:
```py
from pygreenfoot import World
from actor import MyActor

class MyWorld(World):
  def __init__(self):
    super(8, 8, 60)
    self.add_to_world(MyActor(), 1, 1) # adds the actor to the world
```

## config file
the module allows for a config file in the root project named `pygreenfoot.config`.
Each line consist of an attribute and value separated by an `=` per default.

| Attribute | value type | Default | Function | 
| :-- | :--- | :-- | :--- |
| generateDiagram | boolean | `true` | whether to generate an plantuml diagram/image |
| generateImage | boolean | `true` | whether to generate the image diagram (uses external server; requires web access) |
| tempPlantumlFile | boolean | `false` | whether to delete the text file of the diagram afterwards or to keep it| 
| diagramFilename | string | `diagram` | the filename of the diagram text file and image (without extension). The extension is added automatically |
| diagramFolder | string | `_structure` | the folder where to put the files. Use `.` for the same folder as the project (not recommended) |
| imageResourceFolder | string | `images` | where to look for images. This folder will be created if it does not already exist |
| soundResourceFolder | string | `sounds` | where to look for sound files. This folder will be created if it does not already exist |
| fpsLimit | signed int | `60` | The maximum fps for the game |
| defaultWorldSpeed | signed int | `0` | the delay between the cycles of the worlds. These are independent of the fpsLimit |
| windowWidth | optional signed int | `unset` | the windowWidth of the game. If given this will set the window to a fixed width |
| windowHeight | optional signed int | `unset` | same as width, but for the height |
| windowMode | windowMode | `RESIZABLE` | the window mode during the game |

### the types above explained 
| Type | Possible values |
| :--- | :--- |
| boolean | case-insensitive `true` or `false` |
| string | some order of chars. Should not be enclosed by quotation marks (`"`, `'`). |
| signed integer | some integer value >= `0`. E. g. `1`, `5`, `32802` |
| optional | case-insesitive `unset`, `null` or `none` |
| optional signed integer | some value of either `optional` or `signed integer` |
| windowMode | either `RESIZABLE` or `FULLSCREEN` or `BORDERLESS` |


## Editor to use
Use the editor of your joice. Both PyCharm and Visual Studio Code provide an internal integration for plantuml diagrams

## Plantuml integration
Is used to generate an hierachical tree of your project.
When the main application is run, a valid plantuml diagram will be generated in `./_structure/diagram.wsd`. When the python package `plantuml` is installed an image will be created in the same folder. 

### Plantuml extensions in editors
The provided extension IDs below are integrations within the editor window:  
- Visual Studio code: `jebbs.plantuml`  
- PyCharm: `PlantUML integration`
- Other: `https://plantuml.com/de/running`
