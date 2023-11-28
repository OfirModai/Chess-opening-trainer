import copy
import random
import statistics

import pygame

from Piece import *

Board: pygame.Rect = None
Recall = []


def get_opposite(color):
    if color == 'white':
        return 'black'
    return 'white'


def get_random(max_value):
    if max_value == 0: return 0
    return random.randint(0, max_value-1)


def set_board(view):
    kings = {}
    pieces = [[None for i in range(8)] for j in range(8)]
    for i in range(8):
        pieces[1][i] = Pawn(get_opposite(view), (1, i), 1)
        pieces[6][i] = Pawn(view, (6, i), -1)
    king_place, queen_place = 3, 4
    if view == 'white':
        king_place, queen_place = 4, 3
    for i in (0, 7):
        color = view
        if i == 0:
            color = get_opposite(view)
        pieces[i][0] = Rook(color, (i, 0))
        pieces[i][1] = Knight(color, (i, 1))
        pieces[i][2] = Bishop(color, (i, 2))
        pieces[i][king_place] = King(color, (i, king_place))
        kings[color] = (pieces[i][king_place])
        pieces[i][queen_place] = Queen(color, (i, queen_place))
        pieces[i][5] = Bishop(color, (i, 5))
        pieces[i][6] = Knight(color, (i, 6))
        pieces[i][7] = Rook(color, (i, 7))
    return pieces, kings


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


def is_move_in(origin, destination, pieces, view, kings, promoting_to, notes):
    pieces = copy.deepcopy(pieces)
    kings = {
        'white': pieces[kings['white'].position[0]][kings['white'].position[1]],
        'black': pieces[kings['black'].position[0]][kings['black'].position[1]]
    }
    note = make_move_and_get_notation(origin, destination, pieces, view, kings, promoting_to)
    return note in notes


def make_move_and_get_notation(origin, destination, pieces, view, kings, promoting_to=None):
    result = ''
    delete_first = False
    piece = pieces[origin[0]][origin[1]]
    if piece.role == 'king' and abs(destination[1] - origin[1]) == 2:
        # castling
        result = 'o-o-o'
        rook_destination = (origin[0], statistics.mean((origin[1], destination[1])))
        x = origin[1] + 2 * (destination[1] - origin[1])
        if x == -1 or x == 8:
            result = 'o-o'
            if x == 8:
                x = 7
            else:
                x = 0

        pieces[rook_destination[0]][rook_destination[1]] = pieces[origin[0]][x]
        pieces[rook_destination[0]][rook_destination[1]].position = rook_destination
        pieces[origin[0]][x] = None
    else:
        result += role_to_letter(piece.role)
        if piece.role == 'pawn':
            delete_first = True
            result += point_to_notation(origin, view)[0]
        # checking if castling rights needs to be taken
        elif piece.role == 'king':
            piece.castling = {'king_side': False, 'queen_side': False}
        elif piece.role == 'rook' and piece.position in ((kings[view].position[0], 0), (kings[view].position[0], 7)):
            if abs(piece.position[1] - kings[view].position[1]) == 3:
                kings[view].castling['king_side'] = False
            else:
                kings[view].castling['queen_side'] = False
        options = []
        for line in pieces:
            for p in line:
                if p is not None and p.role == piece.role and p.color == piece.color and destination in p.get_possible_moves(
                        pieces):
                    options.append(p.position)
        if len(options) > 1 and piece.role != 'pawn':

            options.remove(origin)
            note = point_to_notation(origin, view)
            x, y = True, True
            for option in options:
                if origin[1] == option[1]:
                    x = False
                elif origin[0] == option[0]:
                    y = False
            if x:
                result += note[0]
            elif y:
                result += note[1]
            else:
                result += note

        if pieces[destination[0]][destination[1]] is not None or (type(pieces[origin[0]][origin[1]]) is Pawn
                                                                  and origin[1] != destination[1]):
            delete_first = False
            result += 'x'
        result += point_to_notation(destination, view)
        if promoting_to is not None:
            result += '=' + role_to_letter(promoting_to.role)
            piece = promoting_to
        # piece movement
        if piece.role == 'pawn' and pieces[destination[0]][destination[1]] is None and origin[1] != destination[1]:
            # the pawn took en passant
            pieces[origin[0]][destination[1]] = None

    turn = pieces[origin[0]][origin[1]].color
    pieces[origin[0]][origin[1]] = None
    pieces[destination[0]][destination[1]] = piece
    piece.position = destination
    if kings[get_opposite(turn)].is_attacked(pieces):
        result += '+'
    if delete_first:
        result = result[1:]

    return result


def __move_piece(origin, destination, pieces):
    pieces[destination[0]][destination[1]] = pieces[origin[0]][origin[1]]
    pieces[destination[0]][destination[1]].position = destination
    pieces[origin[0]][origin[1]] = None


def make_move_by_note_and_get_positions(note, pieces, view, turn):
    promote_to = None
    if note[:1] == 'o':
        y = 0
        if turn == view: y = 7
        if note == 'o-o-o':
            if view == 'white':
                __move_piece((y, 4), (y, 2), pieces)
                __move_piece((y, 0), (y, 3), pieces)
            else:
                __move_piece((y, 3), (y, 5), pieces)
                __move_piece((y, 7), (y, 4), pieces)
        else:
            if view == 'white':
                __move_piece((y, 4), (y, 6), pieces)
                __move_piece((y, 7), (y, 5), pieces)
            else:
                __move_piece((y, 3), (y, 1), pieces)
                __move_piece((y, 0), (y, 2), pieces)
        return None
    if note[-1:] == '+': note = note[:-1]
    if note[-2] == '=':
        promote_to = letter_to_Piece(note[-1:])
        note = note[:-2]
    destination = notations_to_point(note[-2:], view)
    role, x, y = None, None, None
    origin = ()
    note = note[:-2]
    if len(note) != 0:
        if note[-1:] == 'x': note = note[:-1]
        if len(note) == 3:
            origin = notations_to_point(note[1:])
        if ord('a') <= ord(note[-1:]) <= ord('h'):
            # we have orientation for column
            x = notations_to_point(note[-1:] + '1', view)[1]
        elif ord('1') <= ord(note[-1:]) <= ord('8'):
            y = notations_to_point('a' + note[-1:], view)[0]
        role = letter_to_Piece(note[:1]).role
    else:
        role = 'pawn'
    if origin == ():
        for line in pieces:
            for piece in line:
                if piece is not None and turn == piece.color and role == piece.role and \
                        destination in piece.get_possible_moves(pieces) and (
                        (x is None or piece.position[1] == x) and (y is None or piece.position[0] == y)):
                    origin = piece.position
    __move_piece(origin, destination, pieces)
    if promote_to is not None:
        pieces[destination[0]][destination[1]] = promote_to
        promote_to.position = destination
        promote_to.color = turn
    return origin, destination
