from __future__ import division
import pygame
from resources import res
import ui
import avatar
import character
import title
import stage
from skill import Skill

class Battle(object):
    def __init__(self, main):
        self.main = main
        res.play_music('underfoot.ogg')
        self.ui = pygame.sprite.LayeredUpdates()
        self.selection = ' '
        self.event = None
        self.turn_count = 0
        self.queue = []
        self.turn = True #True for player, False for enemy
        self.phase = 0
        self.skillbuttons = []
        self.turn_indicator = TurnIndicator(self)
        self.player_panel = PlayerPanel(self)
        self.select(self.main.data[0])
        self.enemy_panel = EnemyPanel(self)
        self.field = Field(self, 0, self.turn_indicator.rect.height,
                            10, 5, stage.Sewer)
        self.message = ui.TextBox(0, self.turn_indicator.rect.height+self.field.rect.height,
                        640, 480-self.turn_indicator.rect.height-self.field.rect.height, [' '])
        self.ui.add(self.player_panel, self.enemy_panel, self.turn_indicator,
                    self.field, PressAny(self))
        self.main.data[0].enter_field(0, 0, self.field)
        monster1 = character.Character('Lugaru',
                avatar=avatar.Lugaru(), basestat=character.LugaruStat())
        monster2 = character.Character('Clay Golem',
                avatar=avatar.ClayGolem(), basestat=character.ClayGolemStat())
        monster1.enter_field(4, 1, self.field)
        monster2.enter_field(4, 2, self.field)
        self.select(monster1)
    def select(self, character):
        if character.player:
            self.player = character
            self.player_panel.character = character
            self.player_panel.render()
            self.make_skill_buttons(character)
        else:
            self.enemy = character
            self.enemy_panel.character = character
            self.enemy_panel.render()
    def make_skill_buttons(self, character):
        for button in self.skillbuttons:
            button.kill()
        self.skillbuttons = []
        for i in range(len(character.skill)):
            button = SkillButton(i, character.skill[i])
            self.ui.add(button)
            self.skillbuttons.append(button)
    def next_phase(self):
        self.phase += 1
        self.field.move_highlights = []
        if self.phase == 1:
            self.turn = not self.turn
            if self.turn and len(self.field.players)>0:
                self.select(self.field.players[0])
        elif self.phase == 2:
            for character in self.field.characters:
                if len(character.queue)>0:
                    Skill.queue.append(character.queue)
                    #Funnel the combos into one list so we can sort them
                character.queue = []
            for button in self.skillbuttons:
                button.kill()
            self.skillbuttons = []
            self.ui.add(self.message)
        elif self.phase == 3:
            #Tick down
            for character in self.field.characters:
                character.every_turn()
                if character.player == self.turn:
                    character.every_own_turn()
            for tile in self.field.tiles:
                expired_effects = []
                for effect in tile.effects:
                    effect.do()
                    effect.duration -= 1
                    if effect.duration == 0:
                        expired_effects.append(effect)
            for tile in self.field.tiles:
                for effect in tile.effects:
                    if effect in expired_effects:
                        tile.effects.remove(effect)
            self.turn_count += 1
            self.phase = 0
            Skill.queue = []
            Skill.active_action = None
            Skill.active_combo = []
            if self.turn and len(self.field.players)>0:
                self.select(self.field.players[0])
        self.turn_indicator.render()
    def resolve(self):
        self.message.text = []
        if Skill.active_action:
            Skill.active_action.affected_area = []
        if Skill.active_index==len(Skill.active_combo):
            #End of combo
            for character in self.field.characters:
                character.stagger = 0
            Skill.active_index = 0
            if len(Skill.queue)>0:
                def compare_speed(combo):
                    opener = combo[0]
                    startup = opener.startup / opener.owner.speed
                    if opener.owner.player == self.turn and opener.type == "attack":
                        startup = startup*2
                    return startup
                Skill.queue.sort(key=compare_speed)
                Skill.active_combo = Skill.queue.pop(0)
            else:
                self.next_phase()
        if len(Skill.active_combo) > 0:
            Skill.active_action = Skill.active_combo[Skill.active_index]
            if Skill.active_action.owner.staggered:
                self.message.text.append("{} is staggered!".format(Skill.active_action.owner.name))
                Skill.active_index = len(Skill.active_combo)
            else:
                if Skill.active_index == 0:
                    self.message.text.append("{} uses {}!".format(Skill.active_action.owner.name,
                        Skill.active_action.name))
                else:
                    self.message.text.append("{} combos into {}!".format(Skill.active_action.owner.name,
                        Skill.active_action.name))
                Skill.active_action.do()
                if Skill.active_action not in Skill.active_combo:
                    Skill.active_action.surprise_stagger = 0
                Skill.active_index += 1
        self.player_panel.render()
        self.enemy_panel.render()
        self.message.render()
    def draw(self):
        self.main.canvas.fill((20, 20, 20))
        self.ui.update()
        self.ui.draw(self.main.canvas)
    def run(self):
        self.draw()
        if self.event:
            if self.phase==2:
                self.resolve()
            elif not self.turn:
                self.next_phase()
            self.event = None


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
        
