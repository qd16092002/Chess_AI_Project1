import pygame
import pygame_gui

from engine.ChessEngine import GameState
from data.config import *


class GameInit:
    def __init__(self):

        self.screen = pygame.display.get_surface()
        self.IMAGES = {}

        self.__loadImages()
        self.image_black_win = pygame.transform.scale(pygame.image.load('./data/images/black_win.jpg'), (2.62*SQ_SIZE,SQ_SIZE))
        self.image_black_win.set_alpha(200)
        self.image_white_win = pygame.transform.scale(pygame.image.load('./data/images/white_win.jpg'), (2.62*SQ_SIZE,SQ_SIZE))
        self.image_white_win.set_alpha(200)

        self.__loadSound()

        # Surface for board game
        self.background = pygame.Surface((WIDTH_WINDOW_AI, HEIGHT_WINDOW_AI))
        self.background.fill((32, 32, 32))

        #   ---------------------------------- GUI ----------------------------------   #
        self.manager = pygame_gui.UIManager((WIDTH_WINDOW, HEIGHT_WINDOW), theme_path="./data/theme_custom.json")
        self.__loadGUI()

        self.gs = GameState()
        self.clock = pygame.time.Clock()

        self.click = ()  # Represent location of square which is pushed by mouse
        self.playerClicks = []
        self.moveMade = False
        self.validMoves = self.gs.getValidMoves()
        self.running = True
        self.gameOver = False

        self.editChessPanel()

    def __loadGUI(self):

        self.chess_panel = pygame_gui.elements.UIWindow(
            rect=pygame.Rect((LEFT_PANEL, TOP_PANEL), (WIDTH_PANEL, HEIGHT_PANEL)),
            manager=self.manager,
            window_display_title='Panel chess'
        )

        self.text_box = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect((LEFT_MOVE_BOX, TOP_MOVE_BOX), (WIDTH_MOVE_BOX, HEIGHT_MOVE_BOX)),
            html_text='',
            manager=self.manager,
            container=self.chess_panel
        )

        self.label_turn = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((LEFT_TURN, TOP_TURN), (WIDTH_LABEL, HEIGHT_LABEL)),
            text='Turn: ', manager=self.manager,
            container=self.chess_panel
        )

        self.label_possible_move = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((LEFT_POSSIBLE_MOVE, TOP_POSSIBLE_MOVE), (WIDTH_LABEL, HEIGHT_LABEL)),
            text='Possible moves: ', manager=self.manager,
            container=self.chess_panel
        )

        self.label_incheck = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((LEFT_INCHECK, TOP_INCHECK), (WIDTH_LABEL, HEIGHT_LABEL)),
            text='In Check : ', manager=self.manager,
            container=self.chess_panel
        )

    def __loadImages(self):
        pieces = ['wp', 'wR', 'wN', 'wB', 'wK',
                  'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
        for piece in pieces:
            self.IMAGES[piece] = pygame.transform.scale(pygame.image.load(f"data/images/chess/{piece}.png"),
                                                        (SQ_SIZE, SQ_SIZE))

    # Load sound into memory
    def __loadSound(self):
        self.sound_move = pygame.mixer.Sound('./data/sound/move.wav')
        self.sound_capture = pygame.mixer.Sound('./data/sound/capture.wav')

    def drawGameScreen(self):
        self.screen.blit(self.background, (0, 0))
        self.drawBoard()
        self.drawLastMove()
        self.drawPiece()
        self.highlightSquares()
        self.screen.blit(self.screen, (0, 0))
        self.manager.draw_ui(self.screen)
        if self.gameOver:
            self.drawGameOver()

    def drawLastMove(self):
        if self.gs.moveLog:
            lastMove = self.gs.moveLog[-1]
            surface = pygame.Surface((SQ_SIZE, SQ_SIZE))
            surface.set_alpha(100)
            surface.fill((153, 255, 255))
            x, y = lastMove.sqStart[0], lastMove.sqStart[1]
            x1, y1 = lastMove.sqEnd[0], lastMove.sqEnd[1]
            self.screen.blit(surface, (y * SQ_SIZE, x * SQ_SIZE))
            self.screen.blit(surface, (y1 * SQ_SIZE, x1 * SQ_SIZE))

    def drawBoard(self):
        for i in range(DIMENSION):
            for j in range(DIMENSION):
                color = colorBoard[(i + j) % 2]
                x = i * SQ_SIZE
                y = j * SQ_SIZE
                pygame.draw.rect(self.screen, color, pygame.Rect(x, y, SQ_SIZE, SQ_SIZE))

    def drawPiece(self):
        for i in range(DIMENSION):
            for j in range(DIMENSION):
                piece = self.gs.board[i][j]
                if piece != "--":
                    self.screen.blit(self.IMAGES[piece], pygame.Rect(j * SQ_SIZE, i * SQ_SIZE, SQ_SIZE, SQ_SIZE))

    def drawGameOver(self):
        if self.gs.turn == 'w':
            self.screen.blit(self.image_black_win, (191, 223))
        else:
            self.screen.blit(self.image_white_win, (191, 223))

    def highlightSquares(self):
        sqHighlight = []

        if self.click:
            for move in self.validMoves:
                if move.sqStart == self.click:
                    sqHighlight.append(move.sqEnd)

            for (x, y) in sqHighlight:
                # pygame.draw.rect(screen, colorBoard[2], pygame.Rect(y*SQ_SIZE, x*SQ_SIZE, SQ_SIZE, SQ_SIZE))
                surface = pygame.Surface((SQ_SIZE, SQ_SIZE))
                surface.set_alpha(150)
                surface.fill(colorBoard[2])
                self.screen.blit(surface, (y * SQ_SIZE, x * SQ_SIZE))

    def editChessPanel(self):
        self.text_box.set_text(self.gs.getMoveNotation())
        self.label_turn.set_text(self.gs.getTurn())
        self.label_possible_move.set_text(f'Possible moves: {len(self.validMoves)}')
        self.label_incheck.set_text(f'In Check : {self.gs.inCheck}')

    def clickUserHandler(self):
        pos = pygame.mouse.get_pos()
        x = int(pos[1] / SQ_SIZE)
        y = int(pos[0] / SQ_SIZE)

        # Check valid screen
        if x in range(8) and y in range(8):

            # case when first click is empty piece or another team
            # or first click same as second click
            if self.click == (x, y) or (not self.click and (
                    self.gs.board[x][y] == '--' or self.gs.board[x][y][0] != self.gs.turn)):
                # print('Reset click')
                self.click = ()
                self.playerClicks = []
            else:
                self.click = (x, y)
                self.playerClicks.append(self.click)

            if len(self.playerClicks) == 2:
                id_click = 1000 * self.playerClicks[0][0] + 100 * self.playerClicks[0][1] + 10 * self.playerClicks[1][
                    0] + self.playerClicks[1][1]
                for move in self.validMoves:
                    if move.moveID == id_click:
                        if move.capturedPiece == '--':
                            pygame.mixer.Sound.play(self.sound_move)
                        else:
                            pygame.mixer.Sound.play(self.sound_capture)
                        self.gs.makeMove(move)
                        self.moveMade = True
                        break

                self.click = ()
                self.playerClicks = []
