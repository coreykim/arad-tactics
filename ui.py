import pygame
from resources import res

def outlined_text(text, color, bordercolor):
    notcolor = [c^0xFF for c in bordercolor]
    font = res.load_font(16)
    base = font.render(text, 0, bordercolor, notcolor)
    size = base.get_width() + 2, base.get_height() + 2
    image = pygame.Surface(size, 16)
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
    def __init__(self, rect, color):
        super(Frame, self).__init__()
        self.rect = pygame.Rect(rect)
        self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.image.fill(color)

class Message(Frame):
    def __init__(self, rect, lines, fontsize):
        self.lines = lines
        rect = pygame.Rect(rect)
        rect.height = max(len(lines)*fontsize, rect.height)