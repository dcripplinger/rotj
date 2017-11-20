# -*- coding: UTF-8 -*-

import pygame
import random

from battle_warlord_rect import Ally, Enemy
from constants import BLACK, GAME_WIDTH, GAME_HEIGHT
from helpers import get_max_soldiers, get_max_tactical_points, load_image, load_stats
from text import create_prompt

COLORS = [
    {
        'soldiers': 640,
        'color': (255,127,127), # pink
        'soldiers_per_pixel': 10,
    },
    {
        'soldiers': 2560,
        'color': (255,106,0), # orange
        'soldiers_per_pixel': 40,
    },
    {
        'soldiers': 10240,
        'color': (255,216,0), # yellow
        'soldiers_per_pixel': 160,
    },
    {
        'soldiers': 40960,
        'color': (0,148,255), # light blue
        'soldiers_per_pixel': 640,
    },
    {
        'soldiers': 163840,
        'color': (0,51,255), # dark blue
        'soldiers_per_pixel': 2560,
    },
    {
        'soldiers': 655360,
        'color': (0,228,0), # green
        'soldiers_per_pixel': 10240,
    },
    {
        'soldiers': 2621440,
        'color': (160,160,160), # gray
        'soldiers_per_pixel': 40960,
    },
    {
        'soldiers': 10485760,
        'color': (160,160,160), # gray
        'soldiers_per_pixel': 40960,
    },
    {
        'soldiers': 1000000000,
        'color': (210,64,64), # dark red
        'soldiers_per_pixel': 81920,
    },
]


class Battle(object):
    def __init__(self, screen, game, allies, enemies, battle_type):
        self.time_elapsed = 0.0
        self.game = game
        self.battle_type = battle_type
        level = self.game.game_state['level']
        self.allies = []
        for ally in allies:
            json_stats = load_stats(ally['name'])
            self.allies.append(Ally({
                'name': ally['name'],
                'strength': json_stats['strength'],
                'intelligence': json_stats['intelligence'],
                'defense': json_stats['defense'],
                'agility': json_stats['agility'],
                'evasion': json_stats['evasion'],
                'tactical_points': ally['tactical_points'],
                'max_tactical_points': get_max_tactical_points(ally['name'], level),
                'soldiers': ally['soldiers'],
                'max_soldiers': get_max_soldiers(ally['name'], level),
            }))
        self.enemies = []
        for enemy in enemies:
            soldiers = random.choice(enemy['stats']['soldiers'])
            self.enemies.append(Enemy({
                'name': enemy['name'],
                'strength': enemy['stats']['strength'],
                'intelligence': enemy['stats']['intelligence'],
                'defense': enemy['stats']['defense'],
                'agility': enemy['stats']['agility'],
                'evasion': enemy['stats']['evasion'],
                'tactical_points': enemy['stats']['tactical_points'],
                'max_tactical_points': enemy['stats']['tactical_points'],
                'soldiers': soldiers,
                'max_soldiers': soldiers,
            }))
        self.state = 'start' # potential states: start, menu, action, report, report_selected, retreat, all_out, battle, tactic, tactic_ally, tactic_enemy, item, item_ally, item_enemy, dialog, win, lose, execute
        self.warlord = None # the warlord whose turn it is (to make a choice or execute, depending on self.state)
        self.menu = None
        self.portraits = {
            warlord['name']: load_image('portraits/{}.png'.format(warlord['name']))
            for warlord in (allies + enemies)
        }
        self.portrait = None
        self.screen = screen
        self.set_bar_color()
        self.set_start_dialog()

    def set_start_dialog(self):
        script = ''
        for enemy in self.enemies:
            script += '{} approaching.\n'.format(enemy.name.title())
        self.left_dialog = create_prompt(script, silent=True)

    def set_bar_color(self):
        max_max_soldiers = max([ally.max_soldiers for ally in self.allies])
        for color_info in COLORS:
            if max_max_soldiers < color_info['soldiers']:
                color = color_info['color']
                soldiers_per_pixel = color_info['soldiers_per_pixel']
                break
        for ally in self.allies:
            ally.color = color
            ally.soldiers_per_pixel = soldiers_per_pixel
            ally.build_soldiers_bar()
        for enemy in self.enemies:
            enemy.color = color
            enemy.soldiers_per_pixel = soldiers_per_pixel
            enemy.build_soldiers_bar()

    def update(self, dt):
        self.time_elapsed += dt
        for ally in self.allies:
            ally.update(dt)
        for enemy in self.enemies:
            enemy.update(dt)
        if self.state == 'start':
            self.left_dialog.update(dt)

    def handle_input(self, pressed):
        if self.stat == 'start':
            self.left_dialog.handle_input(pressed)

    def draw(self):
        self.screen.fill(BLACK)
        top_margin = 16
        for i, ally in enumerate(self.allies):
            ally.draw()
            self.screen.blit(ally.surface, (0, i*24+top_margin))
        for i, enemy in enumerate(self.enemies):
            enemy.draw()
            self.screen.blit(enemy.surface, (GAME_WIDTH/2, i*24+top_margin))
        if self.portrait:
            self.screen.blit(self.portrait, self.get_portrait_position())
        if self.left_dialog:
            self.screen.blit(self.left_dialog.surface, (0, 128+top_margin))

    def get_portrait_position(self):
        return ((0 if self.is_ally_turn() else GAME_WIDTH-48), 192)

    def is_ally_turn(self):
        return self.warlord in [ally.name for ally in self.allies]

    def handle_input(self, pressed):
        pass
