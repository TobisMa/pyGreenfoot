import os
from typing import IO, Union

import pygame

pygame.mixer.init()

class Sound(pygame.mixer.Sound):    
    def __init__(self, filename_or_buffer: Union[IO, str]) -> None:
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()
        
        if isinstance(filename_or_buffer, str):
            from pygreenfoot import Application
            filename_or_buffer = os.path.join(Application.get_app().sound_folder, filename_or_buffer)
            
        pygame.mixer.Sound.__init__(self, filename_or_buffer)
        
    @staticmethod
    def stop_all(fadeout_time_ms: int = 0) -> None:
        if pygame.mixer.get_init() is not None:
            pygame.mixer.fadeout(fadeout_time_ms)
