class GameState:
    rival = {'b': 'w', 'w': 'b'}
    trans = {'b': 'Black', 'w': "White"}

    def __init__(self):

        self.getFunctionMove = {'p': self._getPawnMoves, 'R': self._getRookMoves,
                                'N': self._getKnightMoves, 'B': self._getBishopMoves,
                                'Q': self._getQueenMoves, 'K': self._getKingMoves}
        self.piece_ingame = {'wp': 8, 'wR': 2,
                             'wN': 2, 'wB': 2,
                             'wQ': 1, 'wK': 1,
                             'bp': 8, 'bR': 2,
                             'bN': 2, 'bB': 2,
                             'bQ': 1, 'bK': 1
                             }

        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

        self.turn = 'w'
        self.moveLog = []

        self.kingLocation = {'w': (7, 4), 'b': (0, 4)}
        self.inCheck = False

        self.enpassant_possible = ()
        self.enpassant_log = [()]
        # Format in ((x_pin,y_pin), (x_check,y_check), (dx,dy))
        self.pins = []
        # Format in ((x,y), (dx,dy))
        self.checks = []

        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(True, True, True, True)]

    def makeMove(self, move):

        if move.capturedPiece != '--':
            self.piece_ingame[move.capturedPiece] -= 1
        if move.isPawnPromotion:
            if self.turn == 'w':
                self.piece_ingame['wp'] -= 1
                self.piece_ingame['wQ'] += 1
            else:
                self.piece_ingame['bp'] -= 1
                self.piece_ingame['bQ'] += 1

        # Edit board
        self.board[move.sqEnd[0]][move.sqEnd[1]] = self.board[move.sqStart[0]][move.sqStart[1]]
        self.board[move.sqStart[0]][move.sqStart[1]] = '--'

        # If King move
        if move.movePiece[1] == 'K':
            self.kingLocation[self.turn] = (move.sqEnd[0], move.sqEnd[1])

        # If pawn promotion
        if move.isPawnPromotion:
            self.board[move.sqEnd[0]][move.sqEnd[1]] = self.turn + 'Q'
        v_enpassant = {'b': -1, 'w': 1}

        # If en passant move
        if move.isEnpassant:
            square_attacked = (move.sqEnd[0] + v_enpassant[move.movePiece[0]], move.sqEnd[1])
            self.board[square_attacked[0]][square_attacked[1]] = "--"

        # Detect en passant
        if move.movePiece[1] == 'p' and abs(move.sqStart[0] - move.sqEnd[0]) == 2:
            des = move.sqEnd
            self.enpassant_possible = ((move.sqStart[0] + move.sqEnd[0]) // 2, (move.sqStart[1] + move.sqEnd[1]) // 2)
        else:
            self.enpassant_possible = ()

        self.enpassant_log.append(self.enpassant_possible)

        # castle move
        if move.is_castle_move:
            if move.sqEnd[1] - move.sqStart[1] == 2:  # king-side castle move
                self.board[move.sqStart[0]][move.sqStart[1] + 1] = f'{self.turn}R'
                self.board[move.sqEnd[0]][move.sqEnd[1] + 1] = '--'  # erase old rook

            else:  # queen-side castle move
                self.board[move.sqStart[0]][move.sqStart[1] - 1] = f'{self.turn}R'
                self.board[move.sqEnd[0]][move.sqEnd[1] - 2] = '--'  # erase old rook

        self.updateCastleRights(move)
        self.castle_rights_log.append(
            CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                         self.current_castling_rights.wqs, self.current_castling_rights.bqs))
        self.turn = self.rival[self.turn]
        self.moveLog.append(move)

    def undoMove(self):
        if self.moveLog:
            move = self.moveLog.pop()


            self.board[move.sqStart[0]][move.sqStart[1]] = move.movePiece
            self.board[move.sqEnd[0]][move.sqEnd[1]] = move.capturedPiece
            self.turn = self.rival[self.turn]

            if move.capturedPiece != '--':
                self.piece_ingame[move.capturedPiece] += 1
            if move.isPawnPromotion:
                if self.turn == 'w':
                    self.piece_ingame['wp'] += 1
                    self.piece_ingame['wQ'] -= 1
                else:
                    self.piece_ingame['bp'] += 1
                    self.piece_ingame['bQ'] -= 1


            # If king move, update king position
            if move.movePiece[1] == 'K':
                self.kingLocation[self.turn] = (move.sqStart[0], move.sqStart[1])

            # If en passant move: restore pawn piece
            v_enpassant = {'b': -1, 'w': 1}
            if move.isEnpassant:
                # Get position of attacked pawn piece
                square_attacked = (move.sqEnd[0] + v_enpassant[move.movePiece[0]], move.sqEnd[1])
                self.board[move.sqEnd[0]][move.sqEnd[1]] = '--'
                self.board[square_attacked[0]][square_attacked[1]] = move.capturedPiece

            self.enpassant_log.pop()
            self.enpassant_possible = self.enpassant_log[-1]

            # undo castle rights
            self.castle_rights_log.pop()
            self.current_castling_rights = self.castle_rights_log[-1]

            if move.is_castle_move:
                if move.sqEnd[1] - move.sqStart[1] == 2:  # king-side castle move
                    self.board[move.sqStart[0]][move.sqStart[1] + 1] = '--'
                    self.board[move.sqEnd[0]][move.sqEnd[1] + 1] = f'{self.turn}R'

                else:  # queen-side castle move
                    self.board[move.sqStart[0]][move.sqStart[1] - 1] = '--'
                    self.board[move.sqEnd[0]][move.sqEnd[1] - 2] = f'{self.turn}R'

    def getValidMoves(self):

        temp_castle_rights = CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                          self.current_castling_rights.wqs, self.current_castling_rights.bqs)
        moves = []
        king_moves = self._getKingValidMoves()
        moves.extend(king_moves)
        self.pins, self.checks = self._getPinAndCheckPieces()

        attacked_square = self._getAttackSquare(self.board)

        num_checkers = len(self.checks)
        if num_checkers != 0:
            self.inCheck = True

        if num_checkers == 0:
            self.inCheck = False
            #   Get move of pin piece
            for pin in self.pins:
                type_pin = self.board[pin[0][0]][pin[0][1]][1]
                # Get square between check and king
                dx = abs(pin[1][0] - self.kingLocation[self.turn][0])
                dy = abs(pin[1][1] - self.kingLocation[self.turn][1])
                if dx == dy:
                    d = dx
                else:
                    d = dx + dy
                square = []
                for i in range(1, d + 1):
                    square.append((self.kingLocation[self.turn][0] + i * pin[2][0],
                                   self.kingLocation[self.turn][1] + i * pin[2][1]))
                moves_pin = self.getFunctionMove[type_pin](pin[0][0], pin[0][1], self.board)
                for move in moves_pin:
                    if move.sqEnd in square:
                        moves.append(move)

            #   Get move of another piece
            pin_tmp = [i[0] for i in self.pins]
            for i in range(8):
                for j in range(8):
                    # Check black or white
                    if self.turn == self.board[i][j][0]:
                        # Check type of piece
                        piece = self.board[i][j][1]
                        if (i, j) not in pin_tmp and piece != 'K':
                            moves.extend(self.getFunctionMove[piece](i, j, self.board))

            # Get castle move
            self.getCastleMoves(moves, attacked_square)

        elif num_checkers == 1:
            # Get capture move
            capture_moves = []
            all_move = []
            for i in range(8):
                for j in range(8):
                    # Check black or white
                    if self.turn == self.board[i][j][0]:
                        # Check type of piece
                        piece = self.board[i][j][1]
                        if piece != 'K':
                            all_move.extend(self.getFunctionMove[piece](i, j, self.board))

            for move in all_move:
                if move.sqEnd == self.checks[0][0]:
                    capture_moves.append(move)

            # Get push move
            push_move = []
            type_check = self.board[self.checks[0][0][0]][self.checks[0][0][1]][1]
            if type_check == 'R' or type_check == 'B' or type_check == 'Q':

                # Get square between king and check
                square = []
                dx = abs(self.checks[0][0][0] - self.kingLocation[self.turn][0])
                dy = abs(self.checks[0][0][1] - self.kingLocation[self.turn][1])
                if dx == dy:
                    d = dx
                else:
                    d = dx + dy
                for i in range(1, d):
                    square.append((self.kingLocation[self.turn][0] + i * self.checks[0][1][0],
                                   self.kingLocation[self.turn][1] + i * self.checks[0][1][1]))
                for move in all_move:
                    if move.sqEnd in square:
                        push_move.append(move)

            moves.extend(push_move)
            moves.extend(capture_moves)
        else:
            moves = king_moves

        # if not moves:
        #     print("Check mate")
        self.current_castling_rights = temp_castle_rights

        return moves

    def _getKingValidMoves(self):

        boardCopy = [row[:] for row in self.board]
        boardCopy[self.kingLocation[self.turn][0]][self.kingLocation[self.turn][1]] = '--'
        kingMoves = []

        # Lấy các nước đi của vua
        tmp = self._getKingMoves(self.kingLocation[self.turn][0], self.kingLocation[self.turn][1], self.board)

        # Lấy các ô có thể bị tấn công bởi đối thủ
        attack_square = self._getAttackSquare(boardCopy)
        # Kiểm tra nước đi của vua có hợp lệ hay không
        for move in tmp:
            if move.sqEnd not in attack_square:
                kingMoves.append(move)
        return kingMoves

    def _getAttackSquare(self, boardCopy):
        attackSquare = []
        self.turn = self.rival[self.turn]
        for i in range(8):
            for j in range(8):
                # Check black or white
                if self.turn == boardCopy[i][j][0]:
                    # Check type of piece
                    piece = self.board[i][j][1]
                    moves = self.getFunctionMove[piece](i, j, boardCopy, True)
                    for move in moves:
                        attackSquare.append(move.sqEnd)

        self.turn = self.rival[self.turn]
        return attackSquare

    def _getPinAndCheckPieces(self):

        checks = []
        pins = []
        sqStart = self.kingLocation[self.turn]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1))

        for i in range(len(directions)):
            direction = directions[i]
            j = 1
            possible_pin = ()
            while True:
                sqEnd = (sqStart[0] + j * direction[0], sqStart[1] + j * direction[1])
                if self._checkValidRowCol(sqEnd):
                    piece = self.board[sqEnd[0]][sqEnd[1]]
                    if piece[0] == self.turn:
                        if possible_pin:
                            break
                        else:
                            possible_pin = (sqEnd[0], sqEnd[1])
                    elif piece[0] == self.rival[self.turn]:
                        if (0 <= i <= 3 and piece[1] == "R") or (4 <= i <= 7 and piece[1] == "B") or (
                                j == 1 and piece[1] == "p" and (
                                (piece[0] == "w" and 6 <= i <= 7) or (piece[0] == "b" and 4 <= i <= 5))) or (
                                piece[1] == "Q"):
                            if possible_pin:
                                pins.append((possible_pin, sqEnd, direction))
                                break
                            else:
                                checks.append((sqEnd, direction))
                                break
                        else:
                            break
                    j += 1
                else:
                    break

        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2),
                        (2, -1), (2, 1), (-1, -2), (1, -2))

        for move in knight_moves:
            sqEnd = (sqStart[0] + move[0], sqStart[1] + move[1])
            if self._checkValidRowCol(sqEnd):
                end_piece = self.board[sqEnd[0]][sqEnd[1]]
                # enemy knight attacking a king
                if end_piece[0] == self.rival[self.turn] and end_piece[1] == "N":
                    checks.append((sqEnd, move))

        return pins, checks

    def _getPawnMoves(self, r, c, board, attackAble=False):
        moves = []
        vP = {'b': [(2, 0), (1, 0), (1, 1), (1, -1)],
              'w': [(-2, 0), (-1, 0), (-1, 1), (-1, -1)]}
        if attackAble:
            des = (r + vP[self.turn][2][0], c + vP[self.turn][2][1])
            if self._checkValidRowCol(des):
                moves.append(Move((r, c), des, board))

            des = (r + vP[self.turn][3][0], c + vP[self.turn][3][1])
            if self._checkValidRowCol(des):
                moves.append(Move((r, c), des, board))
            return moves

        # Check special move and detect en passant movself.board
        if self.turn == 'b' and r == 1:
            des = (r + vP[self.turn][0][0], c)
            mid = ((des[0] + r) // 2, (des[1] + c) // 2)
            if board[des[0]][des[1]] == '--' and board[mid[0]][mid[1]] == '--':
                moves.append(Move((r, c), des, board))

        if self.turn == 'w' and r == 6:
            des = (r + vP[self.turn][0][0], c)
            mid = ((des[0] + r) // 2, (des[1] + c) // 2)
            if board[des[0]][des[1]] == '--' and board[mid[0]][mid[1]] == '--':
                moves.append(Move((r, c), des, board))

        des = (r + vP[self.turn][1][0], c)
        if self._checkValidRowCol(des) and board[des[0]][des[1]] == '--':
            moves.append(Move((r, c), des, board))

        # Check attack move and en passant attack

        des = (r + vP[self.turn][2][0], c + vP[self.turn][2][1])
        if self._checkValidRowCol(des) and board[des[0]][des[1]][0] == self.rival[self.turn]:
            moves.append(Move((r, c), des, board))
        if des == self.enpassant_possible:
            move = Move((r, c), des, board, enPassantSquare=self.enpassant_possible)
            # print("-------------------Generator Move en passant --------------------")
            # util.move_print_detail(move)
            # print("-------------------Generator Move en passant --------------------")
            moves.append(move)

        des = (r + vP[self.turn][3][0], c + vP[self.turn][3][1])
        if self._checkValidRowCol(des) and board[des[0]][des[1]][0] == self.rival[self.turn]:
            moves.append(Move((r, c), des, board))
        if des == self.enpassant_possible:
            move = Move((r, c), des, board, enPassantSquare=self.enpassant_possible)
            moves.append(move)
            # print("-------------------Generator Move en passant --------------------")
            # util.move_print_detail(move)
            # print("-------------------Generator Move en passant --------------------")

        return moves

    def _getKnightMoves(self, r, c, board, attackAble=False):
        moves = []
        vN = {'b': [(2, 1), (2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2), (-2, 1), (-2, -1)],
              'w': [(-2, -1), (-1, -2), (-2, 1), (-1, 2), (2, 1), (2, -1), (1, 2), (1, -2)]}
        start = (r, c)
        # can attack
        for i in range(8):
            end = (r + vN[self.turn][i][0], c + vN[self.turn][i][1])
            if self._checkValidRowCol(end) and (attackAble or self._checkCollision(start, end, board)):
                moves.append(Move(start, end, board))
        return moves

    def _getRookMoves(self, r, c, board, attackAble=False):
        moves = []
        vR = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        start = (r, c)
        for i in range(4):
            j = 1
            while True:
                end = (r + j * vR[i][0], c + j * vR[i][1])
                if self._checkValidRowCol(end):
                    typeCollision = self._checkCollision(start, end, board)
                    if typeCollision == 2:
                        moves.append(Move(start, end, board))
                        j += 1
                    elif typeCollision == 1 or (typeCollision == 0 and attackAble):
                        moves.append(Move(start, end, board))
                        break
                    else:
                        break
                else:
                    break
        return moves

    def _getBishopMoves(self, r, c, board, attackAble=False):
        moves = []
        vB = [(1, 1), (-1, -1), (-1, 1), (1, -1)]
        start = (r, c)
        for i in range(4):
            j = 1
            while True:
                end = (r + j * vB[i][0], c + j * vB[i][1])
                if self._checkValidRowCol(end):
                    typeCollision = self._checkCollision(start, end, board)
                    if typeCollision == 2:
                        moves.append(Move(start, end, board))
                        j += 1
                    elif typeCollision == 1 or (typeCollision == 0 and attackAble):
                        moves.append(Move(start, end, board))
                        break
                    else:
                        break
                else:
                    break
        return moves

    def _getQueenMoves(self, r, c, board, attackAble=False):
        return self._getRookMoves(r, c, board, attackAble) + self._getBishopMoves(r, c, board, attackAble)

    def _getKingMoves(self, r, c, board, attackAble=False):
        moves = []
        start = (r, c)
        vK = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1)]

        for i in range(8):
            end = (r + vK[i][0], c + vK[i][1])
            if self._checkValidRowCol(end) and (attackAble or self._checkCollision(start, end, board)):
                moves.append(Move(start, end, board))

        return moves

    def updateCastleRights(self, move):
        if move.capturedPiece == "wR":
            if move.sqEnd[1] == 0:  # left rook
                self.current_castling_rights.wqs = False
            elif move.sqEnd[1] == 7:  # right rook
                self.current_castling_rights.wks = False
        elif move.capturedPiece == "bR":
            if move.sqEnd[1] == 0:  # left rook
                self.current_castling_rights.bqs = False
            elif move.sqEnd[1] == 7:  # right rook
                self.current_castling_rights.bks = False

        if move.movePiece == 'wK':
            self.current_castling_rights.wqs = False
            self.current_castling_rights.wks = False
        elif move.movePiece == 'bK':
            self.current_castling_rights.bqs = False
            self.current_castling_rights.bks = False
        elif move.movePiece == 'wR':
            if move.sqStart == (7, 0):
                self.current_castling_rights.wqs = False
            elif move.sqStart == (7, 7):  # right rook
                self.current_castling_rights.wks = False
        elif move.movePiece == 'bR':
            if move.sqStart == (0, 0):
                self.current_castling_rights.bqs = False
            if move.sqStart == (0, 7):
                self.current_castling_rights.bks = False

    def getCastleMoves(self, moves, attacked_square):

        if self.turn == 'w':
            if self.current_castling_rights.wks:
                self.getKingSideCastleMoves(moves, attacked_square)
            if self.current_castling_rights.wqs:
                self.getQueenSideCastleMoves(moves, attacked_square)

        else:
            if self.current_castling_rights.bks:
                self.getKingSideCastleMoves(moves, attacked_square)
            if self.current_castling_rights.bqs:
                self.getQueenSideCastleMoves(moves, attacked_square)

    def getKingSideCastleMoves(self, moves, attacked_square):
        r = self.kingLocation[self.turn][0]
        c = self.kingLocation[self.turn][1]
        # print(r,c,sep="   ")
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.squareUnderAttack(r, c + 1, attacked_square) and not self.squareUnderAttack(r, c + 2,
                                                                                                    attacked_square):
                moves.append(Move((r, c), (r, c + 2),
                                  self.board, is_castle_move=True))

    def getQueenSideCastleMoves(self, moves, attacked_square):
        r = self.kingLocation[self.turn][0]
        c = self.kingLocation[self.turn][1]
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.squareUnderAttack(r, c - 1, attacked_square) and not self.squareUnderAttack(r, c - 2,
                                                                                                    attacked_square):
                moves.append(Move((r, c), (r, c - 2),
                                  self.board, is_castle_move=True))

    @staticmethod
    def squareUnderAttack(r, c, attacked_square):
        if (r, c) in attacked_square:
            return True
        return False

    @staticmethod
    def _checkValidRowCol(p):
        if p[0] in range(8) and p[1] in range(8):
            return True
        return False

    @staticmethod
    def _checkCollision(start, end, board):
        # 0 represent collision with same team
        # 1 represent collision with enemy
        # 2 represent no collision
        if board[end[0]][end[1]][0] == '-':
            return 2
        if board[start[0]][start[1]][0] == board[end[0]][end[1]][0]:
            return 0
        return 1

    def getMoveNotation(self):
        s = '{0:4}{1:7}{2:7}'.format("", "White", "Black")
        move_turn = 0
        for move in self.moveLog:
            if move_turn % 2 == 0:
                turn = f'{str(move_turn // 2 + 1)}.'
                s += '\n{0:4}'.format(turn)
            s += '{0:7}'.format(move.getChessNotation())
            move_turn += 1
        return s

    def getTurn(self):
        s = f"Turn: {self.trans[self.turn]}"
        return s


