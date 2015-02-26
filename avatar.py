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
        self.parts = parts
        self.owner = None
        self.image = res.load_image('blank.png')
        self.rect = pygame.Rect(0,0,1,1)
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
    def update(self):
        self.frame_count += self.animation.speed
        if self.frame_count >= len(self.animation.frames):
            self.frame_count = 0
        self.image = self.images[self.animation.frames[int(self.frame_count)]]
    def play_animation(self, animation):
        self.frame_count = 0
        self.animation = animation
        self.image = self.images[self.animation.frames[int(self.frame_count)]]

class Player(Avatar):
    def __init__(self, parts):
        super(Player, self).__init__(parts)
    def build_sprite(self, parts, pos_dict):
        sprite_parts = []
        part_names = []
        sprite_width = 0
        sprite_height = 0
        for layer in ['', 'a', 'b', 'c']:
            for i, part in enumerate(parts):
                sheet = os.path.join(res.dir, part+layer)
                if os.path.exists(sheet+'.png'):
                    part_names.append(part+layer)
                    sprite_parts.append(res.unpack_sheet(part+layer, ignore=2))
                    if sprite_parts[-1][0].get_width() > sprite_width:
                        sprite_width = sprite_parts[-1][0].get_width()
                    if sprite_parts[-1][0].get_height() > sprite_height:
                        sprite_height = sprite_parts[-1][0].get_height()
        built = []
        for i in range(len(sprite_parts[0])):
            built.append(pygame.Surface((sprite_width, sprite_height), flags=SRCALPHA))
        for i in range(len(part_names)):
            if part_names[i] in pos_dict:
                pos = pos_dict[part_names[i]]
            else:
                pos = (0,0)
            for j in range(len(sprite_parts[i])):
                built[j].blit(sprite_parts[i][j], pos)
        return built

class Slayer(Player):
    coordinates = {
            'sm_body0000': (0,0),
            'sm_coat0000a': (8,26),
            'sm_coat0100a': (10,30),
            'sm_coat0200a': (10,32),
            'sm_hair0000a': (-5,18), 
            'sm_pants0000a': (23,55), 
            'sm_pants0000b': (44,-201),
            'sm_shoes0000a': (15, 84),
            'sm_shoes0000b': (38,-201),
            'mswd0000b': (-56, -201),
            'mswd0000c': (-42, -201),
            }
    height = 115
    center = (65, 135)
    def __init__(self, parts = ['sm_body0000', 'sm_coat0000',
                'sm_hair0000', 'sm_pants0000', 'sm_shoes0000',
                'mswd0000']):
        super(Slayer, self).__init__(parts)
        self.idle = Animation(frames = range(91, 96), speed=0.12)
        self.attack1 = Animation(frames = range(0, 10), speed=0.4)
        self.cast1 = Animation(frames = range(75, 90), speed=0.4)
        self.hit1 = Animation(frames = range(96, 99), speed=0.12)
        self.portrait = res.unpack_sheet('defaultfaces')[0]
        self.images = self.build_sprite(parts, self.coordinates)
        self.rect = self.images[0].get_rect
        self.play_animation(self.idle)