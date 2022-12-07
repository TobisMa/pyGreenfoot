import pygreenfoot

class TestScene(pygreenfoot.Scene):
    def __init__(self) -> None:
        pygreenfoot.Scene.__init__(self, 800, 600, 1)
        
    def act(self) -> None:
        print("Hello World")