class Move:
    """
    Class represent a move in game.
    It contains:  starting point coordinates, ending point coordinates, piece move and piece is captured
    """
    _rankMap = {0: 8, 1: 7, 2: 6, 3: 5, 4: 4, 5: 3, 6: 2, 7: 1}
    _fileMap = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}

    def __init__(self, sqStart, sqEnd, board, enPassantSquare=(), is_castle_move=False):
        self.sqStart = sqStart
        self.sqEnd = sqEnd
        self.movePiece = board[sqStart[0]][sqStart[1]]
        self.capturedPiece = board[sqEnd[0]][sqEnd[1]]

        self.isPawnPromotion = self.movePiece[1] == 'p' and self.sqEnd[0] in (0, 7)

        self.isEnpassant = (enPassantSquare != ())
        if self.isEnpassant:
            rival = {'w': 'b', 'b': 'w'}
            self.capturedPiece = f'{rival[self.movePiece[0]]}p'

        self.is_castle_move = is_castle_move

        self.moveID = 1000 * self.sqStart[0] + 100 * self.sqStart[1] + 10 * self.sqEnd[0] + self.sqEnd[1]

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getRankFile(self, r, c):
        return self._fileMap[c] + str(self._rankMap[r])

    def getChessNotation(self):

        if self.isPawnPromotion:
            return self.getRankFile(self.sqEnd[0], self.sqEnd[1]) + "Q"

        if self.is_castle_move:
            if self.sqEnd[1] == 1:
                return "0-0-0"
            else:
                return "0-0"

        if self.isEnpassant:
            return self.getRankFile(self.sqStart[0], self.sqStart[1])[0] + "x" + self.getRankFile(self.sqEnd[0],
                                                                                                  self.sqEnd[
                                                                                                      1]) + " e.p."
        if self.capturedPiece != "--":
            if self.movePiece[1] == "p":
                return self.getRankFile(self.sqStart[0], self.sqStart[1])[0] + "x" + self.getRankFile(self.sqEnd[0],
                                                                                                      self.sqEnd[1])
            else:
                return self.movePiece[1] + "x" + self.getRankFile(self.sqEnd[0], self.sqEnd[1])
        else:
            if self.movePiece[1] == "p":
                return self.getRankFile(self.sqEnd[0], self.sqEnd[1])
            else:
                return self.movePiece[1] + self.getRankFile(self.sqEnd[0], self.sqEnd[1])


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

    def __eq__(self, other):
        if self.wks == other.wks and self.bks == other.bks and self.wqs == other.wqs and self.bqs == other.bqs:
            return True
        return False
