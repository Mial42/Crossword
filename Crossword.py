import sys
import time
import random

start = time.perf_counter()

height_x_width = sys.argv[1] #eg 11x13
height = int(height_x_width[:height_x_width.index('x')])
width = int(height_x_width[height_x_width.index('x') + 1:])
size = height * width
#max_word_size = min(height, width)
number_of_blocked_squares = int(sys.argv[2])
filename = sys.argv[3]

seed_strings = {} #Tuple of coordinates : tuple of (orientation, word)
word_dict = {} #Length : a list of words of that length
letter_dict = {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 0, 'h': 0, 'i': 0, 'j': 0, 'k': 0, 'l': 0, 'm': 0, 'n': 0, 'o':0, 'p': 0, 'q': 0, 'r': 0, 's': 0, 't':0, 'u': 0, 'v': 0, 'w': 0, 'x': 0, 'y': 0, 'z': 0} #Letter:how common it is in the text file
alphabet = {"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"}
word_to_score = {} #This is going to be the word : score heuristic based on common letters
lookup_table = {} #All possible proto-words to the list of words that they can make
words_3_to_5 = set()
words_6_or_more = {} #Tuple: Length, letter, position to set of words that fit that
max_bucket_length = 5

if width <= 5 or height <= 5:
    max_bucket_length = 5


top_row = set(range(0, width))
left_side = set(range(0, size, width))
right_side = set(range(width - 1, size, width))
bottom_row = set(range(size - width, size))

t_l_corner = 0
t_r_corner = width - 1
b_l_corner = size - width
b_r_corner = size - 1


if len(sys.argv) > 4:
    i = 4
    while i < len(sys.argv):
        seed_string = sys.argv[i] #Looks like H0x0begin
        orientation = seed_string[0].upper()
        seed_string_y_index = int(seed_string[1:seed_string.index('x')])
        post_x_seed_string = seed_string[seed_string.index('x') + 1:]  #The seed string after the 'x' seperating y and x index
        seed_string_x_index = ''
        temp_i = 0
        for char in post_x_seed_string:
            if char.isdigit():
                seed_string_x_index = seed_string_x_index = seed_string_x_index + char
                temp_i = temp_i + 1
            else:
                break
        word = post_x_seed_string[temp_i:] #Remember to change this
        seed_string_x_index = int(seed_string_x_index)
        if (seed_string_y_index, seed_string_x_index) not in seed_strings:
            seed_strings[(seed_string_y_index, seed_string_x_index)] = [(orientation, word.lower())]
        else:
            seed_strings[(seed_string_y_index, seed_string_x_index)].append((orientation, word.lower()))
        i = i + 1


def generate_empty_board(): #Creates a string of length size of '-' characters
    return '-' * size


def integrate_seed_strings(board): #Takes the seed strings and integrates them into the board
    board = list(board)
    for coordinates in seed_strings:
        for given_word in seed_strings[coordinates]:
            my_row = coordinates[0]
            my_col = coordinates[1]
            my_orientation = given_word[0]
            my_word = given_word[1]
            start_index = coords_to_index(my_row, my_col)
            if my_orientation == 'H': #If orientation is horizontal
                index = start_index
                for character in my_word:
                    board[index] = character
                    index = index + 1
            else: #If orientation is vertical
                index = start_index
                for character in my_word:
                    board[index] = character
                    index = index + width
    return ''.join(board)


def index_to_coords(index):
    row = index // width
    col = index % width
    return row, col


def coords_to_index(row, col):
    return row * width + col


def print_puzzle(board):
    for i in range(0, len(board), width):
        x = board[i: i + width]
        temp = '  '.join(x)
        print(temp)


def check_block_symmetry(board): #Checks if the puzzle is 180 degree symmetric
    for index in range(size):
        if board[index] == '#':
            if board[-1 * index - 1] != '#':
                return False
    return True


