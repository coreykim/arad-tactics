from __future__ import division
import random
import avatar
from math import *

class Skill(object):
    """Needs map, Character(), and map-related backend globals"""
    def __init__(self, name, type, startup=50, damage=[], stagger=[],
                preview_area=[], ai_priority = 10, postmove=True,
                finisher=False, drive_requirement=0, drive_cost=0):
        self.name = name
        self.type = type
        self.startup = startup
        self.damage = damage
        self.stagger = stagger
        self.drive_requirement = drive_requirement
        self.drive_cost = drive_cost
        self.preview_area = preview_area #For preview and for AI
        self.affected_area = [] #For resolution phase display
        self.sound = None
        self.miss_sound = load_sound("miss.wav")
        self.owner = None
        self.ai_priority = ai_priority
        self.postmove = postmove
        self.finisher = finisher
        self.used = 0
        self.usable = 1
        self.timer = 0
        self.cooldown = 0
        self.surprise_stagger = 0
    def get_desc_header(self):
        text = [self.name, "Startup: {}".format(self.startup)]
        if len(self.damage)>0:
            text += ["Damage: {}".format(self.damage[0])]
        if len(self.damage)>1:
            for additional_damage in self.damage[1:]:
                text[-1] += ", {}".format(additional_damage)
        if len(self.stagger)>0:
            text += ["Stagger: {}".format(self.stagger[0]+self.surprise_stagger)]
        if len(self.stagger)>1:
            for additional_stagger in self.stagger[1:]:
                text[-1] += ", {}".format(additional_stagger+self.surprise_stagger)
        if self.drive_requirement>0:
            text += ["Requires {} Drive".format(self.drive_requirement)]
        if self.drive_cost>0:
            text += ["Costs {} Drive".format(self.drive_cost)]
        return text
    def get_desc_body(self):
        return []
    def pre_use(self):
        '''Check if this skill is currently usable by its owner'''
        if self.owner.moved and not self.postmove:
            return False
        if self.used >= self.usable:
            return False
        if len(self.owner.queue)>0:
            if self.type=="defend":
                return False
            if self.used > 0 and self.owner.queue[-1] is not self:
                return False
        if self.owner.drive < self.drive_requirement:
            return False
        if self.timer > 0:
            return False
        return True
    def calculate_priority(self, pos = None):
        '''Find the number of valid targets to calculate priority of attack, for AI purposes.'''
        '''Optional arguments allow calculations for positions that we're not actually at.'''
        if pos:
            origin_x, origin_y = pos[0], pos[1]
        else:
            origin_x, origin_y = self.owner.x, self.owner.y
        if Combat.phase == "reaction":
            directions = [self.owner.direction]
        else:
            directions = [1, -1]
        targets = [0, 0]
        for i, direction in enumerate(directions):
            for tile in self.preview_area:
                x, y = origin_x+tile[0]*direction, origin_y+tile[1]
                if x in range(MAP_WIDTH) and y in range(MAP_HEIGHT):
                    if map[x][y].occupant:
                        if map[x][y].occupant.side != self.owner.side:
                            targets[i] += 1.0
                            if (x - origin_x)*map[x][y].occupant.direction > 0: #if this is a back attack
                                targets[i] += 0.5
        if Combat.phase == "reaction":
            return targets[0]*self.ai_priority, self.owner.direction
        else:
            #Compare forward versus backward aiming priority
            if targets[0] >= targets[1]:
                return targets[0]*self.ai_priority, 1
            else:
                return targets[1]*self.ai_priority, -1
    def queue(self):
        if not self.pre_use():
            return
        else:
            self.owner.queue.append(self)
            print "{} queued {}.".format(self.owner.name, self.name)
            #Set flags
            self.used += 1
            self.owner.combo_count += 1
            if self.finisher or self.type is "defend":
                self.owner.done = True
    def combo_check(self, targets):
        if Combat.combo_index is not 0:
            passed_targets = []
            for target in targets:
                if self.startup <= target.stagger_last or target.staggered:
                    passed_targets.append(target)
                else:
                    print "{} broke out of the combo.".format(target.name)
            return passed_targets
        else:
            return targets
    def sheet_unpack(self, item):
        icon = []
        sheet = load_image(item+'.png', scale=1, convert=False)
        '''item is the path minus extension to the sheet, dest is a list of images to blit onto'''
        with open(os.path.join(resources_dir, item+'.txt'), 'r') as sheet_map:
            for i, line in enumerate(sheet_map):
                x_size=(int(line.split()[4]))
                y_size=(int(line.split()[5]))
                icon.append(pygame.Surface((x_size, y_size), flags=SRCALPHA))
        with open(os.path.join(resources_dir, item+'.txt'), 'r') as sheet_map:
            for i, line in enumerate(sheet_map):
                index=(int(line.split()[0]))
                x_start=(int(line.split()[2]))
                y_start=(int(line.split()[3]))
                x_size=(int(line.split()[4]))
                y_size=(int(line.split()[5]))
                cutout = (x_start, y_start, x_size, y_size)
                icon[index].blit(sheet, (0, 0), cutout)
                if SCALE == int(SCALE):
                    icon[index]=pygame.transform.scale(icon[index],
                        (int(icon[index].get_width()*SCALE), int(icon[index].get_height()*SCALE)))
                else:
                    icon[index]=pygame.transform.smoothscale(icon[index],
                        (int(icon[index].get_width()*SCALE), int(icon[index].get_height()*SCALE)))
        return icon
    #Targeting functions
    def tiles_in_radius(self, center_x, center_y, radius):
        tiles = []
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                if abs(x-center_x)+abs(y-center_y)<=radius:
                    tiles.append((x, y))
        return tiles
    def target_area(self, tiles, friendlies=False, enemies=True):
        targets = []
        for tile in tiles:
            x, y = self.owner.x+tile[0]*self.owner.direction, self.owner.y+tile[1]
            if not tile in self.affected_area:
                self.affected_area.append(tile)
            if x in range(MAP_WIDTH) and y in range(MAP_HEIGHT):
                if map[x][y].occupant:
                    if (not map[x][y].occupant.dead and (
                        (map[x][y].occupant.side != self.owner.side and
                        enemies==True) or
                        (map[x][y].occupant.side == self.owner.side and
                        friendlies==True))):
                        targets.append(map[x][y].occupant)
        return self.combo_check(targets)
    def target_projectile(self, tiles, pierce=0):
        targets = []
        pierce = pierce
        for tile in tiles:
            if not tile in self.affected_area:
                self.affected_area.append(tile)
            x, y = self.owner.x+tile[0]*self.owner.direction, self.owner.y+tile[1]
            if x > MAP_WIDTH-1 or x < 0 or y > MAP_HEIGHT or y < 0:
                break
            if map[x][y].occupant:
                if map[x][y].occupant.side != self.owner.side and not map[x][y].occupant.dead:
                    targets.append(map[x][y].occupant)
                    if pierce==0:
                        break
                    else:
                        pierce -= 1
        return self.combo_check(targets)
    #Effect functions
    def do_damage(self, targets, base_damage, stagger=10):
        stagger += self.surprise_stagger
        print "{} stagger".format(stagger)
        if self.owner.avatar:
            if self.owner.avatar.attack1:
                self.owner.avatar.play_anim(self.owner.avatar.attack1, 0.5)
        damaged_targets = []
        for target in targets:
            if not target.dead:
                damage = sqrt(self.owner.power/target.power)*base_damage
                #Adjust for combo
                if not self.finisher:
                    damage = damage*(1+0.2*Combat.combo_index)/len(Combat.current_combo)
                for effect in self.owner.effects:
                    damage, stagger = effect.outgoing_damage(damage, stagger, self, target)
                for effect in target.effects:
                    damage, stagger = effect.incoming_damage(damage, stagger, self)
                target.take_damage(int(damage))
                target.stagger_current += stagger
                if target.stagger_total + target.stagger_last + target.stagger_current >=target.resilience:
                    target.staggered = True
                if damage > 0:
                    damaged_targets.append(target)
                    severity = damage/target.max_hp
                    if severity < 0.2:
                        target.hitfx = load_image("hitfx01.bmp", colorkey=(-1,0))
                    elif severity < 0.4:
                        target.hitfx = load_image("hitfx02.bmp", colorkey=(-1,0))
                    elif severity < 0.6:
                        target.hitfx = load_image("hitfx03.bmp", colorkey=(-1,0))
                    elif severity < 0.8:
                        target.hitfx = load_image("hitfx04.bmp", colorkey=(-1,0))
                    else:
                        target.hitfx = load_image("hitfx05.bmp", colorkey=(-1,0))
        if len(damaged_targets)>0:
            self.sound.play()
        else:
            self.miss_sound.play()
        for target in damaged_targets:
            if target.dead:
                damaged_targets.remove(target)
                print "Detected dead target"
        return damaged_targets
    def knockback_on_stagger(self, targets, knockback=1):
        knocked_back = []
        def column(character):
            return character.x
        if self.owner.direction==1:
            targets.sort(key=column, reverse=True)
        else:
            targets.sort(key=column, reverse=False)
        for target in targets:
            if target.staggered and not target.dead:
                dx = 0
                for i in range(knockback)[::-1]:
                    x = target.x + self.owner.direction * (i+1)
                    y = target.y
                    if x in range(MAP_WIDTH):
                        if not map[x][y].occupant:
                            dx = self.owner.direction * (i+1)
                            break
                if dx > 0:
                    target.change_pos(dx, 0)
                knocked_back.append(target)
        return knocked_back
    def dash(self, distance):
        dx=0
        for i in range(distance):
            x = self.owner.x + self.owner.direction * (1 + i)
            y = self.owner.y
            if x > MAP_WIDTH-1 or x < 0:
                dx = self.owner.direction*i
                break
            elif map[x][y].occupant:
                dx = self.owner.direction*i
                break
            elif i == distance-1:
                dx = self.owner.direction*(i+1)
        if dx > 0:
            self.owner.change_pos(dx, 0)
    def port_behind(self, targets):
        eligible_targets = []
        for target in targets:
            if not target.dead:
                x, y = target.x, target.y
                behind_x = int(x+copysign(1,x-self.owner.x))
                if behind_x in range(MAP_WIDTH) and y in range(MAP_HEIGHT):
                    if not map[behind_x][y].occupant:
                        eligible_targets.append(target)
        if len(eligible_targets)>0:
            target = eligible_targets[random.randrange(len(eligible_targets))]
            dx, dy = target.x+int(copysign(1,target.x-self.owner.x))-self.owner.x, target.y-self.owner.y
            self.owner.direction = -int(copysign(1,target.x-self.owner.x))
            self.owner.change_pos(dx, dy)
    def apply_effect(self, targets, effect, duration=3):
        for target in targets:
            if not target.dead:
                target.gain_effect(effect, duration=duration)
    def tick(self):
        pass
