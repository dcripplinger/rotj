# -*- coding: UTF-8 -*-

from math import ceil, floor

import pygame

from constants import TILE_SIZE
from helpers import is_half_second
from sprite import Sprite


class Hero(Sprite):
    def __init__(
        self, tmx_data, game, character, position, speed=10, direction='s', walking=False, cells=None, follower=None, tiled_map=None,
    ):
        super(Hero, self).__init__(tmx_data, game, character, position, speed, direction, walking, follower, tiled_map)
        self.cells = cells
        self.wall_sound = pygame.mixer.Sound('data/audio/wall.wav')
        self.playing_wall_sound = False
        self.playing_wall_sound_time_elapsed = 0.0

    def handle_cell(self):
        props = self.cells.get(tuple(self.position))
        if not props:
            return
        teleport = props.get('teleport')
        if teleport:
            if isinstance(teleport, dict):
                teleports = [teleport]
            else:
                teleports = teleport
            for tele in teleports:
                if 'conditions' in tele and not self.game.conditions_are_met(tele['conditions']):
                    continue
                new_map = tele.get('map')
                new_direction = tele.get('direction', self.direction)
                if new_map:
                    self.game.set_current_map(new_map, [tele['x'], tele['y']], new_direction)
                else:
                    self.tiled_map.load_company_sprites([tele['x'], tele['y']], new_direction, 'under')
                break

    def update(self, dt):
        super(Hero, self).update(dt)
        if self.playing_wall_sound:
            self.playing_wall_sound_time_elapsed += dt
            if self.playing_wall_sound_time_elapsed > 0.25:
                self.playing_wall_sound_time_elapsed = 0.0
                self.playing_wall_sound = False
        elif self.hitting_wall:
            self.playing_wall_sound = True
            self.wall_sound.play()
            self.hitting_wall = False # this is for when we don't change direction, we just stop trying to move
