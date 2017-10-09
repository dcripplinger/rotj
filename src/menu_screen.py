# -*- coding: UTF-8 -*-

import pygame
from pygame.locals import *

from constants import GAME_WIDTH
from helpers import load_save_states
from text import MenuBox, TextBox


MAIN_MENU = [
    'GAME START',
    'REGISTER HISTORY BOOK',
    'ERASE HISTORY BOOK',
    'COPY HISTORY BOOK',
]


class MenuScreen(object):
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.screen_state = 'unstarted'
        self.state = load_save_states()
        self.start_prompt = TextBox(
            'Which history do you continue?', width=160, height=80, border=True, double_space=True, appear='scroll',
        )
        self.start_menu = None
        self.main_menu = None
        self.load_main_menu()

    def load_main_menu(self):
        if all(self.state): # if all three save slots are full
            self.main_menu = MenuBox([MAIN_MENU[0], MAIN_MENU[2]])
        elif any(self.state): # if any of the three save slots is populated
            self.main_menu = MenuBox(MAIN_MENU)
        else:
            self.main_menu = MenuBox([MAIN_MENU[1],])

    def load_start_menu(self):
        slots = ['{}~{:~<8}~L{:02}'.format(i+1, slot['name'], slot['level']) for i, slot in enumerate(self.state)]
        self.start_menu = MenuBox(slots)

    def draw(self):
        self.screen.fill((0,0,0))
        if self.screen_state == 'main':
            self.screen.blit(self.main_menu.surface, ((GAME_WIDTH - self.main_menu.get_width())/2, 16))
        elif self.screen_state == 'start':
            self.screen.blit(self.start_prompt.surface, ((GAME_WIDTH - self.start_prompt.width)/2, 160))
            self.screen.blit(self.start_menu.surface, ((GAME_WIDTH - self.start_menu.get_width())/2, 16))

    def update(self, dt):
        if self.screen_state == 'unstarted':
            pygame.mixer.music.load('data/audio/music/menu.wav')
            pygame.mixer.music.play(-1)
            self.screen_state = 'main'
            self.main_menu.focus()
        elif self.screen_state == 'main':
            self.main_menu.update(dt)
        elif self.screen_state == 'start':
            self.start_menu.update(dt)
            self.start_prompt.update(dt)

    def handle_input(self, pressed):
        self.main_menu.handle_input(pressed)
        if self.start_menu:
            self.start_menu.handle_input(pressed)
        if pressed[K_x]:
            if self.main_menu.get_choice() == MAIN_MENU[0]:
                self.screen_state = 'start'
                self.load_start_menu()
                self.start_menu.focus()