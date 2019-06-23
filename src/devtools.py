# -*- coding: UTF-8 -*-

import os

import pygame
from pygame.locals import *

from text import MenuBox


# This returns the string that represents an on or off switch.
# Here's how it works:
# I drew a couple of 16x8 images of an off switch and an on switch.
# I then cut those images in half and saved them in the font directory.
# The off switch is colored white and the on switch is colored green
# to make it more obvious which means a feature switch is off vs on.
# Finally, I mapped the following characters to those images:
# "[" left_off_switch.png
# "]" right_off_switch.png
# "<" left_on_switch.png
# ">" right_on_switch.png
# Thus, all this function has to do is return the correct pair of
# characters based on the argument `on`.
def _get_switch_string(on):
    if on:
        return '<>'
    else:
        return '[]'


class Devtools(object):
    def __init__(self, game):
        self.game = game
        self.make_menu(0)
        self.select_sound = pygame.mixer.Sound(os.path.join('data', 'audio', 'select.wav'))
        
    def make_menu(self, current_choice):
        items = ['{} {}'.format(_get_switch_string(on), name) for name, on in self.game.devtools.items()]
        self.menu = MenuBox(items, current_choice=current_choice)
        self.menu.focus()

    def get_surface(self):
        return self.menu.surface

    def update(self, dt):
        self.menu.update(dt)

    def handle_input(self, pressed):
        self.menu.handle_input(pressed)
        if pressed[K_x]:
            self.select_sound.play()
            # crop the feature switch image here so we just have the feature switch name
            choice = self.menu.get_choice()[3:]
            self.game.devtools[choice] = not self.game.devtools[choice]
            self.make_menu(self.menu.current_choice)
