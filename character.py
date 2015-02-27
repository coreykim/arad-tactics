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

class CharacterFlags(object):
    def __init__(self):
        self.moved = False #Disables further movement and postmove
        self.staggered = False #Disables actions in queue from resolving
        self.combo_count = 0 #Disables movement, starts combo
        self.done = False #Disables further action this turn
        self.dead = False #Disables everything forever

class Character(object):
    """Needs map, map-related globals, PyGame for sprites"""
    def __init__(self, name, job="monster", avatar=None, basestat=None, hero=False, ai=None):
        self.name = name
        self.job = job
        self.avatar = avatar
        if self.avatar:
            self.avatar.owner = self
        self.basestat = basestat
        self.load_stats()
        self.hero = hero
        self.ai = ai
        self.direction = None
        if self.ai:
            self.ai.owner = self
        self.x = self.y = None
        self.flags = CharacterFlags()
        self.skill = []
        self.attack = []
        self.defend = []
        self.special = []
        self.passive = []
        self.effects = []
    def load_stats(self):
        if self.basestat:
            self.hp = self.max_hp = self.basestat.hp
            self.resilience = self.max_resilience = self.basestat.resilience
            self.power = self.basestat.power
            self.speed = self.basestat.speed
            self.movement = self.basestat.movement
            self.drive = 0
    def enter_field(self, x, y, direction=None):
        if not direction:
            if self.hero:
                self.direction = 1
            else:
                self.direction = -1
        map[x][y].occupant = self #???
        pass
    def learn_skill(self, SkillClass):
        skill = SkillClass()
        skill.owner = self
        self.skill.append = skill
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
            self.effects.append(effect)
    def lose_effect(self, effect):
        '''Takes effect instances'''
        self.effects.remove(effect)
    def take_damage(self, damage):
        if damage > 0:
            self.hp -= damage
        if self.hp <= 0 and self.dead == False:
            self.die()
    def die(self):
        pass