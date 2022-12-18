from pygreenfoot import World, Actor, PyGreenfoot, keys, Application
import pygreenfoot


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
                
        if PyGreenfoot.is_mouse_button_pressed(1) and PyGreenfoot.is_mouse_in_window():
            self.turn_towards(*PyGreenfoot.get_mouse_position())
            
        if PyGreenfoot.is_key_pressed("left"):
            self.rot -= 90
        
        if PyGreenfoot.is_key_pressed("right"):
            self.rot += 90
            
        if PyGreenfoot.is_key_pressed("up"):
            self.move(1)
        if PyGreenfoot.is_key_pressed("down"):
            self.move(-1)
        
            
class MyActor2(Actor):
    def __init__(self) -> None:
        Actor.__init__(self)
        self.image = "wizard.png"
    
    def act(self) -> None:
        pass

class TestScene(World):
    def __init__(self) -> None:
        World.__init__(self, 16, 16, 60)
        self.add_to_world(MyActor(), 1, 1)
        self.add_to_world(MyActor2(), 3, 3)
        self.set_background("cell.jpg")
        
    def act(self) -> None:
        ...
        # print("W")
    
    
        
