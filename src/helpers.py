# -*- coding: UTF-8 -*-

import json
import os
import shutil

import pygame

from constants import ITEMS

# WARNING: Don't import anything from the rotj repo into here. To avoid circular imports,
# we are restricting this module to only functions that do not depend on any other rotj
# modules. If you need to make a function available to other modules but it also depends
# on a module, perhaps make it in the same module it would depend on. See text.create_prompt
# as an example.

RESOURCES_DIR = 'data'


def get_tactics(stats, level, pretty=True):
    if 'tactics_by_level' in stats:
        tactics = stats['tactics_by_level'][min(level, len(stats['tactics_by_level'])) - 1]
    else:
        tactics = stats['tactics']
    if pretty:
        return ['{:~<10}'.format(tactic.title().replace(' ', '~')) for tactic in tactics]
    else:
        return tactics


def get_equip_based_stat_value(stat, equips):
    return sum([ITEMS[equip['name']].get(stat, 0) for equip in equips])


def load_stats(name):
    with open('data/stats/{}.json'.format(name)) as f:
        json_data = json.loads(f.read())
    return json_data


def get_max_soldiers(warlord, level=None):
    assert level is not None
    with open('data/stats/{}.json'.format(warlord)) as f:
        json_data = json.loads(f.read())
    if 'max_soldiers_by_level' in json_data:
        soldiers = json_data['max_soldiers_by_level'][level-1]
    else:
        soldiers = json_data['max_soldiers']
    return soldiers


def get_max_tactical_points(warlord, level=None):
    assert level is not None
    with open('data/stats/{}.json'.format(warlord)) as f:
        json_data = json.loads(f.read())
    if 'tactical_points_by_level' in json_data:
        tactical_points = json_data['tactical_points_by_level'][level-1]
    else:
        tactical_points = json_data['tactical_points']
    return tactical_points


def get_enemy_stats(warlord):
    with open('data/stats/{}.json'.format(warlord)) as f:
        json_data = json.loads(f.read())
    return {
        'strength': json_data['strength'],
        'defense': json_data['defense'],
        'intelligence': json_data['intelligence'],
        'agility': json_data['agility'],
        'evasion': json_data['evasion'],
        'tactical_points': json_data['tactical_points'],
        'attack_points': json_data['attack_points'],
        'armor_class': json_data['armor_class'],
        'tactics': json_data['tactics'],
        'soldiers': json_data['soldiers'],
    }


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
