import pygame
from resources import res

def outlined_text(text, color=(255,255,255), bordercolor=(1,1,1)):
    notcolor = [c^0xFF for c in bordercolor]
    font = res.load_font(16)
    base = font.render(text, 0, bordercolor, notcolor)
    size = base.get_width()+2, base.get_height()+2
    image = pygame.Surface(size)
    image.fill(notcolor)
    base.set_colorkey(0)
    image.blit(base, (0, 0))
    image.blit(base, (2, 0))
    image.blit(base, (0, 2))
    image.blit(base, (2, 2))
    base.set_colorkey(0)
    base.set_palette_at(1, color)
    image.blit(base, (1, 1))
    image.set_colorkey(notcolor)
    return image

class Frame(pygame.sprite.Sprite):
    '''Static sprites that never change'''
    def __init__(self, rect, color=None):
        super(Frame, self).__init__()
        self.rect = pygame.Rect(rect)
        self.color = color
        self.active = False
        self.render()
    def render(self):
        self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        if self.color:
            self.image.fill(self.color)
    def input(self, event):
        pass

class Clicky(Frame):
    '''An area that can be clicked and changes appearance on mouseover'''
    def __init__(self, rect, color=None, activecolor=None):
        super(Clicky, self).__init__(rect, color=color)
        self.activecolor = activecolor
        self.layer = 100
    def input(self, event, caller):
        pos = pygame.mouse.get_pos()
        pos = (pos[0]*640/pygame.display.get_surface().get_width(),
                pos[1]*480/pygame.display.get_surface().get_height())
        if self.rect.collidepoint(pos):
            if event.type==pygame.MOUSEMOTION:
                self.mousemotion(caller)
            elif event.type==pygame.MOUSEBUTTONDOWN:
                self.mousebuttondown(caller)
            elif event.type==pygame.MOUSEBUTTONUP:
                self.mousebuttonup(caller)
        else:
            self.active = False
            self.render()
    def mousemotion(self, caller):
        self.active = True
        self.render()
    def mousebuttondown(self, caller):
        pass
    def mousebuttonup(self, caller):
        pass