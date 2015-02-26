import pygame, os
from resources import res

class Avatar(pygame.sprite.Sprite):
    '''An animated image to represent a game object'''
    def __init__(self, parts):
        self.owner = None
        self.image = res.load_image('blank.png')
        self.frame_count = 0
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

class Player(Avatar):
    '''obsolete'''
    def __init__(self, parts):
        super(Player, self).__init__(parts)
    def build_sprite(self, parts, pos_dict, adjust=(0,0), crop=(0,0)):
        sprite_parts = []
        part_names = []
        sprite_width = 0
        sprite_height = 0
        for layer in ['', 'd', 'c', 'b', 'a']:
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
            built.append(pygame.Surface((sprite_width-crop[0],
                sprite_height-crop[1]), flags=pygame.SRCALPHA))
        for i in range(len(part_names)):
            if part_names[i] in pos_dict:
                pos = pos_dict[part_names[i]]
            else:
                pos = (0,0)
            pos = (pos[0]+adjust[0], pos[1]+adjust[1])
            for j in range(len(sprite_parts[i])):
                built[j].blit(sprite_parts[i][j], pos)
        return built

class PlayerAssembler(Player):
    '''obsolete'''
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
            'ft_coat0000a': (13, 36),
            'ft_hair0000a': (1, 25),
            'ft_hair0000b': (-3, -252),
            'ft_pants0000d': (12, 40),
            'ft_shoes0000a': (2, -252),
            'ft_shoes0000b': (25, -253),
            }
    def __init__(self, parts = ['sm_body0000', 'sm_coat0000',
                'sm_hair0000', 'sm_pants0000', 'sm_shoes0000',
                'mswd0000']):
        super(PlayerAssembler, self).__init__(parts)
        self.images = self.build_sprite(parts, self.coordinates, adjust=(5, 15), crop=(130, 230))
        self.rect = self.images[0].get_rect

def save(avatar):
    for i, frame in enumerate(avatar.images):
        pygame.image.save(avatar.images[i], 'saved/'+str(i)+'.png')
def display(avatar):
    pygame.display.init()
    pygame.display.set_mode((1280,960))
    clock = pygame.time.Clock()
    screen = pygame.display.get_surface()
    canvas = pygame.Surface((640,480))
    frame = 90
    back_rect = avatar.images[0].get_rect()
    play = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                play = not play
        screen.fill((10,10,10))
        canvas = pygame.Surface((640,480))
        canvas.fill((250, 200, 250), back_rect)
        print frame
        canvas.blit(avatar.images[int(frame)], (0,0))
        canvas = pygame.transform.scale(canvas, (1280, 960))
        screen.blit(canvas, (0, 0))
        if play:
            frame += 1
        if frame >= len(avatar.images):
            frame = 0
        pygame.display.flip()
        clock.tick(2)
            
slayer = PlayerAssembler(['ft_body0000', 'ft_coat0000', 'ft_hair0000', 'ft_pants0000', 'ft_shoes0000'])
save(slayer)