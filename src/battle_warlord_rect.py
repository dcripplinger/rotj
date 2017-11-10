# -*- coding: UTF-8 -*-

import pygame

from constants import GAME_WIDTH


class BattleWarlordRectBase(object):
    def __init__(self, name):
        self.name = name
        self.surface = pygame.Surface((GAME_WIDTH/2, 24))


class Ally(BattleWarlordRectBase):
    def __init__(self, name):
        super(Ally, self).__init__(name)


class Enemy(BattleWarlordRectBase):
    def __init__(self, name):
        super(Enemy, self).__init__(name)
