import pygame

from GameMode.GameInit import GameInit
from data.config import *
from data.util import logGameStatus


class PlayMode(GameInit):

    def __init__(self):
        super().__init__()

    def mainLoop(self):
        while self.running:
            self.time_delta = self.clock.tick(MAX_FPS) / 1000
            #   Handle event
            self.__eventHandler()

            #  move update
            if self.moveMade:
                self.validMoves = self.gs.getValidMoves()
                if len(self.validMoves) == 0:
                    self.gameOver = True

                self.editChessPanel()
                self.moveMade = False

            #   Update screen
            self.manager.update(self.time_delta)
            self.drawGameScreen()
            pygame.display.update()

    def __eventHandler(self):
        for event in pygame.event.get():
            # Event occurs when click X button
            if event.type == pygame.QUIT:
                print("Game Quit")
                self.running = False
            # Event occurs when click into screen
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.clickUserHandler()
            # Event occurs when press into a key
            elif event.type == pygame.KEYDOWN:
                # Press r to reset
                if event.key == pygame.K_r:
                    self.__reset()

                # Press z to undo
                elif event.key == pygame.K_z:
                    self.gs.undoMove()
                    self.moveMade = True
                    self.gameOver = False


                elif event.key == pygame.K_u:
                    logGameStatus(self.gs.piece_ingame)

            self.manager.process_events(event)

    def __reset(self):
        self.__init__()
        print("Reset game")
