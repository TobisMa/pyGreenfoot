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

###
Now use the world to add/remove actors. Actors are classes subclassing `pygreenfoot.Actor`. 
The act methods on worlds and actors are called once per frame and used for whatever you want.
It is also possible to change the current world

# Plantuml integration
Is used to generate an hierachical tree of your project.
When the main application is run, a valid plantuml diagram will be generated in `./_structure/diagram.wsd`. When the python package `plantuml` is installed a image will be created in the same folder. 


# Editor to use
Use the editor of your joice. Both PyCharm and Visual Studio Code provide an internal integration for plantuml diagrams
