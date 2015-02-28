import pygame
from resources import res

class StageElement(object):
    '''A piece of the stage on which the battle takes place.'''
    def __init__(self, image, duration=1, pos=(0,0), spacing=(50,50)):
        self.pos = pos
        self.spacing = spacing
        self.frames = []
        self.add_frame(image, duration=duration)
        self.frame_index = 0
    def add_frame(self, image, duration=1):
        frame = res.load_image(image)
        self.frames += [frame]*duration
    def animate(self):
        if self.frame_index == len(self.frames)-1:
            self.frame_index = 0
        else:
            self.frame_index += 1
class Stage(pygame.sprite.Sprite):
    def __init__(self):
        self.render()
    def render(self):
        self.image = pygame.Surface((1920, 960))
        for element in self.elements:
            pos = ((element.pos[0])*2, (element.pos[1])*2)
            self.image.blit(element.frames[element.frame_index], pos)
    def update(self):
        for element in self.elements:
            element.animate()

class PineForest(Stage):
    '''A collection of elements'''
    def __init__(self):
        self.elements = (
                        [StageElement('stages/PineForest/02far0.img/0.png', pos=(0, -75))] +
                        [StageElement('stages/PineForest/02mid0.img/0.png', pos=(0, -75))] +
                        [StageElement('stages/PineForest/02tile00.img/0.png', pos=(0, 85),
                            spacing=(112, 240))] +
                        [StageElement('stages/PineForest/02obj001.img/0.png', pos=(75, 65))]
                        )
        self.render()
class FrostForest(Stage):
    '''A collection of elements'''
    def __init__(self):
        self.elements = ([StageElement('stages/PineForest/02far0f.img/0.png', pos=(0, -75))] +
                        [StageElement('stages/PineForest/02mid0f.img/0.png', pos=(0, -75))] +
                        [StageElement('stages/PineForest/02tile00f.img/0.png', pos=(0, 85),
                            spacing=(112, 240))] +
                        [StageElement('stages/PineForest/02obj001f.img/0.png', pos=(75, 65))]
                        )
        self.render()
class Temple(Stage):
    def __init__(self):
        self.elements = ([StageElement('stages/Temple/aganzo.img/0.png', pos=(112, -75),
                            spacing=(112, 240))] +
                        [StageElement('stages/Temple/aganzo.img/1.png', pos=(0, -75))]
                        )
class Castle(Stage):
    def __init__(self):
        self.elements = ([StageElement('stages/Castle/far_dr.img/0.png', pos=(0, -105))] +
                        [StageElement('stages/Castle/200tile0.img/0.png', pos=(0, -105),
                            spacing=(112, 240))] +
                        [StageElement('stages/Castle/200tile0.img/4.png', pos=(224, -105))]
                        )
        self.render()

class Blank(Stage):
    def __init__(self):
        self.elements = ([StageElement('blank.png', pos=(0, 0))])

class Sewer(Stage):
    def __init__(self):
        anim01 = StageElement('stages/Sewer/dcfarstreamani.img/0.png', pos=(0, 72), duration=3, spacing=(320,1))
        anim01.add_frame('stages/Sewer/dcfarstreamani.img/1.png', duration=3)
        anim01.add_frame('stages/Sewer/dcfarstreamani.img/2.png', duration=3)
        anim01.add_frame('stages/Sewer/dcfarstreamani.img/3.png', duration=3)
        anim01.add_frame('stages/Sewer/dcfarstreamani.img/4.png', duration=3)
        self.elements = ([StageElement('stages/Sewer/dcfar.img/0.png', pos=(0, 0), spacing=(320,1))] +
                        [anim01] +
                        [StageElement('stages/Sewer/tileb.img/0.png', pos=(0, 155), spacing=(112, 97))]
                        )
        self.render()