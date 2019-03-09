# -*- coding: UTF-8 -*-

from math import ceil
from datetime import datetime
import os
import time

import pygame
from pygame.locals import *

from constants import BLACK, ITEMS, WHITE
from helpers import is_half_second, load_image

CHARS = {
    '0': load_image(os.path.join('font', '0.png')),
    '1': load_image(os.path.join('font', '1.png')),
    '2': load_image(os.path.join('font', '2.png')),
    '3': load_image(os.path.join('font', '3.png')),
    '4': load_image(os.path.join('font', '4.png')),
    '5': load_image(os.path.join('font', '5.png')),
    '6': load_image(os.path.join('font', '6.png')),
    '7': load_image(os.path.join('font', '7.png')),
    '8': load_image(os.path.join('font', '8.png')),
    '9': load_image(os.path.join('font', '9.png')),
    'a': load_image(os.path.join('font', 'a.png')),
    'b': load_image(os.path.join('font', 'b.png')),
    'c': load_image(os.path.join('font', 'c.png')),
    'd': load_image(os.path.join('font', 'd.png')),
    'e': load_image(os.path.join('font', 'e.png')),
    'f': load_image(os.path.join('font', 'f.png')),
    'g': load_image(os.path.join('font', 'g.png')),
    'h': load_image(os.path.join('font', 'h.png')),
    'i': load_image(os.path.join('font', 'i.png')),
    'j': load_image(os.path.join('font', 'j.png')),
    'k': load_image(os.path.join('font', 'k.png')),
    'l': load_image(os.path.join('font', 'l.png')),
    'm': load_image(os.path.join('font', 'm.png')),
    'n': load_image(os.path.join('font', 'n.png')),
    'o': load_image(os.path.join('font', 'o.png')),
    'p': load_image(os.path.join('font', 'p.png')),
    'q': load_image(os.path.join('font', 'q.png')),
    'r': load_image(os.path.join('font', 'r.png')),
    's': load_image(os.path.join('font', 's.png')),
    't': load_image(os.path.join('font', 't.png')),
    'u': load_image(os.path.join('font', 'u.png')),
    'v': load_image(os.path.join('font', 'v.png')),
    'w': load_image(os.path.join('font', 'w.png')),
    'x': load_image(os.path.join('font', 'x.png')),
    'y': load_image(os.path.join('font', 'y.png')),
    'z': load_image(os.path.join('font', 'z.png')),
    'A': load_image(os.path.join('font', 'caps', 'a.png')),
    'B': load_image(os.path.join('font', 'caps', 'b.png')),
    'C': load_image(os.path.join('font', 'caps', 'c.png')),
    'D': load_image(os.path.join('font', 'caps', 'd.png')),
    'E': load_image(os.path.join('font', 'caps', 'e.png')),
    'F': load_image(os.path.join('font', 'caps', 'f.png')),
    'G': load_image(os.path.join('font', 'caps', 'g.png')),
    'H': load_image(os.path.join('font', 'caps', 'h.png')),
    'I': load_image(os.path.join('font', 'caps', 'i.png')),
    'J': load_image(os.path.join('font', 'caps', 'j.png')),
    'K': load_image(os.path.join('font', 'caps', 'k.png')),
    'L': load_image(os.path.join('font', 'caps', 'l.png')),
    'M': load_image(os.path.join('font', 'caps', 'm.png')),
    'N': load_image(os.path.join('font', 'caps', 'n.png')),
    'O': load_image(os.path.join('font', 'caps', 'o.png')),
    'P': load_image(os.path.join('font', 'caps', 'p.png')),
    'Q': load_image(os.path.join('font', 'caps', 'q.png')),
    'R': load_image(os.path.join('font', 'caps', 'r.png')),
    'S': load_image(os.path.join('font', 'caps', 's.png')),
    'T': load_image(os.path.join('font', 'caps', 't.png')),
    'U': load_image(os.path.join('font', 'caps', 'u.png')),
    'V': load_image(os.path.join('font', 'caps', 'v.png')),
    'W': load_image(os.path.join('font', 'caps', 'w.png')),
    'X': load_image(os.path.join('font', 'caps', 'x.png')),
    'Y': load_image(os.path.join('font', 'caps', 'y.png')),
    'Z': load_image(os.path.join('font', 'caps', 'z.png')),
    ' ': load_image(os.path.join('font', 'space.png')),
    '~': load_image(os.path.join('font', 'space.png')), # cheap way to force space integrity by making multiple words and spaces look like one word
    '.': load_image(os.path.join('font', 'period.png')),
    ',': load_image(os.path.join('font', 'comma.png')),
    ':': load_image(os.path.join('font', 'colon.png')),
    "'": load_image(os.path.join('font', 'apostrophe.png')),
    '"': load_image(os.path.join('font', 'quote.png')),
    '?': load_image(os.path.join('font', 'question.png')),
    '!': load_image(os.path.join('font', 'exclamation.png')),
    '/': load_image(os.path.join('font', 'slash.png')),
    '*': load_image(os.path.join('font', 'asterisk.png')),
    '-': load_image(os.path.join('font', 'mdash.png')), # yes, the game uses mdashes like they were hyphens
    # what looks like a hyphen in the game is not used as a hyphen, but it appears as a character you can
    # include in creating a save file. Since what looks like an mdash in the game is used as a hyphen, I'm
    # using the unicode character "ndash", or U+2013, to invoke this character that looks like a hyphen and
    # is not commonly used in the game. Note that in some editors, like sublime, the ndash and mdash look
    # the same. This unicode character is an ndash.
    u'–': load_image(os.path.join('font', 'hyphen.png')), # this unicode is an ndash, U+2013
    u'©': load_image(os.path.join('font', 'copyright.png')),
    u'▶': load_image(os.path.join('font', 'arrow.png')),
    u'▼': load_image(os.path.join('font', 'down_arrow.png')),
    u'★': load_image(os.path.join('font', 'star.png')),
    u'ŕ': load_image(os.path.join('font', 'mdash.png')), # this is a hack to show hyphens without capitalizing the next letter
}


