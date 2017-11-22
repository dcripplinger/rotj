# -*- coding: UTF-8 -*-

import random

import pygame
from pygame.locals import *

from battle_warlord_rect import Ally, Enemy
from constants import BLACK, GAME_WIDTH, GAME_HEIGHT
from helpers import get_max_soldiers, get_max_tactical_points, load_image, load_stats
from text import create_prompt, MenuGrid

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

RETREAT_TIME_PER_PERSON = 0.2


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
        self.state = 'start'
            # potential states: start, menu, action, report, report_selected, retreat, all_out, battle, tactic,
            # tactic_ally, tactic_enemy, item, item_ally, item_enemy, dialog, win, lose, execute
        self.warlord = None # the warlord whose turn it is (to make a choice or execute, depending on self.state)
        self.menu = None
        self.portraits = {
            warlord['name']: load_image('portraits/{}.png'.format(warlord['name']))
            for warlord in (allies + enemies)
        }
        self.portrait = None
        self.pointer_right = load_image('pointer.png')
        self.pointer_left = pygame.transform.flip(self.pointer_right, True, False)
        self.screen = screen
        self.right_dialog = None
        self.set_bar_color()
        self.set_start_dialog()
        self.select_sound = pygame.mixer.Sound('data/audio/select.wav')
        self.selected_enemy_index = None
        self.switch_sound = pygame.mixer.Sound('data/audio/switch.wav')

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
        elif self.state == 'menu':
            self.menu.update(dt)
        elif self.state == 'retreat':
            if not self.warlord:
                self.right_dialog.update(dt)
                if not self.right_dialog.has_more_stuff_to_show() and self.get_leader().state == 'wait':
                    self.warlord = self.get_leader().name
                    self.time_elapsed = 0.0
                    self.right_dialog.shutdown()
            else:
                if self.time_elapsed > RETREAT_TIME_PER_PERSON:
                    self.time_elapsed -= RETREAT_TIME_PER_PERSON
                    self.get_current_warlord().flip_sprite()
                    self.warlord = self.get_next_ally_name()
                    if not self.warlord:
                        self.game.end_battle()

    def get_next_ally_name(self):
        if not self.warlord:
            return self.get_leader().name
        found = False
        for ally in self.allies:
            if ally.soldiers == 0:
                continue
            if ally.name == self.warlord:
                found = True
                continue
            if found: # This happens on the ally AFTER the one found
                return ally.name
        return None

    def handle_input_start(self, pressed):
        self.left_dialog.handle_input(pressed)
        if (pressed[K_x] or pressed[K_z]) and not self.left_dialog.has_more_stuff_to_show():
            self.state = 'menu'
            self.left_dialog = None
            self.warlord = self.allies[0].name
            self.portrait = self.portraits[self.warlord]
            self.create_menu()
            self.move_current_warlord_forward()

    def handle_input_menu(self, pressed):
        self.menu.handle_input(pressed)
        if pressed[K_x]:
            self.select_sound.play()
            if self.menu.get_choice() == 'RETREAT':
                self.handle_retreat()
            elif self.menu.get_choice() == 'REPORT':
                self.handle_report()

    def handle_input_report(self, pressed):
        if pressed[K_UP]:
            self.switch_sound.play()
            self.selected_enemy_index = self.get_previous_live_enemy_index()
        elif pressed[K_DOWN]:
            self.switch_sound.play()
            self.selected_enemy_index = self.get_next_live_enemy_index()
        elif pressed[K_z]:
            self.state = 'menu'
            self.menu.focus()
            self.selected_enemy_index = None

    def handle_input(self, pressed):
        if self.state == 'start':
            self.handle_input_start(pressed)
        elif self.state == 'menu':
            self.handle_input_menu(pressed)
        elif self.state == 'report':
            self.handle_input_report(pressed)

    def get_next_live_enemy_index(self):
        if self.selected_enemy_index is None:
            return self.get_first_live_enemy_index()
        found = False
        index = self.selected_enemy_index
        while not found:
            index += 1
            if index >= len(self.enemies):
                index = 0
            enemy = self.enemies[index]
            if enemy.soldiers == 0:
                continue
            found = True
        return index

    def get_previous_live_enemy_index(self):
        if self.selected_enemy_index is None:
            return self.get_first_live_enemy_index()
        found = False
        index = self.selected_enemy_index
        while not found:
            index -= 1
            if index < 0:
                index = len(self.enemies)-1
            enemy = self.enemies[index]
            if enemy.soldiers == 0:
                continue
            found = True
        return index

    def handle_report(self):
        self.state = 'report'
        self.menu.unfocus()
        self.selected_enemy_index = self.get_first_live_enemy_index()

    def get_first_live_enemy_index(self):
        for i, enemy in enumerate(self.enemies):
            if enemy.soldiers > 0:
                return i
        return None

    def handle_retreat(self):
        self.state = 'retreat'
        self.move_current_warlord_back()
        self.right_dialog = create_prompt("{}'s army retreated.".format(self.get_leader().name.title()))
        self.warlord = None

    def move_current_warlord_forward(self):
        warlord = self.get_current_warlord()
        warlord.move_forward()

    def move_current_warlord_back(self):
        warlord = self.get_current_warlord()
        warlord.move_back()

    def get_current_warlord(self):
        if not self.warlord:
            return None
        for warlord in self.allies + self.enemies:
            if warlord.name == self.warlord:
                return warlord

    def create_menu(self):
        first_column = ['BATTLE', 'TACTIC', 'DEFEND', 'ITEM']
        if self.warlord == self.get_leader().name:
            choices = [first_column, ['ALL-OUT', 'RETREAT', 'REPORT', 'RISK-IT']]
        else:
            choices = first_column
        self.menu = MenuGrid(choices, border=True)
        self.menu.focus()

    def get_leader(self):
        for ally in self.allies:
            if ally.soldiers > 0:
                return ally
        assert False, 'should not call this function if everyone is dead'

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
        if self.menu:
            self.screen.blit(self.menu.surface, ((GAME_WIDTH - self.menu.get_width())/2, 128 + top_margin))
        if self.right_dialog:
            self.screen.blit(self.right_dialog.surface, (GAME_WIDTH-self.right_dialog.width, 128+top_margin))
        if self.selected_enemy_index is not None:
            self.screen.blit(self.pointer_right, (GAME_WIDTH-96, self.selected_enemy_index*24+top_margin))

    def get_portrait_position(self):
        return ((16 if self.is_ally_turn() else GAME_WIDTH-64), 160)

    def is_ally_turn(self):
        if not self.warlord:
            return True
        return self.warlord in [ally.name for ally in self.allies]
