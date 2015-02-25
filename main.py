import pygame
import title

MODE = 720, 480

pygame.display.init()
pygame.mixer.pre_init(buffer=512)
try:
    pygame.mixer.init()
except Exception:
    pass

pygame.display.set_mode(MODE)
pygame.display.set_caption("Arad Tactics")
title.Title().run()