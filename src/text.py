# -*- coding: UTF-8 -*-

import pygame

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
    'A': load_image('font/A.png'),
    'B': load_image('font/B.png'),
    'C': load_image('font/C.png'),
    'D': load_image('font/D.png'),
    'E': load_image('font/E.png'),
    'F': load_image('font/F.png'),
    'G': load_image('font/G.png'),
    'H': load_image('font/H.png'),
    'I': load_image('font/I.png'),
    'J': load_image('font/J.png'),
    'K': load_image('font/K.png'),
    'L': load_image('font/L.png'),
    'M': load_image('font/M.png'),
    'N': load_image('font/N.png'),
    'O': load_image('font/O.png'),
    'P': load_image('font/P.png'),
    'Q': load_image('font/Q.png'),
    'R': load_image('font/R.png'),
    'S': load_image('font/S.png'),
    'T': load_image('font/T.png'),
    'U': load_image('font/U.png'),
    'V': load_image('font/V.png'),
    'W': load_image('font/W.png'),
    'X': load_image('font/X.png'),
    'Y': load_image('font/Y.png'),
    'Z': load_image('font/Z.png'),
    ' ': load_image('font/space.png'),
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
