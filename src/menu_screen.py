# -*- coding: UTF-8 -*-

import pygame

from constants import GAME_WIDTH
from text import MenuBox


class MenuScreen(object):
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.started = False
        self.main_menu = MenuBox(['choice 1', 'choice 2'])

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