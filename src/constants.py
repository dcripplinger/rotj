# -*- coding: UTF-8 -*-

from pygame.locals import *

# colors
WHITE = (255,255,255)
BLACK = (0,0,0)
COPPER = (164, 82, 41)

# sizes
TILE_SIZE = 16 # pixels
GAME_WIDTH = 256 # pixels (before scaling)
GAME_HEIGHT = 240 # pixels (before scaling)

MAP_NAMES = [
    'overworld',
    'tunnels_of_the_north',
    'cave_of_gadianton',
    'sierra_pass',
    'cavity_of_a_rock',
    'passage_to_gid',
    'house_of_moroni',
    'melek',
    'melek_empty_house',
]

CAVE_MUSIC = {
    'intro': 'data/audio/music/cave_intro.wav',
    'repeat': 'data/audio/music/cave.wav',
}

SHOP_MUSIC = {
    'intro': None,
    'repeat': 'data/audio/music/shop.wav',
}

MAP_MUSIC = {
    'melek': {
        'intro': None,
        'repeat': 'data/audio/music/menu.wav',
    },
    'house_of_moroni': SHOP_MUSIC,
    'melek_empty_house': SHOP_MUSIC,
    'overworld': {
        'intro': None,
        'repeat': 'data/audio/music/march.wav',
    },
    'tunnels_of_the_north': CAVE_MUSIC,
    'cave_of_gadianton': CAVE_MUSIC,
    'sierra_pass': CAVE_MUSIC,
    'cavity_of_a_rock': CAVE_MUSIC,
    'passage_to_gid': CAVE_MUSIC,
}

ITEMS = {
    # weapons
    'dagger': {
        'attack_points': 10,
        'equip_type': 'weapon',
        'cost': 50,
    },
    'flail': {
        'attack_points': 15,
        'equip_type': 'weapon',
        'cost': 100,
    },

    # armor
    'robe': {
        'armor_class': 20,
        'equip_type': 'armor',
        'cost': 100,
    },

    # helmets
    'bandana': {
        'armor_class': 10,
        'equip_type': 'helmet',
        'cost': 50,
    },

    # company items (elixirs, resurrect, etc)
    'elixir~a': {
        'map_usage': 'company', # means you can use the item on a member of the company (aka traveling party)
        'healing_points': 100, # exactly 100 soldiers recover strength
        'cost': 20,
    },
    'elixir~b': {
        'map_usage': 'company',
        'healing_points': 500,
        'cost': 50,
    },
    'elixir~c': {
        'map_usage': 'company',
        'healing_points': 1000,
        'cost': 200,
    },
    'elixir~d': {
        'map_usage': 'company',
        'healing_points': 4500,
        'cost': 500,
    },
    'resurrect': {
        'map_usage': 'company',
        'cost': 100,
    },

    # gullwing (city map usage)
    'gullwing': {
        'map_usage': 'city', # means it brings up a menu of main visited cities to teleport to
        'cost': 200,
    },

    # map items
    'key': {
        'map_usage': 'map', # means it interacts with the cell/tile you're on
    },
}

NAMED_TELEPORTS = {
    'zarahemla': [152,187],
}

MAX_COMPANY_SIZE = 7

# we may or may not reference these
EVENT_NAMES = {
    QUIT: 'QUIT',
    ACTIVEEVENT: 'ACTIVEEVENT',
    KEYDOWN: 'KEYDOWN',
    KEYUP: 'KEYUP',
    MOUSEMOTION: 'MOUSEMOTION',
    MOUSEBUTTONDOWN: 'MOUSEBUTTONDOWN',
    MOUSEBUTTONUP: 'MOUSEBUTTONUP',
    JOYAXISMOTION: 'JOYAXISMOTION',
    JOYBALLMOTION: 'JOYBALLMOTION',
    JOYHATMOTION: 'JOYHATMOTION',
    JOYBUTTONDOWN: 'JOYBUTTONDOWN',
    JOYBUTTONUP: 'JOYBUTTONUP',
    VIDEORESIZE: 'VIDEORESIZE',
    VIDEOEXPOSE: 'VIDEOEXPOSE',
}
