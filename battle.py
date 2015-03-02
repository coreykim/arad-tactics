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
        self.phase = 0
        self.player_turn = True
        self.turn_indicator = TurnIndicator(self)
        self.field = Field(self, 0, self.turn_indicator.rect.height,
                            10, 5, stage.Temple)
        self.ui.add(self.turn_indicator, self.field)
        self.main.data[0].enter_field(0, 0, self.field)
    def draw(self):
        self.main.canvas.fill((20, 20, 20))
        self.ui.update()
        self.ui.draw(self.main.canvas)
    def run(self):
        if self.selection == 'turn':
            self.turn += 1
            self.phase += 1
            if self.phase == 4:
                self.phase = 0
            self.turn_indicator.render()
            self.selection = ' '
        self.draw()

class TurnIndicator(ui.Frame):
    def __init__(self, caller):
        frames = ['player_action.png', 'enemy_reaction.png',
                    'enemy_action.png', 'player_reaction.png']
        self.frame = []
        self.caller = caller
        for frame in frames:
            self.frame.append(res.load_image(frame))
        self.rect = pygame.Rect(320-int(self.frame[0].get_width()/2),
                0, self.frame[0].get_width(), self.frame[0].get_height())
        super(TurnIndicator, self).__init__(self.rect)
        self.selection = 'turn'
    def render(self):
        self.image = pygame.Surface((self.rect.width, self.rect.height),
                                    flags=pygame.SRCALPHA)
        if self.active:
            self.image.fill(self.highlightcolor)
        self.image.blit(self.frame[self.caller.phase], (0, 0))
    def mousebuttondown(self, caller, event):
        if event.button==1:
            caller.selection = self.selection
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
    horizon = 270
    def __init__(self, caller, x, y, columns, rows, background):
        self.caller = caller
        self.columns = columns
        self.rows = rows
        self.rect = pygame.Rect(x, y, 640, 360)
        self.background = background(self)
        self.camera = pygame.Rect(self.grid_tilt, self.background.height-360, 640, 360)
        self.zoom = 0
        self.canvas_rect = pygame.Rect(-self.grid_tilt, 0,
                self.grid_width*columns+self.grid_tilt*rows,
                self.grid_height*rows+self.horizon+4)
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
        if event.button==5:
            self.zoom = min(self.zoom+0.25, 1)
    def mousebuttonup(self, caller, event):
        if event.button==1:
            self.held = False
            pos = event.pos
            pos = (pos[0]*640/pygame.display.get_surface().get_width(),
                    pos[1]*480/pygame.display.get_surface().get_height())
            tile_y = (pos[1]-self.rect.top)/self.grid_height
            tile_x = (pos[0]-self.grid_tilt*self.rows+
                    (pos[1]-self.rect.top)*self.grid_tilt/self.grid_height-
                    self.canvas_rect.left)/self.grid_width
            print tile_x, tile_y
            if tile_x in range(self.columns) and tile_y in range(self.rows):
                pass
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
        self.canvas.set_clip(self.camera)
        if len(self.background.animations) > 0:
            self.background.add_animations(self.canvas)
            self.canvas.set_clip(pygame.Rect(0, self.horizon-50, self.canvas.get_width(), 50))
            self.canvas.blit(self.background.static_floor, (0,0))
            self.canvas.set_clip(self.camera)
        self.render_occupants()
        self.subcanvas = pygame.Surface((self.camera.width, self.camera.height))
        self.subcanvas.blit(self.canvas, (0,0), area=self.camera)
        self.subcanvas = pygame.transform.smoothscale(self.subcanvas, (
            self.rect.width, min(self.rect.height, self.camera.height/self.camera.width*self.rect.width)))
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.fill((20,20,20))
        self.image.blit(self.subcanvas, (0, int(self.rect.height-self.subcanvas.get_height())))
    def render_gridlines(self):
        overlay = pygame.Surface((self.background.width,
                                self.background.height)).convert()
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
        overlay.set_alpha(180)
        self.background.static.blit(overlay, (0,0))
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