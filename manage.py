import pygame
from resources import res
import ui
import avatar
import title
import battle

class Manage(object):
    def __init__(self, main):
        self.main = main
        pygame.mixer.music.fadeout(1000)
        self.selection = ' '
        self.party_index = 0
        self.ui = pygame.sprite.LayeredUpdates()
        self.ui.add(ui.Frame((50, 20, 640-50, 480-20), color=(20,20,20)))
        self.ui.add(ui.Frame((0, 20, 50, 50), color=(20,20,20)))
        char = self.main.data[self.party_index]
        align = (120, 50)
        self.ui.add(ui.TextLine(align[0], align[1], char.name))
        self.ui.add(ui.TextLine(align[0], align[1]+20, 'HP: {}/{}'.format(
            char.hp, char.max_hp)))
        self.ui.add(ui.TextLine(align[0], align[1]+35, 'Resilience: {}'.format(
            char.basestat.resilience)))
        self.ui.add(ui.TextLine(align[0], align[1]+50, 'Power: {}'.format(
            char.basestat.power)))
        self.ui.add(ui.TextLine(align[0], align[1]+65, 'Speed: {}'.format(
            char.basestat.speed)))
        self.ui.add(CharacterPreview(char.avatar))
        self.ui.add(ui.TextSelection(0, 0, ('next', 'Next')))
    def draw(self):
        self.main.canvas.fill((80, 80, 80))
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
        if self.selection=='next':
            self.main.routine = battle.Battle(self.main)

class CharacterPreview(ui.Frame):
    def __init__(self, avatar):
        self.avatar = avatar
        rect = (400, 30, 100, 140)
        super(CharacterPreview, self).__init__(rect)
    def render(self):
        self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.image.blit(self.avatar.image, (int(self.rect.width/2)
            - self.avatar.center[0], self.avatar.height-self.avatar.center[1]))
    def update(self):
        self.avatar.update()
        self.render()