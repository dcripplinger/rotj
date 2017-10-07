#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os

import pygame

from game import Game

os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"

if __name__ == '__main__':
    screen = pygame.display.set_mode((1600, 900))
    pygame.mixer.init()
    try:
        game = Game(screen)
        game.run()
    except:
        pygame.quit()
        raise