class Swing(Skill):
    def __init__(self):
        Skill.__init__(self, "Swing", "attack", startup=10, damage=[100],
                        stagger=[12], preview_area=[(1,-1),(1,0),(2,0),(1,1)])
        self.sound = load_sound("hit.wav")
        self.icon = self.sheet_unpack('slayer_skill_icon')[8]
    def get_desc_body(self):
        return ["Generate 5 Drive if you make contact with an enemy."]
    def do(self):
        targets = self.target_area(self.preview_area)
        damaged = self.do_damage(targets, self.damage[0], stagger=self.stagger[0])
        if len(damaged)>0:
            self.owner.drive=min(self.owner.drive+5, 100)
class Thrust(Skill):
    def __init__(self):
        Skill.__init__(self, "Thrust", "attack", startup=12, damage=[120],
                        stagger=[14], preview_area=[(1,0),(2,0),(3,0)])
        self.sound = load_sound("hit.wav")
        self.icon = self.sheet_unpack('slayer_skill_icon')[42]
    def get_desc_body(self):
        return ["Generate 5 Drive if you make contact with an enemy."]
    def do(self):
        targets = self.target_area(self.preview_area)
        damaged = self.do_damage(targets, self.damage[0], stagger=self.stagger[0])
        if len(damaged)>0:
            self.owner.drive+=min(self.owner.drive+5, 100)
