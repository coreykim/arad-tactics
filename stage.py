import pygame
from resources import res

class StageElement(object):
    def __init__(self, file, pos=(0, 0), spacing=(640, 480)):
        self.image = res.load_image(file)
        self.pos = pos
        self.spacing = spacing

class StageAnimation(object):
    def __init__(self, files, pos=(0, 0), spacing=(640, 480), speed=0.25):
        self.images = []
        for file in files:
            self.images.append(res.load_image(file))
        self.pos = pos
        self.spacing = spacing
        self.frame = 0
        self.speed = speed
    def update(self):
        self.frame += self.speed
        if self.frame >= len(self.images):
            self.frame = 0

class Stage(object):
    def __init__(self, field, backs, horizon=270, floors=[], animations=[]):
        self.width = max(field.rect.width, 
                field.grid_width*field.columns+field.grid_tilt*field.rows)
        self.height = max(field.rect.height,
                field.grid_height*field.rows+horizon+4)
        self.horizon = horizon
        self.static = pygame.Surface((self.width, self.height))
        self.static_floor = pygame.Surface((self.width, self.height), flags=pygame.SRCALPHA)
        self.animations = animations
        for back in backs+floors:
            repeat = int(self.width/back.spacing[0])+1
            for i in range(repeat):
                self.static.blit(back.image,
                        (back.pos[0]+back.spacing[0]*i,
                        back.pos[1]))
        for floor in floors:
            repeat = int(self.width/floor.spacing[0])+1
            for i in range(repeat):
                self.static_floor.blit(floor.image,
                        (floor.pos[0]+floor.spacing[0]*i,
                        floor.pos[1]))
    def add_animations(self, surface):
        for animated in self.animations:
            animated.update()
            repeat = int(self.width/animated.spacing[0])+1
            for i in range(repeat):
                surface.blit(animated.images[int(animated.frame)],
                        (animated.pos[0]+animated.spacing[0]*i,
                        animated.pos[1]))


class PineForest(Stage):
    def __init__(self, field):
        backs = ([StageElement('stages/PineForest/02far0.img/0.png')] +
                    [StageElement('stages/PineForest/02mid0.img/0.png')] +
                    [StageElement('stages/PineForest/02tile00.img/0.png', pos=(0, 330),
                        spacing=(224, 240))]
                    )
        super(PineForest, self).__init__(field, backs)
class FrostForest(Stage):
    def __init__(self, field):
        backs = ([StageElement('stages/PineForest/02far0f.img/0.png', pos=(0, 0))] +
                    [StageElement('stages/PineForest/02mid0f.img/0.png', pos=(0, 0))] +
                    [StageElement('stages/PineForest/02tile00f.img/0.png', pos=(0, 330),
                        spacing=(224, 240))]
                    )
        super(FrostForest, self).__init__(field, backs)
class Temple(Stage):
    def __init__(self, field):
        backs = ([StageElement('stages/Temple/aganzo.img/0.png', pos=(0, 0),
                            spacing=(224, 240))])
        super(Temple, self).__init__(field, backs, horizon=270)
class Castle(Stage):
    def __init__(self, field):
        backs = ([StageElement('stages/Castle/far_dr.img/0.png', pos=(0, 0),
                        spacing=(630,480))])
        floors = ([StageElement('stages/Castle/200tile0.img/0.png', pos=(0, -50),
                        spacing=(224, 240))] +
                    [StageElement('stages/Castle/200tile0.img/4.png', pos=(224, -50),
                        spacing=(224, 240))])
        super(Castle, self).__init__(field, backs, floors=floors)
class Sewer(Stage):
    def __init__(self, field):
        backs = ([StageElement('stages/Sewer/dcfar.img/0.png', pos=(0, 0),
                spacing=(640, 480))]
                )
        floors = ([StageElement('stages/Sewer/tileb.img/0.png', pos=(0, 330),
                spacing=(224, 195))]
                )
        animations = ([StageAnimation([
                        'stages/Sewer/dcfarstreamani.img/0.png',
                        'stages/Sewer/dcfarstreamani.img/1.png',
                        'stages/Sewer/dcfarstreamani.img/2.png',
                        'stages/Sewer/dcfarstreamani.img/3.png',
                        'stages/Sewer/dcfarstreamani.img/4.png'],
                        pos=(0,146), spacing=(640,480))])
        super(Sewer, self).__init__(field, backs, horizon=360, floors=floors, animations=animations)