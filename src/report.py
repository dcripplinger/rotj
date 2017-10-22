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
        'name': 'defense',
        'abbr': 'DEF',
    },
    {
        'name': 'intelligence',
        'abbr': 'INT',
    },
    {
        'name': 'agility',
        'abbr': 'AGI',
    },
    {
        'name': 'evasion',
        'abbr': 'EVA',
    },
    {
        'name': 'tactical_points',
        'abbr': 'T.P',
    },
    {
        'name': 'attack_points',
        'abbr': 'A.P',
    },
    {
        'name': 'armor_class',
        'abbr': 'A.C',
    },
]


class Bars(object):
    def __init__(self, number):
        self.num_bars = int(number/255.0*20)
        self.surface = pygame.Surface((80, 8))
        for i in range(self.num_bars):
            pygame.draw.rect(self.surface, COPPER, (i*4, 1, 3, 6))


class Report(object):
    def __init__(self, name, level, equips):
        self.equips = equips
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

    def get_equip_based_stat_value(self, stat):
        return sum([equip.get(stat, 0) for equip in self.equips])

    def blit_stats(self):
        self.surface.blit(self.portrait, (16, 32))
        self.surface.blit(TextBox(self.name.title()).surface, (16, 96))
        for i, stat in enumerate(STATS):
            if stat['name'] in ['attack_points', 'armor_class']:
                stat_value = self.get_equip_based_stat_value(stat['name'])
            else:
                stat_value = self.stats[stat['name']]
            self.surface.blit(TextBox("{}~~{:~<3}".format(stat['abbr'], stat_value)).surface, (80, i*16+32))
            self.surface.blit(Bars(stat_value).surface, (160, i*16+32))
