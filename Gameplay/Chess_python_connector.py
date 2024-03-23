from Gameplay.Pieces.Bishop import Bishop
from Gameplay.Pieces.King import King
from Gameplay.Pieces.Knight import Knight
from Gameplay.Pieces.Pawn import Pawn
from Gameplay.Pieces.Queen import Queen
from Gameplay.Pieces.Rook import Rook


def point_to_notation(point, view):
    result = ''
    if view == 'black':
        result += chr(ord('h') - point[1])
        result += str(point[0] + 1)
    else:
        result += chr(ord('a') + point[1])
        result += str(8 - point[0])
    return result


def notations_to_point(notation, view):
    result = [0, 0]
    if view == 'black':
        result[0] = int(notation[1]) - 1
        result[1] = abs(ord('h') - ord(notation[0]))
    else:
        result[0] = 8 - int(notation[1])
        result[1] = abs(ord('a') - ord(notation[0]))
    return tuple(result)


def role_to_letter(role):
    if role == 'knight':
        return 'N'
    elif role == 'bishop':
        return 'B'
    elif role == 'rook':
        return 'R'
    elif role == 'king':
        return 'K'
    elif role == 'queen':
        return 'Q'
    return ''


def letter_to_Piece(letter):
    if letter == 'N':

        return Knight('white', (0, 0))
    elif letter == 'B':
        return Bishop('white', (0, 0))
    elif letter == 'R':
        return Rook('white', (0, 0))
    elif letter == 'K':
        return King('white', (0, 0))
    elif letter == 'Q':
        return Queen('white', (0, 0))
    return Pawn('white', (0, 0), 1)


def get_opposite(color):
    if color == 'white':
        return 'black'
    return 'white'
