import pygame
from resources import res
from ui import outlined_text

class Title(object):
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.canvas = pygame.Surface((640, 480))
        self.clock = pygame.time.Clock()
        self.quit = False
    def tick(self):
        self.clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
            if event.type == pygame.VIDEORESIZE:
                self.screen=pygame.display.set_mode(event.dict['size'], pygame.RESIZABLE)
    def update(self):
        self.canvas = pygame.transform.smoothscale(self.canvas,
            (pygame.display.get_surface().get_width(),
            pygame.display.get_surface().get_height()))
        self.screen.blit(self.canvas, (0,0))
        pygame.display.flip() #Check out .update()
    def run(self):
        #Initial draw of title screen
        options = [
            ('continue', 'Continue'),
            ('start', 'Start new game'),
            ('exit', 'Exit'),
            ]
        res.play_music('characterSelectStage.ogg')
        pygame.display.flip()
        while True:
            if self.quit:
                return
            self.tick()
            self.canvas = pygame.Surface((640, 480), pygame.SRCALPHA)
            #Insert UI elements, return to quit loop
            self.canvas.fill((142,61,125))
            self.canvas.blit(res.load_image('0.png'), (0,0))
            self.canvas.blit(res.load_image('fighter_illust.png'), (0,0))
            self.canvas.blit(outlined_text(options[1][1], (255,255,255),
                            (1,1,1)), (450,50))
            self.canvas.blit(outlined_text(options[1][1], (255,255,100),
                            (1,1,1)), (450,150))
            self.update()