import pygame
from resources import res
import ui
import avatar
import title

class Battle(object):
    def __init__(self, main):
        self.main = main
        self.ui = pygame.sprite.LayeredUpdates()
        self.turn = 0
        self.phase = 'action'
        self.player_turn = True
        self.ui.add(ui.TextLine(0,0,"lolol this is gonna take a while don't get your hopes up"))
    def draw(self):
        self.main.canvas.fill((80, 80, 255))
        self.ui.update()
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
        self.draw()

class Tile(object):
    def __init__(self):
        self.occupant = []
        self.effect = []
        self.terrain = [] #like a permanent effect
class Map(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        