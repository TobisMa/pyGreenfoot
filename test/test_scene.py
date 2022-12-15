from pygreenfoot import World, Actor, PyGreenfoot, keys, Application


class MyActor(Actor):
    def __init__(self):
        Actor.__init__(self)
        self.image = "hase.png"
      
    def act(self) -> None:
        if PyGreenfoot.is_key_pressed("."):
            print(".")
        elif PyGreenfoot.is_key_pressed(keys.K_0):
            print(0)
        
        if PyGreenfoot.get_mouse_wheel():
            print(PyGreenfoot.get_mouse_wheel())
            
        if PyGreenfoot.is_key_pressed("backspace"):
            self.x += 1
            

class TestScene(World):
    def __init__(self) -> None:
        World.__init__(self, 16, 16, 60)
        self.add_to_world(MyActor())
        self.set_background("cell.jpg")
        
    def act(self) -> None:
        ...
        # print("W")
    
    
        
