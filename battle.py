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
        self.player_panel = PlayerPanel(self)
        self.player_panel.select(self.main.data[0])
        self.enemy_panel = EnemyPanel(self)
        self.field = Field(self, 0, self.turn_indicator.rect.height,
                            10, 5, stage.Sewer)
        self.ui.add(self.player_panel, self.enemy_panel, self.turn_indicator, self.field)
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

class PlayerPanel(ui.Frame):
    def __init__(self, caller):
        self.rect = pygame.Rect(0, 0, 320-16, 41)
        self.image = pygame.Surface(self.rect.size)
        self.character = None
        super(PlayerPanel, self).__init__(self.rect, color=(100, 100, 240))
    def render(self):
        self.image.fill((20, 20, 20))
        if self.character:
            self.image.blit(self.character.avatar.portrait, (0, 15))
            font = res.load_font(14)
            base = font.render(self.character.name, 0, (255, 255, 255), (20, 20, 20))
            self.image.blit(base, (0, 0))
            health_empty = pygame.Rect(27, 15, 320-16-27, 12)
            self.image.fill((80, 80, 80), rect=health_empty)
            health_full = pygame.Rect(27, 15, int((320-16-27)*
                            self.character.hp/self.character.max_hp), 12)
            self.image.fill((20, 220, 20), rect=health_empty)
            drive_empty = pygame.Rect(27, 28, 320-16-27, 12)
            self.image.fill((80, 80, 80), rect=drive_empty)
    def select(self, character):
        self.character = character
        self.render()
        
class EnemyPanel(ui.Frame):
    def __init__(self, caller):
        self.rect = pygame.Rect(320+15, 0, 320-15, 41)
        self.image = pygame.Surface(self.rect.size)
        self.character = None
        super(EnemyPanel, self).__init__(self.rect, color=(240, 100, 100))

class TurnIndicator(ui.Frame):
    def __init__(self, caller):
        frames = ['player_action.png', 'enemy_reaction.png',
                    'enemy_action.png', 'player_reaction.png']
        self.frame = []
        self.caller = caller
        for frame in frames:
            self.frame.append(res.load_image(frame))
        self.rect = pygame.Rect(int(320-self.frame[0].get_width()/2),
                0, self.frame[0].get_width(), self.frame[0].get_height())
        super(TurnIndicator, self).__init__(self.rect)
        self.selection = 'turn'
        self.fps = None #FOR TESTING ONLY
    def render(self):
        self.image = pygame.Surface((self.rect.width, self.rect.height),
                                    flags=pygame.SRCALPHA)
        if self.active:
            self.image.fill(self.highlightcolor)
        self.image.blit(self.frame[self.caller.phase], (0, 0))
    def mousebuttondown(self, caller, event):
        if event.button==1:
            caller.selection = self.selection
            caller.ui.remove(self.fps)
            self.fps = ui.TextLine(0, 480-16, str(caller.main.clock.get_fps()))
            caller.ui.add(self.fps) #FOR TESTING ONLY

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
    def __init__(self, caller, x, y, columns, rows, stage):
        self.caller = caller
        self.columns = columns
        self.rows = rows
        self.rect = pygame.Rect(x, y, 640, 360)
        self.stage = stage(self)
        self.horizon = self.stage.horizon
        self.camera = pygame.Rect(self.grid_tilt, self.stage.height-360,
                                    640, 360)
        self.zoom_resolution = [(640,360)]
        while self.zoom_resolution[-1][0] < self.stage.width:
            x = int(min(self.stage.width, self.zoom_resolution[-1][0]+
                                        self.zoom_resolution[0][0]*0.25))
            y = int(min(self.stage.height, x*360/640))
            self.zoom_resolution.append((x, y))
        self.zoom = 0
        self.render_gridlines()
        self.tiles = [[Tile()
                for row in range(rows)]
                    for column in range(columns)]
        super(Field, self).__init__(self.rect)
        self.characters = []
    def mousebuttondown(self, caller, event):
        if event.button==1:
            self.held = True
        if event.button==4 and self.zoom != len(self.zoom_resolution)-1:
            self.change_zoom(+1)
        if event.button==5 and self.zoom != 0:
            self.change_zoom(-1)
    def mousebuttonup(self, caller, event):
        if event.button==1:
            self.held = False
            pos = event.pos
            pos = (pos[0]*640/pygame.display.get_surface().get_width()*
                    self.camera.width/self.rect.width+self.camera.left,
                    (pos[1]*480/pygame.display.get_surface().get_height()
                    -self.rect.top) * self.camera.width/self.rect.width
                    +self.camera.top-self.horizon)
            tile_y = pos[1]/self.grid_height
            tile_x = (pos[0]-pos[1]*self.grid_tilt/self.grid_height)/self.grid_width
            if 0<=tile_x<self.columns and 0<=tile_y<self.rows:
                print int(tile_x), int(tile_y)
    def mousemotion(self, caller, event):
        self.active = True
        if self.held:
            dx, dy = event.rel
            dx = -int(0.5+dx*self.camera.width/self.rect.width)
            new_x = max(self.camera.left + dx, 0)
            new_x = min(new_x, self.stage.width-self.camera.width)
            self.camera.left = new_x
    def change_zoom(self, amount):
        self.zoom += amount
        self.camera.width = int(self.zoom_resolution[self.zoom][0])
        self.camera.height = int(self.zoom_resolution[self.zoom][1])
        self.camera.top = int(self.stage.height-self.camera.height)
    def update(self):
        for character in self.characters:
            character.avatar.update()
        self.render()
    def render(self):
        self.canvas = self.stage.static.copy()
        self.canvas.set_clip(self.camera)
        if len(self.stage.animations) > 0:
            self.stage.add_animations(self.canvas)
            self.canvas.set_clip(pygame.Rect(0, self.horizon-50, self.canvas.get_width(), 50))
            self.canvas.blit(self.stage.static_floor, (0,0))
            self.canvas.set_clip(self.camera)
        self.render_occupants()
        self.subcanvas = pygame.Surface((self.camera.width, self.camera.height))
        self.subcanvas.blit(self.canvas, (0,0), area=self.camera)
        self.subcanvas = pygame.transform.smoothscale(self.subcanvas, (
            self.rect.width, min(self.rect.height, int(self.camera.height/self.camera.width*self.rect.width))))
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.fill((20,20,20))
        self.image.blit(self.subcanvas, (0, int(self.rect.height-self.subcanvas.get_height())))
    def render_gridlines(self):
        overlay = pygame.Surface((self.stage.width,
                                self.stage.height)).convert()
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
        self.stage.static.blit(overlay, (0,0))
        self.stage.static_floor.blit(overlay, (0,0))
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