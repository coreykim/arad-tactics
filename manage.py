import pygame
from resources import res
import ui
import avatar

class CharacterSelect(ui.Frame):
    def __init__(self, avatar, character_name, i):
        self.avatar = avatar
        self.name = character_name
        rect = (170+200*i, 100, 100, 150)
        super(CharacterSelect, self).__init__(rect)
    def render(self):
        self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        if self.active:
            self.highlight = pygame.Surface(self.rect.size)
            self.highlight.fill((240,220,120))
            self.highlight.set_alpha(50)
            self.image.blit(self.highlight, (0,0))
            text = ui.outlined_text(self.name, (240,220,120))
            self.image.blit(text, (int(self.rect.width/2-text.get_width()/2),
                            self.avatar.height+5))
        else:
            text = ui.outlined_text(self.name)
            self.image.blit(text, (int(self.rect.width/2-text.get_width()/2),
                            self.avatar.height+5))
        self.image.blit(self.avatar.image, (int(self.rect.width/2)
            - self.avatar.center[0], self.avatar.height-self.avatar.center[1]))
    def update(self):
        self.avatar.update()
        self.render()

class Manage(object):
    def __init__(self, main):
        self.main = main
        self.ui = pygame.sprite.LayeredUpdates()
        if not self.main.data:
            self.selection = None
            elements = [ui.TextLine(0, 30, 'Select a class:')]
            for element in elements:
                element.rect = element.rect.move(
                        320-int(element.rect.width/2), 0)
                self.ui.add(element)
            choices = [
                (avatar.Slayer(), 'Slayer'),
                (avatar.Fighter(), 'Fighter')
                ]
            for i, choice in enumerate(choices):
                element = CharacterSelect(choice[0], choice[1], i)
                self.ui.add(element)
    def draw(self):
        self.main.canvas.blit(res.load_image('0.png'), (0,0))
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
        if not self.main.data:
            self.new_game = True
        else:
            self.new_game = False
        self.event_handler()
        self.draw()