class GhostSlash(Skill):
    def __init__(self):
        Skill.__init__(self, "Ghost Slash", "attack", startup=8, damage=[200],
                        stagger=[18], preview_area=[(1,0),(2,0),(3,0)],
                        finisher=True)
        self.sound = load_sound("hit.wav")
        self.icon = self.sheet_unpack('slayer_skill_icon')[10]
    def get_desc_body(self):
        return ["Finisher (ends your turn on use, "
                "does full damage at the end of combos).", 
                "Inflicts knockback against staggered enemies."]
    def do(self):
        targets = self.target_area(self.preview_area)
        damaged = self.do_damage(targets, self.damage[0], stagger=self.stagger[0])
        self.knockback_on_stagger(damaged)
class MoonlightSlash(Skill):
    def __init__(self):
        Skill.__init__(self, "Moonlight Slash", "attack", startup=13,
                        damage=[140, 140, 240], stagger=[13, 16, 8],
                        preview_area=[(1,-1),(1,0),(2,0),(1,1)])
        self.sound = load_sound("hit.wav")
        self.icon = self.sheet_unpack('slayer_skill_icon')[160]
        self.usable = 3
        self.consecutive_hits = 0
    def get_desc_header(self):
        text = [self.name, "Startup: {}".format(self.startup)]
        if self.used < 3:
            index = self.used
        else:
            index = 2
        damage_line = "Damage: {}".format(self.damage[index])
        stagger_line = "Stagger: {}".format(self.stagger[index]+self.surprise_stagger)
        if self.used < 2:
            damage_line += "->{}".format(self.damage[index+1])
            stagger_line += "->{}".format(self.stagger[index+1]+self.surprise_stagger)
        text.append(damage_line)
        text.append(stagger_line)
        return text
    def get_desc_body(self):
        return ["Can be used up to three times consecutively.  "
                "Properties change on consecutive use."]
    def do(self):
        targets = self.target_area(self.preview_area)
        damaged = self.do_damage(targets, self.damage[self.consecutive_hits],
                                stagger=self.stagger[self.consecutive_hits])
        self.consecutive_hits += 1
        self.knockback_on_stagger(damaged)
    def tick(self):
        self.consecutive_hits = 0
