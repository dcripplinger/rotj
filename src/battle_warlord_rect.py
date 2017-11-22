# -*- coding: UTF-8 -*-

import math

import pygame

from constants import BLACK, GAME_WIDTH
from helpers import load_image
from text import TextBox

WIDTH = GAME_WIDTH/2
HEIGHT = 24
TEXT_AREA_CHAR_LEN = 8
TEXT_AREA_WIDTH = TEXT_AREA_CHAR_LEN*8
MAX_BAR_WIDTH = 64


class BattleWarlordRectBase(object):
    def __init__(self, warlord):
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
        self.sprite = self.stand
        self.state = 'wait'
        self.rel_pos = 0
        self.rel_target_pos = None
            # relative target position when advancing or retreating the sprite (0 to MAX_BAR_WIDTH-16)

    def move_forward(self):
        self.state = 'forward'
        self.rel_target_pos = 16

    def move_back(self):
        self.state = 'backward'
        self.rel_target_pos = 0

    def get_healed(soldiers):
        pass

    def flip_sprite(self):
        self.sprite = pygame.transform.flip(self.sprite, True, False)

    def get_damaged(soldiers):
        pass

    def update_soldiers_change(delta):
        pass

    def build_soldiers_bar(self):
        self.soldiers_bar = pygame.Surface((math.ceil(self.soldiers/self.soldiers_per_pixel), 8))
        self.soldiers_bar.fill(self.color)

    def build_soldiers_box(self):
        self.soldiers_box = TextBox(str(self.soldiers), width=TEXT_AREA_WIDTH, adjust='right')

    def draw(self):
        self.surface.fill(BLACK)
        self.surface.blit(self.name_box.surface, self.name_box_position)
        self.surface.blit(self.soldiers_box.surface, self.soldiers_box_position)
        self.surface.blit(self.soldiers_bar, self.soldiers_bar_position)
        self.surface.blit(self.sprite, self.get_sprite_position())

    def update(self, dt):
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

    def switch_sprite(self):
        if self.sprite == self.walk:
            self.sprite = self.stand
        else:
            self.sprite = self.walk


class Ally(BattleWarlordRectBase):
    def __init__(self, name):
        super(Ally, self).__init__(name)
        self.name_box_position = (0,0)
        self.soldiers_box_position = (0, 16)

    def get_sprite_position(self):
        return (TEXT_AREA_WIDTH + self.rel_pos, 0)

    def build_soldiers_bar(self):
        super(Ally, self).build_soldiers_bar()
        self.soldiers_bar_position = (TEXT_AREA_WIDTH, 16)


class Enemy(BattleWarlordRectBase):
    def __init__(self, name):
        super(Enemy, self).__init__(name)
        self.name_box_position = (WIDTH - TEXT_AREA_WIDTH, 0)
        self.soldiers_box_position = (WIDTH - TEXT_AREA_WIDTH, 16)
        self.stand = pygame.transform.flip(self.stand, True, False)
        self.walk = pygame.transform.flip(self.walk, True, False)
        self.sprite = self.stand

    def get_sprite_position(self):
        return (WIDTH - TEXT_AREA_WIDTH - 16 - self.rel_pos, 0)

    def build_soldiers_bar(self):
        super(Enemy, self).build_soldiers_bar()
        self.soldiers_bar_position = (WIDTH - TEXT_AREA_WIDTH - self.soldiers_bar.get_width(), 16)
