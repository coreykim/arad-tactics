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
            if self.animation is not self.idle:
                self.animation = self.idle
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
                built.append(pygame.Surface(size))
                built[-1].fill((124, 248, 0))
        for part in parts:
            sprite_part = res.unpack_sheet(part)
            for i in range(len(sprite_part)):
                built[i].blit(sprite_part[i], (0,0))
                built[i] = built[i].convert()
                built[i].set_colorkey((124, 248, 0))
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
        self.attack1 = Animation(frames = range(30, 36), speed=0.4)
        self.attack2 = Animation(frames = range(65, 71), speed=0.4)
        self.cast1 = Animation(frames = range(92, 95)+range(93, 95), speed=0.4)
        self.hit1 = Animation(frames = range(76, 78), speed=0.12)
        self.play_animation(self.idle)
        self.height = 120
        self.center = (62, 150)
        self.portrait = res.load_image('FighterIcon.png')

class Lugaru(Avatar):
    def __init__(self):
        super(Lugaru, self).__init__(['lugaru'])
        self.idle = Animation(frames = range(33, 37), speed=0.12)
        self.attack1 = Animation(frames = range(0, 6), speed=0.4)
        self.hit1 = Animation(frames = [15]*3, speed=0.1)
        self.play_animation(self.idle)
        self.height = 80
        self.center = 65, 100
        self.portrait = res.unpack_sheet('monsterface')[11]

class ClayGolem(Avatar):
    def __init__(self):
        super(ClayGolem, self).__init__(['claygolem'])
        self.idle = Animation(frames = [16]*25+range(16, 25), speed=0.12)
        self.attack1 = Animation(frames = range(8, 16), speed=0.2)
        self.hit1 = Animation(frames = [39]*3, speed=0.1)
        self.play_animation(self.idle)
        self.height = 150
        self.center = 130, 205
        self.portrait = res.unpack_sheet('monsterface')[22]

class Kazan(Avatar):
    def __init__(self):
        super(Kazan, self).__init__(['ghostkhazan1'])
        for image in self.images:
            image.set_alpha(40)
        self.idle = Animation(frames = range(8), speed=0.12)
        self.play_animation(self.idle)
        self.height = 110
        self.center = 50, 115

class Bremen(Avatar):
    def __init__(self):
        super(Bremen, self).__init__(['ghostbremen1'])
        for image in self.images:
            image.set_alpha(40)
        self.idle = Animation(frames = range(8), speed=0.12)
        self.play_animation(self.idle)
        self.height = 110
        self.center = 50, 115