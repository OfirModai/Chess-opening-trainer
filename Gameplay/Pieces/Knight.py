from Gameplay.Pieces.Piece import Piece


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