class Guard(Skill):
    def __init__(self):
        Skill.__init__(self, "Guard", "defend", startup=1)
        self.icon = self.sheet_unpack('slayer_skill_icon')[24]
    def get_desc_body(self):
        return ["Reduces incoming frontal damage by 75%."]
    def do(self):
        self.owner.gain_effect(E_Guard, duration=1)
class Backstep(Skill):
    def __init__(self):
        Skill.__init__(self, "Backstep", "defend", startup=5, preview_area=[(-1,0)])
        self.icon = self.sheet_unpack('common_skill_icon')[0]
    def get_desc_body(self):
        return ["Move back one tile to gain the Dodge effect.  ",
                "You avoid damage from frontal attacks with 10 or more startup, "
                "but you still receive stagger.  The amount of startup "
                "it takes to hit you increases by 2 for each hit dodged."]
    def do(self):
        targets = self.target_area(self.preview_area)
        if len(targets)==0 and self.preview_area[0][0]+self.owner.x in range(MAP_WIDTH):
            self.affected_area = []
            self.owner.change_pos(-self.owner.direction, 0)
            self.owner.gain_effect(E_Dodge, duration=1)
class HurricaneRush(Skill):
    def __init__(self):
        Skill.__init__(self, "Hurricane Rush", "attack", startup=12, preview_area=[(1,0),(2,0),(3,0),(4,0)])
        self.desc = (["Damage: 50", "Startup: 12", "Stagger: 30",
                    "A medium speed attack that moves the user forward by up to 2 tiles, " 
                    "then hits 2 spaces in front.  "
                    "Knocks back by 1 tile against staggered enemies."])
        self.sound = load_sound("hit.wav")
    def do(self):
        self.dash(2)
        targets = self.target_area([(1,0),(2,0)])
        damaged = self.do_damage(targets, 50, stagger=30)
        self.knockback_on_stagger(damaged)
class PowerWave(Skill):
    def __init__(self):
        Skill.__init__(self, "Power Wave", "attack", startup=15, preview_area=[(1,0),(2,0),(2,-1),(2,1)],
            postmove=False)
        self.desc = (["Damage: 25", "Startup: 15", "Stagger: 15",
                    "A slow attack that covers a lot of area.  "
                    "Knocks back by 1 tile against staggered enemies.  Can't be used after moving."])
        self.sound = load_sound("hit.wav")
        self.icon = self.sheet_unpack('slayer_skill_icon')[4]
    def do(self):
        targets = self.target_area(self.preview_area)
        damaged = self.do_damage(targets, 25, stagger=15)
        self.knockback_on_stagger(damaged)
