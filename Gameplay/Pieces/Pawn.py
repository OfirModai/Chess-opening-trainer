from Gameplay.Pieces.Piece import Piece


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

