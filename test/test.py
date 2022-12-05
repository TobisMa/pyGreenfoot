import sys
sys.path.append(".")

from pygreenfoot.scene import Scene


from pygreenfoot import Application
from test_scene import TestScene
app = Application()
app.add_scene(TestScene)
app.current_scene = TestScene()
app.start()

while (app.is_running()):
    for event in app.get_events():
        pass
    app.update()
    