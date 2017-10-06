#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
from math import ceil, floor
import os
import pygame
from pygame.locals import *
import pyscroll
from pyscroll.group import PyscrollGroup
from pytmx.util_pygame import load_pygame
import subprocess
import sys
import time

RESOURCES_DIR = '../data'
MAP_NAMES = [
    'overworld',
    'tunnels_of_the_north',
    'cave_of_gadianton',
    'sierra_pass',
    'cavity_of_a_rock',
    'passage_to_gid',
]
HERO_MOVE_SPEED = 10  # tiles per second.
TILE_SIZE = 16 # pixels
GAME_WIDTH = 256 # pixels (before scaling)
GAME_HEIGHT = 240 # pixels (before scaling)
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
WHITE = (255,255,255)
BLACK = (0,0,0)

os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"


def is_half_second():
    t = pygame.time.get_ticks()/1000.0
    return round(t - int(t)) == 0


def load_image(filename):
    return pygame.image.load(os.path.join(RESOURCES_DIR, filename))


def get_map_filename(filename):
    return os.path.join(RESOURCES_DIR, "maps", filename)


CHARS = {
    '0': load_image('../data/images/font/0.png'),
    '1': load_image('../data/images/font/1.png'),
    '2': load_image('../data/images/font/2.png'),
    '3': load_image('../data/images/font/3.png'),
    '4': load_image('../data/images/font/4.png'),
    '5': load_image('../data/images/font/5.png'),
    '6': load_image('../data/images/font/6.png'),
    '7': load_image('../data/images/font/7.png'),
    '8': load_image('../data/images/font/8.png'),
    '9': load_image('../data/images/font/9.png'),
    'a': load_image('../data/images/font/a.png'),
    'b': load_image('../data/images/font/b.png'),
    'c': load_image('../data/images/font/c.png'),
    'd': load_image('../data/images/font/d.png'),
    'e': load_image('../data/images/font/e.png'),
    'f': load_image('../data/images/font/f.png'),
    'g': load_image('../data/images/font/g.png'),
    'h': load_image('../data/images/font/h.png'),
    'i': load_image('../data/images/font/i.png'),
    'j': load_image('../data/images/font/j.png'),
    'k': load_image('../data/images/font/k.png'),
    'l': load_image('../data/images/font/l.png'),
    'm': load_image('../data/images/font/m.png'),
    'n': load_image('../data/images/font/n.png'),
    'o': load_image('../data/images/font/o.png'),
    'p': load_image('../data/images/font/p.png'),
    'q': load_image('../data/images/font/q.png'),
    'r': load_image('../data/images/font/r.png'),
    's': load_image('../data/images/font/s.png'),
    't': load_image('../data/images/font/t.png'),
    'u': load_image('../data/images/font/u.png'),
    'v': load_image('../data/images/font/v.png'),
    'w': load_image('../data/images/font/w.png'),
    'x': load_image('../data/images/font/x.png'),
    'y': load_image('../data/images/font/y.png'),
    'z': load_image('../data/images/font/z.png'),
    'A': load_image('../data/images/font/A.png'),
    'B': load_image('../data/images/font/B.png'),
    'C': load_image('../data/images/font/C.png'),
    'D': load_image('../data/images/font/D.png'),
    'E': load_image('../data/images/font/E.png'),
    'F': load_image('../data/images/font/F.png'),
    'G': load_image('../data/images/font/G.png'),
    'H': load_image('../data/images/font/H.png'),
    'I': load_image('../data/images/font/I.png'),
    'J': load_image('../data/images/font/J.png'),
    'K': load_image('../data/images/font/K.png'),
    'L': load_image('../data/images/font/L.png'),
    'M': load_image('../data/images/font/M.png'),
    'N': load_image('../data/images/font/N.png'),
    'O': load_image('../data/images/font/O.png'),
    'P': load_image('../data/images/font/P.png'),
    'Q': load_image('../data/images/font/Q.png'),
    'R': load_image('../data/images/font/R.png'),
    'S': load_image('../data/images/font/S.png'),
    'T': load_image('../data/images/font/T.png'),
    'U': load_image('../data/images/font/U.png'),
    'V': load_image('../data/images/font/V.png'),
    'W': load_image('../data/images/font/W.png'),
    'X': load_image('../data/images/font/X.png'),
    'Y': load_image('../data/images/font/Y.png'),
    'Z': load_image('../data/images/font/Z.png'),
    ' ': load_image('../data/images/font/space.png'),
    '.': load_image('../data/images/font/period.png'),
    ',': load_image('../data/images/font/comma.png'),
    "'": load_image('../data/images/font/apostrophe.png'),
    '"': load_image('../data/images/font/quote.png'),
    '?': load_image('../data/images/font/question.png'),
    '!': load_image('../data/images/font/exclamation.png'),
    '/': load_image('../data/images/font/slash.png'),
    '-': load_image('../data/images/font/mdash.png'), # yes, the game uses mdashes like they were hyphens
    # what looks like a hyphen in the game is not used as a hyphen, but it appears as a character you can
    # include in creating a save file. Since what looks like an mdash in the game is used as a hyphen, I'm
    # using the unicode character "ndash", or U+2013, to invoke this character that looks like a hyphen and
    # is not commonly used in the game. Note that in some editors, like sublime, the ndash and mdash look
    # the same. This unicode character is an ndash.
    u'–': load_image('../data/images/font/hyphen.png'), # this unicode is an ndash, U+2013
    u'©': load_image('../data/images/font/copyright.png'),
}


