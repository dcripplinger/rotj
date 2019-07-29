# -*- coding: UTF-8 -*-

import pygame
from pygame.locals import *
import pyscroll
from pytmx.util_pygame import load_pygame

from constants import BLACK, BLUE, ORANGE, RED, TILE_SIZE, WHITE
from helpers import get_map_filename, is_quarter_second, load_image
from sprite import AiSprite

XMIN = 7
XMAX = 292
YMIN = 7
YMAX = 392
SPEED = 100 # tiles per second when moving
MAP_WIDTH = 300
MAP_HEIGHT = 400

class PauseMap(object):
    def __init__(self, screen, game, position):
        # init basic values
        self.screen = screen
        self.game = game
        self.player_position = list(position)
        self.bound_position(position)
        self.direction = [0, 0]
        map_filename = get_map_filename('overworld_map.tmx')
        self.tmx_data = load_pygame(map_filename)

        # set all visible tiles to transparent
        visible_minitiles = [[0] * 60 for i in range(80)]
        layer = self.tmx_data.get_layer_by_name('blackout')
        tileset = self.tmx_data.tilesets[2]
        for tile in self.game.game_state['beaten_path'].keys():
            X, Y = [int(i) for i in tile.split()]
            for x in range(X-8, X+9):
                if x <= 0 or x >= MAP_WIDTH:
                    continue
                for y in range(Y-7, Y+8):
                    if y <= 0 or y >= MAP_HEIGHT:
                        continue
                    mini_x, mini_y = self.mini_coordinates((x, y))
                    # Here, mini coordinates are 0-indexed.
                    mini_x -= 1
                    mini_y -= 1
                    visible_minitiles[mini_y][mini_x] += 1
                    # This is a hack that only works if we leave the file overworld_map.tmx alone.
                    # Pytmx will come up with its own gids for tiles and not use the ones in the tmx file.
                    # If overworld_map.tmx does not have the single transparent tile in the "blackout" layer,
                    # that type of tile never gets assigned the gid of 344.
                    # Here is an explanation of what exactly pytmx is doing and why:
                    # https://github.com/bitcraft/PyTMX/blob/3fb9788dd66ecfd0c8fa0e9f38c582337d89e1d9/pytmx/pytmx.py#L330
                    layer.data[y][x] = 344

        # init pyscroll regular map
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.screen.get_size())
        self.map_layer.zoom = 1
        self.group = pyscroll.group.PyscrollGroup(map_layer=self.map_layer)
                    
        # Mark spot where player currently is
        you_are_here = AiSprite(tmx_data=self.tmx_data, game=game, character='you_are_here', position=position, direction='s', wander=False)
        self.group.add(you_are_here)

        # init pyscroll minimap
        self.minimap = load_image('minimap.png')
        for x in range(60):
            for y in range(80):
                # Mark the minitile as black if there are 0 to 12 visible tiles corresponding to it.
                # This is because there is a maximum of 25 tiles that can get mapped to a minitile.
                if visible_minitiles[y][x] < 13:
                    self.minimap.set_at((x, y), BLACK)

    def bound_position(self, position):
        self.position = [min(XMAX, max(XMIN, position[0])), min(YMAX, max(YMIN, position[1]))]

    def get_group_center(self):
        return [int((coord + 0.5) * TILE_SIZE) for coord in self.position]

    def mini_coordinates(self, coordinates):
        mini_x = int(round(coordinates[0] * 1.0 / MAP_WIDTH * 60))
        mini_y = int(round(coordinates[1] * 1.0 / MAP_HEIGHT * 80))
        if mini_x < 1:
            mini_x = 1
        if mini_y < 1:
            mini_y = 1
        if mini_x > 60:
            mini_x = 60
        if mini_y > 80:
            mini_y = 80
        return mini_x, mini_y
    
    def draw(self):
        self.group.center(self.get_group_center())
        self.group.draw(self.screen)
        pygame.draw.rect(self.screen, WHITE, (0, 0, 62, 82), 1) # border around minimap
        self.screen.blit(self.minimap, (1, 1))

        # Draw the highlighter box over the minimap
        # Note: x and y are -1 of below calculation for the highlighter being a 3x3 box (need to find top left corner, not center),
        #       but they are +1 of below calculation for blitting it on the whole screen, while the minimap is offset by one (due to the border).
        #       Thus, it evens out. But I wanted to document what was going on.
        x, y = self.mini_coordinates(self.position)
        highlighter_color = RED if is_quarter_second() else ORANGE
        pygame.draw.rect(self.screen, highlighter_color, (x, y, 3, 3), 1)

        # Draw a current position dot on the minimap
        x, y = self.mini_coordinates(self.player_position)
        current_dot_color = BLUE if is_quarter_second() else WHITE
        pygame.draw.rect(self.screen, current_dot_color, (x+1, y+1, 1, 1), 1)

    def update(self, dt):
        self.group.update(dt)
        self.position[0] += self.direction[0] * SPEED * dt
        self.position[1] += self.direction[1] * SPEED * dt
        self.bound_position(self.position)
        self.direction = [0, 0] # Keep the map from moving forever

    def handle_input(self, pressed):
        if pressed[K_UP]:
            self.direction = [0, -1]
        elif pressed[K_DOWN]:
            self.direction = [0, 1]
        elif pressed[K_LEFT]:
            self.direction = [-1, 0]
        elif pressed[K_RIGHT]:
            self.direction = [1, 0]
        else:
            self.direction = [0, 0]

        if pressed[K_z]:
            self.game.close_pause_map()
        elif pressed[K_RETURN]:
            self.game.close_pause_menu()
