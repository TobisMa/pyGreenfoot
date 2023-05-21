from typing import IO, Union

import pygame

from pygreenfoot import get_resource_path

pygame.mixer.init()

class Sound(pygame.mixer.Sound):
    
    """
    pygreenfoot sound class. 
    Look for documentation on https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Sound
    """
    
    def __init__(self, filename_or_buffer: Union[IO, str]) -> None:
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()
        
        if isinstance(filename_or_buffer, str):
            from pygreenfoot import Application
            filename_or_buffer = get_resource_path(filename_or_buffer, "sound")
            
        pygame.mixer.Sound.__init__(self, filename_or_buffer)
        
    @staticmethod
    def stop_all(fadeout_time_ms: int = 0) -> None:
        """
        Stop all played sounds

        Args:
            fadeout_time_ms (int, optional): the fadeout time. Defaults to 0.
        """
        if pygame.mixer.get_init() is not None:
            pygame.mixer.fadeout(fadeout_time_ms)
