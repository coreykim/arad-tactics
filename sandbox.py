import pygame
from resources import res

pygame.init()


start = pygame.time.get_ticks()

pants = pygame.Rect(0, 0.2, 100, 100)
a = pants.width
pants.width += 50
print pants
print a


print pygame.time.get_ticks()-start