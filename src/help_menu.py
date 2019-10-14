# -*- coding: UTF-8 -*-

import os

import pygame
from pygame.locals import *

from constants import BLACK, GAME_WIDTH, GAME_HEIGHT, ITEMS, STATS, TACTICS
from text import create_prompt, MenuBox, MenuGrid


ITEMS_MENU = {
    'HEAL ITEMS': {
        'sort_order': 0,
    },
    'ATTACK ITEMS': {
        'sort_order': 1,
        'conditions': {
            'battle05': True,
        },
    },
    'MAP ITEMS': {
        'sort_order': 2,
    },
    'SAVE ITEMS': {
        'sort_order': 3,
        'conditions': {
            'destroyed_ammonihah_treasure': True,
        },
    },
    'PASSIVE ITEMS': {
        'sort_order': 4,
    },
}


class HelpMenu(object):
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.select_sound = pygame.mixer.Sound(os.path.join('data', 'audio', 'select.wav'))
        self.state = 'main'
        items = [
            'WEAPONS',
            'BODY ARMOR',
            'HELMETS',
            'TACTICS',
            'ITEMS',
            'STATS',
        ]
        self.menu = MenuBox(items, current_choice=0, border=True, title='Help')
        self.menu.focus()
        self.weapons_menu = None
        self.stats_menu = None
        self.body_armor_menu = None
        self.helmets_menu = None
        self.tactics_menu = None
        self.tactics_submenu = None
        self.items_menu = None
        self.items_submenu = None
        self.description = None

    def draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.menu.surface, (0, 0))
        if self.weapons_menu:
            self.screen.blit(self.weapons_menu.surface, (48, 0))
        if self.stats_menu:
            self.screen.blit(self.stats_menu.surface, (48, 0))
        if self.body_armor_menu:
            self.screen.blit(self.body_armor_menu.surface, (48, 0))
        if self.helmets_menu:
            self.screen.blit(self.helmets_menu.surface, (48, 0))
        if self.tactics_menu:
            self.screen.blit(self.tactics_menu.surface, (0, 128))
        if self.tactics_submenu:
            self.screen.blit(self.tactics_submenu.surface, (48, 0))
        if self.items_menu:
            self.screen.blit(self.items_menu.surface, (0, 128))
        if self.items_submenu:
            self.screen.blit(self.items_submenu.surface, (48, 0))
        if self.description:
            self.screen.blit(self.description.surface, (0, 160))

    def update(self, dt):
        if self.description:
            self.description.update(dt)
        elif self.state == 'main':
            self.menu.update(dt)
        elif self.state == 'weapons':
            self.weapons_menu.update(dt)
        elif self.state == 'stats':
            self.stats_menu.update(dt)
        elif self.state == 'body_armor':
            self.body_armor_menu.update(dt)
        elif self.state == 'helmets':
            self.helmets_menu.update(dt)
        elif self.state == 'tactics':
            if self.tactics_submenu:
                self.tactics_submenu.update(dt)
            else:
                self.tactics_menu.update(dt)
        elif self.state == 'items':
            if self.items_submenu:
                self.items_submenu.update(dt)
            else:
                self.items_menu.update(dt)

    def handle_input(self, pressed):
        if self.state == 'main':
            self.menu.handle_input(pressed)
            if pressed[K_x]:
                self.select_sound.play()
                choice = self.menu.get_choice()
                if choice == 'WEAPONS':
                    self.create_weapons_menu()
                if choice == 'STATS':
                    self.create_stats_menu()
                elif choice == 'BODY ARMOR':
                    self.create_body_armor_menu()
                elif choice == 'HELMETS':
                    self.create_helmets_menu()
                elif choice == 'TACTICS':
                    self.create_tactics_menu()
                elif choice == 'ITEMS':
                    self.create_items_menu()
        elif self.state == 'weapons':
            if self.description:
                self.description.handle_input(pressed)
                if (pressed[K_x] or pressed[K_z]) and not self.description.has_more_stuff_to_show():
                    self.description.shutdown()
                    self.description = None
                    self.weapons_menu.focus()
                return
            self.weapons_menu.handle_input(pressed)
            if pressed[K_x]:
                self.select_sound.play()
                choice = self.weapons_menu.get_choice().lower()
                self.description = create_prompt(ITEMS[choice]['description'])
                self.weapons_menu.unfocus()
            elif pressed[K_z]:
                self.weapons_menu = None
                self.menu.focus()
                self.state = 'main'
        elif self.state == 'stats':
            if self.description:
                self.description.handle_input(pressed)
                if (pressed[K_x] or pressed[K_z]) and not self.description.has_more_stuff_to_show():
                    self.description.shutdown()
                    self.description = None
                    self.stats_menu.focus()
                return
            self.stats_menu.handle_input(pressed)
            if pressed[K_x]:
                self.select_sound.play()
                choice = self.stats_menu.get_choice()
                self.description = create_prompt(STATS[choice]['description'])
                self.stats_menu.unfocus()
            elif pressed[K_z]:
                self.stats_menu = None
                self.menu.focus()
                self.state = 'main'
        elif self.state == 'body_armor':
            if self.description:
                self.description.handle_input(pressed)
                if (pressed[K_x] or pressed[K_z]) and not self.description.has_more_stuff_to_show():
                    self.description.shutdown()
                    self.description = None
                    self.body_armor_menu.focus()
                return
            self.body_armor_menu.handle_input(pressed)
            if pressed[K_x]:
                self.select_sound.play()
                choice = self.body_armor_menu.get_choice().lower()
                self.description = create_prompt(ITEMS[choice]['description'])
                self.body_armor_menu.unfocus()
            elif pressed[K_z]:
                self.body_armor_menu = None
                self.menu.focus()
                self.state = 'main'
        elif self.state == 'helmets':
            if self.description:
                self.description.handle_input(pressed)
                if (pressed[K_x] or pressed[K_z]) and not self.description.has_more_stuff_to_show():
                    self.description.shutdown()
                    self.description = None
                    self.helmets_menu.focus()
                return
            self.helmets_menu.handle_input(pressed)
            if pressed[K_x]:
                self.select_sound.play()
                choice = self.helmets_menu.get_choice().lower()
                self.description = create_prompt(ITEMS[choice]['description'])
                self.helmets_menu.unfocus()
            elif pressed[K_z]:
                self.helmets_menu = None
                self.menu.focus()
                self.state = 'main'
        elif self.state == 'tactics':
            if self.description:
                self.description.handle_input(pressed)
                if (pressed[K_x] or pressed[K_z]) and not self.description.has_more_stuff_to_show():
                    self.description.shutdown()
                    self.description = None
                    self.tactics_submenu.focus()
                return
            if self.tactics_submenu:
                self.tactics_submenu.handle_input(pressed)
                if pressed[K_x]:
                    self.select_sound.play()
                    choice = self.tactics_submenu.get_choice().lower()
                    self.description = create_prompt(TACTICS[choice]['description'])
                    self.tactics_submenu.unfocus()
                elif pressed[K_z]:
                    self.tactics_submenu = None
                    self.tactics_menu.focus()
                return
            self.tactics_menu.handle_input(pressed)
            if pressed[K_x]:
                self.select_sound.play()
                # just grab the slot number off the menu choice
                choice = int(self.tactics_menu.get_choice()[0])
                self.create_tactics_submenu(choice)
            elif pressed[K_z]:
                self.tactics_menu = None
                self.menu.focus()
                self.state = 'main'
        elif self.state == 'items':
            if self.description:
                self.description.handle_input(pressed)
                if (pressed[K_x] or pressed[K_z]) and not self.description.has_more_stuff_to_show():
                    self.description.shutdown()
                    self.description = None
                    self.items_submenu.focus()
                return
            if self.items_submenu:
                self.items_submenu.handle_input(pressed)
                if pressed[K_x]:
                    self.select_sound.play()
                    choice = self.items_submenu.get_choice().lower()
                    self.description = create_prompt(ITEMS[choice]['description'])
                    self.items_submenu.unfocus()
                elif pressed[K_z]:
                    self.items_submenu = None
                    self.items_menu.focus()
                return
            self.items_menu.handle_input(pressed)
            if pressed[K_x]:
                self.select_sound.play()
                # just grab the lower case version of the first word off the choice to get the item type
                choice = self.items_menu.get_choice().split()[0].lower()
                self.create_items_submenu(choice)
            elif pressed[K_z]:
                self.items_menu = None
                self.menu.focus()
                self.state = 'main'

    def create_weapons_menu(self):
        self.state = 'weapons'
        weapons = [
            {
                'name': name.title(),
                'attack_points': info['attack_points'],
            }
            for name, info in ITEMS.items()
            if info['type'] == 'weapon' and self.game.conditions_are_met(info.get('conditions'))
        ]
        sorted_weapons = sorted(weapons, key=lambda k: k['attack_points'])
        if len(sorted_weapons) > 10:
            gridded_weapons = [
                [w['name'] for w in sorted_weapons[0:10]],
                [w['name'] for w in sorted_weapons[10:]],
            ]
            self.weapons_menu = MenuGrid(gridded_weapons, border=True)
        else:
            self.weapons_menu = MenuBox([w['name'] for w in sorted_weapons], border=True)
        self.menu.unfocus()
        self.weapons_menu.focus()

    def create_stats_menu(self):
        self.state = 'stats'
        stats = [{'name': name, 'sort_order': info['sort_order']} for name, info in STATS.items()]
        sorted_stats = sorted(stats, key=lambda k: k['sort_order'])
        self.stats_menu = MenuBox([s['name'] for s in sorted_stats], border=True)
        self.menu.unfocus()
        self.stats_menu.focus()

    def create_body_armor_menu(self):
        self.state = 'body_armor'
        body_armor = [
            {
                'name': name.title(),
                'armor_class': info['armor_class'],
            }
            for name, info in ITEMS.items()
            if info['type'] == 'armor' and self.game.conditions_are_met(info.get('conditions'))
        ]
        sorted_body_armor = sorted(body_armor, key=lambda k: k['armor_class'])
        gridded_body_armor = [
            [b['name'] for b in sorted_body_armor[0:10]],
            [b['name'] for b in sorted_body_armor[10:]],
        ]
        self.body_armor_menu = MenuGrid(gridded_body_armor, border=True)
        self.menu.unfocus()
        self.body_armor_menu.focus()

    def create_helmets_menu(self):
        self.state = 'helmets'
        helmets = [
            {
                'name': name.title(),
                'armor_class': info['armor_class'],
            }
            for name, info in ITEMS.items()
            if info['type'] == 'helmet' and self.game.conditions_are_met(info.get('conditions'))
        ]
        sorted_helmets = [h['name'] for h in sorted(helmets, key=lambda k: k['armor_class'])]
        self.helmets_menu = MenuBox(sorted_helmets, border=True)
        self.menu.unfocus()
        self.helmets_menu.focus()

    def create_tactics_menu(self):
        self.state = 'tactics'
        tactics = [
            [
                '1 FIRE DAMAGE',
                '2 WATER DAMAGE',
                '3 HEALING',
            ],
            [
                '4 DEFENSIVE',
                '5 MISC',
                '6 OFFENSIVE',
            ],
        ]
        self.tactics_menu = MenuGrid(tactics, border=True)
        self.menu.unfocus()
        self.tactics_menu.focus()

    def create_tactics_submenu(self, slot):
        tactics = [
            {
                'name': name.title(),
                'min_level': info['min_level'],
            }
            for name, info in TACTICS.items()
            if info['slot'] == slot
        ]
        sorted_tactics = sorted(tactics, key=lambda k: k['min_level'])
        listed_tactics = [t['name'] for t in sorted_tactics]
        self.tactics_submenu = MenuBox(listed_tactics, border=True)
        self.tactics_menu.unfocus()
        self.tactics_submenu.focus()

    def create_items_menu(self):
        self.state = 'items'
        items = [
            {'name': name, 'sort_order': info['sort_order']}
            for name, info in ITEMS_MENU.items()
            if self.game.conditions_are_met(info.get('conditions'))
        ]
        sorted_items = [i['name'] for i in sorted(items, key=lambda k: k['sort_order'])]
        self.items_menu = MenuBox(sorted_items, border=True)
        self.menu.unfocus()
        self.items_menu.focus()

    def create_items_submenu(self, typ):
        items = [
            name.title()
            for name, info in ITEMS.items()
            if info['type'] == typ and self.game.conditions_are_met(info.get('conditions'))
        ]
        sorted_items = sorted(items)
        if len(sorted_items) > 10:
            gridded_items = [
                sorted_items[0:10],
                sorted_items[10:],
            ]
            self.items_submenu = MenuGrid(gridded_items, border=True)
        else:
            self.items_submenu = MenuBox(sorted_items, border=True)
        self.items_menu.unfocus()
        self.items_submenu.focus()