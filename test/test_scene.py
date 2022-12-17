from pygreenfoot import World, Actor, PyGreenfoot, keys, Application


class MyActor(Actor):
    def __init__(self):
        Actor.__init__(self)
        self.image = "hase.png"
        self.image.draw_text("Hello World", 0, 0)
      
    def act(self) -> None:
        if PyGreenfoot.is_key_pressed("a"):
            self.x -= 1
        if PyGreenfoot.is_key_pressed("d"):
            self.x += 1
        
        if PyGreenfoot.is_key_pressed("w"):
            self.y -= 1
        if PyGreenfoot.is_key_pressed("s"):
            self.y += 1
            
        if PyGreenfoot.is_key_pressed("space"):
            self.image.alpha -= 1
            print(self.image.alpha)
        
        if PyGreenfoot.is_key_pressed("enter"):
            print("enter")
            print(self.get_world().get_objects_at(0, 0))
            
        if PyGreenfoot.is_key_pressed("delete"):
            if self.get_world().get_text_at(3, 3) is None:
                self.get_world().show_text("My World", 3, 3)
            else:
                self.get_world().show_text(None, 3, 3)

class TestScene(World):
    def __init__(self) -> None:
        World.__init__(self, 16, 16, 60)
        self.add_to_world(MyActor())
        self.set_background("cell.jpg")
        
    def act(self) -> None:
        ...
        # print("W")
    
    
        
