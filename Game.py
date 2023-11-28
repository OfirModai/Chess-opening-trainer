import math
import random
import time
import Data.mongo_service
import pygame
import Helper
from Display.Button import Button
from Data.State import State


class Game:
    def __init__(self, view, screen, board=None):
        self.recall = Helper.Recall
        self.VIEW = view
        self.rects = {}
        self.screen = screen
        self.board = board if board is not None else pygame.Rect(screen.width * 0.4, screen.height * 0.1,
                                                                 screen.width * 0.4, screen.width * 0.4)
        Helper.Board = self.board
        self.piece_size = self.board.height / 8
        self.WIN = pygame.display.set_mode((self.screen.width, self.screen.height))
        pygame.display.set_caption('Chess opening trainer')
        self.images = {}
        for color in ('white', 'black'):
            for role in ('pawn', 'rook', 'queen', 'king', 'bishop', 'knight'):
                self.images[(color, role)] = pygame.transform.scale(
                    pygame.image.load(f'Images\\{color}{role}.png'), (self.piece_size, self.piece_size))
        self.images[('white', 'board')] = pygame.transform.scale(
            pygame.image.load('Images\\BoardForWhite.png'), (self.board.width, self.board.height))
        self.images[('black', 'board')] = pygame.transform.scale(
            pygame.image.load('Images\\BoardForBlack.png'), (self.board.width, self.board.height))
        self.images['possible_move'] = pygame.transform.scale(
            pygame.image.load('Images\\PossibleMove.png').convert_alpha(), (self.piece_size, self.piece_size))
        pygame.font.init()
        self.font = pygame.font.Font('Data\\Ubuntu-R.ttf', 32)
        self.smallfont = pygame.font.Font('freesansbold.ttf', 24)
        self.text_has_changed = False
        self.state = State(view=view)
        self.moves = []
        self.turn = 'white'
        self.clicked_piece = None
        self.text_has_changed = True
        self.buttons = {
            'headline': Button('headline', 'start position', self.font, ((self.board.right + self.board.left) / 2,
                                                                         self.board.top - self.font.get_height() / 2),
                               'center', True),
            'main': Button('main', 'main', self.font,
                           (self.board.right, self.board.bottom), 'bottomleft'),
            'backwards': Button('backwards', '<<', self.font, (self.board.right, self.board.bottom), 'topleft'),
            'comments': Button('comments', ' ', self.smallfont, (self.board.left, self.board.bottom),
                               'topleft', True, self.board.width),
            'PNG': Button('PNG', '', self.font, (0, self.board.top)
                          , 'topleft', True, self.board.left)
        }
        self.buttons['forward'] = \
            Button('forward', '>>', self.font, (self.buttons['backwards'].rects[0].right, self.board.bottom), 'topleft')
        self.buttons['mode'] = \
            Button('mode', 'setting', self.font, (self.board.right, self.buttons['main'].rects[0].top), 'bottomleft')
        self.clicked_button = None
        self.temporary_buttons = []
        self.__update_buttons()
        Helper.Recall.append(self.state)

    def coordinates_to_rectangle(self, position):
        x = self.board.left + round(self.board.width / 8) * position[1]
        y = self.board.top + round(self.board.height / 8) * position[0]
        return pygame.Rect(x, y, self.piece_size, self.piece_size)

    def screen_position_to_element(self, position):
        if self.board.collidepoint(position):
            # the system receive points like (left,top) but working in (top,left)
            position = (position[1], position[0])
            return (math.floor((position[0] - self.board.top) * 8 / self.board.height),
                    math.floor((position[1] - self.board.left) * 8 / self.board.width))
        for button in self.buttons.values():
            for rect in button.rects:
                if rect.collidepoint(position):
                    return button
        for button in self.temporary_buttons:
            for rect in button.rects:
                if rect.collidepoint(position):
                    return button
        return None

    def draw(self):
        self.WIN.fill((0, 0, 0))
        for button in self.buttons.values():
            for surface, rect in zip(button.surfaces, button.rects):
                self.WIN.blit(surface, rect)
        for button in self.temporary_buttons:
            for surface, rect in zip(button.surfaces, button.rects):
                self.WIN.blit(surface, rect)
        self.WIN.blit(self.images[(self.VIEW, 'board')], (self.board.left, self.board.top))
        for line in self.state.pieces:
            for piece in line:
                if piece is not None:
                    self.WIN.blit(self.images[(piece.color, piece.role)], self.coordinates_to_rectangle(piece.position))
        for move in self.moves:
            self.WIN.blit(self.images['possible_move'], self.coordinates_to_rectangle(move))

        pygame.display.update()

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.clicked_button = None
            element = self.screen_position_to_element(pygame.mouse.get_pos())
            if type(element) is tuple:
                if element in self.moves or self.state.is_promotion_state():
                    # movement of pieces will be made
                    if element not in self.moves and self.state.pieces[element[0]][element[1]] is None:
                        # the user clicked empty square on the promotion screen
                        self.state = self.state.father
                    else:
                        promote_to, destination = None, None
                        if self.state.is_promotion_state():
                            promote_to = self.state.pieces[element[0]][element[1]]
                            y = 0 if element[0] > 3 else 7
                            destination = (y, element[1])
                        else:
                            destination = element

                        # there is a clicked piece and it needs to go to the pressed place
                        if self.buttons['mode'].text == 'setting':
                            self.state = State(father=self.state, clicked_piece=self.clicked_piece,
                                               destination=destination, promote_to=promote_to)
                        else:  # trainer modes
                            state = self.state.get_new_state_if_possible(self.clicked_piece, destination, promote_to)
                            if state is None:
                                self.buttons['comments'].write('wrong move, try again')
                                self.moves.clear()
                                return
                            else:
                                self.state = state
                                self.decide_what_to_do()
                    if not self.state.is_promotion_state(): self.clicked_piece = None
                    self.moves.clear()

                elif self.state.pieces[element[0]][element[1]] is None or self.state.pieces[element[0]][
                        element[1]].color != self.state.turn:
                    # unlegal move
                    self.moves.clear()
                else:
                    # the click is on piece with the right turn need to show the possible moves
                    self.moves = self.state.pieces[element[0]][element[1]].get_possible_moves(self.state.pieces)
                    self.moves = self.state.kings[self.state.turn].clear_illegal_movements(
                        self.state.pieces, (element[0], element[1]), self.moves)
                    self.clicked_piece = self.state.pieces[element[0]][element[1]]
            else:
                if type(element) is Button:
                    self.clicked_button = element
                    if element.name == 'main':
                        return 'main'
                    elif element.name == 'comments':
                        self.state.update_memo('comments', ' ')
                    elif element.name == 'backwards' and self.state.father is not None:
                        self.state = self.state.father
                    elif element.name == 'forward' and len(self.temporary_buttons) > 0:
                        note = self.temporary_buttons[0].text if self.VIEW == self.state.turn or self.buttons[
                            'mode'].text == 'setting' \
                            else self.temporary_buttons[Helper.get_random(len(self.temporary_buttons))].text
                        self.state = State(father=self.state, note=note)
                    elif element.name == 'option':
                        self.state = State(father=self.state, note=element.text)
                    elif element.name == 'mode':
                        if element.text == 'organized trainer':
                            element.write('setting')
                            if self.state.get_text('headline') != 'starting position':
                                while len(Helper.Recall) > 1: Helper.Recall.pop()
                                self.state = Helper.Recall[0]

                        else:
                            if element.text == 'random trainer':
                                element.write('organized trainer')
                                Helper.Recall.append(self.state)
                            else:
                                element.write('random trainer')
                    self.moves.clear()
            self.__update_texts()
            self.__update_buttons()

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            # right click
            element = self.screen_position_to_element(pygame.mouse.get_pos())
            if type(element) is Button and element.name == 'option':
                self.state.delete_continuation(element.text)
                self.__update_buttons()

        elif event.type == pygame.KEYUP:
            if event.unicode == '\r':  # enter
                if len(Helper.Recall) > 1:
                    self.state = Helper.Recall.pop()
                else:
                    self.state = Helper.Recall[0]
                self.decide_what_to_do()

            elif self.clicked_button is not None and self.clicked_button.editable:
                if event.key == 32:  # backspace
                    self.clicked_button.add_to_text(' ')
                elif event.key == 8:
                    self.clicked_button.delete_one()
                else:
                    self.clicked_button.add_to_text(event.unicode)
                self.state.update_memo(self.clicked_button.name, self.clicked_button.text)
        else:
            return False

    def __update_texts(self):
        for b in self.buttons.values():
            if b.editable:
                b.write(self.state.get_text(b.name))

    def __update_buttons(self):
        self.temporary_buttons.clear()
        options = self.state.get_continuation_options()
        if self.buttons['mode'].text[-7:] == 'trainer' and self.state.turn == self.VIEW: return
        for i in range(len(options)):
            self.temporary_buttons.append(
                Button('option', options[i], self.font,
                       (self.board.right + 50, self.board.top * 1.2 + i * 2 * self.font.get_height()), 'topleft'))

    def make_opponent_move(self):
        self.moves.clear()
        self.draw()
        self.__update_buttons()
        note = None
        if self.buttons['mode'].text == 'organized trainer':
            note = self.state.get_next_continuation()
        else:
            note = self.temporary_buttons[
                Helper.get_random(len(self.temporary_buttons))].text
        if note is not None:
            time.sleep(1)
            if self.buttons['mode'].text == 'organized trainer':
                Helper.Recall.append(self.state)
            self.state = State(father=self.state, note=note)
        else:
            self.state = Helper.Recall.pop()
            self.decide_what_to_do()
        self.__update_buttons()
        self.__update_texts()

    def decide_what_to_do(self):
        if self.buttons['mode'].text == 'setting': return
        elif len(self.state.get_continuation_options()) == 0:
            self.state.update_memo('comments', 'end of line, congratulations! \n press enter to continue')
        else:
            self.moves.clear()
            self.__update_buttons()
            self.__update_texts()
            self.draw()
            if self.state.turn != self.state.view:
                self.make_opponent_move()
        self.moves.clear()
        self.__update_buttons()
        self.__update_texts()
