# -*- coding: UTF-8 -*-

from math import ceil, floor

import pygame

from constants import TILE_SIZE
from helpers import is_half_second


def load_character_images(character):
    path = 'data/images/sprites'
    e_stand = pygame.image.load('{}/{}/e/stand.png'.format(path, character)).convert_alpha()
    e_walk = pygame.image.load('{}/{}/e/walk.png'.format(path, character)).convert_alpha()
    return {
        'e': {
            'stand': e_stand,
            'walk': e_walk,
        },
        'n': {
            'stand': pygame.image.load('{}/{}/n/stand.png'.format(path, character)).convert_alpha(),
            'walk': pygame.image.load('{}/{}/n/walk.png'.format(path, character)).convert_alpha(),
        },
        's': {
            'stand': pygame.image.load('{}/{}/s/stand.png'.format(path, character)).convert_alpha(),
            'walk': pygame.image.load('{}/{}/s/walk.png'.format(path, character)).convert_alpha(),
        },
        'w': {
            'stand': pygame.transform.flip(e_stand, True, False),
            'walk': pygame.transform.flip(e_walk, True, False),
        },
    }


class Sprite(pygame.sprite.Sprite):
    def __init__(self, tmx_data, game, character, position, speed=10, direction='s', walking=False):
        super(Sprite, self).__init__()
        self.position = position
        self.old_position = self.position
        self.tmx_data = tmx_data
        self.velocity = self.velocity_from_speed_direction_walking(speed, direction, walking)
        self.game = game
        self.character = character
        # tiles per second the character moves when moving. Differs from velocity, which is a combination of speed and direction.
        self.speed = speed
        self.images = load_character_images(character)
        self.direction = direction
        self.image = self.images[self.direction]['stand']

        self.rect = self.image.get_rect()
        self.rect.topleft = [floor(TILE_SIZE*self.position[0]), floor(TILE_SIZE*self.position[1])]

    def velocity_from_speed_direction_walking(self, speed, direction, walking=True):
        if not walking:
            return [0,0]
        if direction == 'n' and not self.is_a_wall([0, -1]):
            return [0, -speed]
        elif direction == 's' and not self.is_a_wall([0, 1]):
            return [0, speed]
        elif direction == 'w' and not self.is_a_wall([-1, 0]):
            return [-speed, 0]
        elif direction == 'e' and not self.is_a_wall([1, 0]):
            return [speed, 0]
        else:
            return [0, 0]

    def update(self, dt):
        self.update_position(dt)
        self.update_image()

    def update_image(self):
        self.image = self.images[self.direction]['stand' if is_half_second() else 'walk']

    def move(self, direction):
        '''
        Moves sprite in direction if not already in a move transition. Returns true if actually starts a move of one tile unit.
        '''
        if self.velocity != [0, 0]:
            return False
        if direction is None:
            self.velocity = [0,0]
            return False
        self.direction = direction
        self.velocity = self.velocity_from_speed_direction_walking(self.speed, self.direction)
        return True

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
        pass # we use this in the class Hero (which inherits from here) to teleport to different maps

    def is_a_wall(self, offset):
        x = self.position[0] + offset[0]
        y = self.position[1] + offset[1]
        if x < 0 or y < 0 or x >= self.tmx_data.width or y >= self.tmx_data.height:
            return True
        props = self.tmx_data.get_tile_properties(x, y, 0) or {}
        return props.get('wall') == 'true'
