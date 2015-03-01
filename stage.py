import pygame
from resources import res

class StageElement(object):
    def __init__(self, file, pos=(0, 0), spacing=(640, 480)):
        self.image = res.load_image(file)
        self.pos = pos
        self.spacing = spacing

class Stage(object):
    def __init__(self, field, elements, animations=[]):
        width = max(field.rect.width, 
                field.grid_width*field.columns+field.grid_tilt*field.rows)
        height = max(field.rect.height,
                field.grid_height*field.rows+field.horizon+4)
        self.static = pygame.Surface((width, height), flags=pygame.SRCALPHA)
        for element in elements:
            repeat = int(width/element.spacing[0])+1
            for i in range(repeat):
                self.static.blit(element.image,
                        (element.pos[0]+element.spacing[0]*i,
                        element.pos[1]))
            

class PineForest(Stage):
    '''A collection of elements'''
    def __init__(self, field):
        elements = ([StageElement('stages/PineForest/02far0.img/0.png')] +
                    [StageElement('stages/PineForest/02mid0.img/0.png')] +
                    [StageElement('stages/PineForest/02tile00.img/0.png', pos=(0, 330),
                        spacing=(224, 240))]
                    )
        super(PineForest, self).__init__(field, elements)
class FrostForest(Stage):
    '''A collection of elements'''
    def __init__(self, field):
        elements = ([StageElement('stages/PineForest/02far0f.img/0.png', pos=(0, 0))] +
                        [StageElement('stages/PineForest/02mid0f.img/0.png', pos=(0, 0))] +
                        [StageElement('stages/PineForest/02tile00f.img/0.png', pos=(0, 330),
                            spacing=(224, 240))]
                        )
        super(FrostForest, self).__init__(field, elements)
class Temple(Stage):
    def __init__(self, field):
        elements = ([StageElement('stages/Temple/aganzo.img/0.png', pos=(0, 90),
                            spacing=(224, 240))]
                        )
        super(Temple, self).__init__(field, elements)
class Castle(Stage):
    def __init__(self, field):
        elements = ([StageElement('stages/Castle/far_dr.img/0.png', pos=(0, 0))] +
                        [StageElement('stages/Castle/200tile0.img/0.png', pos=(0, 0),
                            spacing=(224, 240))] +
                        [StageElement('stages/Castle/200tile0.img/4.png', pos=(224, 0))]
                        )
        super(Castle, self).__init__(field, elements)

# class Blank(Stage):
    # def __init__(self):
        # self.elements = ([StageElement('blank.png', pos=(0, 0))])

# class Sewer(Stage):
    # def __init__(self):
        # anim01 = StageElement('stages/Sewer/dcfarstreamani.img/0.png', pos=(0, 72), duration=3, spacing=(320,1))
        # anim01.add_frame('stages/Sewer/dcfarstreamani.img/1.png', duration=3)
        # anim01.add_frame('stages/Sewer/dcfarstreamani.img/2.png', duration=3)
        # anim01.add_frame('stages/Sewer/dcfarstreamani.img/3.png', duration=3)
        # anim01.add_frame('stages/Sewer/dcfarstreamani.img/4.png', duration=3)
        # self.elements = ([StageElement('stages/Sewer/dcfar.img/0.png', pos=(0, 0), spacing=(640,1))] +
                        # [anim01] +
                        # [StageElement('stages/Sewer/tileb.img/0.png', pos=(0, 155), spacing=(224, 97))]
                        # )
        # self.render()