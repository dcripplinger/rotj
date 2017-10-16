# -*- coding: UTF-8 -*-

import json
import os
import shutil

import pygame

# WARNING: Don't import anything from the rotj repo into here. To avoid circular imports,
# we are restricting this module to only functions that do not depend on any other rotj
# modules. If you need to make a function available to other modules but it also depends
# on a module, perhaps make it in the same module it would depend on. See text.create_prompt
# as an example.

RESOURCES_DIR = 'data'

MAX_SOLDIERS = {
    'moroni': {'by_level': [100,100,100]},
    'teancum': {'by_level': [100,100,100]},
    'amalickiah': {'by_level': [100,100,100]},
}


def get_max_soldiers(warlord, level=None):
    assert level is not None
    return MAX_SOLDIERS[warlord]['by_level'][level]


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


def create_save_state(slot, name):
    with open('data/state/{}.json'.format(slot), 'w') as f:
        f.write(json.dumps({'name': name, 'level': 0, 'slot': int(slot)}))


def copy_save_state(from_slot, to_slot):
    shutil.copyfile('data/state/{}.json'.format(from_slot), 'data/state/{}.json'.format(to_slot))


def load_json_file_if_exists(filename):
    if os.path.isfile(filename):
        with open(filename) as f:
            json_data = json.loads(f.read())
    else:
        json_data = {}
    return json_data
