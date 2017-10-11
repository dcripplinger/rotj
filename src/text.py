# -*- coding: UTF-8 -*-

from math import ceil
from datetime import datetime

import pygame
from pygame.locals import *

from constants import BLACK, WHITE
from helpers import load_image

CHARS = {
    '0': load_image('font/0.png'),
    '1': load_image('font/1.png'),
    '2': load_image('font/2.png'),
    '3': load_image('font/3.png'),
    '4': load_image('font/4.png'),
    '5': load_image('font/5.png'),
    '6': load_image('font/6.png'),
    '7': load_image('font/7.png'),
    '8': load_image('font/8.png'),
    '9': load_image('font/9.png'),
    'a': load_image('font/a.png'),
    'b': load_image('font/b.png'),
    'c': load_image('font/c.png'),
    'd': load_image('font/d.png'),
    'e': load_image('font/e.png'),
    'f': load_image('font/f.png'),
    'g': load_image('font/g.png'),
    'h': load_image('font/h.png'),
    'i': load_image('font/i.png'),
    'j': load_image('font/j.png'),
    'k': load_image('font/k.png'),
    'l': load_image('font/l.png'),
    'm': load_image('font/m.png'),
    'n': load_image('font/n.png'),
    'o': load_image('font/o.png'),
    'p': load_image('font/p.png'),
    'q': load_image('font/q.png'),
    'r': load_image('font/r.png'),
    's': load_image('font/s.png'),
    't': load_image('font/t.png'),
    'u': load_image('font/u.png'),
    'v': load_image('font/v.png'),
    'w': load_image('font/w.png'),
    'x': load_image('font/x.png'),
    'y': load_image('font/y.png'),
    'z': load_image('font/z.png'),
    'A': load_image('font/caps/a.png'),
    'B': load_image('font/caps/b.png'),
    'C': load_image('font/caps/c.png'),
    'D': load_image('font/caps/d.png'),
    'E': load_image('font/caps/e.png'),
    'F': load_image('font/caps/f.png'),
    'G': load_image('font/caps/g.png'),
    'H': load_image('font/caps/h.png'),
    'I': load_image('font/caps/i.png'),
    'J': load_image('font/caps/j.png'),
    'K': load_image('font/caps/k.png'),
    'L': load_image('font/caps/l.png'),
    'M': load_image('font/caps/m.png'),
    'N': load_image('font/caps/n.png'),
    'O': load_image('font/caps/o.png'),
    'P': load_image('font/caps/p.png'),
    'Q': load_image('font/caps/q.png'),
    'R': load_image('font/caps/r.png'),
    'S': load_image('font/caps/s.png'),
    'T': load_image('font/caps/t.png'),
    'U': load_image('font/caps/u.png'),
    'V': load_image('font/caps/v.png'),
    'W': load_image('font/caps/w.png'),
    'X': load_image('font/caps/x.png'),
    'Y': load_image('font/caps/y.png'),
    'Z': load_image('font/caps/z.png'),
    ' ': load_image('font/space.png'),
    '~': load_image('font/space.png'), # cheap way to force space integrity by making multiple words and spaces look like one word
    '.': load_image('font/period.png'),
    ',': load_image('font/comma.png'),
    "'": load_image('font/apostrophe.png'),
    '"': load_image('font/quote.png'),
    '?': load_image('font/question.png'),
    '!': load_image('font/exclamation.png'),
    '/': load_image('font/slash.png'),
    '-': load_image('font/mdash.png'), # yes, the game uses mdashes like they were hyphens
    # what looks like a hyphen in the game is not used as a hyphen, but it appears as a character you can
    # include in creating a save file. Since what looks like an mdash in the game is used as a hyphen, I'm
    # using the unicode character "ndash", or U+2013, to invoke this character that looks like a hyphen and
    # is not commonly used in the game. Note that in some editors, like sublime, the ndash and mdash look
    # the same. This unicode character is an ndash.
    u'–': load_image('font/hyphen.png'), # this unicode is an ndash, U+2013
    u'©': load_image('font/copyright.png'),
    u'▶': load_image('font/arrow.png'),
}