class TextBox(object):
    def __init__(
        self, text, width=None, height=None, adjust='left', border=False, double_space=False, appear='instant', fade_speed=1.5,
        title=None, indent=0, silent=False,
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

        # These variables are only relevant when appear == 'scroll'
        self.lines_available_now = int(ceil((self.height/8 - (3 if border else 0)) / (2.0 if double_space else 1.0)))
        self.scroll_speed = 0.02 # seconds per character printed
        self.starting_line = 0
        self.max_starting_line = 0

        self.lines_available = (
            len(self.lines) if appear=='scroll'
            else self.lines_available_now
        )
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
        self.silent = silent

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
        for y, line in enumerate(self.lines[self.starting_line:]):
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
                # if word.endswith('1052'):
                #     import pdb; pdb.set_trace()
                # is_number is used for displaying numbers in a more readable format, where every other triplet of
                # characters is a bit transparent over a black background, making them a bit gray.
                is_number = True
                for char in word:
                    if char not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ',', '.', '?', '!', ' ', '~', '/']:
                        is_number = False
                        break
                if is_number:
                    numbers_left = 0
                    # This is just in case there is a space or punctuation somewhere in the word.
                    for char in word:
                        if char in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                            numbers_left += 1
                        else:
                            break
                for char in word:
                    if self.appear == 'scroll' and y == self.lines_to_show - 1 and chars_printed == self.chars_to_show:
                        break
                    if char not in CHARS:
                        raise Exception('char not in CHARS. char={}, text="{}"'.format(char, self.text))
                    if (
                        is_number
                        and numbers_left > 0
                        and char in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
                        and (numbers_left-1) % 6 >= 3
                    ):
                        char_image = pygame.Surface((8, 8))
                        fade_box = pygame.Surface((8, 8))
                        fade_box.set_alpha(48)
                        fade_box.fill(BLACK)
                        char_image.blit(CHARS[char], (0, 0))
                        char_image.blit(fade_box, (0, 0))
                        numbers_left -= 1
                    else:
                        char_image = CHARS[char]
                        if is_number and char in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                            numbers_left -= 1
                    surface.blit(char_image, (x*8, vertical_pos))
                    x += 1
                    chars_printed += 1
                    if is_number and numbers_left == 0 and chars_printed < len(word):
                        for remaining_char in word[chars_printed:]:
                            if remaining_char in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                                numbers_left += 1
                            else:
                                break
                if self.appear == 'scroll' and y == self.lines_to_show - 1 and chars_printed == self.chars_to_show:
                    break
                surface.blit(CHARS[' '], (x*8, vertical_pos))
                x += 1
                chars_printed += 1
        if self.border:
            pygame.draw.rect(surface, WHITE, (3, 3, self.width-6, self.height-6), 2)
        if self.show_down_arrow() and is_half_second():
            surface.blit(CHARS[u'▼'], (self.width/2, vertical_pos + (16 if self.double_space else 8)))
        if self.title:
            for i, char in enumerate(self.title):
                surface.blit(CHARS[char], (i*8+16, 0))
        self.surface = surface

    def show_down_arrow(self):
        return self.appear == 'scroll' and not self.has_more_stuff_to_show_now() and self.has_more_stuff_to_show()

    def has_more_stuff_to_show(self):
        lines_shown = self.lines_to_show + self.starting_line
        has_more_lines_to_show = lines_shown < self.lines_available and lines_shown < len(self.lines)
        has_more_chars_to_show = self.appear == 'scroll' and self.chars_to_show < len(self.lines[lines_shown - 1])
        return has_more_lines_to_show or has_more_chars_to_show

    def has_more_stuff_to_show_now(self):
        '''
        Only ever use this in the case of appear == 'scroll'
        '''
        # This is to make room for the continuation arrow if it isn't the end of the whole text.
        lines_available_now = (
            self.lines_available_now if self.starting_line + self.lines_available_now >= len(self.lines)
            else self.lines_available_now - 1
        )

        has_more_lines_to_show_now = self.lines_to_show < lines_available_now and self.lines_to_show < len(self.lines)
        has_more_chars_to_show = self.chars_to_show < len(self.lines[self.starting_line + self.lines_to_show - 1])
        return has_more_lines_to_show_now or has_more_chars_to_show

    def update(self, dt, force=False):
        if not self.started:
            self.started = True
            if self.appear == 'scroll' and not self.silent:
                self.typing_sound.play(-1)
        if not self.needs_update and force == False:
            return
        if self.appear == 'fade':
            self.time_elapsed += dt
            if self.has_more_stuff_to_show():
                if self.time_elapsed > self.fade_speed:
                    self.time_elapsed -= self.fade_speed
                    self.lines_to_show += 1 if self.double_space else 2
                    self.lines_to_show = min(self.lines_to_show, self.lines_available)
                    self.update_surface()
            else:
                self.needs_update = False
        elif self.appear == 'scroll':
            if self.has_more_stuff_to_show_now():
                self.time_elapsed += dt
                while self.time_elapsed > self.scroll_speed:
                    self.time_elapsed -= self.scroll_speed
                    if self.chars_to_show < len(self.lines[self.starting_line + self.lines_to_show - 1]):
                        self.chars_to_show += 1
                    elif self.has_more_stuff_to_show_now():
                        self.chars_to_show = 1
                        self.lines_to_show += 1
            elif self.has_more_stuff_to_show():
                if self.starting_line < self.max_starting_line:
                    self.starting_line += 1
                    self.chars_to_show = 1
                    if not self.silent:
                        self.typing_sound.stop()
                    time.sleep(.2)
                    if not self.silent:
                        self.typing_sound.play(20)
                    time.sleep(.1)
                else:
                    if not self.silent:
                        self.typing_sound.stop()
            else:
                self.needs_update = False
                if not self.silent:
                    self.typing_sound.stop()
            self.update_surface()

    def shutdown(self):
        if not self.silent:
            self.typing_sound.stop()

    def handle_input(self, pressed):
        if self.show_down_arrow() and pressed[K_x]:
            if not self.silent:
                self.typing_sound.play(-1)
            self.max_starting_line += self.lines_available_now - 1


