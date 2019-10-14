# -*- coding: UTF-8 -*-

import os

import pygame
from pygame.locals import *

from constants import BLACK, GAME_WIDTH, GAME_HEIGHT, ITEMS
from text import MenuBox, MenuGrid


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

    def draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.menu.surface, (0, 0))
        if self.weapons_menu:
            self.screen.blit(self.weapons_menu.surface, (48, 0))

    def update(self, dt):
        if self.state == 'main':
            self.menu.update(dt)
        elif self.state == 'weapons':
            self.weapons_menu.update(dt)

    def handle_input(self, pressed):
        if pressed[K_x]:
            self.select_sound.play()
        if self.state == 'main':
            self.menu.handle_input(pressed)
            if pressed[K_x]:
                choice = self.menu.get_choice()
                if choice == 'WEAPONS':
                    self.create_weapons_menu()
        elif self.state == 'weapons':
            self.weapons_menu.handle_input(pressed)
            if pressed[K_x]:
                choice = self.weapons_menu.get_choice().lower()
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