# -*- coding: UTF-8 -*-

import json
import os

import pygame

from constants import BLACK, COPPER, GAME_WIDTH, GAME_HEIGHT
from helpers import (
    get_equip_based_stat_value, get_max_soldiers, get_max_tactical_points, get_tactics, hyphenate, load_image,
    load_stats,
)
from text import MenuGrid, TextBox

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
    def __init__(self, name=None, level=None, equips=None, stats=None, headless=False):
        '''
        Either provide (name, level, equips) or provide (stats)
        '''
        self.equips = equips
        self.name = name.lower() if name else None
        self.level = level
        self.surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        self.surface.fill(BLACK)
        self.tp_star = None
        self.soldiers_star = None
        if name == None: # This is an enemy report
            self.stats = stats
            self.name = stats['name']
            self.stats_provided = True
        else: # This is an ally report
            self.stats = load_stats(self.name)
            self.stats_provided = False
            if 'tactical_points_by_level' in self.stats:
                self.tp_star = TextBox('*')
            if 'max_soldiers_by_level' in self.stats:
                self.soldiers_star = TextBox('*')
        if self.name == 'shiz' and headless:
            portrait_name = 'shiz_headless'
        else:
            portrait_name = self.name
        self.portrait = load_image(os.path.join('portraits', '{}.png'.format(portrait_name)))
        self.blit_stats()

    def blit_stats(self):
        self.surface.blit(self.portrait, (16, 32))
        self.surface.blit(TextBox(self.name.title()).surface, (16, 16))
        for i, stat in enumerate(STATS):
            if stat['name'] in ['attack_points', 'armor_class']:
                if self.stats_provided:
                    stat_value = self.stats[stat['name']]
                else:
                    stat_value = get_equip_based_stat_value(stat['name'], self.equips)
            elif stat['name'] == 'tactical_points':
                if self.stats_provided:
                    stat_value = self.stats[stat['name']]
                else:
                    stat_value = self.get_tactical_points()
            else:
                stat_value = self.stats[stat['name']]
            self.surface.blit(TextBox("{}~{:~>3}".format(stat['abbr'], stat_value)).surface, (96, i*16+32))
            self.surface.blit(Bars(stat_value).surface, (160, i*16+32))
        tactics = self.get_tactics()
        tactics = [tactics[:3], tactics[3:]]
        grid = MenuGrid(tactics, border=True, title='TACTICS')
        self.surface.blit(grid.surface, (48, 160))
        self.surface.blit(TextBox("SOLDIERS").surface, (16, 96))
        soldiers = "{:~>8}".format(self.get_max_soldiers())
        self.surface.blit(TextBox(soldiers).surface, (16, 112))
        if self.tp_star:
            self.surface.blit(self.tp_star.surface, (120, 112))
        if self.soldiers_star:
            self.surface.blit(self.soldiers_star.surface, (80, 96))

    def get_max_soldiers(self):
        if 'max_soldiers_by_level' in self.stats:
            return self.stats['max_soldiers_by_level'][self.level-1]
        return self.stats['max_soldiers']

    def get_tactical_points(self):
        if 'tactical_points_by_level' in self.stats:
            return self.stats['tactical_points_by_level'][self.level-1]
        return self.stats['tactical_points']

    def get_tactics(self):
        return get_tactics(self.stats, self.level)


class CompanyReport(object):
    def __init__(self, company, money, food, experience, level):
        self.surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        self.surface.fill(BLACK)
        tactician_found = False
        soldiers_text = ""
        for index, warlord in enumerate(company):
            if index == 0:
                if warlord['name'] == 'shiz' and warlord.get('headless'):
                    portrait_name = 'shiz_headless'
                else:
                    portrait_name = warlord['name']
                portrait = load_image(os.path.join('portraits', '{}.png'.format(portrait_name)))
                self.surface.blit(portrait, (16, 32))
                self.surface.blit(TextBox('LEADER').surface, (72, 48))
                self.surface.blit(TextBox(warlord['name'].title()).surface, (72, 64))
            soldiers_text += "{}\n".format(warlord['name'].title())
            soldiers_text += "~{:~>8}/{:~>8}\n".format(warlord['soldiers'], get_max_soldiers(warlord['name'], level))
            if warlord.get('tactician'):
                tactician_found = True
                self.surface.blit(TextBox('STRAT.').surface, (176, 120))
                self.surface.blit(TextBox(hyphenate(warlord['name'].title(), 10)).surface, (176, 136))
                tp_text = "~TP~LEFT\n"
                tp_text += "~{:~>7}\n".format(warlord['tactical_points'])
                tp_text += "~MAX~TP\n"
                tp_text += "~{:~>7}".format(get_max_tactical_points(warlord['name'], level))
                self.surface.blit(TextBox(tp_text).surface, (176, 160))
        soldiers_box = TextBox(soldiers_text, border=True)
        self.surface.blit(soldiers_box.surface, (0, 96))
        spoils_text = "~MONEY\n"
        spoils_text += "~{:~>8}~\n".format(money)
        spoils_text += "~FOOD\n"
        spoils_text += "~{:~>8}~\n".format(food)
        spoils_text += "~EXP\n"
        spoils_text += "~{:~>8}~".format(experience)
        spoils_box = TextBox(spoils_text, border=True, title="LEVEL~{:02d}".format(level))
        self.surface.blit(spoils_box.surface, (GAME_WIDTH-96, 32))
        if not tactician_found:
            self.surface.blit(TextBox('STRAT.').surface, (176, 120))
            self.surface.blit(TextBox('None').surface, (176, 136))
