# -*- coding: UTF-8 -*-

import json
import os
import shutil

import pygame

from constants import ATTACK_POINTS, ARMOR_CLASS, ITEMS, TACTICS

# WARNING: Don't import anything from the rotj repo into here. To avoid circular imports,
# we are restricting this module to only functions that do not depend on any other rotj
# modules except constants. If you need to make a function available to other modules but it also depends
# on a module, perhaps make it in the same module it would depend on. See text.create_prompt
# as an example.

RESOURCES_DIR = 'data'


def unpretty(string_or_strings):
    if isinstance(string_or_strings, str):
        return _unpretty_string(string_or_strings)
    else:
        return [_unpretty_string(s) for s in string_or_strings]


def _unpretty_string(s):
    '''
    Returns version of string with ~ stripped and lower case
    '''
    return s.strip('~').lower()


def get_intelligence(warlord):
    stats = load_stats(warlord)
    return stats['intelligence']


def can_level_up(warlord):
    stats = load_stats(warlord)
    return 'max_soldiers_by_level' in stats and 'max_soldiers' not in stats


def get_tactic_for_level(level):
    for tactic in TACTICS:
        if TACTICS[tactic]['min_level'] == level:
            return tactic
    return None


def get_tactics(stats_or_warlord, level, pretty=True):
    if isinstance(stats_or_warlord, str):
        stats = load_stats(stats_or_warlord)
    else:
        stats = stats_or_warlord
    if 'tactics' in stats:
        tactics = stats['tactics']
    else:
        tactics = []
        for slot in range(1,7):
            tactics.append(_get_max_tactic(intelligence=stats['intelligence'], level=level, slot=slot))
    if pretty:
        return ['{:~<10}'.format(tactic.title().replace(' ', '~')) for tactic in tactics]
    else:
        return tactics


def _get_max_tactic(intelligence=0, level=0, slot=0):
    found_tactic = ""
    min_intelligence = 0
    min_level = 0
    for tactic_name, tactic in TACTICS.items():
        if tactic['slot'] != slot:
            continue
        if tactic['min_intelligence'] > intelligence:
            continue
        if tactic['min_level'] > level:
            continue
        if (
            tactic['min_level'] > min_level
            or (tactic['min_level'] == min_level and tactic['min_intelligence'] > min_intelligence)
        ):
            min_level = tactic['min_level']
            min_intelligence = tactic['min_intelligence']
            found_tactic = tactic_name
    return found_tactic


def get_equip_based_stat_value(stat, equips):
    return sum([ITEMS[equip['name']].get(stat, 0) for equip in equips])


def get_attack_points_by_level(level):
    return ATTACK_POINTS[level]


def get_armor_class_by_level(level):
    return ARMOR_CLASS[level]


def load_stats(name):
    with open('data/stats/{}.json'.format(name)) as f:
        json_data = json.loads(f.read())
    return json_data


def get_max_soldiers(warlord=None, level=None, stats=None, is_ally=True):
    if stats is None:
        with open('data/stats/{}.json'.format(warlord)) as f:
            json_data = json.loads(f.read())
    else:
        json_data = stats
    if is_ally:
        if 'max_soldiers' in json_data:
            soldiers = json_data['max_soldiers']
        else:
            soldiers = json_data['max_soldiers_by_level'][level-1]
    else:
        if 'max_soldiers_by_enemy_level' in json_data:
            soldiers = json_data['max_soldiers_by_enemy_level'].get(str(level)) or json_data['max_soldiers']
        elif 'max_soldiers_by_level' in json_data and level is not None:
            soldiers = json_data['max_soldiers_by_level'][level-1]
        else:
            soldiers = json_data['max_soldiers']
    return soldiers


def hyphenate(text, chars):
    if len(text) > chars:
        return '{}{}\n{}'.format(
            text[0:chars-1],
            '-' if '-' not in text[chars-2:chars] else '',
            text[chars-1:],
        )
    else:
        return text


