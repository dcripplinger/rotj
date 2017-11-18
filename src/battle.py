# -*- coding: UTF-8 -*-

import pygame
import random

from battle_warlord_rect import Ally, Enemy
from constants import BLACK, GAME_WIDTH, GAME_HEIGHT
from helpers import get_max_soldiers, get_max_tactical_points, load_image, load_stats


class Battle(object):
    def __init__(self, screen, game, allies, enemies, battle_type):
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

    def update(self, dt):
        for ally in self.allies:
            ally.update(dt)
        for enemy in self.enemies:
            enemy.update(dt)

    def draw(self):
        self.screen.fill(BLACK)
        for i, ally in enumerate(self.allies):
            ally.draw()
            self.screen.blit(ally.surface, (0, i*24))
        for i, enemy in enumerate(self.enemies):
            enemy.draw()
            self.screen.blit(enemy.surface, (GAME_WIDTH/2, i*24))
        if self.portrait:
            self.screen.blit(self.portrait, self.get_portrait_position())

    def get_portrait_position(self):
        return ((0 if self.is_ally_turn() else GAME_WIDTH-48), 192)

    def is_ally_turn(self):
        return self.warlord in [ally.name for ally in self.allies]

    def handle_input(self, pressed):
        pass
