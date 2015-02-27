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
        self.field = Field(7, 5, stage.Sewer())
        self.ui.add(self.field)
        self.field.place_character(self.main.data[0], 0, 0)
        self.ui.add(ui.TextLine(0,0,"lolol this is gonna take a while don't get your hopes up"))
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
    horizon = 200
    def __init__(self, columns, rows, background):
        self.columns = columns
        self.rows = rows
        self.rect = pygame.Rect(0, 0,
                max(1280, self.grid_width*columns+self.grid_tilt*rows),
                max(960, self.grid_height*rows+self.horizon))
        self.tiles = [[Tile()
                for row in range(rows)]
                    for column in range(columns)]
        self.background = background
        self.gridlines = True
        super(Field, self).__init__(self.rect)
        self.zoom = 1 #Does nothing yet
        self.characters = []
    def mousebuttondown(self, caller, event):
        if event.button==1:
            self.held = True
        if event.button==4:
            self.render_occupants()
    def mousebuttonup(self, caller, event):
        if event.button==1:
            self.held = False
        if event.button==5:
            print "scrolled down"
    def mousemotion(self, caller, event):
        self.active = True
        if self.held:
            dx, dy = event.rel
            dx = min(dx, -self.rect.left)
            dx = max(dx, 640-self.rect.left-self.rect.width)
            dx = dx*640/pygame.display.get_surface().get_width()
            self.rect = self.rect.move((dx, 0))
    def update(self):
        self.background.update()
        for character in self.characters:
            character.avatar.update()
        self.render()
    def render(self):
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.background.render()
        self.image.blit(self.background.image, (0,0))
        if self.gridlines:
            self.render_gridlines()
        self.render_occupants()
    def render_gridlines(self):
        overlay = pygame.Surface((self.rect.width, self.rect.height))
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
        self.image.blit(overlay, (0,0))
    def render_occupants(self):
        for column in range(self.columns):
            for row in range(self.rows):
                for occupant in self.tiles[column][row].occupant:
                    x_blit = ((column+0.5)*self.grid_width+
                            (row+0.5)*self.grid_tilt)
                    y_blit = self.horizon+(row+0.5)*self.grid_height+4
                    self.image.blit(occupant.avatar.image,
                        (x_blit-occupant.avatar.center[0],
                        y_blit-occupant.avatar.center[1]))
    def place_character(self, character, x, y):
        if not self.tiles[x][y].blocked:
            self.tiles[x][y].occupant.append(character)
            self.characters.append(character)
            character.enter_field(x, y)