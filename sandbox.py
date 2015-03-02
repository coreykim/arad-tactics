import pygame
from resources import res

pygame.init()

a = res.load_image('default_fighter.png')
camera = pygame.Rect(50, 50, 500, 500)

start = pygame.time.get_ticks()

b = pygame.Surface((2000, 2000))
b.blit(a, (0,0))
c = pygame.Surface((2000, 2000))
c.blit(b, (0,0), area=camera)
print pygame.time.get_ticks()-start