# -*- coding: UTF-8 -*-

import os
import time

import pygame
from pygame.locals import *

from constants import GAME_WIDTH
from helpers import is_half_second, load_image
from text import TextBox


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
            warlord: load_image(os.path.join('portraits', '{}.png'.format(warlord)))
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
            'helaman': "The son of Alma and a great Nephite captain. Not one of his soldiers ever perished.",
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
        self.title_image = load_image('title.png').convert_alpha()
        copyright_text = (
            u'© DAVID RIPPLINGER,~2019\n'
            u'FREE UNDER THE MIT LICENSE\n'
            u'BASED ON "DESTINY OF AN EMPEROR"\n'
            u'© HIROSHI MOTOMIYA,~1989'
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
                self.game.set_screen_state('menu')
                pygame.mixer.music.stop()
                time.sleep(0.5)
            else:
                pygame.mixer.music.stop()
                time.sleep(0.5)
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
        pygame.mixer.music.set_volume(1.0)

    def update(self, dt):
        for update_obj in self.to_update:
            update_obj.update(dt)
        self.time_elapsed += dt
        if self.current_page == 0:
            if self.current_music is None:
                pygame.mixer.music.load(os.path.join('data', 'audio', 'music', 'title_theme_intro.wav'))
                pygame.mixer.music.play()
                self.current_music = 'intro'
            elif self.current_music == 'intro' and not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(os.path.join('data', 'audio', 'music', 'title_theme_body.wav'))
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