class EnemyPanel(ui.Frame):
    def __init__(self, caller):
        self.rect = pygame.Rect(320+15, 0, 320-15, 41)
        self.image = pygame.Surface(self.rect.size)
        self.character = None
        super(EnemyPanel, self).__init__(self.rect, color=(240, 100, 100))
    def render(self):
        self.image.fill((20, 20, 20))
        if self.character:
            portrait = self.character.avatar.portrait
            self.image.blit(pygame.transform.flip(portrait, 1, 0), (320-15-portrait.get_width(), 15))
            font = res.load_font(14)
            base = font.render(self.character.name, 0, (255, 255, 255), (20, 20, 20))
            self.image.blit(base, (320-15-base.get_width(), 0))
            health_empty = pygame.Rect(0, 15, 320-15-portrait.get_width(), 12)
            self.image.fill((80, 80, 80), rect=health_empty)
            health_full = pygame.Rect(int((320-15-portrait.get_width())*(1-self.character.hp/self.character.max_hp)), 15,
                                    int((320-15-portrait.get_width())*(self.character.hp/self.character.max_hp)), 12)
            self.image.fill((20, 220, 20), rect=health_full)
            drive_empty = pygame.Rect(0, 28, 320-15-portrait.get_width(), 12)
            self.image.fill((80, 80, 80), rect=drive_empty)

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
    def render(self):
        self.image = pygame.Surface((self.rect.width, self.rect.height),
                                    flags=pygame.SRCALPHA)
        if self.active:
            self.image.fill(self.highlightcolor)
        if self.caller.turn and self.caller.phase == 0:
            index = 0
        elif not self.caller.turn and self.caller.phase in [1, 2]:
            index = 1
        elif not self.caller.turn and self.caller.phase == 0:
            index = 2
        else:
            index = 3
        self.image.blit(self.frame[index], (0, 0))
    def mousebuttondown(self, caller, event):
        if event.button==1 and self.caller.phase!=2 and self.caller.turn:
            self.caller.next_phase()

