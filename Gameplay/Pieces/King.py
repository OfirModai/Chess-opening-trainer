from Gameplay.Pieces.Piece import Piece


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
