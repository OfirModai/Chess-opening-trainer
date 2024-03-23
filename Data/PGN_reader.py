from Data.State import State
import Data.mongo_service as mongo
import Gameplay.Chess_python_connector


def read(file_name: str):
    reader = open(f'Data/PGN/{file_name}.pgn')
    view = None
    for x in mongo.offline_book:
        if x['_id'] == '999':
            view = x['orientation']
            break
    pgn = reader.read()
    states = [State(view=view)]
    memo = {get_FEN_from_pieces(states[0].pieces, view): states[0]}
    lines = pgn.split('\n')
    current_headline = ''
    starting_positions = []
    i = 0
    # concat lines of moves to get organized
    while i < len(lines):
        # detect in which positions we ae on this book
        if len(lines[i])>4 and lines[i][1:4] == 'FEN':
            starting_positions.append(lines[i].split(' ')[1][1:])
        if lines[i] == '': lines.pop(i)
        elif lines[i][0] != '[' and i + 1 < len(lines) and lines[i + 1] != '' and lines[i + 1][0] != '[':
            lines[i] += lines[i + 1]
            lines.pop(i+1)
        else: i += 1
    for line in lines:
        if line[0] == '[':
            # the moves start from some position, we find it
            if line[1:4] == 'FEN':
                fen = line.split(' ')[1][1:]
                states = None
                for state in memo.values():
                    if get_FEN_from_pieces(state.pieces, view) == fen:
                        states = [state]
                        break
                if states is None:
                    raise Exception('FEN given with no previous position, can\'t assume the png')
            # we get specified name for the variation
            elif line[1:6] == 'Event':
                name = (line.split('\"')[1]).split(':')[1]
                current_headline = f'{file_name} : {name}' if 'ntro' not in name else ''
        elif line != '\n':
            words = line.split(' ')
            while len(words) > 0:
                word = words.pop(0)
                # add comments
                if '{' in word:
                    comment = ''
                    while '}' not in words[0]:
                        word = words.pop(0)
                        # ignore drawings
                        if '[' in word:
                            while ']' not in words[0]:
                                word = words.pop(0)
                            word = words.pop(0)
                            parts = word.split(']')
                            if len(parts[1]) > 0:
                                word = parts[1]
                            else: word = words.pop(0)
                            words.insert(0, word)
                        if '}' not in word: comment += word + " "
                    word = words.pop(0)
                    parts = word.split('}')
                    comment += parts[0]
                    if len(comment) > 0 and not states[-1].has_comment(): states[-1].update_memo('comments', comment)
                    if len(parts[1]) > 0: words.insert(0, parts[1])
                # open variation
                elif word[0] == '(':
                    states.append(states[-1].father)
                    words.insert(0, word[1:])
                # close variation
                elif word[-1] == ')':
                    count = 0
                    while len(word) > 0 and word[-1] == ')':
                        count += 1
                        word = word[0:-1]
                    move = clean_move(word)
                    if move != '':
                        states[-1] = State(father=states[-1], note=move)
                        fen = get_FEN_from_pieces(states[-1].pieces, view)
                        if current_headline != '': states[-1].update_memo('headline', current_headline)
                        elif fen in starting_positions: states[-1].update_memo('headline', file_name)
                        memo[fen] = states[-1]
                    for i in range(count):
                        states.pop()
                elif word == '*':
                    break
                elif word[-1] in ('.', '\n') or word[0] == '$':
                    continue
                else:
                    move = clean_move(word)
                    states[-1] = State(father=states[-1], note=move)
                    fen = get_FEN_from_pieces(states[-1].pieces, view)
                    if current_headline != '': states[-1].update_memo('headline', current_headline)
                    elif fen in starting_positions: states[-1].update_memo('headline', file_name)
                    memo[fen] = states[-1]

            states = [State(view=view)]
    reader.close()


def clean_move(move):
    if len(move) < 2: return move
    if move[-2:] in ('!!', '!?', '?!', '??'): return move[:-2]
    if move[-1] in ('!', '?'): return move[:-1]
    return move


def get_FEN_from_pieces(pieces, view):
    result = ''
    transpose = view == 'black'
    for line in range(8):
        if transpose: line = 7 - line
        spaces_count = 0
        for col in range(8):
            if transpose: col = 7 - col
            if pieces[line][col] is None:
                spaces_count += 1
            else:
                if spaces_count != 0: result += str(spaces_count)
                spaces_count = 0
                char = Gameplay.Chess_python_connector.role_to_letter(pieces[line][col].role)
                if char == '': char = 'p'
                char = char.lower() if pieces[line][col].color == 'black' else char.upper()
                result += char
        if spaces_count != 0:
            result += str(spaces_count)
        result += '/'
    return result[:-1]
