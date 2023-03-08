def move_print_detail(move):
    print("is Enpassant: ", move.isEnpassant)
    print("sqStart : ", move.sqStart)
    print("sqEnd: ", move.sqEnd)
    print("capture Piece: ", move.capturedPiece)


def turn_print(turn):
    if turn == 'w':
        print("Turn belongs to white")
    else:
        print("Turn belongs to black")


def getNumberOfMoves(moves):
    print(f'It has total {len(moves)} possible moves')


def logGameStatus(capturePieces: type({})):
    print("Display game status:")
    print("-------------------------White-------------------------")
    for u, v in capturePieces.items():
        print(u, v, sep=" : ", end='\n')

    print("-------------------------Black-------------------------")


def printBoard(board):
    print('[', end='')
    for i in range(8):
        str = ','.join(board[i])
        print('[', end='')
        print(str, end='],')
        print('')
    print(']')


def print_squares(squares):
    print("Print Square")
    for square in squares:
        print(f'({square[0]},{square[1]})', end="     ")
    print("")


def printPinAndCheck(pins, checks):
    if len(checks) == 0:
        print("No checker")
    if len(pins) == 0:
        print("No pinner")

    print("Print checks: ")
    for i in range(len(checks)):
        print("Tọa độ: ", checks[i][0][0], checks[i][0][1], "Hướng: ", checks[i][1][0], checks[i][1][1], sep=", ",
              end="\n")

    print("Print pins: ")
    for i in range(len(pins)):
        print("Điểm pin: ", pins[i][0][0], pins[i][0][1], "Điểm check: ", pins[i][1][0], pins[i][0][1], sep=", ",
              end="\n")
