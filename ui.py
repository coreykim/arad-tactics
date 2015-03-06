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
    highlightcolor = (240,220,120)
    '''A barebones UI element that detects inputs'''
    def __init__(self, rect, color=None):
        super(Frame, self).__init__()
        self.rect = pygame.Rect(rect)
        self.color = color
        self.active = False
        self.held = False
        self.render()
    def render(self):
        self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        if self.color:
            self.image.fill(self.color)
    def input(self, event, caller):
        if event.type==pygame.MOUSEMOTION:
            self.mousemotion(caller, event)
        elif event.type==pygame.MOUSEBUTTONDOWN:
            self.mousebuttondown(caller, event)
        elif event.type==pygame.MOUSEBUTTONUP:
            self.mousebuttonup(caller, event)
    def mousemotion(self, caller, event):
        self.active = True
        self.render()
    def mousebuttondown(self, caller, event):
        pass
    def mousebuttonup(self, caller, event):
        pass
    def lose_focus(self):
        self.render()

class Image(Frame):
    def __init__(self, x, y, image):
        self.image = image
        rect = self.image.get_rect().move(x, y)
        super(Image, self).__init__(rect)
    def render(self):
        pass
class ImageButton(Frame):
    def __init__(self, x, y, file, selection):
        self.graphic = res.load_image(file)
        rect = pygame.Rect(x, y, self.graphic.get_width()+2,
                                self.graphic.get_height()+2)
        super(ImageButton, self).__init__(rect)
        self.selection = selection
    def render(self):
        self.image = pygame.Surface((self.rect.width, self.rect.height),
                                    flags=pygame.SRCALPHA)
        if self.active:
            self.image.fill(self.highlightcolor)
        self.image.blit(self.graphic, (1, 1))
    def mousebuttondown(self, caller, event):
        if event.button==1:
            caller.selection = self.selection

class TextLine(Frame):
    def __init__(self, x, y, text):
        self.text = text
        rect = outlined_text(self.text).get_rect().move(x, y)
        super(TextLine, self).__init__(rect)
    def render(self):
        self.image = outlined_text(self.text)

class TextBox(Frame):
    def __init__(self, x, y, width, height, text):
        self.text = text
        rect = pygame.Rect(x, y, width, height)
        super(TextBox, self).__init__(rect)
    def render(self):
        text = res.string2image(self.text, wraplength = self.rect.width-8,
                                bgcolor = (20, 20, 20), border = 4)
        self.image = pygame.Surface(self.rect.size)
        self.image.fill((20, 20, 20))
        self.image.blit(text, (0, 0))
        

class TextSelection(Frame):
    def __init__(self, x, y, option):
        self.selection = option[0]
        self.text = '< '+option[1]+' >'
        rect = outlined_text(self.text).get_rect()
        rect = rect.move(x, y)
        super(TextSelection, self).__init__(rect)
    def render(self):
        if self.active:
            self.image = outlined_text(self.text, color=self.highlightcolor)
        else:
            self.image = outlined_text(self.text)
    def mousebuttondown(self, caller, event):
        if event.button==1:
            caller.selection = self.selection