class TextBox(object):
    def __init__(
        self, text, width=None, height=None, adjust='left', border=False, double_space=False, appear='instant', fade_speed=1.5,
        title=None, indent=0,
    ):
        self.text = text
        self.title = title
        self.lines = text.split('\n')
        self.words = {}
        self.indent = indent
        for line in self.lines:
            self.words[line] = line.split()
        self.width = width if width else max([len(line) for line in self.lines])*8 + (16 if border else 0) + 8*indent
        self.adjust = adjust
        self.border = border
        self.double_space = double_space
        self.text_width = (self.width - (16 if border else 0) - 8*indent) / 8
        if width:
            self.fix_lines()
        self.height = height if height else (
            len(self.lines) * (2 if double_space else 1) * 8 + (24 if border else 0) - (8 if border and double_space else 0)
        )
        self.time_elapsed = 0
        self.fade_speed = fade_speed
        self.scroll_speed = 0.02 # seconds per character printed
        self.lines_available = ceil((self.height/8 - (3 if border else 0)) / (2.0 if double_space else 1.0))
        self.appear = appear
        self.lines_to_show = (
            2 if appear=='fade' and not double_space
            else 1 if appear=='fade' and double_space
            else 1 if appear=='scroll'
            else len(self.lines)
        )
        self.typing_sound = pygame.mixer.Sound('data/audio/typing.wav')
        self.needs_update = False if appear=='instant' else True
        self.started = False

        # chars to show on the last line to show
        self.chars_to_show = 0
        
        self.lines_to_show = min(self.lines_to_show, self.lines_available)
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
        # if self.text == 'Which history do you continue?':
        #     import pdb; pdb.set_trace()
        y_space = 2 if self.double_space else 1
        surface = pygame.Surface((self.width, self.height))
        surface.fill(BLACK)
        for y, line in enumerate(self.lines):
            chars_printed = 0
            if self.lines_to_show == y:
                break
            x = (1 if self.border else 0) + self.indent + (
                (self.text_width-len(line))/2 if self.adjust=='center'
                else self.text_width-len(line) if self.adjust=='right'
                else 0
            )
            vertical_pos = (y * y_space + (2 if self.border else 0)) * 8
            for word in self.words[line]:
                for char in word:
                    if self.appear == 'scroll' and y == self.lines_to_show - 1 and chars_printed == self.chars_to_show:
                        break
                    surface.blit(CHARS[char], (x*8, vertical_pos))
                    x += 1
                    chars_printed += 1
                if self.appear == 'scroll' and y == self.lines_to_show - 1 and chars_printed == self.chars_to_show:
                    break
                surface.blit(CHARS[' '], (x*8, vertical_pos))
                x += 1
                chars_printed += 1
        if self.border:
            pygame.draw.rect(surface, WHITE, (3, 3, self.width-6, self.height-6), 2)
        self.surface = surface

    def has_more_stuff_to_show(self):
        has_more_lines_to_show = self.lines_to_show < self.lines_available and self.lines_to_show < len(self.lines)
        has_more_chars_to_show = self.appear == 'scroll' and self.chars_to_show < len(self.lines[self.lines_to_show - 1])
        return has_more_lines_to_show or has_more_chars_to_show

    def update(self, dt):
        if not self.started:
            self.started = True
            if self.appear == 'scroll':
                self.typing_sound.play(-1)
        if not self.needs_update:
            return
        self.time_elapsed += dt
        if self.appear == 'fade':
            if self.has_more_stuff_to_show():
                if self.time_elapsed > self.fade_speed:
                    self.time_elapsed -= self.fade_speed
                    self.lines_to_show += 1 if self.double_space else 2
                    self.lines_to_show = min(self.lines_to_show, self.lines_available)
                    self.update_surface()
            else:
                self.needs_update = False
        elif self.appear == 'scroll':
            if self.has_more_stuff_to_show():
                while self.time_elapsed > self.scroll_speed:
                    self.time_elapsed -= self.scroll_speed
                    if self.chars_to_show < len(self.lines[self.lines_to_show - 1]):
                        self.chars_to_show += 1
                    elif self.has_more_stuff_to_show():
                        self.chars_to_show = 1
                        self.lines_to_show += 1
            else:
                self.needs_update = False
                self.typing_sound.stop()
            self.update_surface()


class MenuBox(object):
    def __init__(self, choices):
        self.choices = choices
        self.current_choice = 0
        self.is_active = False
        self.blink = False
        self.text_box = TextBox('\n'.join(choices), double_space=True, border=True, indent=1)
        self.surface = self.text_box.surface
        self.switch_sound = pygame.mixer.Sound('data/audio/switch.wav')

    def focus(self):
        self.is_active = True
        self.highlight_choice()

    def highlight_choice(self):
        self.blink = True
        self.time_since_highlight_choice = 0

    def unfocus(self):
        self.is_active = False
        self.surface.blit(CHARS[' '], (8, self.current_choice * 16 + 16))

    def update_blink(self, dt):
        self.time_since_highlight_choice += dt
        self.blink = (round(self.time_since_highlight_choice - int(self.time_since_highlight_choice)) == 0)

    def get_choice(self):
        return self.choices[self.current_choice]

    def update(self, dt):
        if self.is_active:
            self.update_blink(dt)
            pointer_location = (8, self.current_choice * 16 + 16)
            if self.blink:
                self.surface.blit(CHARS[u'▶'], pointer_location)
            else:
                self.surface.blit(CHARS[' '], pointer_location)

    def get_width(self):
        return self.text_box.width

    def handle_input(self, pressed):
        if not self.is_active:
            return
        if pressed[K_UP]:
            self.surface.blit(CHARS[' '], (8, self.current_choice * 16 + 16))
            self.current_choice -= 1
            if self.current_choice == -1:
                self.current_choice = len(self.choices) - 1
            self.highlight_choice()
            self.switch_sound.play()
        elif pressed[K_DOWN]:
            self.surface.blit(CHARS[' '], (8, self.current_choice * 16 + 16))
            self.current_choice += 1
            if self.current_choice == len(self.choices):
                self.current_choice = 0
            self.highlight_choice()
            self.switch_sound.play()