def check_vertical_horizontal(board): #Checks if every empty square has both vertical and horizontal components
    for square in range(size):
        if board[square] != '#':
            if square == t_l_corner:
                if board[square + width] == '#' or board[square + 1] == '#':
                    return False
            elif square == t_r_corner:
                if board[square + width] == '#' or board[square - 1] == '#':
                    return False
            elif square == b_l_corner:
                if board[square - width] == '#' or board[square + 1] == '#':
                    return False
            elif square == b_r_corner:
                if board[square - width] == '#' or board[square - 1] == '#':
                    return False
            elif square in top_row:
                if board[square + width] == '#' or board[square + 1] == '#' and board[square - 1] == '#':
                    return False
            elif square in bottom_row:
                if board[square - width] == '#' or board[square - 1] == '#' and board[square + 1] == '#':
                    return False
            elif square in left_side:
                if board[square + 1] == '#' or board[square + width] == '#' and board[square - width] == '#':
                    return False
            elif square in right_side:
                if board[square - 1] == '#' or board[square - width] == '#' and board[square + width] == '#':
                    return False
            else:
                if board[square - 1] == '#' and board[square + 1] == '#' or board[square - width] == '#' and board[square + width] == '#':
                    return False
    return True


def check_word_length(board): #Checks if every word is at least three letters long
    global size
    for row_start in range(0, size, width):
        row = range(row_start, row_start + width)
        temp = 0
        for square in row:
            if board[square] != '#':
                temp = temp + 1
            else:
                if 0 < temp < 3:
                    return False
                else:
                    temp = 0
    for col_start in range(0, width):
        col = range(col_start, size, width)
        temp = 0
        for square in col:
            if board[square] != '#':
                temp = temp + 1
            else:
                if 0 < temp < 3:
                    return False
                else:
                    temp = 0
    return True


def check_continuity(board): #Checks if there are any "walls" on the board; returns true if there is one
    board_to_be_flood_filled = list(board)
    if '-' not in board_to_be_flood_filled:
        return True
    def flood_fill(index):
        if board_to_be_flood_filled[index] != '-' and not board_to_be_flood_filled[index].isalpha():
            return
        else:
            board_to_be_flood_filled[index] = '*'
            if index == t_l_corner:
                flood_fill(index + 1)
                flood_fill(index + width)
            elif index == t_r_corner:
                flood_fill(index - 1)
                flood_fill(index + width)
            elif index == b_l_corner:
                flood_fill(index + 1)
                flood_fill(index - width)
            elif index == b_r_corner:
                flood_fill(index - 1)
                flood_fill(index - width)
            elif index in top_row:
                flood_fill(index + 1)
                flood_fill(index - 1)
                flood_fill(index + width)
            elif index in bottom_row:
                flood_fill(index + 1)
                flood_fill(index - 1)
                flood_fill(index - width)
            elif index in left_side:
                flood_fill(index + 1)
                flood_fill(index - width)
                flood_fill(index + width)
            elif index in right_side:
                flood_fill(index - 1)
                flood_fill(index + width)
                flood_fill(index - width)
            else:
                flood_fill(index + width)
                flood_fill(index - width)
                flood_fill(index + 1)
                flood_fill(index - 1)
    flood_fill(board_to_be_flood_filled.index('-'))
    return board_to_be_flood_filled.count('*') + board_to_be_flood_filled.count('#') == size


def legal(board): #Returns false if the board's squares are not valid, else returns true
    return check_continuity(board) and check_word_length(board) and check_block_symmetry(board) and check_vertical_horizontal(board)


def place_implied_squares(board): #Loops through the board and place opposite blocked squares + hopefully also ones
    board = list(board)
    for index in range(size):
        if board[index] == '#':
            if board[index * -1 - 1].isalpha():
                return None
            board[index * -1 - 1] = '#'
        if board[index] == '-':
            if not board[index * -1 -1].isalpha():
                board[index * -1 - 1] = '-'
        if board[index].isalpha():
            if board[index * -1 - 1] == '@':
                board[index * -1 - 1] = '-'
    return ''.join(board)