class PowerGeyser(Skill):
    def __init__(self):
        Skill.__init__(self, "Power Geyser", "attack", startup=20,
            preview_area=[(1,0),(2,0),(2,-1),(2,1),(3,-2),(3,-1),(3,0),(3,1),(3,2),(4,-1),(4,0),(4,1)],
            postmove=False, finisher=True)
        self.desc = (["Damage: 50", "Startup: 20", "Stagger: 20",
                    "A slow attack that covers a massive area.  "
                    "Knocks back by 2 tiles against staggered enemies.  Can't be used after moving.  "
                    "Does full damage when used at the end of a combo."])
        self.sound = load_sound("hit.wav")
        self.icon = self.sheet_unpack('slayer_skill_icon')[6]
    def do(self):
        targets = self.target_area(self.preview_area)
        damaged = self.do_damage(targets, 50, stagger=20)
        self.apply_effect(damaged, E_AcidBurn, duration=5)
        self.knockback_on_stagger(damaged, knockback=2)
class EinTrigger(Skill):
    def __init__(self):
        Skill.__init__(self, "Ein Trigger", "attack", startup=10, preview_area=[(1,0),(2,0),(3,0),(4,0)])
        self.desc = (["Damage: 20 + 20", "Startup: 10", "Stagger: 10 + 10",
                    "A somewhat fast attack that hits an enemy immediately in front for 20 damage and stagger, " 
                    "then follows up with a range 4 projectile that hits the first enemy in a forward line for 20 damage.  "
                    "The melee hit knocks back by 1 tile against staggered enemies, but the projectile "
                    "has no knockback."])
        self.sound = load_sound("hit.wav")
    def do(self):
        targets = self.target_area([(1,0)])
        damaged = self.do_damage(targets, 20, stagger=10)
        self.knockback_on_stagger(damaged)
        targets = self.target_projectile(self.preview_area)
        self.do_damage(targets, 20, stagger=10)
class Blackout(Skill):
    def __init__(self):
        Skill.__init__(self, "Blackout", "attack", startup=10, preview_area=[(1,0),(2,0),(3,0)])
        self.desc = (["Damage: 20", "Startup: 10", "Stagger: 5",
                    "A tricky attack that attempts to teleport the user behind the first enemy within its range.  " 
                    "The teleport fails if the space behind its target is already occupied.  Whether or not the "
                    "teleport is successful, it is followed up by a range 1 melee attack."])
        self.sound = load_sound("hit.wav")
    def do(self):
        targets = self.target_projectile(self.preview_area)
        self.port_behind(targets)
        targets = self.target_area([(1,0)])
        self.do_damage(targets, 20, stagger=5)
class AcidVomit(Skill):
    def __init__(self):
        Skill.__init__(self, "Acid Vomit", "attack", startup=10, preview_area=[(1,0),(2,0)], ai_priority=6)
        self.sound = load_sound("splash.wav")
    def do(self):
        targets = self.target_area(self.preview_area)
        damaged = self.do_damage(targets, 20, stagger=10)
        self.apply_effect(damaged, E_AcidBurn, duration=3)

class Special(Skill):
    def __init__(self, name, cooldown=0, drive_requirement=0, drive_cost=0):
        Skill.__init__(self, name, "special", drive_requirement=drive_requirement,
            drive_cost=drive_cost)
        self.cooldown = cooldown
    def get_desc_header(self):
        if self.timer > 0:
            text = [self.name, "Time until ready: {}".format(self.timer)]
        else:
            text = [self.name, "Cooldown: {}".format(self.cooldown)]
        if self.drive_requirement>0:
            text += ["Requires {} Drive".format(self.drive_requirement)]
        if self.drive_cost>0:
            text += ["Costs {} Drive".format(self.drive_cost)]
        return text
    def queue(self):
        if not self.pre_use():
            return
        else:
            print "{} queued {}.".format(self.owner.name, self.name)
            #Set flags
        if self.owner.avatar.cast1:
            self.owner.avatar.play_anim(self.owner.avatar.cast1, 0.5)
        self.do()
        self.timer = self.cooldown
    def tick(self):
        if self.timer > 0:
            self.timer -= 1
        if self.timer < 0:
            self.timer = 0

