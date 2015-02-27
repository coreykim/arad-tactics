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
        self.phase = 'action'
        self.player_turn = True
        self.field = Field(10, 5, stage.Sewer())
        self.ui.add(self.field)
        self.field.place_character(self.main.data[0], 0, 0)
    def draw(self):
        self.main.canvas.fill((80, 80, 255))
        self.ui.update()
        self.ui.draw(self.main.canvas)
    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.main.quit = True
            if event.type == pygame.VIDEORESIZE:
                self.main.screen=pygame.display.set_mode(event.dict['size'], pygame.RESIZABLE)
            for sprite in self.ui.sprites():
                sprite.input(event, self)
    def run(self):
        self.event_handler()
        self.draw()

class Tile(object):
    def __init__(self):
        self.occupant = []
        self.effect = []
        self.terrain = [] #like a permanent effect
        self.blocked = False
class Field(ui.Frame):
    grid_width = 120
    grid_height = 30
    grid_tilt = 35
    horizon = 350
    def __init__(self, columns, rows, background):
        self.zoom = 1
        self.columns = columns
        self.rows = rows
        self.rect = pygame.Rect(0, 24, 640, 360)
        self.canvas_rect = pygame.Rect(0, 0,
                self.grid_width*columns+self.grid_tilt*rows,
                self.grid_height*rows+self.horizon+4)
        self.tiles = [[Tile()
                for row in range(rows)]
                    for column in range(columns)]
        self.background = background
        self.gridlines = True
        self.render_gridlines()
        super(Field, self).__init__(self.rect)
        self.characters = []
    def mousebuttondown(self, caller, event):
        if event.button==1:
            self.held = True
        if event.button==4:
            self.zoom = max(self.zoom-0.2, 0.6)
    def mousebuttonup(self, caller, event):
        if event.button==1:
            self.held = False
        if event.button==5:
            self.zoom = min(self.zoom+0.2, 1.4)
    def mousemotion(self, caller, event):
        self.active = True
        if self.held:
            dx, dy = event.rel
            dx = min(dx, -self.canvas_rect.left)
            dx = max(dx, 640-self.canvas_rect.left-int(self.canvas_rect.width*self.zoom))
            dx = dx*640/pygame.display.get_surface().get_width()
            self.canvas_rect = self.canvas_rect.move((dx, 0))
    def update(self):
        self.background.update()
        for character in self.characters:
            character.avatar.update()
        self.render()
    def render(self):
        self.canvas = pygame.Surface((self.canvas_rect.width,
                                    self.canvas_rect.height))
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.background.render()
        self.canvas.blit(self.background.image, (0, 0))
        if self.gridlines:
            self.canvas.blit(self.gridlines_image, (0, 0))
        self.render_occupants()
        self.canvas = pygame.transform.smoothscale(self.canvas, (
            int(self.canvas_rect.width*self.zoom),
            int(self.canvas_rect.height*self.zoom)))
        self.image.blit(self.canvas, (self.canvas_rect.left,
                    self.rect.height-int(self.zoom*self.canvas_rect.height))) #int(-140*self.zoom)
    def render_gridlines(self):
        overlay = pygame.Surface((self.canvas_rect.width,
                                self.canvas_rect.height))
        overlay = overlay.convert()
        overlay.fill((254, 254, 254))
        overlay.set_colorkey((254, 254, 254))
        lightgrey = (200, 200, 200)
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
        self.gridlines_image = overlay
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
    def place_character(self, character, x, y):
        if not self.tiles[x][y].blocked:
            self.tiles[x][y].occupant.append(character)
            self.characters.append(character)
            character.enter_field(x, y)