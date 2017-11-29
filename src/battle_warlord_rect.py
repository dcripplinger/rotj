# -*- coding: UTF-8 -*-

import math
import random

import pygame

from constants import BLACK, GAME_WIDTH, TACTICS
from helpers import load_image
from text import TextBox

WIDTH = GAME_WIDTH/2
HEIGHT = 24
TEXT_AREA_CHAR_LEN = 8
TEXT_AREA_WIDTH = TEXT_AREA_CHAR_LEN*8
MAX_BAR_WIDTH = 64


class BattleWarlordRectBase(object):
    def __init__(self, warlord, battle):
        self.battle = battle
        self.stats = warlord
        self.name = warlord['name']
        self.surface = pygame.Surface((WIDTH, HEIGHT))
        name_in_box = self.name.title()
        if len(name_in_box) > TEXT_AREA_CHAR_LEN:
            name_in_box = '{}{}\n{}'.format(
                name_in_box[0:7],
                '-' if '-' not in name_in_box[6:8] else '',
                name_in_box[7:],
            )
        self.name_box = TextBox(name_in_box)
        self.soldiers = warlord['soldiers']
        self.max_soldiers = warlord['max_soldiers']
        self.color = None
        self.soldiers_per_pixel = None
        self.build_soldiers_box()
        self.stand = load_image('sprites/{}/e/stand.png'.format(self.name))
        self.walk = load_image('sprites/{}/e/walk.png'.format(self.name))
        self.stand_s = load_image('sprites/{}/s/stand.png'.format(self.name))
        self.walk_s = load_image('sprites/{}/s/walk.png'.format(self.name))
        self.sprite = self.stand
        self.state = 'wait'
        self.rel_pos = 0
        self.rel_target_pos = None
            # relative target position when advancing or retreating the sprite (0 to MAX_BAR_WIDTH-16)
        self.strength = warlord['strength']
        self.attack_points = warlord['attack_points']
        self.weapon_power = int(100*math.exp(0.0155*self.attack_points)-88)
        self.compounded_strength = self.strength * self.weapon_power / 256.0 / 256.0
        self.tactics = warlord['tactics']
        self.intelligence = warlord['intelligence']
        self.tactic_danger = self.compute_tactic_danger()
        self.tactical_points = warlord['tactical_points']
        self.bad_statuses = set()
        self.index = warlord['index']
        self.boosts = {}
        self.attack_exposure = 1.0 - warlord['defense'] / 255.0
        self.agility = warlord['agility']
        self.evasion = warlord['evasion']
        self.items = warlord['items']
        self.hit_type = None
        self.hit_image_a = True
        self.hit_time = 0

    def animate_all_out(self):
        self.state = 'animate_all_out'
        self.animate_time = 0

    def animate_hit(self, hit_type):
        self.hit_type = hit_type
        self.hit_image_a = True
        self.hit_time = 0

    def get_tactical_points(self):
        if 'liahona' in [item['name'] for item in self.items]:
            return self.tactical_points
        else:
            return self.battle.ally_tactical_points

    def get_danger(self):
        return max(self.tactic_danger, self.get_preliminary_damage())

    def compute_tactic_danger(self):
        assassin = self.intelligence / 255.0 / 3.0 * self.max_soldiers if 'assassin' in self.tactics else 0.0
        fire = self.intelligence / 255.0 * self.get_max_tactic_damage(slot=1)
        water = self.intelligence / 255.0 * self.get_max_tactic_damage(slot=2)
        heal = self.intelligence / 255.0 * self.get_max_tactic_damage(slot=3)
        return max(assassin, fire, water, heal)

    def get_max_tactic_damage(self, slot=None):
        if slot is None:
            return 0
        tactic = self.tactics[slot-1]
        if tactic == '':
            return 0
        return TACTICS[tactic].get('max_damage', 0)

    def get_preliminary_damage(self):
        # including *25 for accurate get_danger() results, simulating a good damage potential
        hulk_boost = self.boosts.get('hulk_boost', 1.0)
        return self.compounded_strength * self.get_soldier_gain() * 25 * hulk_boost

    def get_damage(self, excellent=False):
        return self.get_preliminary_damage() * self.get_damage_potential(excellent=excellent)

    def get_damage_potential(self, excellent=False):
        # including /25.0 to make up for the *25 in get_preliminary_damage()
        if excellent:
            return 51 / 25.0
        return random.choice([25, 25, 25, 25, 25, 25, 25, 25, 23, 23, 23, 23, 23, 23, 20, 20]) / 25.0

    def get_soldier_gain(self):
        return int(math.pow(2, len(str(self.soldiers))-1))

    def move_forward(self):
        self.state = 'forward'
        self.rel_target_pos = 16

    def move_to_front(self):
        self.state = 'forward'
        self.rel_target_pos = 48

    def move_back(self):
        self.state = 'backward'
        self.rel_target_pos = 0

    def get_healed(self, soldiers):
        self.update_soldiers_change(soldiers)

    def flip_sprite(self):
        self.sprite = pygame.transform.flip(self.sprite, True, False)

    def get_damaged(self, soldiers):
        self.update_soldiers_change(-soldiers)

    def update_soldiers_change(self, delta):
        self.soldiers += delta
        self.build_soldiers_bar()
        self.build_soldiers_box()

    def build_soldiers_bar(self):
        if self.soldiers == 0:
            width = 0
        else:
            width = max(math.ceil(self.soldiers/self.soldiers_per_pixel), 1)
        self.soldiers_bar = pygame.Surface((width, 8))
        self.soldiers_bar.fill(self.color)

    def build_soldiers_box(self):
        self.soldiers_box = TextBox(str(self.soldiers), width=TEXT_AREA_WIDTH, adjust='right')

    def draw(self):
        self.surface.fill(BLACK)
        self.surface.blit(self.name_box.surface, self.name_box_position)
        self.surface.blit(self.soldiers_box.surface, self.soldiers_box_position)
        self.surface.blit(self.soldiers_bar, self.soldiers_bar_position)
        if self.soldiers > 0:
            sprite_pos = self.get_sprite_position()
            self.surface.blit(self.sprite, sprite_pos)
            if self.hit_type:
                self.surface.blit(self.hit_images[self.hit_type][self.hit_image_a], sprite_pos)

    def update(self, dt):
        animate_time = 0.5

        if self.state == 'forward':
            self.switch_sprite()
            self.rel_pos += int(dt*100)
            if self.rel_pos > self.rel_target_pos:
                self.rel_pos = self.rel_target_pos
                self.state = 'wait'
        elif self.state == 'backward':
            self.switch_sprite()
            self.rel_pos -= int(dt*100)
            if self.rel_pos < 0:
                self.rel_pos = 0.0
                self.state = 'wait'
        elif self.state == 'animate_all_out':
            self.switch_sprite()
            self.animate_time += dt
            if self.animate_time > animate_time:
                self.state = 'wait'

        # animate the hits independent of the overall state, use hit_type instead
        if self.hit_type:
            self.hit_time += dt
            self.hit_image_a = not self.hit_image_a
            if self.hit_time > animate_time:
                self.hit_type = None

    def switch_sprite(self):
        if self.sprite == self.walk:
            self.sprite = self.stand
        else:
            self.sprite = self.walk


