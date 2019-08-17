# -*- coding: UTF-8 -*-

from math import ceil, floor
import os
import random

import pygame

from constants import TILE_SIZE
from helpers import is_half_second


def load_character_images(character):
    path = 'data/images/sprites'
    e_stand = pygame.image.load('{}/{}/e/stand.png'.format(path, character)).convert_alpha()
    e_walk = pygame.image.load('{}/{}/e/walk.png'.format(path, character)).convert_alpha()
    if os.path.isdir('{}/{}/w'.format(path, character)):
        w_stand = pygame.image.load('{}/{}/w/stand.png'.format(path, character)).convert_alpha()
        w_walk = pygame.image.load('{}/{}/w/walk.png'.format(path, character)).convert_alpha()
    else:
        w_stand = pygame.transform.flip(e_stand, True, False)
        w_walk = pygame.transform.flip(e_walk, True, False)
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
            'stand': w_stand,
            'walk': w_walk,
        },
    }


class Sprite(pygame.sprite.Sprite):
    def __init__(self, tmx_data, game, character, position, speed=10, direction='s', walking=False, follower=None, tiled_map=None):
        super(Sprite, self).__init__()
        self.tiled_map = tiled_map
        self.name = character
        self.position = list(position)
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
        self.follower = follower
        self.hitting_wall = False # actually only needed for Hero

    def velocity_from_speed_direction_walking(self, speed, direction, walking=True, ignore_walls=False):
        if not walking:
            return [0,0]
        if direction == 'n' and (ignore_walls or not self.is_a_wall([0, -1])):
            return [0, -speed]
        elif direction == 's' and (ignore_walls or not self.is_a_wall([0, 1])):
            return [0, speed]
        elif direction == 'w' and (ignore_walls or not self.is_a_wall([-1, 0])):
            return [-speed, 0]
        elif direction == 'e' and (ignore_walls or not self.is_a_wall([1, 0])):
            return [speed, 0]
        else:
            return [0, 0]

    def update(self, dt):
        self.update_position(dt)
        self.update_image()

    def update_image(self):
        self.image = self.images[self.direction]['stand' if is_half_second() else 'walk']

    def move(self, direction, ignore_walls=False):
        '''
        Moves sprite in direction if not already in a move transition. Returns true if actually starts a move of one tile unit.
        '''
        if self.velocity != [0, 0]:
            return False
        if direction is None:
            self.velocity = [0,0]
            return False
        self.direction = direction
        self.velocity = self.velocity_from_speed_direction_walking(self.speed, self.direction, ignore_walls=ignore_walls)
        moved = self.velocity != [0,0]
        if self.follower and moved: # the leader is actually starting a move to a new tile
            self.follower.move_to(self.position)
        return moved

    def move_to(self, position, ignore_walls=False):
        if position[0] > self.position[0]:
            direction = 'e'
        elif position[0] < self.position[0]:
            direction = 'w'
        elif position[1] > self.position[1]:
            direction = 's'
        elif position[1] < self.position[1]:
            direction = 'n'
        else:
            direction = None
        return self.move(direction, ignore_walls=ignore_walls)

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

    def is_a_wall(self, offset, update_hitting_wall=True):
        x = self.position[0] + offset[0]
        y = self.position[1] + offset[1]
        if x < 0 or y < 0 or x >= self.tmx_data.width or y >= self.tmx_data.height:
            return True
        props = self.tmx_data.get_tile_properties(x, y, 0) or {}
        is_map_wall = props.get('wall') == 'true'
        is_ai_sprite = False
        if self.tiled_map:
            is_ai_sprite = True if self.tiled_map.ai_sprites.get((x,y)) else False
        is_a_wall = is_map_wall or is_ai_sprite
        if update_hitting_wall:
            self.hitting_wall = is_a_wall
        return is_a_wall


class AiSprite(Sprite):
    def __init__(
        self, tmx_data, game, character, position, speed=5, direction='s', walking=False, wander=False, follower=None,
        tiled_map=None, dialog=None, walk=None,
    ):
        super(AiSprite, self).__init__(tmx_data, game, character, position, speed, direction, walking, follower, tiled_map)
        self.wander = wander
        self.elapsed_time = 0.0
        if self.tiled_map:
            self.tiled_map.ai_sprites[tuple(position)] = self
        self.dialog = dialog
        self.walk = walk

    def is_a_wall(self, offset, update_hitting_wall=True):
        if super(AiSprite, self).is_a_wall(offset, update_hitting_wall):
            return True
        x = self.position[0] + offset[0]
        y = self.position[1] + offset[1]
        if self.tiled_map.hero.position == [x,y]:
            return True
        if self.tiled_map.follower_one and self.tiled_map.follower_one.position == [x,y]:
            return True
        if self.tiled_map.follower_two and self.tiled_map.follower_two.position == [x,y]:
            return True
        return False

    def update(self, dt):
        self.elapsed_time += dt
        if self.character == 'nehor':
            cutoff = .02 # nehor moves fast
        elif self.walk:
            cutoff = 0 # if self.walk is set, they constantly move (move_maybe() will check velocity in this case)
        else:
            cutoff = 1 # everyone else possibly moves every second
        if self.elapsed_time > cutoff:
            self.elapsed_time -= cutoff
            self.move_maybe()
        super(AiSprite, self).update(dt)

    def move_maybe(self):
        moved = None
        if self.walk and self.game.conditions_are_met(self.walk.get('conditions')) and self.velocity == [0, 0]:
            destination = [self.walk['to']['x'], self.walk['to']['y']]
            if self.position == destination:
                if 'game_state_action' in self.walk:
                    self.game.set_game_state_condition(self.walk['game_state_action'])
                if 'reset' in self.walk:
                    self.position = [self.walk['reset']['x'], self.walk['reset']['y']]
                else:
                    self.walk = None
            else:
                moved = self.move_to(destination, ignore_walls=True)
                direction = self.direction
        else:
            if not self.wander:
                return
            if self.tiled_map.map_menu: # don't do random movements if the menu is open
                return
            # every time we might move the ai_sprite, the probability is 0.33 unless nehor
            if random.random() < 0.33 or self.character == 'nehor':
                direction = random.choice(['n', 's', 'e', 'w'])
                moved = self.move(direction)

        if moved:
            self.tiled_map.ai_sprites[self.get_new_pos_from_direction(direction)] = self
            try:
                del self.tiled_map.ai_sprites[tuple(self.position)]
            except KeyError: # I had an error once where mysteriously the key wasn't there.
                pass

    def get_new_pos_from_direction(self, direction):
        if direction == 'n':
            return (self.position[0], self.position[1]-1)
        elif direction == 's':
            return (self.position[0], self.position[1]+1)
        elif direction == 'e':
            return (self.position[0]+1, self.position[1])
        elif direction == 'w':
            return (self.position[0]-1, self.position[1])