class TextBox(object):
    def __init__(
        self, text, width, height, adjust='left', border=True, double_space=False, appear='instant', fade_speed=1.5,
    ):
        self.text = text
        self.lines = text.split('\n')
        self.words = {}
        for line in self.lines:
            self.words[line] = line.split()
        self.width = width
        self.height = height
        self.adjust = adjust
        self.border = border
        self.double_space = double_space
        self.text_width = width/8
        self.fix_lines()
        self.time_elapsed = 0
        self.fade_speed = fade_speed
        self.lines_to_show = (
            2 if appear=='fade' and not double_space
            else 1 if appear=='fade' and double_space
            else len(self.lines)
        )
        self.update_surface()

    def fix_lines(self):
        new_lines = []
        for line in self.lines:
            fitting_words = []
            left_over = self.text_width
            for words_index, word in enumerate(self.words[line]):
                account_for_space = 0 if words_index==len(self.words[line])-1 else 1
                to_consume = len(word) + account_for_space
                if to_consume <= left_over:
                    fitting_words.append(word)
                    left_over = left_over - to_consume
                else:
                    new_lines.append(' '.join(fitting_words))
                    fitting_words = [word]
                    left_over = self.text_width - to_consume
            if len(fitting_words) > 0:
                new_lines.append(' '.join(fitting_words))
        self.lines = new_lines
        self.words = {}
        for line in self.lines:
            self.words[line] = line.split()

    def update_surface(self):
        y_space = 2 if self.double_space else 1
        surface = pygame.Surface((self.width, self.height))
        surface.fill(BLACK)
        for y, line in enumerate(self.lines):
            if self.lines_to_show == y:
                break
            x = (
                (self.text_width-len(line))/2 if self.adjust=='center'
                else self.text_width-len(line) if self.adjust=='right'
                else 0
            )
            for word in self.words[line]:
                for char in word:
                    surface.blit(CHARS[char], (x*8, y*8*y_space))
                    x += 1
                surface.blit(CHARS[' '], (x*8, y*8*y_space))
                x += 1
        self.surface = surface

    def update(self, dt):
        self.time_elapsed += dt
        if self.lines_to_show < len(self.lines) and self.time_elapsed > self.fade_speed:
            self.time_elapsed -= self.fade_speed
            self.lines_to_show += 1 if self.double_space else 2
            self.update_surface()


