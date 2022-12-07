import sys

sys.path.append(".")
from pygreenfoot import Application
from pygreenfoot import EventType
from pygreenfoot import Scene
from pygreenfoot import keys
from test_scene import TestScene

app = Application()
app.add_scene(TestScene)
app.current_scene = TestScene()
app.start()

while (app.is_running()):
    app.update()
    