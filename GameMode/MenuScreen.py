import pygame
import pygame_menu
import sys
from data.config import *


class MenuScreen:
    def __init__(self, screen):
        self.screen = screen
        # Setting menu background
        self.bg = pygame.transform.scale(pygame.image.load("./data/images/bg.jpg"), (WIDTH_WINDOW, HEIGHT_WINDOW))
        # theme setting
        font = pygame_menu.font.FONT_8BIT
        my_theme = pygame_menu.Theme(background_color=(0, 0, 0, 50),
                                     widget_background_color=(0, 255, 0, 50),
                                     widget_font_color=(255, 102, 255),
                                     widget_margin=(0, 10),
                                     widget_padding=10,
                                     widget_font=font,
                                     widget_font_size=24,
                                     title_font_size=24
                                     )

        self.menu = pygame_menu.Menu('Chess game - Group 1', 300, 300,
                                     theme=my_theme)
        self.menu.add.button("Play", button_id='PvP')
        self.menu.add.button("Play with AI", button_id='PvC')
        self.menu.add.button("Quit", sys.exit, 1)

        self.running = True

    def mainLoop(self):
        while self.running:
            events = pygame.event.get()
            self.menu.update(events)

            self._draw_background()
            self.menu.draw(self.screen)
            pygame.display.update()

    def _draw_background(self):
        self.screen.blit(self.bg, (0, 0))
