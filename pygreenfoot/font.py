import pygame

FONTS = pygame.font.get_fonts()


def default_font() -> str:
    return pygame.font.get_default_font() 