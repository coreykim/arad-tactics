import pygame
import main
from resources import res

MODE = 640, 480

pygame.display.init()
pygame.mixer.pre_init(buffer=2048)
try:
    pygame.mixer.init()
except Exception:
    pass

pygame.display.set_mode(MODE, pygame.RESIZABLE)
pygame.display.set_caption('Arad Tactics')
pygame.display.set_icon(res.load_image('icon.png'))
main.Main().run()