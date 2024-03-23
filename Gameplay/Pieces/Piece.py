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





