# -*- coding: UTF-8 -*-

import pygame

from battle_warlord_rect import Ally, Enemy
from constants import BLACK, GAME_WIDTH, GAME_HEIGHT
from helpers import load_image


class Battle(object):
    def __init__(self, screen, game, allies, enemies, battle_type):
        self.battle_type = battle_type
        self.allies = [Ally(ally) for ally in allies]
        self.enemies = [Enemy(enemy) for enemy in enemies]
        self.state = 'start' # potential states: start, menu, action, report, report_selected, retreat, all_out, battle, tactic, tactic_ally, tactic_enemy, item, item_ally, item_enemy, dialog, win, lose, execute
        self.warlord = None # the warlord whose turn it is (to make a choice or execute, depending on self.state)
        self.menu = None
        self.portraits = {
            warlord['name']: load_image('portraits/{}.png'.format(warlord['name']))
            for warlord in (allies + enemies)
        }
        self.portrait = None
        self.screen = screen
        self.game = game

    def update(self, dt):
        pass

    def draw(self):
        self.screen.fill(BLACK)
        for i, ally in enumerate(self.allies):
            self.screen.blit(ally.surface, (0, i*24))
        for i, enemy in enumerate(self.enemies):
            self.screen.blit(enemy.surface, (GAME_WIDTH/2, i*24))
        if self.portrait:
            self.screen.blit(self.portrait, self.get_portrait_position())

    def get_portrait_position(self):
        return ((0 if self.is_ally_turn() else GAME_WIDTH-48), 192)

    def is_ally_turn(self):
        return self.warlord in [ally.name for ally in self.allies]

    def handle_input(self, pressed):
        pass
