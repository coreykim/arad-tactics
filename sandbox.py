import pygame
pygame.init()
from resources import res

a = res.load_image('default_slayer.png') #320
a = pygame.transform.smoothscale(a, (100, 100))
#b = a.copy()

def create_new():
    for c in range(10):
        c = pygame.Surface((4000, 3000))
        c.blit(a, (0,0))
        #camera = pygame.Rect(0, 0, 200, 200)
        #b.set_clip(camera)
        #b.blit(a, (0,0))
def copy():
    b = a.copy()
def new():
    b = pygame.Surface((100, 100), flags=pygame.SRCALPHA)
    print b.get_bounding_rect().width
new()
print pygame.time.get_ticks()