from pygreenfoot import Application, World

class MyWorld(World):
    def __init__(self):
        World.__init__(self, 4, 4, 40)
        self.set_background("cell.jpg")
        

if __name__ == '__main__':	Application.main()