class Hero(pygame.sprite.Sprite):
    def __init__(self, tmx_data, cells, game):
        pygame.sprite.Sprite.__init__(self)
        self.velocity = [0.0, 0.0]
        self.position = [153.0, 187.0]
        self.old_position = self.position
        self.tmx_data = tmx_data
        self.cells = cells
        self.game = game

        side_stand = load_image('../gextract/tiles16/000000030.png').convert_alpha()
        side_walk = load_image('../gextract/tiles16/000000031.png').convert_alpha()
        self.images = {
            'e': {
                'stand': side_stand,
                'walk': side_walk,
            },
            'n': {
                'stand': load_image('../gextract/tiles16/000000028.png').convert_alpha(),
                'walk': load_image('../gextract/tiles16/000000029.png').convert_alpha(),
            },
            's': {
                'stand': load_image('../gextract/tiles16/000000026.png').convert_alpha(),
                'walk': load_image('../gextract/tiles16/000000027.png').convert_alpha(),
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


class Map(object):
    def __init__(self, screen, map_name, game):
        self.game = game
        map_filename = get_map_filename('{}.tmx'.format(map_name))
        json_filename = get_map_filename('{}.json'.format(map_name))
        self.screen = screen
        self.tmx_data = load_pygame(map_filename)
        with open(json_filename) as f:
            json_data = json.loads(f.read())
        self.cells = {(cell['x'], cell['y']): cell for cell in json_data}
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.screen.get_size())
        self.map_layer.zoom = 1
        self.group = PyscrollGroup(map_layer=self.map_layer)
        self.hero = Hero(self.tmx_data, self.cells, self.game)
        self.group.add(self.hero)

    def draw(self):
        self.group.center(self.hero.rect.center)
        self.group.draw(self.screen)

    def update(self, dt):
        self.group.update(dt)

    def move_hero(self, direction):
        self.hero.move(direction)
        # when I add followers, they would move here too

    def handle_input(self, pressed):
        if pressed[K_UP]:
            self.move_hero('n')
        elif pressed[K_DOWN]:
            self.move_hero('s')
        elif pressed[K_RIGHT]:
            self.move_hero('e')
        elif pressed[K_LEFT]:
            self.move_hero('w')
        else:
            self.move_hero(None)


class TitlePage(object):
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.transition_times = [48, 64, 85, 106, 127, 148, 169, 200]
        self.warlords = [
            'moroni', 'teancum', 'amalickiah',
            'nehor', 'amlici', 'mathoni',
            'zerahemnah', 'zoram', 'lehi',
            'alma', 'nephi', 'samuel',
            'shiz', 'helaman', 'lachoneus',
        ]
        self.portraits = {
            warlord: load_image('../data/images/portraits/{}.png'.format(warlord))
            for warlord in self.warlords
        }
        self.biographies = {
            'moroni': "The greatest captain in all of Nephite history.",
            'teancum': "A legendary Nephite captain and spy. Unmatched in his skill with a javelin.",
            'amalickiah': "Brother in arms with Moroni, endowed with equally great strength and cunning.",
            'nehor': "Founder of a violent and rebellious religion known as the Order of the Nehors.",
            'amlici': "The first of many to seek to dethrone the judges and set himself as a king over the Nephites.",
            'mathoni': "King of the Lamanite nation, which sought continually to destroy the Nephites.",
            'zerahemnah': "Lamanite captain whose men were feared everywhere for their ferocity and brutality.",
            'zoram': "Believed his city to be the only ones saved by God. Seceded from the Nephites.",
            'lehi': "The son of Zoram and the most experienced commander in warfare.",
            'alma': "The first chief judge of the Nephites. Lauded for both his leadership and battle strategy.",
            'nephi': "The greatest Nephite prophet ever. Single-handedly defeated an entire generation of robbers.",
            'samuel': "A Lamanite prophet and wanderer, nearly as famous as Nephi.",
            'shiz': "Stronger even than Moroni, was rumored to be unkillable.",
            'helaman': "The son of Alma and a great Nephite captain. Not one of his soliders ever perished.",
            'lachoneus': "A courageous Nephite chief judge tasked with bringing peace during the nation's bloodiest era.",
        }
        self.bio_text_boxes = {
            warlord: TextBox(self.biographies[warlord], GAME_WIDTH-72, 40, appear='fade')
            for warlord in self.warlords
        }
        self.name_text_boxes = {
            warlord: TextBox(warlord.title(), GAME_WIDTH-84, 8, adjust='right')
            for warlord in self.warlords
        }
        self.title_image = load_image('../data/images/title.png').convert_alpha()
        copyright_text = (
            u'© DAVID RIPPLINGER, 2017\n'
            u'FREE UNDER THE MIT LICENSE\n'
            u'BASED ON "DESTINY OF AN EMPEROR"\n'
            u'© HIROSHI MOTOMIYA, 1989'
        )
        self.copyright = TextBox(copyright_text, GAME_WIDTH, 4*16, adjust='center', double_space=True)
        self.press_start = TextBox('PRESS ENTER', GAME_WIDTH, 16, adjust='center')
        intro_text = (
            'This is the story of the wars fought among the great Nephite nation over two thousand years ago, '
            'somewhere on the American continent.'
        )
        self.intro = TextBox(intro_text, GAME_WIDTH-8*4, 7*16, double_space=True, appear='fade')
        foreword_text = (
            'Many of the 236 warlords in the game were designed based on the stories or characteristics of people in '
            'the Book of Mormon, offering a massive and detailed retelling of '
            'the book\'s war chapters. Travel back to that exciting period now in the full-scale Role Playing '
            'Simulation of the "Reign of the Judges".'
        )
        self.foreword = TextBox(foreword_text, GAME_WIDTH-32, 7*16, appear='fade', fade_speed=3)
        self.reset()

    def handle_input(self, pressed):
        if pressed[K_RETURN]:
            if self.current_page == 0:
                self.game.screen_state = 'game'
                pygame.mixer.music.stop()
                time.sleep(0.5)
            else:
                self.reset()

    def draw(self):
        self.screen.fill((0,0,0))
        if self.current_page == 0:
            self.screen.blit(self.title_image, ((GAME_WIDTH - self.title_image.get_width())/2, 16))
            self.screen.blit(self.copyright.surface, (0, 136))
            if is_half_second():
                self.screen.blit(self.press_start.surface, (0, 112))
        elif self.current_page == 1:
            self.screen.blit(self.title_image, ((GAME_WIDTH - self.title_image.get_width())/2, 16))
            if self.time_elapsed > self.transition_times[0]+3:
                self.to_update.add(self.intro)
                self.screen.blit(self.intro.surface, (32, 112))
        elif self.current_page == 2:
            warlords = self.warlords[0:3]
            t = self.time_elapsed-self.transition_times[1]
            self.draw_portraits(warlords, t)
            self.draw_biographies(warlords, t)
        elif self.current_page == 3:
            warlords = self.warlords[3:6]
            t = self.time_elapsed-self.transition_times[2]
            self.draw_portraits(warlords, t)
            self.draw_biographies(warlords, t)
        elif self.current_page == 4:
            warlords = self.warlords[6:9]
            t = self.time_elapsed-self.transition_times[3]
            self.draw_portraits(warlords, t)
            self.draw_biographies(warlords, t)
        elif self.current_page == 5:
            warlords = self.warlords[9:12]
            t = self.time_elapsed-self.transition_times[4]
            self.draw_portraits(warlords, t)
            self.draw_biographies(warlords, t)
        elif self.current_page == 6:
            warlords = self.warlords[12:15]
            t = self.time_elapsed-self.transition_times[5]
            self.draw_portraits(warlords, t)
            self.draw_biographies(warlords, t)
        elif self.current_page == 7:
            if self.transition_times[6]+3 < self.time_elapsed < self.transition_times[7]-5:
                self.to_update.add(self.foreword)
                self.screen.blit(self.foreword.surface, (32, 80))

    def draw_portraits(self, warlords, elapsed):
        if 1 < elapsed < 21:
            t = 1 if elapsed > 2 else elapsed-1
            x_margin = 8
            x_left = (x_margin-GAME_WIDTH)*t + GAME_WIDTH
            x_right = (GAME_WIDTH-x_margin)*t - 48
            self.screen.blit(self.portraits[warlords[0]], (x_left,16))
            self.screen.blit(pygame.transform.flip(self.portraits[warlords[1]], True, False), (x_right,80))
            self.screen.blit(self.portraits[warlords[2]], (x_left,144))

    def draw_biographies(self, warlords, elapsed):
        if elapsed > 21:
            return
        if elapsed > 3:
            self.to_update.add(self.bio_text_boxes[warlords[0]])
            self.screen.blit(self.bio_text_boxes[warlords[0]].surface, (64, 16))
        if elapsed > 6:
            self.screen.blit(self.name_text_boxes[warlords[0]].surface, (64, 56))
        if elapsed > 8:
            self.to_update.add(self.bio_text_boxes[warlords[1]])
            self.screen.blit(self.bio_text_boxes[warlords[1]].surface, (8, 80))
        if elapsed > 11:
            self.screen.blit(self.name_text_boxes[warlords[1]].surface, (8, 120))
        if elapsed > 13:
            self.to_update.add(self.bio_text_boxes[warlords[2]])
            self.screen.blit(self.bio_text_boxes[warlords[2]].surface, (64, 144))
        if elapsed > 16:
            self.screen.blit(self.name_text_boxes[warlords[2]].surface, (64, 184))

    def reset(self):
        self.current_music = None
        self.time_elapsed = 0.0
        self.current_page = 0
        self.to_update = set()

    def update(self, dt):
        for update_obj in self.to_update:
            update_obj.update(dt)
        self.time_elapsed += dt
        if self.current_page == 0:
            if self.current_music is None:
                pygame.mixer.music.load('../data/audio/music/title_theme_intro.wav')
                pygame.mixer.music.play()
                self.current_music = 'intro'
            elif self.current_music == 'intro' and not pygame.mixer.music.get_busy():
                pygame.mixer.music.load('../data/audio/music/title_theme_body.wav')
                pygame.mixer.music.play(-1)
                self.current_music = 'body'
            if self.time_elapsed > self.transition_times[0]:
                self.current_page = 1
        elif self.current_page == 1:
            if self.time_elapsed > self.transition_times[1]:
                self.current_page = 2
                self.to_update.clear()
        elif self.current_page == 2:
            if self.time_elapsed > self.transition_times[2]:
                self.current_page = 3
                self.to_update.clear()
        elif self.current_page == 3:
            if self.time_elapsed > self.transition_times[3]:
                self.current_page = 4
                self.to_update.clear()
        elif self.current_page == 4:
            if self.time_elapsed > self.transition_times[4]:
                self.current_page = 5
                self.to_update.clear()
        elif self.current_page == 5:
            if self.time_elapsed > self.transition_times[5]:
                self.current_page = 6
                self.to_update.clear()
        elif self.current_page == 6:
            if self.time_elapsed > self.transition_times[6]:
                self.current_page = 7
                self.to_update.clear()
        elif self.current_page == 7:
            if self.time_elapsed > self.transition_times[7]:
                self.reset()


class Game(object):
    def __init__(self, screen):
        self.real_screen = screen
        self.virtual_width = GAME_WIDTH
        self.virtual_height = GAME_HEIGHT
        self.virtual_screen = pygame.Surface((self.virtual_width, self.virtual_height))
        self.clock = pygame.time.Clock()
        self.fps = 1000
        self.screen_state = "title"
        self.maps = {name: Map(self.virtual_screen, name, self) for name in MAP_NAMES}
        self.current_map = self.maps['overworld']
        pygame.key.set_repeat(10, 10)
        pygame.event.set_blocked(MOUSEMOTION)
        pygame.event.set_blocked(ACTIVEEVENT)
        pygame.event.set_blocked(VIDEORESIZE)
        pygame.event.set_blocked(KEYUP)
        self.title_page = TitlePage(self.virtual_screen, self)
        self.fitted_screen = None # gets initialized in resize_window()
        self.window_size = screen.get_size()
        self.resize_window(self.window_size)

    def set_current_map(self, map_name, position, direction):
        self.current_map = self.maps[map_name]
        self.current_map.hero.position = position
        self.current_map.hero.direction = direction

    def resize_window(self, size):
        self.real_screen = pygame.display.set_mode(size)
        (width, height) = size
        width_multiplier = width*1.0 / self.virtual_width
        height_multiplier = height*1.0 / self.virtual_height
        multiplier = min(width_multiplier, height_multiplier)
        fitted_width = int(self.virtual_width*multiplier)
        fitted_height = int(self.virtual_height*multiplier)
        fitted_x_pos = (width - fitted_width) / 2
        fitted_y_pos = (height - fitted_height) / 2
        self.fitted_screen = self.real_screen.subsurface(
            (fitted_x_pos, fitted_y_pos, fitted_width, fitted_height)
        )

    def scale(self):
        self.real_screen.fill((0,0,0))
        pygame.transform.scale(self.virtual_screen, self.fitted_screen.get_size(), self.fitted_screen)

    def draw(self):
        if self.screen_state == 'game':
            self.current_map.draw()
        elif self.screen_state == 'title':
            self.title_page.draw()
        self.scale()

    def update(self, dt):
        if self.screen_state == 'game':
            self.current_map.update(dt)
        elif self.screen_state == 'title':
            self.title_page.update(dt)

    def is_a_wall(self, offset):
        x = self.hero.position[0] + offset[0]
        y = self.hero.position[1] + offset[1]
        if x < 0 or y < 0 or x >= self.tmx_data.width or y >= self.tmx_data.height:
            return True
        props = self.tmx_data.get_tile_properties(x, y, 0)
        return props['wall'] == 'true'

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                pygame.quit()
                return
            print event
        pressed = pygame.key.get_pressed()
        if pressed[K_ESCAPE]:
            self.running = False
            pygame.quit()
            print(" ")
            time.sleep(0.5)
            print("Shutdown... Complete")
            sys.exit()
            return
        if self.screen_state == "game":
            self.current_map.handle_input(pressed)
        elif self.screen_state == 'title':
            self.title_page.handle_input(pressed)

    def get_new_window_size_and_fit_screen(self):
        p = subprocess.Popen(['xwininfo', '-name', 'pygame window'], stdout=subprocess.PIPE)
        (win_info, _) = p.communicate()
        for line in win_info.split('\n'):
            data = line.split()
            if len(data) != 2:
                continue
            if data[0] == 'Width:':
                new_width = int(data[1])
            elif data[0] == 'Height:':
                new_height = int(data[1])
        if self.window_size[0] != new_width or self.window_size[1] != new_height:
            self.resize_window((new_width, new_height))


    def run(self):
        self.running = True
        try:
            while self.running:
                dt = self.clock.tick(self.fps)/1000.0
                self.handle_input()
                self.update(dt)
                self.draw()
                pygame.display.flip()
        except KeyboardInterrupt:
            self.running = False
            pygame.quit()


if __name__ == '__main__':
    screen = pygame.display.set_mode((1600, 900))
    pygame.mixer.init()
    try:
        game = Game(screen)
        game.run()
    except:
        pygame.quit()
        raise
