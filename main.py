from pygreenfoot import Application, World

class T(World):
    def __init__(self):
        World.__init__(self, 60, 60, 1)
        self.set_background("cell.jpg")
        

if __name__ == '__main__':	Application.main(T)
