import pygame
from resources import res
import ui
import random

class TitleSelection(ui.Clicky):
    def __init__(self, x, y, option):
        self.option = option
        rect = ui.outlined_text(self.option[1]).get_rect()
        rect = rect.move(x, y)
        super(TitleSelection, self).__init__(rect)
    def render(self):
        if self.active:
            self.image = ui.outlined_text(self.option[1], color=(230,230,100))
        else:
            self.image = ui.outlined_text(self.option[1])
    def mousebuttondown(self, caller):
        caller.selection = self.option[0]

class Title(object):
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.ui = pygame.sprite.LayeredUpdates()
        self.canvas = pygame.Surface((640, 480))
        self.clock = pygame.time.Clock()
        self.selection = ""
        self.quit = False
    def tick(self):
        self.clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
            if event.type == pygame.VIDEORESIZE:
                self.screen=pygame.display.set_mode(event.dict['size'], pygame.RESIZABLE)
            for sprite in self.ui.sprites():
                sprite.input(event, self)
    def update(self):
        self.ui.draw(self.canvas)
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
        self.ui.add(TitleSelection(450, 50, options[0]))
        self.ui.add(TitleSelection(450, 100, options[1]))
        self.ui.add(TitleSelection(450, 150, options[2]))
        splash = str(random.randrange(5))
        res.play_music('characterSelectStage.ogg')
        while True:
            if self.quit or self.selection=='exit':
                return
            self.tick()
            self.canvas = pygame.Surface((640, 480), pygame.SRCALPHA)
            #Insert UI elements, return to quit loop
            self.canvas.blit(res.load_image('0.png'), (0,0))
            self.canvas.blit(res.load_image('illust'+splash+'.png'), (0,0))
            self.update()