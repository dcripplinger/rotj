# -*- coding: UTF-8 -*-

import pygame
from pygame.locals import *
import pyscroll
from pytmx.util_pygame import load_pygame

from helpers import (
    get_map_filename
)
from sprite import Sprite
from text import create_prompt

class Cutscene(object):
    def __init__(self, game, screen, scene):
        self.game = game
        self.screen = screen
        self.scene = scene
        map_filename = get_map_filename(
            '_palace.tmx' if scene == 0 else 'house_of_moroni.tmx' if scene == 1 else '_palace.tmx'
        )
        self.tmx_data = load_pygame(map_filename)
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.screen.get_size())
        self.map_layer.zoom = 1
        self.group = pyscroll.group.PyscrollGroup(map_layer=self.map_layer)
        if scene == 1:
            self.sprite = Sprite(self.tmx_data, self.game, 'moroni', [19, 13], direction='w')
            self.group.add(self.sprite)
            dialog_text = "Moroni retired and went to his house to spend the remainder of his days."
            self.timer = 2
        elif scene == 2:
            self.sprite = Sprite(self.tmx_data, self.game, 'pahoran', [17, 14], direction='s')
            self.group.add(self.sprite)
            dialog_text = "Pahoran returned to the judgment seat to regulate the laws of the land."
            self.timer = 2
        else:
            self.sprite = None
            dialog_text = "When Moroni saw that Teancum had died, he was exceedingly sorrowful. For Teancum had been a true friend of liberty. But now Teancum was dead, and had gone the way of the whole earth."
            self.timer = 2
        self.dialog = create_prompt(dialog_text)
        self.state = 'wait'

    def get_group_center(self):
        if self.scene == 0:
            return (0, 768)
        if self.scene == 1:
            return (240, 240)
        return (272, 256) # scene 2

    def draw(self):
        self.group.center(self.get_group_center())
        self.group.draw(self.screen)
        if self.state == 'dialog':
            self.screen.blit(self.dialog.surface, (0, 160))

    def update(self, dt):
        if self.state == 'wait':
            self.timer -= dt
            if self.timer <= 0:
                self.state = 'dialog'
        elif self.state == 'dialog':
            self.dialog.update(dt)
        if self.sprite:
            self.sprite.update(dt)

    def handle_input(self, pressed):
        if self.state == 'dialog':
            self.dialog.handle_input(pressed)
        if not self.dialog.has_more_stuff_to_show() and pressed[K_x]:
            self.game.set_screen_state('fade_cutscene')
            if self.scene == 2:
                pygame.mixer.music.fadeout(2000)