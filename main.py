from pygreenfoot import Application, World
from pygreenfoot import PyGreenfoot

class MyWorld(World):
    def __init__(self):
        World.__init__(self, 45, 45, 40)
        self.set_background("cell.jpg")
        for i in range(self.width):
            for j in range(self.height):
                ...
                # self.show_text(str(i * j)[:2], i, j)
        self.show_text("A", 44, 44)
        
    def act(self):
        shift_pressed = PyGreenfoot.is_key_pressed("shift")
        movement = 30 * -PyGreenfoot.get_mouse_wheel()
        if shift_pressed:
            Application.get_app().move_world(movement, 0)
        else:
            Application.get_app().move_world(0, movement)
        
        if PyGreenfoot.is_key_pressed("ctrl") and PyGreenfoot.is_key_pressed("q") and shift_pressed:
            Application.get_app().stop()
        

if __name__ == '__main__':	Application.main()
