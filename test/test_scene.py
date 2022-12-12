from pygreenfoot import World, Actor, PyGreenfoot, keys, Application


class MyActor(Actor):        
    def act(self) -> None:
        if PyGreenfoot.is_key_pressed("."):
            print(".")
        elif PyGreenfoot.is_key_pressed(keys.K_0):
            print(0)
        
        if PyGreenfoot.get_mouse_wheel():
            print(PyGreenfoot.get_mouse_wheel())
            

class TestScene(World):
    def __init__(self) -> None:
        World.__init__(self, 800, 600, 1)
        self.add_to_world(MyActor())
        
    def act(self) -> None:
        ...
        # print("W")
    
    
        