class Tile(object):
    def __init__(self):
        self.occupant = []
        self.effects = []
        self.terrain = [] #like a permanent effect

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
        self.moved = False
        self.render_gridlines()
        self.tile = [[Tile()
                for row in range(rows)]
                    for column in range(columns)]
        self.tiles = []
        for column in self.tile:
            for tile in column:
                self.tiles.append(tile)
        self.move_highlights = []
        self.white_highlight = self.draw_highlight((200, 200, 200))
        self.yellow_highlight = self.draw_highlight((200, 200, 20))
        super(Field, self).__init__(self.rect)
        self.characters = []
        self.players = []
        self.enemies = []
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
            if not self.moved and not self.caller.phase==2:
                pos = event.pos
                pos = (pos[0]*640/pygame.display.get_surface().get_width()*
                        self.camera.width/self.rect.width+self.camera.left,
                        (pos[1]*480/pygame.display.get_surface().get_height()
                        -self.rect.top) * self.camera.width/self.rect.width
                        +self.camera.top-self.horizon)
                tile_y = pos[1]/self.grid_height
                tile_x = (pos[0]-pos[1]*self.grid_tilt/self.grid_height)/self.grid_width
                if 0<=tile_x<self.columns and 0<=tile_y<self.rows:
                    tile_x, tile_y = int(tile_x), int(tile_y)
                    if not self.is_blocked_at(tile_x, tile_y) and self.caller.phase==0 and self.caller.turn:
                        if len(self.move_highlights)>0:
                            self.caller.player.move(tile_x, tile_y)
                            self.move_highlights = []
                        else:
                            self.move_highlights += self.caller.player.movement_area()
                    elif ((tile_x, tile_y) == (self.caller.player.x, self.caller.player.y)
                                            and self.caller.phase==0):
                        self.caller.player.direction = -self.caller.player.direction
                    elif len(self.tile[tile_x][tile_y].occupant)>0:
                        for character in self.tile[tile_x][tile_y].occupant:
                            self.caller.select(character)
        self.moved = False
    def mousemotion(self, caller, event):
        self.active = True
        if self.held:
            dx, dy = event.rel
            if not (dx, dy) == (0, 0):
                dx = -int(0.5+dx*self.camera.width/self.rect.width)
                new_x = max(self.camera.left + dx, 0)
                new_x = min(new_x, self.stage.width-self.camera.width)
                self.camera.left = new_x
                self.moved = True
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
        self.render_highlights()
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
                for occupant in self.tile[column][row].occupant:
                    if occupant.direction == 1:
                        x_blit = ((column+0.5)*self.grid_width+
                                (row+0.5)*self.grid_tilt)
                        y_blit = self.horizon+(row+0.5)*self.grid_height+4
                        self.canvas.blit(occupant.avatar.image,
                            (x_blit-occupant.avatar.center[0],
                            y_blit-occupant.avatar.center[1]))
                    else:
                        x_blit = ((column+0.5)*self.grid_width+
                                (row+0.5)*self.grid_tilt)
                        y_blit = self.horizon+(row+0.5)*self.grid_height+4
                        self.canvas.blit(pygame.transform.flip(occupant.avatar.image, 1, 0),
                            (x_blit+occupant.avatar.center[0]-occupant.avatar.image.get_width(),
                            y_blit-occupant.avatar.center[1]))
    def render_highlights(self):
        overlay = pygame.Surface((self.stage.width,
                                self.stage.height), flags=pygame.SRCALPHA)
        if len(self.move_highlights)>0:
            for tile in self.move_highlights:
                x = self.grid_tilt*tile[1]+self.grid_width*tile[0]
                y = self.horizon+self.grid_height*tile[1]
                self.canvas.blit(self.white_highlight, (x, y))
    def draw_highlight(self, color): #Run this in init() once per color that we want to have and save it
        highlight = pygame.Surface((self.grid_width+self.grid_tilt, self.grid_height+1))
        pointlist = [(1, 1), #Upper left
                    (self.grid_width-1, 1), #Upper right
                    (self.grid_tilt+self.grid_width-1, self.grid_height-1), #Lower right
                    (self.grid_tilt+1, self.grid_height-1)] #Lower left
        pygame.draw.polygon(highlight, color, pointlist, 0)
        highlight.set_colorkey((0, 0, 0))
        highlight = highlight.convert()
        highlight.set_alpha(60)
        return highlight
    def is_blocked_at(self, x, y, check_players=True, check_enemies=True, check_terrain=True, check_effects=True):
        if x not in range(self.columns) or y not in range(self.rows):
            return True
        tile = self.tile[x][y]
        for occupant in tile.occupant:
            if check_players and occupant.player:
                return True
            if check_enemies and not occupant.player:
                return True
        if check_terrain:
            for terrain in tile.terrain:
                if terrain.block:
                    return True
        if check_effects:
            for effect in tile.effects:
                if effect.block:
                    return True
        return False

class SkillButton(ui.Frame):
    def __init__(self, i, skill):
        self.skill = skill
        x = 1+(self.skill.icon.get_width()+2)*(i%5)
        y = 402+1+(self.skill.icon.get_height()+2)*int(i/5)
        rect = pygame.Rect(x, y, self.skill.icon.get_width()+2,
                                self.skill.icon.get_height()+2)
        super(SkillButton, self).__init__(rect)
    def render(self):
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        if self.active and self.skill.pre_use():
            self.image.fill(self.highlightcolor)
        else:
            self.image.fill((20, 20, 20))
        if not self.skill.pre_use():
            self.image.set_alpha(40)
        self.image.blit(self.skill.icon, (1, 1))
    def mousebuttondown(self, caller, event):
        self.skill.add_to_queue()
        for button in caller.skillbuttons:
            button.render()

class PressAny(ui.Frame):
    def __init__(self, caller):
        super(PressAny, self).__init__(pygame.Rect(-1, -1, 641, 481))
        self.caller = caller
        self.image = pygame.Surface((0, 0))
    def mousebuttondown(self, caller, event):
        self.caller.event = event