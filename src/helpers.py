# -*- coding: UTF-8 -*-

import json
import os

import pygame

RESOURCES_DIR = 'data'


def load_image(filename):
    return pygame.image.load(os.path.join(RESOURCES_DIR, "images", filename))


def get_map_filename(filename):
    return os.path.join(RESOURCES_DIR, "maps", filename)


def is_half_second():
    '''
    Returns if the game time is in the bottom half of a second.
    '''
    t = pygame.time.get_ticks()/1000.0
    return round(t - int(t)) == 0


def load_save_states():
    return [load_json_file_if_exists('data/state/{}.json'.format(x)) for x in [1,2,3]]


def erase_save_state(slot):
    os.remove('data/state/{}.json'.format(slot))


def load_json_file_if_exists(filename):
    if os.path.isfile(filename):
        with open(filename) as f:
            json_data = json.loads(f.read())
    else:
        json_data = {}
    return json_data
