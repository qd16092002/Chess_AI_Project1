import math

import pygame
import pygame_gui.elements

from engine.AIEngine import AIEngine
from GameMode.GameInit import GameInit
from multiprocessing import Process, Queue
from data.config import *


class PlayAIMode(GameInit):

    def __init__(self):
        super().__init__()
        self.aiTurn = 'b'
        self.aiEngine = AIEngine(self.aiTurn)
        self.screen = pygame.display.set_mode((WIDTH_WINDOW_AI, HEIGHT_WINDOW_AI))
        self.manager.set_window_resolution((WIDTH_WINDOW_AI, HEIGHT_WINDOW_AI))
        self.__loadGUIAI()

        self.total_nodes_log = []
        self.total_branch_cutoff_log = []
        self.total_nodes_leaf_log = []
        self.executionTime_log = []
        self.signal = True

        self.editAIPanel()

        self.human_turn = True
        self.ai_thinking = False
        self.isEndGame = False
        self.find_move_process = None
        self.q = Queue()

    def mainLoop(self):

        while self.running:
            self.time_delta = self.clock.tick(MAX_FPS) / 1000
            self.human_turn = self.gs.turn != self.aiTurn
            self.__eventHandler()

            if not self.human_turn and self.signal and not self.gameOver:
                self.__AIProcess()

            if self.moveMade:
                if not self.human_turn:
                    self.validMoves = self.gs.getValidMoves()
                    # if len(self.validMoves) == 0:
                    #     self.gameOver = True
                    self.editAIPanel()
                # else:
                #     if self.aiEngine.bestMove is None:
                #         self.gameOver = True

                self.isEndGame = self.__checkEndGame(self.gs)
                self.aiEngine.isEndGame = self.isEndGame
                print("end game: ",self.isEndGame)
                self.editChessPanel()
                self.moveMade = False
                self.signal = True

            #   Update screen
            self.manager.update(self.time_delta)
            self.drawGameScreen()
            pygame.display.update()

    def __AIProcess(self):
        if not self.ai_thinking:
            self.find_move_process = Process(target=self.aiEngine.AlphaBetaPruning,
                                             args=(self.gs, DEPTH, - math.inf, math.inf,
                                                   self.q))

            self.find_move_process.start()
            self.ai_thinking = True
        if not self.find_move_process.is_alive():
            self.aiEngine = self.q.get()
            self.ai_thinking = False
            if self.aiEngine.bestMove:
                self.gs.makeMove(self.aiEngine.bestMove)
                if self.aiEngine.bestMove.capturedPiece == '--':
                    pygame.mixer.Sound.play(self.sound_move)
                else:
                    pygame.mixer.Sound.play(self.sound_capture)

                print("------------------")
                print(f"Total time:  {self.aiEngine.executionTime}")
                print(f"Time generate moves: {self.aiEngine.timeGenerateMoves}")
                print("------------------")

                self.total_nodes_log.append(self.aiEngine.total_node)
                self.total_branch_cutoff_log.append(self.aiEngine.total_branch_cutoff)
                self.total_nodes_leaf_log.append(self.aiEngine.total_nodes_leaf)
                self.executionTime_log.append(self.aiEngine.executionTime)

            self.moveMade = True

    def __eventHandler(self):
        for event in pygame.event.get():
            # Event occurs when click X button
            if event.type == pygame.QUIT:
                print("Game Quit")
                self.running = False
            # Event occurs when press into a key
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.human_turn:
                    self.clickUserHandler()

            elif event.type == pygame.KEYDOWN:
                # Press r to reset
                if event.key == pygame.K_r:
                    if self.ai_thinking:
                        self.find_move_process.terminate()
                    self.__reset()

                # Press z to undo
                elif event.key == pygame.K_z:
                    if self.ai_thinking:
                        self.find_move_process.terminate()
                        self.ai_thinking = False
                    self.gs.undoMove()
                    self.guiAIUndo()
                    self.editAIPanel()
                    self.moveMade = True
                    self.signal = False
                    self.gameOver = False

            self.manager.process_events(event)

    def __loadGUIAI(self):
        self.ai_panel = pygame_gui.elements.UIWindow(
            rect=pygame.Rect((LEFT_AI, TOP_AI), (WIDTH_AI, HEIGHT_AI)),
            manager=self.manager,
            window_display_title='Panel AI',
            draggable=False
        )

        self.text_box_ai = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect((LEFT_AI_BOX, TOP_AI_BOX), (WIDTH_AI_BOX, HEIGHT_AI_BOX)),
            html_text='',
            manager=self.manager,
            container=self.ai_panel
        )

        self.label_algo = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((LEFT_TURN, TOP_TURN), (WIDTH_LABEL_AI, HEIGHT_LABEL_AI)),
            text='Algorithm : ', manager=self.manager,
            container=self.ai_panel
        )

        self.label_depth = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((LEFT_POSSIBLE_MOVE, TOP_POSSIBLE_MOVE), (WIDTH_LABEL_AI, HEIGHT_LABEL)),
            text='DEPTH: ' + str(DEPTH), manager=self.manager,
            container=self.ai_panel
        )

        self.label_maxScore = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((LEFT_INCHECK, TOP_INCHECK), (WIDTH_LABEL_AI, HEIGHT_LABEL)),
            text='Max Score: 0', manager=self.manager,
            container=self.ai_panel
        )

    def guiAIUndo(self):
        if self.executionTime_log and self.human_turn:
            self.executionTime_log.pop()
            self.total_nodes_log.pop()
            self.total_branch_cutoff_log.pop()
            self.total_nodes_leaf_log.pop()

    def editAIPanel(self):
        self.label_algo.set_text("Algorithm: " + self.aiEngine.algoSearch)
        self.label_maxScore.set_text("Max Score: " + str(self.aiEngine.maxScore))

        self.text_box_ai.set_text(self.__getTextBoxAI())

    def __getTextBoxAI(self):
        s = '{0:4}{1:9}{2:9}{3:9}{4:4}\n'.format("", "Nodes", "CutOff", "Eval", "Time")
        for i in range(len(self.total_nodes_log)):
            s += '{0:4}{1:<9}{2:<9}{3:<9}{4:<4}\n' \
                .format(f"{i + 1}.", self.total_nodes_log[i],
                        self.total_branch_cutoff_log[i],
                        self.total_nodes_leaf_log[i],
                        str(self.executionTime_log[i])[:6])
        return s

    def __reset(self):
        self.__init__()
        print("Reset game")

    @staticmethod
    def __checkEndGame(gs):
        if gs.piece_ingame['wQ'] == 0 and gs.piece_ingame['bQ'] == 0:
            return True
        if gs.piece_ingame['wQ'] == 1 and gs.piece_ingame['bQ'] == 1:
            white_minor_piece = 0
            black_minor_piece = 0
            for u,v in gs.piece_ingame.items():
                if u[1] == 'N' or u[1] == 'B':
                    if u[0] == 'w':
                        white_minor_piece += v
                    else:
                        black_minor_piece += v
            if white_minor_piece <= 1 and black_minor_piece <= 1:
                return True

        return False