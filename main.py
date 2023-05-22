from typing import List
from pygreenfoot import Application, World
from pygreenfoot import PyGreenfoot
from pygreenfoot import Actor

class MyWorld(World):
    def __init__(self):
        World.__init__(self, 10, 10, 40)
        self.set_background("Background Pits Muted.png")
        for i in range(self.width):
            for j in range(self.height):
                ...
                # self.show_text(str(i * j)[:2], i, j)
        self.show_text("A", 44, 44)
        # Application.get_app().show_scrollbar = [False, False]
        self.add_to_world(MA(), 2, 2)
        self.world_speed = 0.05
        
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
        self.set_image("hase.png")
        self.get_image().scale(40, 40)
        
    def act(self):
        if PyGreenfoot.is_key_pressed("w"):
            self.y -= 1
        if PyGreenfoot.is_key_pressed("a"):
            self.x -= 1
        if PyGreenfoot.is_key_pressed("s"):
            self.y += 1
        if PyGreenfoot.is_key_pressed("d"):
            self.x += 1
        

if __name__ == '__main__':	Application.main()