class Kazan(Special):
    def __init__(self):
        Special.__init__(self, "Kazan", cooldown=6)
        self.icon = self.sheet_unpack('slayer_skill_icon')[52]
    def get_desc_body(self):
        return ["Summons Kazan in front of you.",
                "Allies within 1 tile of Kazan deal +12% damage.  "
                "Each turn, Kazan hits all enemies within 1 tile for 40 damage.  "
                "Ghosts are intangible and do not take up space on the field."]
    def do(self):
        effect = T_Kazan(self.owner.x+self.owner.direction, self.owner.y, 
                    self.owner)
class Bremen(Special):
    def __init__(self):
        Special.__init__(self, "Bremen", cooldown=6, drive_requirement=20)
        self.icon = self.sheet_unpack('slayer_skill_icon')[84]
    def get_desc_body(self):
        return ["Summons Bremen in front of you.",
                "Enemies within 1 tile of Bremen take +12% damage.  "
                "Each turn, Bremen hits all enemies within 1 tile for 40 damage.  "
                "Ghosts are intangible and do not take up space on the field."]
    def do(self):
        effect = T_Bremen(self.owner.x+self.owner.direction, self.owner.y, 
                    self.owner)
class Unshackle(Special):
    def __init__(self):
        Special.__init__(self, "Unshackle", cooldown=10)
        self.icon = self.sheet_unpack('slayer_skill_icon')[80]
    def get_desc_body(self):
        return ["Unshackles adjacent friendly ghosts.  Unshackled ghosts have their "
                "effects increased by 25%, their radii increased "
                "by 1, and re-apply their effects once immediately upon "
                "unshackling.  Only unshackles one ghost per tile.  If "
                "multiple ghosts occupy the same tile, only the first one "
                "will become unshackled."]
    def do(self):
        tiles = self.tiles_in_radius(self.owner.x, self.owner.y, 1)
        for tile in tiles:
            tile = map[tile[0]][tile[1]]
            for effect in tile.effects:
                if effect.ghost and effect.side==self.owner.side:
                    print "Buffed {}".format(effect.name)
                    effect.strength *= 1.25
                    effect.damage *= 1.25
                    effect.radius += 1
                    effect.do()
                    break
class Retreat(Special):
    def __init__(self):
        Special.__init__(self, "Retreat", cooldown=0)
        self.icon = self.sheet_unpack('common_skill_icon')[2]
    def get_desc_body(self):
        return ["A test skill to go back to the party management page "
                "without having to win or lose.",
                "WARNING: THIS WILL MESS EVERYTHING UP"]
    def do(self):
        Combat.victory = True
class Effect(object):
    def __init__(self, name, duration, icon=None, id_name=None, duration_stacking=False):
        self.name = name
        self.owner = None
        self.duration = duration
        self.duration_stacking = duration_stacking
        if icon:
            self.icon=icon
        else:
            self.icon=self.name[:2]
        if id_name:
            self.id_name=id_name
        else:
            self.id_name=self.name
    def get_desc_body(self):
        return []
    def tick(self):
        pass
    def incoming_damage(self, damage, stagger, attack):
        return damage, stagger
    def outgoing_damage(self, damage, stagger, attack, target):
        return damage, stagger
    def merge(self, existing_effect):
        self.owner = existing_effect.owner
        existing_effect.owner.effects.append(self)
class E_Guard(Effect):
    def __init__(self, duration, extras):
        Effect.__init__(self, "Guard", duration)
    def get_desc_body(self):
        return ["Reduces incoming frontal damage by 75%.  "]
    def incoming_damage(self, damage, stagger, attack):
        if self.owner.direction * (attack.owner.x - self.owner.x) > 0:
            damage = damage*0.25
        return damage, stagger
class E_Dodge(Effect):
    def __init__(self, duration, extras):
        Effect.__init__(self, "Dodge", duration)
        self.dodge_count = 0
    def get_desc_body(self):
        return ["Avoids attacks with {} or more startup. ".format(
                10+self.dodge_count)]
    def incoming_damage(self, damage, stagger, attack):
        if (attack.startup/attack.owner.speed >
               (10+self.dodge_count)/self.owner.speed and
               self.owner.direction * (attack.owner.x - self.owner.x) > 0):
            damage = 0
            self.dodge_count += 2
        return damage, stagger
