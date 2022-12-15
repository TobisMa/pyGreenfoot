from pygreenfoot import World, Actor, PyGreenfoot, keys, Application


class MyActor(Actor):
    def __init__(self):
        Actor.__init__(self)
        self.image = "actor.png"
      
    def act(self) -> None:
        if PyGreenfoot.is_key_pressed("."):
            print(".")
        elif PyGreenfoot.is_key_pressed(keys.K_0):
            print(0)
        
        if PyGreenfoot.get_mouse_wheel():
            print(PyGreenfoot.get_mouse_wheel())
            
        if PyGreenfoot.is_key_pressed("backspace"):
            self.x += 4
            

class TestScene(World):
    def __init__(self) -> None:
        World.__init__(self, 800, 600, 1)
        self.add_to_world(MyActor())
        
    def act(self) -> None:
        ...
        # print("W")
    
    
        
