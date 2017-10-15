# -*- coding: UTF-8 -*-

from math import ceil, floor

import pygame

from constants import TILE_SIZE
from helpers import is_half_second

HERO_MOVE_SPEED = 10  # tiles per second.


class Hero(pygame.sprite.Sprite):
    def __init__(self, tmx_data, cells, game):
        pygame.sprite.Sprite.__init__(self)
        self.velocity = [0.0, 0.0]
        self.position = [13.0, 12.0]
        self.old_position = self.position
        self.tmx_data = tmx_data
        self.cells = cells
        self.game = game

        side_stand = pygame.image.load('data/images/sprites/moroni/e/stand.png').convert_alpha()
        side_walk = pygame.image.load('data/images/sprites/moroni/e/walk.png').convert_alpha()
        self.images = {
            'e': {
                'stand': side_stand,
                'walk': side_walk,
            },
            'n': {
                'stand': pygame.image.load('data/images/sprites/moroni/n/stand.png').convert_alpha(),
                'walk': pygame.image.load('data/images/sprites/moroni/n/walk.png').convert_alpha(),
            },
            's': {
                'stand': pygame.image.load('data/images/sprites/moroni/s/stand.png').convert_alpha(),
                'walk': pygame.image.load('data/images/sprites/moroni/s/walk.png').convert_alpha(),
            },
            'w': {
                'stand': pygame.transform.flip(side_stand, True, False),
                'walk': pygame.transform.flip(side_walk, True, False),
            },
        }
        self.direction = 's'
        self.image = self.images[self.direction]['stand']
        self.walking = True

        self.rect = self.image.get_rect()
        self.rect.topleft = [floor(TILE_SIZE*self.position[0]), floor(TILE_SIZE*self.position[1])]

    def update(self, dt):
        self.update_position(dt)
        self.update_image()

    def update_image(self):
        stand_walk = 'stand' if is_half_second() else 'walk'
        self.image = self.images[self.direction][stand_walk]

    def move(self, direction):
        if self.velocity != [0, 0]:
            return
        if direction is None:
            self.velocity = [0,0]
            return
        self.direction = direction
        if direction == 'n' and not self.is_a_wall([0, -1]):
            self.velocity = [0, -HERO_MOVE_SPEED]
        elif direction == 's' and not self.is_a_wall([0, 1]):
            self.velocity = [0, HERO_MOVE_SPEED]
        elif direction == 'w' and not self.is_a_wall([-1, 0]):
            self.velocity = [-HERO_MOVE_SPEED, 0]
        elif direction == 'e' and not self.is_a_wall([1, 0]):
            self.velocity = [HERO_MOVE_SPEED, 0]
        else:
            self.velocity = [0, 0]

    def update_position(self, dt):
        self.old_position = self.position[:]

        self.position[0] += self.velocity[0] * dt
        if self.velocity[0] > 0 and floor(self.position[0]) != floor(self.old_position[0]):
            self.position[0] = floor(self.position[0])
            self.velocity[0] = 0
            self.handle_cell()
        elif self.velocity[0] < 0 and ceil(self.position[0]) != ceil(self.old_position[0]):
            self.position[0] = ceil(self.position[0])
            self.velocity[0] = 0
            self.handle_cell()

        self.position[1] += self.velocity[1] * dt
        if self.velocity[1] > 0 and floor(self.position[1]) != floor(self.old_position[1]):
            self.position[1] = floor(self.position[1])
            self.velocity[1] = 0
            self.handle_cell()
        elif self.velocity[1] < 0 and ceil(self.position[1]) != ceil(self.old_position[1]):
            self.position[1] = ceil(self.position[1])
            self.velocity[1] = 0
            self.handle_cell()

        self.rect.topleft = [floor(TILE_SIZE*self.position[0]), floor(TILE_SIZE*self.position[1])]

    def handle_cell(self):
        props = self.cells.get(tuple(self.position))
        if not props:
            return
        teleport = props.get('teleport')
        if teleport:
            new_map = teleport.get('map')
            new_direction = teleport.get('direction', self.direction)
            if new_map:
                self.game.set_current_map(new_map, [teleport['x'], teleport['y']], new_direction)
            else:
                self.position = [teleport['x'], teleport['y']]
                self.direction = new_direction

    def is_a_wall(self, offset):
        x = self.position[0] + offset[0]
        y = self.position[1] + offset[1]
        if x < 0 or y < 0 or x >= self.tmx_data.width or y >= self.tmx_data.height:
            return True
        props = self.tmx_data.get_tile_properties(x, y, 0) or {}
        return props.get('wall') == 'true'
