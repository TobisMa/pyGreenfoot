from typing import List
from pygreenfoot import Application, World
from pygreenfoot import PyGreenfoot
from pygreenfoot import Actor

class MyWorld(World):
    def __init__(self):
        World.__init__(self, 55, 45, 40)
        self.set_background("cell.jpg")
        for i in range(self.width):
            for j in range(self.height):
                self.show_text(str(i * j)[:2], i, j)
        self.show_text("A", 44, 44)
        # Application.get_app().show_scrollbar = [False, False]
        a = self.get_actors_generator(MA)
        
    def act(self):
        shift_pressed = PyGreenfoot.is_key_pressed("shift")
        movement = 30 * -PyGreenfoot.get_mouse_wheel()
        if shift_pressed:
            Application.get_app().move_world(movement, 0)
        else:
            Application.get_app().move_world(0, movement)
        
        if movement != 0:
            print(f"{movement=}")

        if PyGreenfoot.is_key_pressed("ctrl") and PyGreenfoot.is_key_pressed("Q"):
            Application.get_app().stop()
        elif PyGreenfoot.is_key_pressed("r"):
            print(Application.get_app().delta_pos)
            Application.get_app().set_world_position(0, 0)
            
class MA(Actor):
    def __init__(self):
        Actor.__init__(self)
        a = self.get_actors_in_range(3, MA)
        a[0].test_method
        
    def test_method(self):
        pass
        

if __name__ == '__main__':	Application.main()
