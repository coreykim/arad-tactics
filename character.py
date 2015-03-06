from __future__ import division
from Queue import Queue
import random
import math
from resources import res
import skill

class BaseStat(object):
    def __init__(self, hp=500, resilience=50, power=50, speed=50):
        self.hp = hp
        self.resilience = resilience
        self.power = power
        self.speed = speed
        self.drive = 100
        self.movement = 3
class SlayerStat(BaseStat):
    def __init__(self):
        BaseStat.__init__(self, hp=1000, resilience=50, power=60, speed=50)
class FighterStat(BaseStat):
    def __init__(self):
        BaseStat.__init__(self, hp=1000, resilience=55, power=50, speed=60)
class LugaruStat(BaseStat):
    def __init__(self):
        BaseStat.__init__(self, hp=400, resilience=30, power=30, speed=60)
class ClayGolemStat(BaseStat):
    def __init__(self):
        BaseStat.__init__(self, hp=900, resilience=70, power=55, speed=30)

class Character(object):
    def __init__(self, name, job="monster", avatar=None, basestat=None, player=False, ai=None):
        self.name = name
        self.job = job
        self.avatar = avatar
        if self.avatar:
            self.avatar.owner = self
        self.basestat = basestat
        self.load_stats()
        self.player = player
        self.ai = ai
        if self.ai:
            self.ai.owner = self
        self.direction = None
        self.x = self.y = None
        self.field = None
        self.moved = False #Disables further movement and postmove
        self.staggered = False #Disables actions in queue from resolving
        self.combo_count = 0 #Disables movement, starts combo
        self.done = False #Disables further action this turn
        self.dead = False #Disables everything forever
        self.skill_points = 0
        self.skill = []
        self.attack = []
        self.defend = []
        self.special = []
        self.passive = []
        self.effects = []
        self.queue = []
    def load_stats(self):
        if self.basestat:
            self.hp = self.max_hp = self.basestat.hp
            self.resilience = self.max_resilience = self.basestat.resilience
            self.power = self.basestat.power
            self.speed = self.basestat.speed
            self.movement = self.basestat.movement
            self.drive = 0
    def every_turn(self):
        self.moved = False #Disables further movement and postmove
        self.staggered = False #Disables actions in queue from resolving
        self.combo_count = 0 #Disables movement, starts combo
        self.done = False #Disables further action this turn
        expired_effects = []
        for effect in self.effects:
            effect.tick()
            effect.duration -= 1
            if effect.duration <= 0:
                expired_effects.append(effect)
        for effect in expired_effects:
            self.lose_effect(effect)
    def every_own_turn(self):
        for skill in self.skill:
            skill.tick()
    def enter_field(self, x, y, field, direction=None):
        if not field.is_blocked_at(x, y):
            self.field = field
            field.tile[x][y].occupant.append(self)
            field.characters.append(self)
            if self.player:
                field.players.append(self)
            else:
                field.enemies.append(self)
            if not direction:
                if self.player:
                    self.direction = 1
                else:
                    self.direction = -1
            self.x, self.y = x, y
            for skill in self.skill:
                skill.field = self.field
    def learn_skill(self, SkillClass):
        skill = SkillClass()
        skill.owner = self
        self.skill.append(skill)
        if skill.type == "attack":
            self.attack.append(skill)
        if skill.type == "defend":
            self.defend.append(skill)
        if skill.type == "special":
            self.special.append(skill)
        if skill.type == "passive":
            self.passive.append(skill)
            skill.on_learn()
    def gain_effect(self, EffectClass, duration, **extras):
        '''Takes effect classes'''
        effect = EffectClass(duration, extras)
        already_has = False
        for existing_effect in self.effects:
            if existing_effect.id_name == effect.id_name:
                already_has = True
        if already_has:
            existing_effect.merge(effect)
        else:
            effect.owner = self
            effect.field = self.field
            self.effects.append(effect)
    def lose_effect(self, effect):
        '''Takes effect instances'''
        self.effects.remove(effect)
    def take_damage(self, damage):
        if damage > 0:
            self.hp -= damage
            if self.avatar.hit1:
                self.avatar.play_animation(self.avatar.hit1)
        if self.hp <= 0 and self.dead == False:
            self.die()
    def die(self):
        self.field.tile[self.x][self.y].occupant.remove(self)
        self.field.characters.remove(self)
        if self.player:
            self.field.players.remove(self)
        else:
            self.field.enemies.remove(self)
    def change_pos(self, dx, dy):
        '''self.field must be defined'''
        #Clamp movement to prevent going off the map
        dx = min(dx, self.field.columns-1-self.x)
        dx = max(dx, -self.x)
        dy = min(dy, self.field.rows-1-self.y)
        dy = max(dy, -self.y)
        #Check if the spot's already taken
        if not self.field.is_blocked_at(self.x+dx, self.y+dy):
            self.field.tile[self.x][self.y].occupant.remove(self)
            self.x += dx
            self.y += dy
            self.field.tile[self.x][self.y].occupant.append(self)
    def movement_area(self):
        '''self.field must be defined'''
        if self.moved:
            return []
        def neighbor(x, y): # First define a function to find empty neighboring tiles or the destination
            neighbors = []
            if not self.field.is_blocked_at(x-1, y,
                                check_players = not self.player,
                                check_enemies = self.player):
                neighbors.append((x-1, y))
            if not self.field.is_blocked_at(x+1, y,
                                check_players = not self.player,
                                check_enemies = self.player):
                neighbors.append((x+1, y))
            if not self.field.is_blocked_at(x, y-1,
                                check_players = not self.player,
                                check_enemies = self.player):
                neighbors.append((x, y-1))
            if not self.field.is_blocked_at(x, y+1,
                                check_players = not self.player,
                                check_enemies = self.player):
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
        for x in range(self.field.columns):
            for y in range(self.field.rows):
                if (x, y) in came_from:
                    current = (x, y)
                    path = [current]
                    while current != (self.x, self.y):
                        current = came_from[current]
                        path.append(current)
                    distance = len(path)-1
                    if distance <= self.movement and not self.field.is_blocked_at(x, y):
                        tiles_in_range.append((x, y))
        return tiles_in_range
    def move(self, dest_x, dest_y):
        '''The character proactively moves itself to a destination.'''
        if self.moved:
            return
        #Clamp destination to map boundaries
        dest_x = min(dest_x, self.field.columns-1)
        dest_x = max(dest_x, 0)
        dest_y = min(dest_y, self.field.rows-1)
        dest_y = max(dest_y, 0)
        #Check if we're already there
        if dest_x == self.x and dest_y == self.y:
            return
        #Check if we can move there
        if (dest_x, dest_y) in self.movement_area():
            if cmp(dest_x-self.x, 0) == -self.direction:
                self.direction = -self.direction
            self.change_pos(dest_x-self.x, dest_y-self.y)
            self.moved=True
        else:
            print "Can't move there."