class MenuBox(object):
    def __init__(self, choices, border=True, title=None, width=None, height=None):
        self.choices = choices
        self.current_choice = 0
        self.is_active = False
        self.blink = False
        self.border = border
        self.create_text_box(title, width, height)
        self.switch_sound = pygame.mixer.Sound('data/audio/switch.wav')

    def create_text_box(self, title, width, height):
        self.text_box = TextBox(
            '\n'.join(self.choices), double_space=True, border=self.border, indent=1, title=title, width=width, height=height,
        )
        self.surface = self.text_box.surface

    def focus(self):
        self.is_active = True
        self.highlight_choice()

    def remove_stars(self):
        choices = []
        for choice in self.choices:
            if choice.startswith(u'★'):
                choice = choice[1:]
            choices.append(choice)
        self.choices = choices

    def highlight_choice(self):
        self.blink = True
        self.time_since_highlight_choice = 0

    def unfocus(self, deselect=False):
        self.is_active = False
        self.surface.blit(CHARS[u' ' if deselect else u'▶'], self.get_pointer_location())

    def update_blink(self, dt):
        self.time_since_highlight_choice += dt
        self.blink = (round(self.time_since_highlight_choice - int(self.time_since_highlight_choice)) == 0)

    def get_choice(self, strip_star=True):
        choice = self.choices[self.current_choice] if len(self.choices) > self.current_choice else None
        if choice and strip_star and choice[0] in (u'★', '*'):
            choice = choice[1:]
        return choice

    def get_choices(self, strip_star=True):
        if not strip_star:
            return list(self.choices)
        choices = []
        for choice in self.choices:
            if choice and choice.startswith(u'★'):
                choice = choice[1:]
            choices.append(choice)
        return choices

    def set_choice(self, index):
        assert 0 <= index < len(self.choices)
        self.current_choice = index

    def get_pointer_location(self):
        return (
            (8 if self.border else 0),
            self.current_choice * 16 + (16 if self.border else 0),
        )

    def update(self, dt):
        self.create_text_box(self.text_box.title, self.text_box.width, self.text_box.height)
        self.text_box.update(dt, force=True)
        if self.is_active:
            self.update_blink(dt)
            pointer_location = self.get_pointer_location()
            if self.blink and len(self.choices) > 0:
                self.surface.blit(CHARS[u'▶'], pointer_location)
            else:
                self.surface.blit(CHARS[u' '], pointer_location)

    def get_width(self):
        return self.text_box.width

    def get_height(self):
        return self.text_box.height

    def handle_input(self, pressed):
        if not self.is_active:
            return
        if pressed[K_UP] and len(self.choices) > 0:
            self.surface.blit(CHARS[' '], self.get_pointer_location())
            self.current_choice -= 1
            if self.current_choice == -1:
                self.current_choice = len(self.choices) - 1
            self.highlight_choice()
            self.switch_sound.play()
        elif pressed[K_DOWN] and len(self.choices) > 0:
            self.surface.blit(CHARS[' '], self.get_pointer_location())
            self.current_choice += 1
            if self.current_choice == len(self.choices):
                self.current_choice = 0
            self.highlight_choice()
            self.switch_sound.play()


