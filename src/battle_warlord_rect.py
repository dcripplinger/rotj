# -*- coding: UTF-8 -*-

import pygame

from constants import BLACK, GAME_WIDTH
from text import TextBox

WIDTH = GAME_WIDTH/2
HEIGHT = 24
TEXT_AREA_CHAR_LEN = 8
TEXT_AREA_WIDTH = TEXT_AREA_CHAR_LEN*8


class BattleWarlordRectBase(object):
    def __init__(self, warlord):
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

    def draw(self):
        self.surface.fill(BLACK)
        self.surface.blit(self.name_box.surface, self.name_box_position)

    def update(self, dt):
        pass


class Ally(BattleWarlordRectBase):
    def __init__(self, name):
        super(Ally, self).__init__(name)
        self.name_box_position = (0,0)


class Enemy(BattleWarlordRectBase):
    def __init__(self, name):
        super(Enemy, self).__init__(name)
        self.name_box_position = (WIDTH - TEXT_AREA_WIDTH, 0)
