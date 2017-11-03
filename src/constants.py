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

ITEMS = {
    # weapons
    'dagger': {
        'attack_points': 10,
        'equip_type': 'weapon',
        'cost': 50,
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
    }
}

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
