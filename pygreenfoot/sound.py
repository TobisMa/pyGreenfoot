from typing import IO, Union

import pygame

pygame.mixer.init()

class Sound(pygame.mixer.Sound):    
    def __init__(self, filename_or_buffer: Union[IO, str]) -> None:
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()
        pygame.mixer.Sound.__init__(self, filename_or_buffer)
        
    @staticmethod
    def stop_all(fadeout_time_ms: int = 0) -> None:
        if pygame.mixer.get_init() is not None:
            pygame.mixer.fadeout(fadeout_time_ms)