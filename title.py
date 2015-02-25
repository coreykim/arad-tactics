import pygame
from resources import res
from ui import outlined_text

class Title(object):
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.quit = False
    def tick(self):
        self.clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
    def update(self):
        pygame.display.flip() #Check out .update()
    def run(self):
        #Initial draw of title screen
        options = [
            ('continue', 'Continue'),
            ('start', 'Start new game'),
            ('exit', 'Exit'),
        ]
        if pygame.mixer.get_init():
            pass #Play music
        self.screen.fill((142,61,125))
        pygame.display.flip()
        while True:
            self.tick()
            if self.quit:
                return
            #Insert UI elements, return to quit loop
            #self.screen.blit(res.load_image('ghostsaya1.png'), (0,0))
            self.screen.blit(outlined_text(options[0][1], (20,80,0), (255,255,0)), (0,0))
            pygame.display.flip()