# -*- coding: UTF-8 -*-

import pygame

from constants import GAME_WIDTH
from helpers import load_state
from text import MenuBox


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
        self.started = False
        self.state = load_state()
        self.load_main_menu()

    def load_main_menu(self):
        if all(self.state): # if all three save slots are full
            self.main_menu = MenuBox([MAIN_MENU[0], MAIN_MENU[2]])
        elif any(self.state): # if any of the three save slots is populated
            self.main_menu = MenuBox(MAIN_MENU)
        else:
            self.main_menu = MenuBox([MAIN_MENU[1],])

    def draw(self):
        self.screen.fill((0,0,0))
        self.screen.blit(self.main_menu.surface, ((GAME_WIDTH - self.main_menu.get_width())/2, 16))

    def update(self, dt):
        if not self.started:
            pygame.mixer.music.load('data/audio/music/menu.wav')
            pygame.mixer.music.play(-1)
            self.started = True
            self.main_menu.focus()
        self.main_menu.update(dt)

    def handle_input(self, pressed):
        self.main_menu.handle_input(pressed)