class MenuGrid(object):
    def __init__(self, choices, border=False, title=None, width=None, height=None):
        '''
        choices: A list of lists where each inner list corresponds to a column in the grid
                 and gets implemented as a MenuBox.
        '''
        self.choices = choices
        self.is_active = False
        self._width = width
        self._height = height
        self.menus = []
        for inner_choices in choices:
            self.menus.append(MenuBox(inner_choices, border=False))
        self.focused_menu = None
        self.focused_menu_index = 0
        self.border = border
        self.title = title
        self.switch_sound = pygame.mixer.Sound('data/audio/switch.wav')
        self.surface = None
        self.set_focused_menu(self.focused_menu_index)
        self.update_surface()

    def focus(self):
        self.is_active = True
        if self.focused_menu:
            self.focused_menu.focus()

    def unfocus(self):
        self.is_active = False
        if self.focused_menu:
            self.focused_menu.unfocus()

    def get_choice(self):
        return self.focused_menu.get_choice() if self.focused_menu else None

    def set_focused_menu(self, index=None):
        index = index if index else self.focused_menu_index
        inner_choice = self.focused_menu.current_choice if self.focused_menu else 0
        if self.focused_menu:
            self.focused_menu.unfocus(deselect=True)
        self.focused_menu = self.menus[index]
        self.focused_menu.focus()
        self.focused_menu.set_choice(inner_choice)
        self.focused_menu_index = index

    def handle_input(self, pressed):
        self.focused_menu.handle_input(pressed)
        if pressed[K_LEFT]:
            valid_menu_found = False
            while not valid_menu_found:
                self.focused_menu_index -= 1
                if self.focused_menu_index < 0:
                    self.focused_menu_index = len(self.menus) - 1
                if self.focused_menu.current_choice < len(self.choices[self.focused_menu_index]):
                    valid_menu_found = True
            self.set_focused_menu()
            self.switch_sound.play()
        elif pressed[K_RIGHT]:
            valid_menu_found = False
            while not valid_menu_found:
                self.focused_menu_index += 1
                if self.focused_menu_index >= len(self.menus):
                    self.focused_menu_index = 0
                if self.focused_menu.current_choice < len(self.choices[self.focused_menu_index]):
                    valid_menu_found = True
            self.set_focused_menu()
            self.switch_sound.play()

    def update(self, dt):
        if self.is_active:
            self.focused_menu.update(dt)
            self.update_surface()

    def update_surface(self):
        surface = pygame.Surface((self.get_width(), self.get_height()))
        x = 8 if self.border else 0
        y = 16 if self.border else 0
        for i, menu in enumerate(self.menus):
            surface.blit(menu.surface, (x, y))
            x += menu.get_width()
        if self.border:
            pygame.draw.rect(surface, WHITE, (3, 3, self.get_width()-6, self.get_height()-6), 2)
        if self.title:
            for i, char in enumerate(self.title):
                surface.blit(CHARS[char], (i*8+16, 0))
        self.surface = surface

    def get_width(self):
        return self._width or sum([menu.get_width() for menu in self.menus]) + (16 if self.border else 0)

    def get_height(self):
        return self._height or max([menu.get_height() for menu in self.menus]) + (24 if self.border else 0)