def place_legal_blocking_squares(board): #Ideally going to wind up placing all the legal blocking sqaures
    board = list(board)
    if size % 2 == 1 and number_of_blocked_squares % 2 == 1:
        board[size // 2] = '#'
    #Probably going to call some kind of csp_backtracking?
    blocks_left = number_of_blocked_squares - board.count('#')
    board = ''.join(board)
    board = board.replace('-', '@')
    board = list(board)
    if size % 2 == 1 and number_of_blocked_squares % 2 == 0:
        if board[size // 2] == '@':
            board[size // 2] = '-'
    board = ''.join(board)
    board = csp_place_blocking_squares(board, blocks_left)
    return board


def get_next_unassigned_var(board): #board is the string representation of an empty board with -, #, @, and given letters
    default_index = board.index('@')                                       #Should look through the board and find the "best" place tof
    default_score = 0         #Score = up score * down score + left_score * right_score
    for index in range(size):
        if board[index] == '@':
            my_score = return_score(board, index)
            if my_score > default_score:
                default_index = index
                default_score = my_score
    return default_index


def return_score(board, index):
    right_score = left_score = up_score = down_score = 0
    if index in top_row:
        up_score = 1
    if index in bottom_row:
        down_score = 1
    if index in left_side:
        left_score = 1
    if index in right_side:
        right_score = 1
    temp_index = index
    while temp_index not in right_side and board[temp_index] != '#':
        right_score = right_score + 1
        temp_index = temp_index + 1
    temp_index = index
    while temp_index not in left_side and board[temp_index] != '#':
        left_score = left_score + 1
        temp_index = temp_index - 1
    temp_index = index
    while temp_index not in top_row and board[temp_index] != '#':
        up_score = up_score + 1
        temp_index = temp_index - width
    temp_index = index
    while temp_index not in bottom_row and board[temp_index] != '#':
        down_score = down_score + 1
        temp_index = temp_index + width
    my_score = left_score * right_score + up_score * down_score
    if up_score == 3 or down_score == 3 or left_score == 3 or right_score == 3:
        my_score -= 10
    if index == t_l_corner or index == b_l_corner or index == t_r_corner or index == t_l_corner:
        my_score -= 10
    return my_score

#Ends with a legal board with blocks_left = 0
#Returns None if blocks_left < 0
#Why not use a different board representation for this with "unassigned" squares being the '@' symbol: These get turned into either '-' or '#'
def csp_place_blocking_squares(board, blocks_left): #Should accept a board a number of blocks left
        if blocks_left < 0 or blocks_left > board.count('@'):
            return None
        elif blocks_left == 0:
            board = board.replace('@', '-')
            if legal(board):
                return board
            else:
                return None
        elif '@' not in board:
            return None
        next_unassigned_var = get_next_unassigned_var(board)
        #next_unassigned_var = board.index('@')
        for possibility in ['#', '-']:
            new_board = create_new_board(board, next_unassigned_var, possibility)
            new_board = place_implied_squares(new_board)
            error = 0
            if new_board is None:
                error = None
            if error is not None:
                new_board = check_unresolvable_three_letter_problems(new_board)
                if new_board is None:
                    error = None
                if error is not None:
                    new_board = check_unresolvable_continuity_problems(new_board)
                    if new_board is None:
                        error = None
                    if error is not None:
                        blocks_left = number_of_blocked_squares - new_board.count('#')
                        result = csp_place_blocking_squares(new_board, blocks_left)
                        if result is not None:
                            return result
        return None


def check_unresolvable_three_letter_problems(board):
    global size
    for row_start in range(0, size, width):
        row = range(row_start, row_start + width)
        certain_uncertain_count = 0
        uncertain_count = 0
        certain_count = 0
        for square in row:
            if board[square] != '#':
                certain_uncertain_count = certain_uncertain_count + 1
                if board[square] == '@':
                    uncertain_count = uncertain_count + 1
                else:
                    certain_count = certain_count + 1
            else:
                if 0 < certain_uncertain_count < 3:
                    if uncertain_count > 0 and certain_count == 0:
                        start_index = square - uncertain_count
                        board = list(board)
                        for i in range(start_index, square):
                            board[i] = '#'
                        board = ''.join(board)
                        certain_count = 0
                        uncertain_count = 0
                        certain_uncertain_count = 0
                    else:
                        return None
                else:
                    certain_uncertain_count = 0
                    uncertain_count = 0
                    certain_count = 0
    for col_start in range(0, width):
        col = range(col_start, size, width)
        certain_count = 0
        uncertain_count = 0
        certain_uncertain_count = 0
        for square in col:
            if board[square] != '#':
                certain_uncertain_count = certain_uncertain_count + 1
                if board[square] == '@':
                    uncertain_count = uncertain_count + 1
                else:
                    certain_count = certain_count + 1
            else:
                if 0 < certain_uncertain_count < 3:
                    if uncertain_count > 0 and certain_count == 0:
                        start_index = square - uncertain_count * width
                        board = list(board)
                        for i in range(start_index, square, width):
                            board[i] = '#'
                        board = ''.join(board)
                        certain_count = 0
                        uncertain_count = 0
                        certain_uncertain_count = 0
                    else:
                        return None
                else:
                    certain_uncertain_count = 0
                    uncertain_count = 0
                    certain_count = 0
    return board


def check_unresolvable_continuity_problems(board):
    board_to_be_flood_filled = list(board)
    if '-' not in board_to_be_flood_filled:
        return board
    def flood_fill(index):
        if board_to_be_flood_filled[index] == '#' or board_to_be_flood_filled[index] == '*':
            return
        else:
            board_to_be_flood_filled[index] = '*'
            if index == t_l_corner:
                flood_fill(index + 1)
                flood_fill(index + width)
            elif index == t_r_corner:
                flood_fill(index - 1)
                flood_fill(index + width)
            elif index == b_l_corner:
                flood_fill(index + 1)
                flood_fill(index - width)
            elif index == b_r_corner:
                flood_fill(index - 1)
                flood_fill(index - width)
            elif index in top_row:
                flood_fill(index + 1)
                flood_fill(index - 1)
                flood_fill(index + width)
            elif index in bottom_row:
                flood_fill(index + 1)
                flood_fill(index - 1)
                flood_fill(index - width)
            elif index in left_side:
                flood_fill(index + 1)
                flood_fill(index - width)
                flood_fill(index + width)
            elif index in right_side:
                flood_fill(index - 1)
                flood_fill(index + width)
                flood_fill(index - width)
            else:
                flood_fill(index + width)
                flood_fill(index - width)
                flood_fill(index + 1)
                flood_fill(index - 1)
    flood_fill(board_to_be_flood_filled.index('-'))
    temp_set = set(board_to_be_flood_filled)
    if len(temp_set) > 3:
        return None
    board_to_be_flood_filled = ''.join(board_to_be_flood_filled)
    new_board = list(board)
    if '@' in temp_set:
        for index in range(size):
            if board_to_be_flood_filled[index] == '@':
                new_board[index] = '#'
    return ''.join(new_board)


def create_new_board(board, square, possibility):
    new_board = list(board)
    new_board[square] = possibility
    new_board = ''.join(new_board)
    return new_board


def board_to_words(board): #Method accepts the board in a string form, returns a dictionary of (startIndex, orientation): word
    global size
    board_dictionary = {}
    for row_start in range(0, size, width):
        row = range(row_start, row_start + width)
        row_string = board[row_start: row_start + width]
        if row_string != '#' * width:
            temp_word = ""
            word_start = True
            for square in row:
                if board[square].isalpha() or board[square] == '-' or board[square] == '@':
                    temp_word = temp_word + board[square]
                    if word_start:
                        start_index = square
                        word_start = False
                else:
                    word_start = True
                    if temp_word != '':
                        board_dictionary[(start_index, 'H')] = temp_word
                    temp_word = ''
            if temp_word != '':
                board_dictionary[(start_index, 'H')] = temp_word

    for col_start in range(0, width):
        col = range(col_start, size, width)
        col_string = board[col_start: size: width]
        if col_string != '#' * height:
            temp_word = ""
            word_start = True
            for square in col:
                if board[square].isalpha() or board[square] == '-' or board[square] == '@':
                    temp_word = temp_word + board[square]
                    if word_start:
                        start_index = square
                        word_start = False
                else:
                    word_start = True
                    if temp_word != '':
                        board_dictionary[(start_index, 'V')] = temp_word
                    temp_word = ''
            if temp_word != '':
                board_dictionary[(start_index, 'V')] = temp_word
    return board_dictionary


test_board = place_legal_blocking_squares(integrate_seed_strings(generate_empty_board()))
test_board_dict = board_to_words(test_board)
temp_test_board_dict_values = test_board_dict.values()
# print(temp_test_board_dict_values)
# for val in temp_test_board_dict_values:
#     print(len(val))
max_word_size = len(max(temp_test_board_dict_values, key=len))
min_word_size = len(min(temp_test_board_dict_values, key=len))

with open(filename) as f:
    for line in f:
        line = line.strip()
        my_length = len(line)
        if line.isalpha() and min_word_size <= my_length <= max_word_size:
            line = line.lower()
            if my_length not in word_dict:
                word_dict[my_length] = []
            if min_word_size <= my_length <= max_bucket_length:
                words_3_to_5.add(line)
            else:
                for letter_index in range(my_length):
                    temp_tuple = (my_length, line[letter_index], letter_index)
                    if temp_tuple not in words_6_or_more:
                        words_6_or_more[temp_tuple] = set()
                    words_6_or_more[temp_tuple].add(line)
            word_dict[my_length].append(line)
            word_to_score[line] = 0
            for letter in alphabet:
                letter_dict[letter] = letter_dict[letter] + line.count(letter)

for word_to_be_scored in word_to_score:
    for letter in word_to_be_scored:
        word_to_score[word_to_be_scored] = word_to_score[word_to_be_scored] + letter_dict[letter]


def word_score(e):
    return word_to_score[e]


def generate_lookup_table(potential_word, original_word):
    if potential_word not in lookup_table:
        lookup_table[potential_word] = set()
    lookup_table[potential_word].add(original_word)
    length = len(potential_word)
    if potential_word == '-' * length:
        return
    for index in range(length):
        if potential_word[index].isalpha():
            new_potential_word = list(potential_word)
            new_potential_word[index] = '-'
            new_potential_word = ''.join(new_potential_word)
            generate_lookup_table(new_potential_word, original_word)


for word in words_3_to_5:
    generate_lookup_table(word, word)


def newer_get_most_constrained_var(board_dict, board): #The word space with the fewest words that could potentially fit
    least_potential_words = 9999
    original_position = (board.index('-'), 'H')
    for position in board_dict:
        word_space = board_dict[position]
        length = len(word_space)
        if '-' in word_space:
            if min_word_size <= length <= max_bucket_length:
                temp_potential_words = len(lookup_table[word_space])
            else:
                temp_set = set(word_dict[length])
                if word_space == '-' * length:
                    temp_potential_words = len(temp_set)
                else:
                    for j in range(length):
                        my_character = word_space[j]
                        if my_character != '-':
                            temp_triple_tuple = (length, my_character, j)
                            if temp_triple_tuple not in words_6_or_more:
                                break
                            temp_set = temp_set.intersection(words_6_or_more[temp_triple_tuple])
                    temp_potential_words = len(temp_set)
            if temp_potential_words < least_potential_words:
                least_potential_words = temp_potential_words
                original_position = position
    return original_position


def new_check_words_are_valid_and_unique(board_to_word, board):
    unique_checker = set()
    least_potential_words = 99999
    if '-' in board:
        original_position = (board.index('-'), 'H')
    else:
        original_position = 'placeholder'
    for position in board_to_word:
        word_space = board_to_word[position]
        length = len(word_space)
        if '-' not in word_space:
            if word_space not in word_to_score:
                return None
            if word_space in unique_checker:
                return None
            unique_checker.add(word_space)
        elif min_word_size <= length <= max_bucket_length:
            if word_space not in lookup_table:
                return None
            else:
                temp_potential_words = len(lookup_table[word_space])
                if temp_potential_words < least_potential_words:
                    least_potential_words = temp_potential_words
                    original_position = position
        elif length > max_bucket_length:
            temp_set = set(word_dict[length])
            if '-' in word_space:
                for j in range(length):
                    my_character = word_space[j]
                    if my_character != '-':
                        temp_triple_tuple = (length, my_character, j)
                        if temp_triple_tuple not in words_6_or_more:
                            return None
                        temp_set = temp_set.intersection(words_6_or_more[temp_triple_tuple])
                        if not temp_set:
                            return None
            temp_potential_words = len(temp_set)
            if temp_potential_words == 0:
                return None
            elif temp_potential_words < least_potential_words:
                least_potential_words = temp_potential_words
                original_position = position
    return original_position


def csp_solve_crossword(board, board_to_word):
    print_puzzle(board)
    print()
    board_to_word = place_words_in_board_dict(board, board_to_word)
    most_constrained_var = new_check_words_are_valid_and_unique(board_to_word, board)
    if most_constrained_var is None:
        return None
    if '-' not in board:
        return board
    #most_constrained_var = newer_get_most_constrained_var(board_to_word, board)
    for pos_word in new_get_sorted_values(most_constrained_var, board_to_word):
        new_board = place_word(board, pos_word, most_constrained_var)
        result = csp_solve_crossword(new_board, board_to_word)
        if result is not None:
            return result
    return None


def place_words_in_board_dict(board, board_dict):
    for pos in board_dict:
        if pos[1] == 'V':
            length = len(board_dict[pos])
            word_space = board[pos[0]:pos[0] + width * length:width]
            board_dict[pos] = word_space
        elif pos[1] == 'H':
            length = len(board_dict[pos])
            word_space = board[pos[0]: pos[0] + length]
            board_dict[pos] = word_space
    return board_dict


def new_get_sorted_values(most_constrained_var, board_to_word):
    word_space = board_to_word[most_constrained_var]
    length = len(word_space)
    if min_word_size <= length <= max_bucket_length:
        if word_space not in lookup_table:
            return []
        return sorted(lookup_table[word_space], key = word_score, reverse=True)
    temp_set = set(word_dict[length])
    if word_space == '-' * length:
        return sorted(temp_set, key = word_score, reverse=True)
    else:
        for j in range(length):
            my_character = word_space[j]
            if my_character != '-':
                temp_triple_tuple = (length, my_character, j)
                if temp_triple_tuple not in words_6_or_more:
                    break
                temp_set = temp_set.intersection(words_6_or_more[temp_triple_tuple])
    return sorted(temp_set, key = word_score, reverse=True)


def place_word(board, pos_word, position):
    board = list(board)
    length = len(pos_word)
    start_index = position[0]
    my_orientation = position[1]
    if my_orientation == 'V':
        letter_index = 0
        for x in range(start_index, start_index + width * length, width):
            board[x] = pos_word[letter_index]
            letter_index = letter_index + 1
    elif my_orientation == 'H':
        letter_index = 0
        for x in range(start_index, start_index + length):
            board[x] = pos_word[letter_index]
            letter_index = letter_index + 1
    return ''.join(board)


def num_words(board, index):
    tbd = board_to_words(board)
    print("Num words with placements at " + str(index) + ": " + str(len(tbd)))
    return len(tbd)



test_board = csp_solve_crossword(test_board, test_board_dict)
print_puzzle(test_board)

print(time.perf_counter() - start)
