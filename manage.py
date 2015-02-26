import pygame
from resources import res
import ui
import avatar

class Manage(object):
    def __init__(self, main):
        self.main = main
        self.ui = pygame.sprite.LayeredUpdates()
        self.slayer = avatar.Slayer()
        print pygame.time.get_ticks()
        if not self.main.data:
            self.selection = None
            elements = [ui.TextLine(0, 30, 'Select a class:'),
                        ui.TextSelection(0, 80, ('slayer', 'Slayer'))]
            for element in elements:
                element.rect = element.rect.move(
                        320-int(element.rect.width/2), 0)
                self.ui.add(element)
    def draw(self):
        self.main.canvas.blit(res.load_image('0.png'), (0,0))
        self.main.canvas.blit(self.slayer.image,
            (250,150))
        self.slayer.update()
        self.ui.draw(self.main.canvas)
    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.main.quit = True
            if event.type == pygame.VIDEORESIZE:
                self.main.screen=pygame.display.set_mode(event.dict['size'], pygame.RESIZABLE)
            for sprite in self.ui.sprites():
                sprite.input(event, self)
    def run(self):
        if not self.main.data:
            self.new_game = True
        else:
            self.new_game = False
        self.event_handler()
        self.draw()