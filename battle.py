from __future__ import division
import pygame
from resources import res
import ui
import avatar
import character
import title
import stage

class Battle(object):
    def __init__(self, main):
        self.main = main
        res.play_music('underfoot.ogg')
        self.ui = pygame.sprite.LayeredUpdates()
        self.turn = 0
        self.selection = ' '
        self.phase = 'action'
        self.player_turn = True
        self.turn_indicator = TurnIndicator()
        self.field = Field(0, self.turn_indicator.rect.height,
                            10, 5, stage.Sewer)
        self.ui.add(self.turn_indicator, self.field)
        self.main.data[0].enter_field(0, 0, self.field)
    def draw(self):
        self.main.canvas.fill((20, 20, 20))
        self.ui.update()
        self.ui.draw(self.main.canvas)
    def run(self):
        if self.selection == 'turn':
            self.turn += 1
            self.selection = ' '
        self.draw()

class TurnIndicator(ui.Frame):
    def __init__(self):
        frames = ['player_action.png', 'enemy_reaction.png',
                    'enemy_action.png', 'player_reaction.png']
        self.frame = []
        for frame in frames:
            self.frame.append(res.load_image(frame))
        self.graphic = self.frame[0]
        self.rect = pygame.Rect(320-int(self.graphic.get_width()/2),
                0, self.graphic.get_width(), self.graphic.get_height())

        super(TurnIndicator, self).__init__(self.rect)
        self.selection = 'turn'
    def render(self):
        self.image = pygame.Surface((self.rect.width, self.rect.height),
                                    flags=pygame.SRCALPHA)
        if self.active:
            self.image.fill(self.highlightcolor)
        self.image.blit(self.graphic, (0, 0))
    def mousebuttondown(self, caller, event):
        if event.button==1:
            caller.selection = self.selection
            self.graphic = self.frame[(caller.turn+1)%4]
            self.render()
class Tile(object):
    def __init__(self):
        self.occupant = []
        self.effect = []
        self.terrain = [] #like a permanent effect
        self.blocked = False
class Field(ui.Frame):
    grid_width = 120
    grid_height = 30
    grid_tilt = 60
    horizon = 350
    def __init__(self, x, y, columns, rows, background):
        self.zoom = 1
        self.columns = columns
        self.rows = rows
        self.rect = pygame.Rect(x, y, 640, 360)
        self.canvas_rect = pygame.Rect(-self.grid_tilt, 0,
                self.grid_width*columns+self.grid_tilt*rows,
                self.grid_height*rows+self.horizon+4)
        self.background = background(self)
        self.render_gridlines()
        self.tiles = [[Tile()
                for row in range(rows)]
                    for column in range(columns)]
        super(Field, self).__init__(self.rect)
        self.characters = []
    def mousebuttondown(self, caller, event):
        if event.button==1:
            self.held = True
        if event.button==4:
            self.zoom = max(self.zoom-0.25, 0.5)
    def mousebuttonup(self, caller, event):
        if event.button==1:
            self.held = False
        if event.button==5:
            self.zoom = min(self.zoom+0.25, 1)
    def mousemotion(self, caller, event):
        self.active = True
        if self.held:
            dx, dy = event.rel
            dx = min(dx, -self.canvas_rect.left)
            dx = max(dx, 640-self.canvas_rect.left-int(self.canvas_rect.width*self.zoom))
            dx = dx*640/pygame.display.get_surface().get_width()
            self.canvas_rect = self.canvas_rect.move((dx, 0))
    def update(self):
        for character in self.characters:
            character.avatar.update()
        self.render()
    def render(self):
        self.canvas = self.background.static.copy()
        self.background.add_animations(self.canvas)
        self.canvas.blit(self.background.static_floor, (0,0))
        self.render_occupants()
        self.canvas = pygame.transform.smoothscale(self.canvas, (
            int(self.canvas_rect.width*self.zoom),
            int(self.canvas_rect.height*self.zoom)))
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.fill((20,20,20))
        self.image.blit(self.canvas, (int(self.canvas_rect.left*self.zoom),
                    int(self.rect.height-self.zoom*self.canvas_rect.height)))
    def render_gridlines(self):
        overlay = pygame.Surface((self.canvas_rect.width,
                                self.canvas_rect.height)).convert()
        overlay.fill((254, 254, 254))
        overlay.set_colorkey((254, 254, 254))
        lightgrey = (150, 150, 150)
        overlay.lock()
        for i in range(self.rows+1):
            pygame.draw.line(overlay, lightgrey, 
                (self.grid_tilt*i,
                self.horizon+i*self.grid_height),
                (self.grid_width*self.columns+self.grid_tilt*i,
                self.horizon+i*self.grid_height)
                )
        for i in range(self.columns+1):
            pygame.draw.line(overlay, lightgrey,
                (self.grid_tilt*self.rows+i*self.grid_width,
                self.horizon+self.grid_height*self.rows),
                (i*self.grid_width, self.horizon)
                )
        overlay.unlock()
        overlay.set_alpha(120)
        self.background.static_floor.blit(overlay, (0,0))
    def render_occupants(self):
        for column in range(self.columns):
            for row in range(self.rows):
                for occupant in self.tiles[column][row].occupant:
                    x_blit = ((column+0.5)*self.grid_width+
                            (row+0.5)*self.grid_tilt)
                    y_blit = self.horizon+(row+0.5)*self.grid_height+4
                    self.canvas.blit(occupant.avatar.image,
                        (x_blit-occupant.avatar.center[0],
                        y_blit-occupant.avatar.center[1]))