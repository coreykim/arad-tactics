from __future__ import division
from Queue import Queue
import random
from math import *
from load import *
from gamevariables import *

class Character(object):
    """Needs map, map-related globals, PyGame for sprites"""
    f_hero = None
    f_monster = None
    def __init__(self, name, x, y, avatar=None, side="enemy", max_hp=1000, resilience=50, power=50, speed=50, technique=50,
                    direction=None, ai=None):
        pass
    def enter_field(self, x, y):
        pass
    
    
    
        self.name = name
        self.x = x
        self.y = y
        self.avatar = avatar
        if self.avatar:
            self.avatar.owner = self
        self.frame=0
        if avatar:
            self.image = avatar.sprite[self.frame]
            self.image_r = avatar.sprite_r[self.frame]
        self.side = side #Player or enemy side
        self.direction = direction #+1 for facing right, -1 for facing left
        if not self.direction:
            if self.side is "enemy": self.direction = -1
            if self.side is "player": self.direction = 1
        #I wrote some combat stats pre-emptively
        self.max_hp = max_hp
        self.hp = self.max_hp
        self.resilience = resilience
        self.drive = 0
        self.stagger_total = 0
        self.stagger_last = 0
        self.stagger_current = 0
        self.power = power
        self.speed = speed
        self.technique = technique
        self.movement = 3
        #Flags
        self.moved = False #Disables further movement and postmove
        self.staggered = False #Disables actions in queue from resolving
        self.combo_count = 0 #Disables movement, starts combo
        self.done = False #Disables further action
        self.dead = False #Disables everything forever
        self.queue = []
        map[x][y].occupant = self
        #Animation related
        self.x_blit = 0
        self.y_blit = 0
        self.hitfx = None
        self.shake = 0
        self.damage_numbers = []
        #End of combat stats
        self.ai = ai
        if self.ai:
            self.ai.owner = self
        #Organize skills into four categories
        self.attacks = []
        self.defends = []
        self.specials = []
        self.passives = []
        #List of effects
        self.effects = []
        #Add to character groups on initialization for easier reference
        Character.all.append(self)
        if self.side == "player":
            Character.players.append(self)
        if self.side == "enemy":
            Character.enemies.append(self)
    def update_sprite(self):
        y_anim_offset=0
        x_anim_offset=0
        if self.shake != 0:
            self.shake += 1
            path = range(4) + range(4)[::-1]
            x_anim_offset = -6 * path[self.shake] * self.direction
        if self.shake == 7:
            self.shake = 0
            x_anim_offset = 0
        if self.avatar:
            self.avatar.frame += self.avatar.anim_speed
            if self.avatar.frame >= len(self.avatar.anim):
                self.avatar.frame = 0
                self.avatar.anim = self.avatar.idle
                self.avatar.anim_speed = self.avatar.idle_speed
        for i, number in enumerate(self.damage_numbers):
            if i == 0:
                number.update()
            elif self.damage_numbers[i-1].frame > 8:
                number.update()
            if number.frame == 40:
                self.damage_numbers.remove(number)
        x_grid = (DIAGONAL*(MAP_HEIGHT-self.y) + GRID_WIDTH*self.x + 
                            (GRID_WIDTH-DIAGONAL)/2 + GRID_X_OFFSET)
        y_grid = GRID_Y_OFFSET + self.y*GRID_HEIGHT + GRID_HEIGHT/2
        if self.direction is 1:
            image = self.avatar.sprite[self.avatar.anim[int(self.avatar.frame)]]
            self.x_blit = int(x_grid + x_anim_offset - self.avatar.center[0])
        elif self.direction is -1:
            image = self.avatar.sprite_r[self.avatar.anim[int(self.avatar.frame)]]
            self.x_blit = int(x_grid - self.avatar.dimensions[0] +
                        x_anim_offset + self.avatar.center[0])
        self.y_blit = int(y_grid + y_anim_offset - self.avatar.center[1])
        return image
    def change_pos(self, dx, dy):
        '''Move the character by a certain amount'''
        #Clamp movement to prevent going off the map
        if self.x + dx >= MAP_WIDTH:
            dx = MAP_WIDTH - 1 - self.x
        if self.x + dx < 0:
            dx = -self.x
        if self.y + dy >= MAP_HEIGHT:
            dy = MAP_HEIGHT - 1 - self.y
        if self.y + dy < 0:
            dy = -self.y
        #Check if the spot's already taken
        if not map[self.x+dx][self.y+dy].occupant:
            map[self.x][self.y].occupant = None
            #Move your body, every every body
            self.x += dx
            self.y += dy
            map[self.x][self.y].occupant = self
        else: print "{} tried to move by ({},{}), but that spot's already taken by {}".format(self.name, 
                    dx, dy, map[self.x+dx][self.y+dy].occupant.name)
    def movement_area(self):
        '''Returns a set of tiles that are within movement range, following movement rules'''
        '''Uses map and map-related globals'''
        if self.moved:
            return []
        def neighbor(x, y): # First define a function to find empty neighboring tiles or the destination
            neighbors = []
            if x-1 in range(MAP_WIDTH):
                if not map[x-1][y].occupant:
                    neighbors.append((x-1, y))
                elif map[x-1][y].occupant.side==self.side:
                    neighbors.append((x-1, y))
            if x+1 in range(MAP_WIDTH):
                if not map[x+1][y].occupant:
                    neighbors.append((x+1, y))
                elif map[x+1][y].occupant.side==self.side:
                    neighbors.append((x+1, y))
            if y-1 in range(MAP_HEIGHT):
                if not map[x][y-1].occupant:
                    neighbors.append((x, y-1))
                elif map[x][y-1].occupant.side==self.side:
                    neighbors.append((x, y-1))
            if y+1 in range(MAP_HEIGHT):
                if not map[x][y+1].occupant:
                    neighbors.append((x, y+1))
                elif map[x][y+1].occupant.side==self.side:
                    neighbors.append((x, y+1))
            return neighbors
        #Start Breadth First Search
        frontier = Queue(maxsize=0)
        frontier.put((self.x, self.y))
        came_from = {}
        came_from[(self.x, self.y)] = None
        while not frontier.empty():
            current = frontier.get()
            for next in neighbor(current[0], current[1]):
                if next not in came_from:
                    frontier.put(next)
                    came_from[next] = current
        #End Breadth First Search
        #Find distance
        tiles_in_range = []
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                if (x, y) in came_from:
                    current = (x, y)
                    path = [current]
                    while current != (self.x, self.y):
                        current = came_from[current]
                        path.append(current)
                    distance = len(path)-1
                    if distance <= self.movement and not map[x][y].occupant:
                        tiles_in_range.append((x, y))
        return tiles_in_range
    def move(self, dx, dy):
        '''The character proactively moves itself by a certain amount.'''
        if self.moved:
            return
        dest_x = self.x + dx
        dest_y = self.y + dy
        #Clamp destination to map boundaries
        if dest_x < 0: dest_x = 0
        if dest_x > MAP_WIDTH-1: dest_x = MAP_WIDTH-1
        if dest_y < 0: dest_y = 0
        if dest_y > MAP_HEIGHT-1: dest_y = MAP_HEIGHT-1
        #Check if we're already there
        if dest_x == self.x and dest_y == self.y:
            return
        #Check if we can move there
        if (dest_x, dest_y) in self.movement_area():
            self.change_pos(dx, dy)
            if cmp(dx, 0) == -self.direction:
                self.direction = -self.direction
            self.moved=True
        else:
            print "Can't move there."
    def pass_control(self):
        '''Passes player control.'''
        if self == Character.player:
            index = Character.players.index(Character.player)
            for i, character in enumerate(Character.players):
                index += 1
                if index > len(Character.players)-1:
                    index = 0
                if not Character.players[index].done:
                    Character.player = Character.players[index]
                    return
            Character.player=None
    def learn_skill(self, SkillClass):
        skill = SkillClass()
        skill.owner = self
        if skill.type == "attack":
            self.attacks.append(skill)
        if skill.type == "defend":
            self.defends.append(skill)
        if skill.type == "special":
            self.specials.append(skill)
        if skill.type == "passive":
            self.passives.append(skill)
    def gain_effect(self, EffectClass, duration, **extras):
        '''Takes effect classes'''
        effect = EffectClass(duration, extras)
        already_has = False
        for existing_effect in self.effects:
            if existing_effect.id_name == effect.id_name:
                already_has = True
        if already_has:
            effect.merge(existing_effect)
        else:
            effect.owner = self
            self.effects.append(effect)
    def lose_effect(self, effect):
        '''Takes effect instances'''
        self.effects.remove(effect)
    def take_damage(self, damage):
        #Damage number display effect
        self.damage_numbers.append(DamageNumber(int(damage)))
        if damage > 0:
            self.hp -= damage
            self.shake = 1
            if self.avatar:
                if self.avatar.hit1:
                    self.avatar.play_anim(self.avatar.hit1, 0.2)
        if self.hp <= 0 and self.dead == False:
            self.die()
    def die(self):
        map[self.x][self.y].occupant = None
        if Character.player == self:
            Character.player = None
        for character in Character.players:
            if character==self:
                Character.players.remove(self)
        for character in Character.enemies:
            if character==self:
                Character.enemies.remove(self)
        for character in Character.all:
            if character==self:
                Character.all.remove(self)
        #When you die your actions are removed from the queue
        for combo in Combat.queue:
            if combo[0].owner == self:
                Combat.queue.remove(combo)

