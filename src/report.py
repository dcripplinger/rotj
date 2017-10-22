# -*- coding: UTF-8 -*-

import json

import pygame

from constants import BLACK, COPPER, GAME_WIDTH, GAME_HEIGHT
from helpers import load_image
from text import TextBox

STATS = [
    {
        'name': 'strength',
        'abbr': 'STR',
    },
    {
        'name': 'intelligence',
        'abbr': 'INT',
    },
    {
        'name': 'attack_points',
        'abbr': 'A.P',
    },
    {
        'name': 'ac',
        'abbr': 'A.C',
    },
    {
        'name': 'tactical_points',
        'abbr': 'T.P',
    },
    {
        'name': 'defense',
        'abbr': 'DEF',
    },
    {
        'name': 'agility',
        'abbr': 'AGI',
    },
    {
        'name': 'evasion',
        'abbr': 'EVA',
    },
]


class Bars(object):
    def __init__(self, number):
        self.num_bars = int(number/255.0*20)
        self.surface = pygame.Surface((80, 8))
        for i in range(self.num_bars):
            pygame.draw.rect(self.surface, COPPER, (i*4, 1, 3, 6))


class Report(object):
    def __init__(self, name, level):
        self.name = name.lower()
        self.level = level
        self.surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        self.surface.fill(BLACK)
        self.stats = self.load_stats()
        self.portrait = load_image('portraits/{}.png'.format(self.name))
        self.blit_stats()

    def load_stats(self):
        with open('data/stats/{}.json'.format(self.name)) as f:
            json_data = json.loads(f.read())
        return json_data

    def blit_stats(self):
        self.surface.blit(self.portrait, (16, 32))
        self.surface.blit(TextBox(self.name.title()).surface, (16, 96))
        for i, stat in enumerate(STATS):
            self.surface.blit(TextBox("{}~~{:~<3}".format(stat['abbr'], self.stats[stat['name']])).surface, (80, i*16+32))
            self.surface.blit(Bars(self.stats[stat['name']]).surface, (160, i*16+32))
