class Piece:
    COUNT = 0

    def __init__(self, color, position):
        self.color = color
        self.position = position
        Piece.COUNT += 1

    def _clear_self_captures(self, pieces, moves):
        to_remove = []
        for move in moves:
            if pieces[move[0]][move[1]] is not None and pieces[move[0]][move[1]].color == self.color:
                to_remove.append(move)
        moves = [x for x in moves if x not in to_remove]
        return moves

    def get_possible_moves(self, pieces):
        return self._clear_self_captures(pieces, self.get_threats(pieces))


class Pawn(Piece):
    def __init__(self, color, position, direction):
        super().__init__(color, position)
        self.role = 'pawn'
        self.name = 'pawn' + str(Piece.COUNT)
        self.direction = direction
        self.__en_passant = None

    def get_possible_moves(self, pieces):
        moves = []
        if pieces[self.position[0] + self.direction][self.position[1]] is None:
            moves.append((self.position[0] + self.direction, self.position[1]))
            # double square movement if the pawn in his start position is allowed
            if (self.position[0] == self.direction == 1 or (self.position[0] == 6 and self.direction == -1)) and (
                    pieces[self.position[0] + self.direction * 2][self.position[1]] is None):
                moves.append((self.position[0] + self.direction * 2, self.position[1]))

        if self.position[1] + 1 < len(pieces[0]) and (
                pieces[self.position[0] + self.direction][self.position[1] + 1] is not None and
                pieces[self.position[0] + self.direction][self.position[1] + 1].color != self.color):
            moves.append((self.position[0] + self.direction, self.position[1] + 1))

        if self.position[1] - 1 >= 0 and (
                pieces[self.position[0] + self.direction][self.position[1] - 1] is not None and
                pieces[self.position[0] + self.direction][self.position[1] - 1].color != self.color):
            moves.append((self.position[0] + self.direction, self.position[1] - 1))

        if self.__en_passant is not None:
            moves.append(self.__en_passant)
        return moves

    def pawn_passed_in(self, side):
        if side == 'left':
            self.__en_passant = self.position[0] + self.direction, self.position[1] - 1
        elif side == 'right':
            self.__en_passant = self.position[0] + self.direction, self.position[1] + 1

    def turn_is_over(self):
        self.__en_passant = None

    def get_threats(self, pieces):
        moves = []
        if self.position[1] + 1 < len(pieces[0]):
            moves.append((self.position[0] + self.direction, self.position[1] + 1))
        if self.position[1] - 1 >= 0:
            moves.append((self.position[0] + self.direction, self.position[1] - 1))
        return moves


class Rook(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.role = 'rook'
        self.name = 'rook' + str(Piece.COUNT)

    def get_threats(self, pieces):
        moves = []
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if j != 0 and i != 0:
                    continue
                y, x = self.position[0] + i, self.position[1] + j
                while 0 <= y < len(pieces) and 0 <= x < len(pieces[0]):
                    moves.append((y, x))
                    if pieces[y][x] is not None:
                        break
                    x += j
                    y += i
        return moves


class Bishop(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.role = 'bishop'
        self.name = 'bishop' + str(Piece.COUNT)

    def get_threats(self, pieces):
        moves = []
        for i in (-1, 1):
            for j in (-1, 1):
                y, x = self.position[0] + i, self.position[1] + j
                while 0 <= y < len(pieces) and 0 <= x < len(pieces[0]):
                    moves.append((y, x))
                    if pieces[y][x] is not None:
                        break
                    x += j
                    y += i
        return moves


class Knight(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.role = 'knight'
        self.name = 'knight' + str(Piece.COUNT)

    def get_threats(self, pieces):
        moves = []
        for i in (-1, -2, 1, 2):
            for j in (-1, -2, 1, 2):
                if abs(i) != abs(j) and 0 <= self.position[0] + i < len(pieces) and \
                        0 <= self.position[1] + j < len(pieces[0]):
                    moves.append((self.position[0] + i, self.position[1] + j))
        return moves


class Queen(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.role = 'queen'
        self.name = 'queen' + str(Piece.COUNT)

    def get_threats(self, pieces):
        moves = []
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                y, x = self.position[0] + i, self.position[1] + j
                while 0 <= y < len(pieces) and 0 <= x < len(pieces[0]):
                    moves.append((y, x))
                    if pieces[y][x] is not None:
                        break
                    x += j
                    y += i
        return moves


class King(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.role = 'king'
        self.name = 'king' + str(Piece.COUNT)
        self.castling = {'king_side': True, 'queen_side': True}

    def get_threats(self, pieces):
        moves = []
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                y, x = self.position[0] + i, self.position[1] + j
                if 0 <= y < len(pieces) and 0 <= x < len(pieces[0]):
                    moves.append((y, x))
        return moves

    def get_possible_moves(self, pieces):
        moves = super().get_possible_moves(pieces)
        if True in self.castling.values():
            for direction in (-1, 1):
                empty = True
                i = self.position[1] + direction
                while empty and 0 < i < 7:
                    if pieces[self.position[0]][i] is not None \
                            or (abs(self.position[1] - i) != 3 and self.__is_threatened_by_enemy(pieces, (
                                    self.position[0], i))):
                        empty = False
                    i = i + direction
                distance = abs(self.position[1] - i)
                if empty and ((distance == 3 and self.castling['king_side']) or
                              (distance == 4 and self.castling['queen_side'])):
                    moves.append((self.position[0], self.position[1] + 2 * direction))
        return moves

    def clear_illegal_movements(self, pieces, want_to_move, moves):
        temp = pieces
        to_remove = []
        for move in moves:
            captured = temp[move[0]][move[1]]
            temp[move[0]][move[1]] = temp[want_to_move[0]][want_to_move[1]]
            temp[want_to_move[0]][want_to_move[1]] = None
            if want_to_move == self.position:
                self.position = move
            if self.is_attacked(temp):
                to_remove.append(move)
            temp[want_to_move[0]][want_to_move[1]] = temp[move[0]][move[1]]
            temp[move[0]][move[1]] = captured
            if move == self.position:
                self.position = want_to_move
        moves = [x for x in moves if x not in to_remove]
        return moves

    def is_attacked(self, pieces):
        return self.__is_threatened_by_enemy(pieces, self.position)

    def __is_threatened_by_enemy(self, pieces, position):
        for line in pieces:
            for p in line:
                if p is not None and p.color != self.color and position in p.get_threats(pieces):
                    return True
        return False
