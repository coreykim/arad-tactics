import pygame
from resources import res
import ui
import manage
import random

class Title(object):
    def __init__(self, main):
        self.main = main
        self.ui = pygame.sprite.LayeredUpdates()
        self.selection = 'root'
        res.play_music('characterSelectStage.ogg')
        self.splash = str(random.randrange(5))
    def draw(self):
        self.main.canvas.blit(res.load_image('0.png'), (0,0))
        self.main.canvas.blit(res.load_image('illust'+self.splash+'.png'), (0,0))
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
        self.event_handler()
        #Initial draw of title screen
        if self.selection=='exit':
            self.main.quit = True
            return
        elif self.selection=="root":
            self.ui.empty()
            root = [
                ('continue', 'Continue'),
                ('start', 'Start new game'),
                ('options', 'Options'),
                ('exit', 'Exit'),
                ]
            self.selection = ' '
            for i in range(len(root)):
                self.ui.add(ui.TextSelection(450, 80+50*i, root[i]))
        elif self.selection== 'options':
            self.ui.empty()
            options = [
                ((640,480), '640x480 (default)'),
                ((800,600), '800x600'),
                ((960,720), '960x720'),
                ((1280,960), '1280x960'),
                ('root', 'Back to main'),
                ]
            self.selection = ' '
            for i in range(len(options)):
                self.ui.add(ui.TextSelection(450, 80+50*i, options[i]))
        elif len(self.selection)==2:
            pygame.display.set_mode(self.selection, pygame.RESIZABLE)
            self.selection = 'options'
        elif self.selection== 'start':
            self.main.routine = manage.Manage(self.main)
        self.draw()