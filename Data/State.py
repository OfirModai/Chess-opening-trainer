import Data.State as State
import Data.mongo_service as mongo
import copy
from Gameplay.Pieces.Bishop import Bishop
from Gameplay.Pieces.Knight import Knight
from Gameplay.Pieces.Pawn import Pawn
from Gameplay import GameOperations, Chess_python_connector
from Gameplay.Pieces.Queen import Queen
from Gameplay.Pieces.Rook import Rook


class State:
    def __init__(self, **kwargs):
        """
        * 3 ways to initiate State:
        * 1. starting position: view
        * 2. move by positions: father, clicked_piece, destination, promote_to(optional)
        * 3. move by note: father, note
        :param kwargs:
        """
        if kwargs is None: raise Exception()
        if 'view' in kwargs:
            self.starting(kwargs['view'])
        elif 'clicked_piece' in kwargs and type(kwargs['clicked_piece']) is Pawn and 'promote_to' not in kwargs and (
                kwargs['clicked_piece'].position[0] + kwargs['clicked_piece'].direction) % 7 == 0:
            self.promote(kwargs['father'], kwargs['clicked_piece'], kwargs['destination'])
        else:
            promote_to = kwargs['promote_to'] if 'promote_to' in kwargs else None
            self.father = kwargs['father'] if promote_to is None else kwargs['father'].father
            self.turn = Chess_python_connector.get_opposite(self.father.turn)
            self.view = self.father.view
            self.pieces = copy.deepcopy(self.father.pieces)
            self.kings = {
                'white': self.pieces[self.father.kings['white'].position[0]][self.father.kings['white'].position[1]],
                'black': self.pieces[self.father.kings['black'].position[0]][self.father.kings['black'].position[1]]
            }
            self.privileged_pawns = []
            for p in self.father.privileged_pawns:
                self.privileged_pawns.append(self.pieces[p.position[0]][p.position[1]])
            if 'note' in kwargs:
                self.note = kwargs['note']
                positions = GameOperations.make_move_by_note_and_get_positions(self.note, self.pieces,
                                                                               self.view, self.father.turn)
            else:
                self.note = GameOperations.make_move_and_get_notation(kwargs['clicked_piece'].position, kwargs['destination'],
                                                                      self.pieces, self.view, self.kings, promote_to)
                positions = kwargs['clicked_piece'].position, kwargs['destination']
            self.moves_played = self.father.moves_played + 1
            if self.father.turn == 'black':
                self.PGN = self.father.PGN + self.note + ' '
            else:
                self.PGN = f'{self.father.PGN}{int((self.moves_played-1)/2)+1}.{self.note} '
            for p in self.privileged_pawns:
                p.turn_is_over()
            self.privileged_pawns.clear()
            if positions is not None:
                origin, destination = positions
                if type(self.pieces[destination[0]][destination[1]]) is Pawn and abs(destination[0] - origin[0]) > 1:
                    # the pawn moved 2 squares, checking if there is a pawn which would have en passant
                    if destination[1] - 1 >= 0 and type(self.pieces[destination[0]][destination[1] - 1]) is Pawn:
                        self.privileged_pawns.append(self.pieces[destination[0]][destination[1] - 1])
                        self.pieces[destination[0]][destination[1] - 1].pawn_passed_in('right')
                    if destination[1] + 1 < len(self.pieces[0]) and type(
                            self.pieces[destination[0]][destination[1] + 1]) is Pawn:
                        self.privileged_pawns.append(self.pieces[destination[0]][destination[1] + 1])
                        self.pieces[destination[0]][destination[1] + 1].pawn_passed_in('left')
            demand = self.father.__memo_unit['_id']
            self.qatalog_number = 0
            options = list(range(10))
            for x in mongo.offline_book:
                if len(x['_id']) <= len(demand) or x['_id'][:len(demand)] != demand: continue
                if int(x['_id'][len(demand)]) in options:
                    options.remove(int(x['_id'][len(demand)]))
                if 'note' in x.keys() and x['note'] == self.note and len(x['_id']) == len(demand) + 1:
                    self.__memo_unit = x
                    return
            self.qatalog_number = options[0]
            if self.father.__memo_unit['headline'] == 'start position':
                headline = self.note
            elif len(self.father.__memo_unit['headline']) < 20:
                headline = self.father.__memo_unit['headline'] + ', ' + self.note
            else:
                headline = self.father.__memo_unit['headline']
            self.__memo_unit = {
                '_id': self.father.__memo_unit['_id'] + str(self.qatalog_number),
                'headline': headline,
                'comments': 'click here to add comment on the position',
                'note': self.note
            }
            mongo.offline_book.append(self.__memo_unit)

    # init for starting position
    def starting(self, view: str):
        self.father = None
        self.view = view
        self.turn = 'white'
        self.pieces, self.kings = GameOperations.set_starting_board(view)
        self.privileged_pawns = []
        self.moves_played = 0
        self.PGN = 'PGN: '
        self.__memo_unit = {
            '_id': '',
            'headline': 'start position',
            'comments': 'click here to change commment',
            'note': ''
        }

    # init for promotion state
    def promote(self, father: State, clicked_piece, promotion_square):
        self.father = father
        self.pieces = [[None for i in range(8)] for j in range(8)]
        x, y, i = promotion_square[1], promotion_square[0], clicked_piece.direction
        self.pieces[y][x] = Queen(clicked_piece.color, (y, x))
        self.pieces[y - i][x] = Knight(clicked_piece.color, (y - i, x))
        self.pieces[y - 2 * i][x] = Rook(clicked_piece.color, (y - 2 * i, x))
        self.pieces[y - 3 * i][x] = Bishop(clicked_piece.color, (y - 3 * i, x))

    def update_memo(self, key, value):
        if self.__memo_unit in mongo.offline_book: mongo.offline_book.remove(self.__memo_unit)
        self.__memo_unit[key] = value
        mongo.offline_book.append(self.__memo_unit)

    def get_text(self, name):
        if not hasattr(self, 'kings'): return ''
        if name in self.__memo_unit.keys(): return self.__memo_unit[name]
        if name == 'PGN': return self.PGN
        raise Exception()

    def is_promotion_state(self):
        return not hasattr(self, 'kings')

    def get_numerical_order(self):
        return int((len(self.__memo_unit['_id']) - 1) / 2) + 1, int(self.turn == 'white')

    def get_next_continuation(self):
        if not hasattr(self, 'last_option_taken'): self.last_option_taken = -1
        if self.last_option_taken + 1 >= len(self.get_continuation_options()): return None
        self.last_option_taken += 1
        return self.get_continuation_options()[self.last_option_taken]

    def get_continuation_options(self):
        if self.is_promotion_state(): return []
        demand = self.__memo_unit['_id']
        options = []
        for x in mongo.offline_book:
            if len(x['_id']) == len(demand) + 1 and x['_id'][:len(demand)] == demand:
                options.append(x['note'])
        return options

    def delete_continuation(self, note):
        if self.is_promotion_state(): return
        demand = self.__memo_unit['_id']
        to_delete = []
        for x in mongo.offline_book:
            if len(x['_id']) == len(demand) + 1 and 'note' in x.keys() and x['note'] == note and x['_id'][:len(demand)] == demand:
                demand = x['_id']
                break
        for x in mongo.offline_book:
            if len(x['_id']) >= len(demand) and x['_id'][:len(demand)] == demand:
                to_delete.append(x)
        for x in to_delete:
            mongo.offline_book.remove(x)

    def get_new_state_if_possible(self, clicked_piece, destination, promote_to):
        if GameOperations.is_move_in(clicked_piece.position, destination, self.pieces, self.view, self.kings, promote_to,
                                     self.get_continuation_options()):
            return State(father=self, clicked_piece=clicked_piece, destination=destination, promote_to=promote_to)
        return None

    def has_comment(self):
        return self.__memo_unit['comments'] != "click here to add comment on the position" and len(self.__memo_unit['comments']) > 1

    def has_meaningful_headline(self):
        return not str(self.__memo_unit['headline'][0]).isnumeric()

    def __str__(self):
        return self.PGN
