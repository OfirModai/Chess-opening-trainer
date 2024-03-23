from Gameplay.Pieces.Piece import Piece


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

