import pygame
from resources import res
import ui
import manage
import random
import avatar
import character
import skill

class Title(object):
    def __init__(self, main):
        self.main = main
        self.ui = pygame.sprite.LayeredUpdates()
        self.selection = 'root'
        res.play_music('characterSelectStage.ogg')
        self.splash = ui.Image(0, 0, res.load_image('illust'+str(random.randrange(5))+'.png'))
        self.splash.rect = self.splash.rect.move(0, 480-self.splash.rect.height)
        self.background = res.load_image('0.png')
        self.main.canvas.blit(self.background, (0,0))
        self.ui.add(self.splash)
    def draw(self):
        self.ui.clear(self.main.canvas, self.background)
        self.ui.draw(self.main.canvas)
        self.ui.update()
    def run(self):
        if self.selection=='exit':
            self.main.quit = True
            return
        elif self.selection=="root":
            self.ui.empty()
            self.ui.add(self.splash)
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
            self.ui.add(self.splash)
            options = [
                ((640,480), '640x480'),
                ((800,600), '800x600'),
                ((960,720), '960x720'),
                ((1280,960), '1280x960'),
                ('root', 'Back'),
                ]
            self.selection = ' '
            for i in range(len(options)):
                self.ui.add(ui.TextSelection(450, 80+50*i, options[i]))
        elif len(self.selection)==2:
            pygame.display.set_mode(self.selection, pygame.RESIZABLE)
            if self.selection[0]*9 == self.selection[1]*16:
                self.main.ratio = (16, 9)
            else:
                self.main.ratio = (16, 12)
            self.selection = 'options'
        elif self.selection== 'start':
            self.ui.empty()
            text = ui.TextLine(0, 30, 'Select a class:')
            text.rect = text.rect.move(
                        320-int(text.rect.width/2), 0)
            self.ui.add(text)
            choices = [
                (avatar.Slayer(), 'Slayer'),
                (avatar.Fighter(), 'Fighter')
                ]
            for i, choice in enumerate(choices):
                self.ui.add(CharacterSelect(choice[0], choice[1], i))
            self.ui.add(ui.TextSelection(500, 420, ('root', 'Back')))
            self.selection = ' '
        self.draw()

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
        if self.active:
            self.avatar.update()
            self.render()
        elif self.avatar.frame_count is not 0:
            self.avatar.frame_count = 0
            self.avatar.update()
            self.render()
    def mousebuttondown(self, caller, event):
        if event.button == 1:
            caller.selection = self.name
            if self.name == 'Slayer':
                stat = character.SlayerStat()
            elif self.name == 'Fighter':
                stat = character.FighterStat()
            new_character = character.Character(self.name, job='slayer',
                avatar=self.avatar, basestat=stat, player=True)
            new_character.learn_skill(skill.Swing)
            new_character.learn_skill(skill.Thrust)
            new_character.learn_skill(skill.Guard)
            new_character.learn_skill(skill.Backstep)
            new_character.learn_skill(skill.MoonlightSlash)
            new_character.learn_skill(skill.GhostSlash)
            new_character.learn_skill(skill.Kazan)
            new_character.learn_skill(skill.Bremen)
            new_character.learn_skill(skill.Unshackle)
            new_character.skill_points += 1
            caller.main.data = [new_character, None, None]
            caller.main.routine = manage.Manage(caller.main)