import pygame
import os
from resources import res
from pygame.locals import SRCALPHA

class Animation(object):
    def __init__(self, frames=[0], speed=0.1):
        self.frames = frames
        self.speed = speed

class Avatar(pygame.sprite.Sprite):
    '''An animated image to represent a game object'''
    def __init__(self, parts):
        self.owner = None
        self.image = res.load_image('blank.png')
        self.frame_count = 0
        self.animation = None
        self.idle = None
        self.attack1 = None
        self.attack2 = None
        self.cast1 = None
        self.cast2 = None
        self.hit1 = None
        self.hit2 = None
        self.portrait = res.load_image('blank.png')
        self.images = self.build_sprite(parts)
        self.rect = self.images[0].get_rect
    def update(self):
        self.frame_count += self.animation.speed
        if self.frame_count >= len(self.animation.frames):
            self.frame_count = 0
        self.image = self.images[self.animation.frames[int(self.frame_count)]]
    def play_animation(self, animation):
        if animation:
            self.frame_count = 0
            self.animation = animation
            self.image = self.images[self.animation.frames[int(self.frame_count)]]
    def build_sprite(self, parts, pos_dict=None):
        built = []
        with open(os.path.join(res.dir, parts[0]+'.txt'), 'r') as sheet_map:
            #Assumes that the first part has a line for every frame
            for line in sheet_map:
                size=(int(line.split()[4]), int(line.split()[5]))
                built.append(pygame.Surface(size, flags=SRCALPHA))
        for part in parts:
            sprite_part = res.unpack_sheet(part)
            for i in range(len(sprite_part)):
                built[i].blit(sprite_part[i], (0,0))
                built[i] = built[i].convert_alpha()
        return built

class Slayer(Avatar):
    def __init__(self):
        super(Slayer, self).__init__(['default_slayer'])
        self.idle = Animation(frames = range(91, 96), speed=0.15)
        self.attack1 = Animation(frames = range(0, 10), speed=0.4)
        self.cast1 = Animation(frames = range(75, 90), speed=0.4)
        self.hit1 = Animation(frames = range(96, 99), speed=0.12)
        self.play_animation(self.idle)
        self.height = 120
        self.center = (125, 198)
        self.portrait = res.load_image('SlayerIcon.png')

class Fighter(Avatar):
    def __init__(self):
        super(Fighter, self).__init__(['default_fighter'])
        self.idle = Animation(frames = range(132, 136), speed=0.15)
        self.attack1 = Animation(frames = range(30, 37), speed=0.4)
        self.attack2 = Animation(frames = range(65, 71), speed=0.4)
        self.cast1 = Animation(frames = range(92, 95), speed=0.4)
        self.hit1 = Animation(frames = range(76, 78), speed=0.12)
        self.play_animation(self.idle)
        self.height = 120
        self.center = (62, 150)
        self.portrait = res.load_image('FighterIcon.png')