class E_KazanWrath(Effect):
    def __init__(self, duration, extras):
        Effect.__init__(self, "Kazan's Wrath", duration, icon="KW")
        self.amount = extras['amount']
    def get_desc_body(self):
        return (["Damage is increased by {}%. ".format(int(self.amount*100))])
    def outgoing_damage(self, damage, stagger, attack, target):
        damage = damage*(1+self.amount)
        return damage, stagger
    def merge(self, existing_effect):
        if existing_effect.amount<self.amount:
            existing_effect.amount=self.amount
        if existing_effect.duration<self.duration:
            existing_effect.duration=self.duration
class E_BremenHaze(Effect):
    def __init__(self, duration, extras):
        Effect.__init__(self, "Bremen's Haze", duration, icon="BH")
        self.amount = extras['amount']
    def get_desc_body(self):
        return (["Resistance is decreased by {}%. ".format(int(self.amount*100))])
    def incoming_damage(self, damage, stagger, attack):
        damage = damage*(1+self.amount)
        return damage, stagger
    def merge(self, existing_effect):
        if existing_effect.amount<self.amount:
            existing_effect.amount=self.amount
        if existing_effect.duration<self.duration:
            existing_effect.duration=self.duration
class E_AcidBurn(Effect):
    def __init__(self, duration, extras):
        Effect.__init__(self, "Acid Burn", duration, icon="AB", duration_stacking=True)
    def get_desc_body(self):
        return (["Take 10 damage each turn. "])
    def tick(self):
        self.owner.take_damage(10)

class TileEffect(Skill):
    def __init__(self, name, x, y, creator, duration=1, avatar=None, stacking=True):
        self.name = name
        self.duration = duration
        self.avatar = avatar
        if self.avatar:
            self.avatar.owner = self
        self.stacking = stacking
        self.owner = None
        self.side = None
        self.x, self.y = x, y
        if x < 0:
            self.x = 0
        if x > MAP_WIDTH-1:
            self.x = MAP_WIDTH-1
        if y < 0:
            self.y = 0
        if y > MAP_HEIGHT-1:
            self.y = MAP_HEIGHT-1
        self.direction = creator.direction
        self.x_blit, self.y_blit = 0, 0
        map[x][y].effects.append(self)
        self.ghost = False
    def target_area(self, tiles, friendly=True):
        targets = []
        for tile in tiles:
            x, y = tile[0], tile[1]
            if x in range(MAP_WIDTH) and y in range(MAP_HEIGHT):
                if map[x][y].occupant:
                    if (self.side==None or 
                        (map[x][y].occupant.side == self.side and friendly) or
                        (map[x][y].occupant.side != self.side and not friendly)):
                        targets.append(map[x][y].occupant)
        return targets
class T_Kazan(TileEffect):
    def __init__(self, x, y, creator, strength=0.12, duration=6):
        TileEffect.__init__(self, "Kazan", x, y, creator, duration=duration, avatar=avatar.Kazan(), stacking=False)
        self.side = creator.side
        self.strength = strength
        self.damage = 40
        self.radius = 1
        self.ghost = True
        self.do()
    def do(self):
        targets = self.target_area(self.tiles_in_radius(self.x, self.y, self.radius), friendly=False)
        for target in targets:
            target.take_damage(self.damage)
        targets = self.target_area(self.tiles_in_radius(self.x, self.y, self.radius), friendly=True)
        for target in targets:
            target.gain_effect(E_KazanWrath, 1, amount = self.strength)
class T_Bremen(TileEffect):
    def __init__(self, x, y, creator, strength=0.12, duration=6):
        TileEffect.__init__(self, "Bremen", x, y, creator, duration=duration, avatar=avatar.Bremen(), stacking=False)
        self.side = creator.side
        self.strength = strength
        self.damage = 40
        self.radius = 1
        self.ghost = True
        self.do()
    def do(self):
        targets = self.target_area(self.tiles_in_radius(self.x, self.y, self.radius), friendly=False)
        for target in targets:
            target.take_damage(self.damage)
            target.gain_effect(E_BremenHaze, 1, amount = self.strength)