class ShopMenu(object):
    def __init__(self, items):
        self._width = 128
        if isinstance(items[0], basestring):
            self.items = [{'name': item, 'cost': ITEMS[item]['cost']} for item in items]
        else:
            self.items = items
        self.current_choice = 0
        self.is_active = False
        self.blink = False
        self.border = None
        self.create_text_box()
        self.switch_sound = pygame.mixer.Sound('data/audio/switch.wav')

    def create_text_box(self):
        lines = []
        for item in self.items:
            lines.append(item['name'].title())
            lines.append('{:~>12}'.format(item['cost']))
        self.text_box = TextBox('\n'.join(lines), double_space=False, indent=1, width=self._width, border=True)
        self.surface = self.text_box.surface

    def focus(self):
        self.is_active = True
        self.highlight_choice()

    def highlight_choice(self):
        self.blink = True
        self.time_since_highlight_choice = 0

    def unfocus(self, deselect=False):
        self.is_active = False
        self.surface.blit(CHARS[u' ' if deselect else u'▶'], self.get_pointer_location())

    def update_blink(self, dt):
        self.time_since_highlight_choice += dt
        self.blink = (round(self.time_since_highlight_choice - int(self.time_since_highlight_choice)) == 0)

    def get_choice(self, strip_star=True):
        item = self.items[self.current_choice]
        if strip_star and item['name'][0] in (u'★', '*'):
            item['name'] = item['name'][1:]
        return item

    def set_choice(self, index):
        assert 0 <= index < len(self.items)
        self.current_choice = index

    def get_pointer_location(self):
        return 8, self.current_choice * 16 + 16

    def update(self, dt):
        self.create_text_box()
        self.text_box.update(dt, force=True)
        if self.is_active:
            self.update_blink(dt)
            pointer_location = self.get_pointer_location()
            if self.blink:
                self.surface.blit(CHARS[u'▶'], pointer_location)
            else:
                self.surface.blit(CHARS[u' '], pointer_location)

    def get_width(self):
        return self.text_box.width

    def get_height(self):
        return self.text_box.height

    def handle_input(self, pressed):
        if not self.is_active:
            return
        if pressed[K_UP]:
            self.surface.blit(CHARS[' '], self.get_pointer_location())
            self.current_choice -= 1
            if self.current_choice == -1:
                self.current_choice = len(self.items) - 1
            self.highlight_choice()
            self.switch_sound.play()
        elif pressed[K_DOWN]:
            self.surface.blit(CHARS[' '], self.get_pointer_location())
            self.current_choice += 1
            if self.current_choice == len(self.items):
                self.current_choice = 0
            self.highlight_choice()
            self.switch_sound.play()



def create_prompt(text, silent=False):
    return TextBox(text, width=160, height=80, border=True, double_space=True, appear='scroll', silent=silent)