class BasicMonster(object):
    '''The basic AI class'''
    def __init__(self, attack_priority=15):
        self.aggro = None #Not used yet
        self.priority_map = [[(0, None, False) #(priority, attack, reverse)
                                for y in range(MAP_HEIGHT)]
                                    for x in range(MAP_WIDTH)]
        self.priority_list = []
    def noncombat_act(self): #This will become obsolete when Main.run_ai is complete
        if Combat.phase == "action":
            if len(self.owner.attacks)>0:
                r = random.randrange(len(self.owner.attacks))
                self.owner.attacks[r].queue()
        self.owner.done = True
    def random_move(self):
        pass
    def build_priority_list(self):
        self.priority_list = []
        #Check stationary attacks
        highest_priority, highest_priority_attack, direction = 0, None, -1
        for attack in self.owner.attacks:
            if attack.pre_use()==True:
                present_priority, present_direction = attack.calculate_priority()
                if present_priority > highest_priority:
                    highest_priority, highest_priority_attack, direction = present_priority, attack, present_direction
        if highest_priority > 0:
            self.priority_list.append((highest_priority, highest_priority_attack, direction, self.owner.x, self.owner.y))
        #Check post-move attacks
        if Combat.phase=="action":
            for tile in self.owner.movement_area():
                highest_priority, highest_priority_attack, direction = 0, None, -1
                for attack in self.owner.attacks:
                    if attack.pre_use()==True:
                        present_priority, present_direction = attack.calculate_priority(pos = tile)
                        #Attacks that aren't postmove get a large priority penalty
                        if attack.postmove == False:
                            present_priority = present_priority/4
                        if present_priority > highest_priority:
                            highest_priority, highest_priority_attack, direction = present_priority, attack, present_direction
                            highest_x, highest_y = tile
                if highest_priority > 0:
                    self.priority_list.append((highest_priority, highest_priority_attack, direction, tile[0], tile[1]))
        if len(self.priority_list)>0:
            def compare_priority(priority):
                return priority[0]
            self.priority_list.sort(key=compare_priority, reverse=True)

class DamageNumber(object):
    '''Flags that show damage taken'''
    def __init__(self, amount):
        self.amount = amount
        self.frame = 0
        self.y_anim_offset = 0
        fontpath = os.path.join(resources_dir, "Code New Roman.otf")
        font = pygame.font.Font(fontpath, 24)
        self.image = font.render(str(amount), 1, white)
    def update(self):
        self.frame += 1
        self.y_anim_offset -= 1