def get_max_tactical_points(warlord=None, level=None, stats=None):
    if stats is None:
        with open('data/stats/{}.json'.format(warlord)) as f:
            json_data = json.loads(f.read())
    else:
        json_data = stats
    if 'tactical_points_by_level' in json_data and level is not None:
        tactical_points = json_data['tactical_points_by_level'][level-1]
    else:
        tactical_points = json_data['tactical_points']
    return tactical_points


def get_enemy_stats(warlord, level=None):
    with open('data/stats/{}.json'.format(warlord)) as f:
        json_data = json.loads(f.read())
    return {
        'strength': json_data['strength'],
        'defense': json_data['defense'],
        'intelligence': json_data['intelligence'],
        'agility': json_data['agility'],
        'evasion': json_data['evasion'],
        'tactical_points': get_max_tactical_points(stats=json_data, level=level),
        'attack_points': json_data['attack_points'] if not level else get_attack_points_by_level(level),
        'armor_class': json_data['armor_class'] if not level else get_armor_class_by_level(level),
        'tactics': get_tactics(json_data, level or 1),
        'soldiers': get_max_soldiers(stats=json_data, level=level, is_ally=False),
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


def is_quarter_second():
    t = pygame.time.get_ticks()/500.0
    return round(t - int(t)) == 0


def load_save_states():
    states = []
    for x in [1,2,3]:
        try:
            state = load_json_file_if_exists(os.path.join('data', 'state', '{}.json'.format(x)))
        except ValueError:
            state = {'corrupt': True, 'level': -1, 'name': '??'}
        states.append(state)
    return states


def save_game_state(slot, game_state):
    with open('data/state/{}.json'.format(slot), 'w') as f:
        f.write(json.dumps(
            game_state,
            sort_keys = True,
            indent = 2,
            separators=(',', ': '),
        ))


def erase_save_state(slot):
    os.remove('data/state/{}.json'.format(slot))


def create_save_state(slot, name):
    with open('data/state/{}.json'.format(slot), 'w') as f:
        f.write(json.dumps({
            'name': name,
            'level': 0,
            'conditions': [],
            'beaten_path': {},
            'visible_tiles': {},
        }))


def copy_save_state(from_slot, to_slot):
    shutil.copyfile('data/state/{}.json'.format(from_slot), 'data/state/{}.json'.format(to_slot))


def load_json_file_if_exists(filename):
    if os.path.isfile(filename):
        with open(filename) as f:
            json_data = json.loads(f.read())
    else:
        json_data = {}
    return json_data


def sort_items(old_list):
    if len(old_list) == 0:
        return []
    return sorted(old_list, key=_item_sort_key)

def _item_sort_key(item):
    if isinstance(item, str):
        return _item_sort_key_by_name(item)
    return _item_sort_key_by_name(item['name'])


def _item_sort_key_by_name(item):
    by_type = _item_sort_key_by_type(item)
    by_rank = _item_sort_key_by_rank(item)
    return (by_type, by_rank, item)
    

ITEM_TYPES = {
    'save': 0,
    'weapon': 1,
    'armor': 2,
    'helmet': 3,
    'heal': 4,
    'attack': 5,
    'map': 6,
    'passive': 7,
}


def _item_sort_key_by_type(item):
    return ITEM_TYPES[ITEMS[item]['type']]
    

def _item_sort_key_by_rank(item):
    typ = ITEMS[item]['type']
    if typ == 'save':
        return 0
    if typ == 'weapon':
        return -ITEMS[item]['attack_points']
    if typ == 'armor':
        return -ITEMS[item]['armor_class']
    if typ == 'helmet':
        return -ITEMS[item]['armor_class']
    if typ == 'heal':
        return -ITEMS[item].get('healing_points', 0)
    if typ == 'attack':
        return 0
    if typ == 'map':
        return 0
    if typ == 'passive':
        return 0
    return 0