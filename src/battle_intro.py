# -*- coding: UTF-8 -*-

import os

import pygame
from pygame.locals import *

from constants import GAME_HEIGHT, GAME_WIDTH, WHITE
from helpers import load_image
from text import create_prompt

COUNTER_SEQUENCE = [K_UP, K_UP, K_DOWN, K_DOWN, K_LEFT, K_RIGHT, K_UP, K_DOWN]


class BattleIntro(object):
    def __init__(self, screen, warlord, text, intro_type='regular'):
        self.screen = screen
        self.portrait = load_image(os.path.join('portraits', '{}.png'.format(warlord)))
        self.dialog = create_prompt(text)
        self.intro_type = intro_type
        self.timer = (
            1 if intro_type == 'zemnarihah1'
            else 5 if intro_type == 'zemnarihah2'
            else 0
        )
        self.flashing = False
        self.white_box = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        self.white_box.fill(WHITE)
        self.flashing_timer = 1.5
        self.countered = False
        self.second_dialog = False
        self._is_finished = False
        self.number_right = 0
        self.tactic_sound = pygame.mixer.Sound(os.path.join('data', 'audio', 'tactic.wav'))

    def draw(self):
        self.screen.blit(self.dialog.surface, (0, 144))
        self.screen.blit(self.portrait, (GAME_WIDTH-64, 160))
        if self.flashing:
            self.screen.blit(self.white_box, (0,0))

    def update(self, dt):
        # make short blurbs stop beeping forever
        if not self.dialog.has_more_stuff_to_show():
            self.dialog.shutdown()

        if self.dialog.has_more_stuff_to_show():
            self.dialog.update(dt)
        elif self.timer and not self.countered and not self.second_dialog:
            self.timer -= dt
            if self.timer <= 0:
                self.timer = 0
                self.tactic_sound.play()
        elif self.countered and not self.second_dialog:
            self.dialog = create_prompt('My thunder failed?! Then brute force will suffice.')
            self.second_dialog = True
        elif self.intro_type in ['zemnarihah1', 'zemnarihah2'] and self.flashing_timer and not self.second_dialog:
            self.flashing = not self.flashing
            self.flashing_timer -= dt
            if self.flashing_timer <= 0:
                self.flashing_timer = 0
        else:
            self._is_finished = True

    def handle_input(self, pressed):
        if self.dialog.has_more_stuff_to_show():
            self.dialog.handle_input(pressed)
        elif self.timer and not self.countered and self.intro_type == 'zemnarihah2' and self.game.conditions_are_met('learned_thunder_counter'):
            if pressed[COUNTER_SEQUENCE[self.number_right]]:
                self.number_right += 1
                if self.number_right == 8:
                    self.countered = True
            elif (
                pressed[K_DOWN]
                or pressed[K_LEFT]
                or pressed[K_RIGHT]
                or pressed[K_UP]
                or pressed[K_x]
                or pressed[K_z]
                or pressed[K_RSHIFT]
                or pressed[K_RETURN]
            ):
                self.number_right = 0

    def is_finished(self):
        return self._is_finished

    def got_thundered(self):
        return (
            self.intro_type in ['zemnarihah1', 'zemnarihah2']
            and not self.timer
            and self._is_finished
            and not self.countered
        )
