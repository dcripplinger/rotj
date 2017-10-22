# -*- coding: UTF-8 -*-

import pygame

from constants import BLACK, GAME_WIDTH, GAME_HEIGHT


class Report(object):
    def __init__(self, name):
        self.name = name
        self.surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        self.surface.fill(BLACK)