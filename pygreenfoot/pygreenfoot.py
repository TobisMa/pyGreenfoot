from .__types import _Key
from .application import Application
from . import keys


__len23 = range(2, 4)


class PyGreenfoot:
    @staticmethod
    def is_key_pressed(key: _Key) -> bool:  # sourcery skip: low-code-quality
        app = Application.get_app()
        if isinstance(key, str):
            if len(key) == 1:
                if key.isdigit() or key.islower():
                    key = getattr(keys, "K_" + key)
                elif key.isupper():
                    shift = all(app.get_key_states(keys.K_LSHIFT, keys.K_RSHIFT))
                    return shift and app.get_key_states(getattr(keys, "K_" + key.lower()))[0]
            else:
                if len(key) in __len23 and key.startswith(("f", "F")):
                    return app.get_key_states(getattr(keys, "K_" + key.upper()))[0]
                
                key = key.lower()
                if key == "meta":
                    return any(app.get_key_states(keys.K_LMETA, keys.K_RMETA))
                elif key in ("ctrl", "strg"):
                    return any(app.get_key_states(keys.K_LCTRL, keys.K_RCTRL))
                elif key == "shift":
                    return any(app.get_key_states(keys.K_LSHIFT, keys.K_RSHIFT))
                elif key == "alt":
                    return app.get_key_states(keys.K_LALT)[0]
                elif key == "alt gr":
                    return app.get_key_states(keys.K_RALT)[0]
                elif key == "backspace":
                    return app.get_key_states(keys.K_BACKSPACE)[0]
                elif key == "delete":
                    return app.get_key_states(keys.K_DELETE)[0]
                elif key == "insert":
                    return app.get_key_states(keys.K_INSERT)[0]
                elif key == ".":
                    return app.get_key_states(keys.K_PERIOD)[0]
                elif key == ",":
                    return app.get_key_states(keys.K_COMMA)[0]
            
        return app.get_key_states(key)[0]