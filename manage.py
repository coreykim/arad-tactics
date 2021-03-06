import pygame
from resources import res
import ui
import avatar
import title
import battle
import skill

class Manage(object):
    def __init__(self, main):
        self.main = main
        pygame.mixer.music.fadeout(1000)
        self.selection = ' '
        self.party_index = 0
        self.ui = pygame.sprite.LayeredUpdates()
        self.ui.add(ui.Frame((50, 20, 640-50, 480-20), color=(20,20,20)))
        self.ui.add(ui.Frame((0, 20, 50, 50), color=(20,20,20)))
        self.char_data = []
        self.show_char(self.main.data[self.party_index])
        self.ui.add(ui.TextSelection(0, 0, ('next', 'Next')))
    def draw(self):
        self.main.canvas.fill((80, 80, 80))
        self.ui.update()
        self.ui.draw(self.main.canvas)
    def run(self):
        self.draw()
        if self.selection=='next':
            self.main.routine = battle.Battle(self.main)
    def show_char(self, char):
        for data in self.char_data:
            self.ui.remove(data)
        self.char_data = []
        self.char_data.append(ui.Image(12, 32, char.avatar.portrait))
        align = (120, 50)
        self.char_data.append(ui.TextLine(align[0], align[1], char.name))
        self.char_data.append(ui.TextLine(align[0], align[1]+20, 'HP: {}/{}'.format(
            char.hp, char.max_hp)))
        self.char_data.append(ui.TextLine(align[0], align[1]+35, 'Resilience: {}'.format(
            char.basestat.resilience)))
        self.char_data.append(ui.TextLine(align[0], align[1]+50, 'Power: {}'.format(
            char.basestat.power)))
        self.char_data.append(ui.TextLine(align[0], align[1]+65, 'Speed: {}'.format(
            char.basestat.speed)))
        self.char_data.append(ui.TextLine(align[0], align[1]+95, 'Skill Points: {}'.format(
            char.skill_points)))
        self.char_data.append(CharacterPreview(char.avatar))
        self.char_data.append(ui.Image(align[0], align[1]+140, char.skill[0].icon))
        for data in self.char_data:
            self.ui.add(data)

soul = [
        (skill.GhostSlash, skill.MoonlightSlash),
        (skill.Bremen)
        ]

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