class Ally(BattleWarlordRectBase):
    def __init__(self, name, battle):
        super(Ally, self).__init__(name, battle)
        self.name_box_position = (0,0)
        self.soldiers_box_position = (0, 16)
        self.hit_images = {
            'attack': {
                True: pygame.transform.flip(load_image('hits/attack/a.png'), True, False),
                False: pygame.transform.flip(load_image('hits/attack/b.png'), True, False),
            },
            'fire': {
                True: pygame.transform.flip(load_image('hits/fire/a.png'), True, False),
                False: pygame.transform.flip(load_image('hits/fire/b.png'), True, False),
            },
            'water': {
                True: pygame.transform.flip(load_image('hits/water/a.png'), True, False),
                False: pygame.transform.flip(load_image('hits/water/b.png'), True, False),
            },
        }

    def get_sprite_position(self):
        return (TEXT_AREA_WIDTH + self.rel_pos, 0)

    def build_soldiers_bar(self):
        super(Ally, self).build_soldiers_bar()
        self.soldiers_bar_position = (TEXT_AREA_WIDTH, 16)


class Enemy(BattleWarlordRectBase):
    def __init__(self, name, battle):
        super(Enemy, self).__init__(name, battle)
        self.name_box_position = (WIDTH - TEXT_AREA_WIDTH, 0)
        self.soldiers_box_position = (WIDTH - TEXT_AREA_WIDTH, 16)
        self.stand = pygame.transform.flip(self.stand, True, False)
        self.walk = pygame.transform.flip(self.walk, True, False)
        self.sprite = self.stand
        self.hit_images = {
            'attack': {
                True: load_image('hits/attack/a.png'),
                False: load_image('hits/attack/b.png'),
            },
            'fire': {
                True: load_image('hits/fire/a.png'),
                False: load_image('hits/fire/b.png'),
            },
            'water': {
                True: load_image('hits/water/a.png'),
                False: load_image('hits/water/b.png'),
            },
        }

    def get_sprite_position(self):
        return (WIDTH - TEXT_AREA_WIDTH - 16 - self.rel_pos, 0)

    def build_soldiers_bar(self):
        super(Enemy, self).build_soldiers_bar()
        self.soldiers_bar_position = (WIDTH - TEXT_AREA_WIDTH - self.soldiers_bar.get_width(), 16)
