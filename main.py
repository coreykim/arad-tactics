import pygame
import title
import avatar

class Main(object):
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.ratio = (16, 12)
        self.canvas = pygame.Surface((self.ratio[0]*40, self.ratio[1]*40))
        self.clock = pygame.time.Clock()
        self.data = None
        self.routine = title.Title(self)
        self.quit = False
    def draw(self):
        self.canvas = pygame.transform.smoothscale(self.canvas,
            (pygame.display.get_surface().get_width(),
            pygame.display.get_surface().get_height()))
        self.screen.blit(self.canvas, (0,0))
        self.canvas = pygame.Surface((self.ratio[0]*40, self.ratio[1]*40))
        pygame.display.flip()
    def run(self):
        while True:
            if self.quit == True:
                return
            self.routine.run()
            self.draw()
            self.clock.tick(30)