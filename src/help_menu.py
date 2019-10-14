# -*- coding: UTF-8 -*-

import os

import pygame
from pygame.locals import *

from constants import BLACK, GAME_WIDTH, GAME_HEIGHT, ITEMS
from text import create_prompt, MenuBox, MenuGrid


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
        ]
        self.menu = MenuBox(items, current_choice=0, border=True, title='Help')
        self.menu.focus()
        self.weapons_menu = None
        self.description = None

    def draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.menu.surface, (0, 0))
        if self.weapons_menu:
            self.screen.blit(self.weapons_menu.surface, (48, 0))
        if self.description:
            self.screen.blit(self.description.surface, (0, 160))

    def update(self, dt):
        if self.description:
            self.description.update(dt)
        elif self.state == 'main':
            self.menu.update(dt)
        elif self.state == 'weapons':
            self.weapons_menu.update(dt)

    def handle_input(self, pressed):
        if self.state == 'main':
            self.menu.handle_input(pressed)
            if pressed[K_x]:
                self.select_sound.play()
                choice = self.menu.get_choice()
                if choice == 'WEAPONS':
                    self.create_weapons_menu()
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

    def create_weapons_menu(self):
        self.state = 'weapons'
        weapons = [
            {
                'name': name.title(),
                'attack_points': info['attack_points'],
            }
            for name, info in ITEMS.items()
            if info['type'] == 'weapon'
        ]
        sorted_weapons = sorted(weapons, key=lambda k: k['attack_points'])
        gridded_weapons = [
            [w['name'] for w in sorted_weapons[0:10]],
            [w['name'] for w in sorted_weapons[10:]],
        ]
        self.weapons_menu = MenuGrid(gridded_weapons, border=True)
        self.menu.unfocus()
        self.weapons_menu.focus()