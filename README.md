# pyGreenfoot

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
  Application.main(MyWorld())  # notice the init call on the world
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
