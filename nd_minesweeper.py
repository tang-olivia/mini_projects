# n-dimensional minesweeper game
#!/usr/bin/env python3

#import typing
import doctest

def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    keys = ("board", "dimensions", "state", "visible")
    # ^ Uses only default game keys. If you modify this you will need
    # to update the docstrings in other functions!
    for key in keys:
        val = game[key]
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f"{key}:")
            for inner in val:
                print(f"    {inner}")
        else:
            print(f"{key}:", val)


# 2-D IMPLEMENTATION


def new_game_2d(nrows, ncolumns, mines):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       nrows (int): Number of rows
       ncolumns (int): Number of columns
       mines (list): List of mines, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, False, False]
        [False, False, False, False]
    """
    return new_game_nd((nrows, ncolumns), mines)


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['visible'] to reveal (row, col).  Then, if (row, col) has no
    adjacent mines (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one mine
    is visible on the board after digging (i.e. game['visible'][mine_location]
    == True), 'victory' when all safe squares (squares that do not contain a
    mine) and no mines are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: victory
    visible:
        [False, True, True, True]
        [False, False, True, True]

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    state: defeat
    visible:
        [True, True, False, False]
        [False, False, False, False]
    """
    return dig_nd(game, (row, col))


def render_2d_locations(game, all_visible=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (mines), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    mines).  game['visible'] indicates which squares should be visible.  If
    all_visible is True (the default is False), game['visible'] is ignored
    and all cells are shown.

    Parameters:
       game (dict): Game state
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                    by game['visible']

    Returns:
       A 2D array (list of lists)

    >>> game = {'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, True, False],
    ...                   [False, False, True, False]]}
    >>> render_2d_locations(game, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations(game, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    return render_nd(game, all_visible)


def render_2d_board(game, all_visible=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                           by game['visible']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'visible':  [[True, True, True, False],
    ...                            [False, False, True, False]]})
    '.31_\\n__1_'
    """
    nrows = game["dimensions"][0]
    ncols = game["dimensions"][1]
    game_display = render_2d_locations(game, all_visible)
    ascii_art = ""

    for row in range(nrows):
        for col in range(ncols):
            ascii_art += game_display[row][col]
        ascii_art += "\n"

    return ascii_art[:-1]


# N-D IMPLEMENTATION


def get_coordinate_value(nd_array, coordinates):
    """
    Given a specific coordinate, return value at that position
    """
    current = nd_array[coordinates[0]]
    for coordinate in coordinates[1:]:
        current = current[coordinate]
    return current

def replace_value(nd_array, coordinates, value):
    if len(coordinates) == 1:
        nd_array[coordinates[0]] = value
        return 
    first = coordinates[0]
    return replace_value(nd_array[first], coordinates[1:], value)


def make_nd_array(coordinates, value):
    """
    Construct nested list with specified dimensions, with 
    each position in the list being the passed in value
    """

    def nd_array_helper(num):
        if num == len(coordinates):
            return value
        nested = [nd_array_helper(num + 1) for _ in range(coordinates[num])]
        return nested

    return nd_array_helper(0)


def return_state(game):
    """
    Return the state of the game
    """
    return game["state"]


def get_board_coords(board):
    """
    Given a board, return a list of all the possible board coordinates
    """
    possible_coords = []

    def get_coords_helper(nested_list, indices=None):
        if indices is None:
            indices = ()
        for i, element in enumerate(nested_list):
            current_index = indices + (i,)
            if isinstance(element, list):
                get_coords_helper(element, current_index)
            else:
                possible_coords.append(current_index)

    get_coords_helper(board)
    return possible_coords

def possible_coords(coordinates):
    nums = []
    for coord in coordinates:
        nums.append([i for i in range(coord)])
    def helper(num_list):
        if not num_list:
            yield ()
            return
        for val in num_list[0]:
            for comb in helper(num_list[1:]):
                yield (val,) + comb
    yield from helper(nums)

def direction_vector(coordinate):
    """
    Given a coordinate, return a list of direction vectors. A
    direction vector allows one to access adjacent squares in 
    the board
    """

    def direction_inner(coordinate, previous, num):
        if num == len(coordinate) - 1:
            return previous
        current_list = [
            (previous_coord + (value,))
            for previous_coord in previous
            for value in (-1, 0, 1)
        ]
        return direction_inner(coordinate, current_list, num + 1)

    return direction_inner(coordinate, [(-1,), (0,), (1,)], 0)


def mine_check(change_vec, dimensions, position):
    """
    Check to see if adjacent positions are within range of the 
    board dimensions. Return True if so, False otherwise.
    """
    check = True
    full_position = ()

    for i, _ in enumerate(dimensions):
        new_position = position[i] + change_vec[i]
        full_position = full_position + (new_position,)
        if not 0 <= new_position < dimensions[i]:
            check = False
    return check, full_position


def update_mine_neighbors(board, mine_loc, change, dimensions):
    """
    Increment values of the squares adjacent to a mine by 1. 
    """
    for change_vec in change:
        check = mine_check(change_vec, dimensions, mine_loc)
        if check[0] and get_coordinate_value(board, check[1]) != ".":
            replace_value(board, check[1], get_coordinate_value(board, check[1]) + 1)


def num_to_success(game):
    """
    Return the required number of covered mines left to flip over
    in order to win
    """
    def success_helper(nested_list, indices=None):
        covered = 0
        if indices is None:
            indices = []
        for i, element in enumerate(nested_list):
            current_index = indices + [i]
            if isinstance(element, list):
                covered += success_helper(element, current_index)
            else:
                if get_coordinate_value(
                    game["board"], current_index
                ) != "." and not get_coordinate_value(game["visible"], current_index):
                    covered += 1
        return covered

    return success_helper(game["board"])


def new_game_nd(dimensions, mines):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Args:
       dimensions (tuple): Dimensions of the board
       mines (list): mine locations as a list of tuples, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    board = make_nd_array(dimensions, 0)
    for mine_location in mines:
        replace_value(board, mine_location, ".")

    change = direction_vector(tuple([0] * len(dimensions)))
    for mine_location in mines:
        update_mine_neighbors(board, mine_location, change, dimensions)

    visible = make_nd_array(dimensions, False)

    return {
        "dimensions": dimensions,
        "board": board,
        "state": "ongoing",
        "visible": visible,
    }


def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the visible to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    mine.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one mine is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a mine) and no mines are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: defeat
    visible:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    change = direction_vector(tuple([0] * len(game["dimensions"])))
    to_reveal = num_to_success(game)

    def dig_helper(game, coordinates):
        if return_state(game) == "defeat" or return_state(game) == "victory":
            return 0

        if get_coordinate_value(game["board"], coordinates) == ".":
            replace_value(game["visible"], coordinates, True)
            game["state"] = "defeat"
            return 1

        if not get_coordinate_value(game["visible"], coordinates):
            replace_value(game["visible"], coordinates, True)
            revealed = 1
        else:
            return 0

        if get_coordinate_value(game["board"], coordinates) == 0:
            for change_vec in change:
                check = mine_check(change_vec, game["dimensions"], coordinates)
                if check[0] and not get_coordinate_value(game["visible"], check[1]):
                    revealed += dig_helper(game, check[1])

        if to_reveal == revealed:
            game["state"] = "victory"
        return revealed

    return dig_helper(game, coordinates)


def render_nd(game, all_visible=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (mines), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    mines).  The game['visible'] array indicates which squares should be
    visible.  If all_visible is True (the default is False), the game['visible']
    array is ignored and all cells are shown.

    Args:
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                           by game['visible']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, False], [False, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    game_display = make_nd_array(game["dimensions"], ".")
    board_coords = get_board_coords(game["board"])

    for coordinate in board_coords:
        coordinate_value = get_coordinate_value(game["board"], coordinate)
        if coordinate_value == 0:
            replace_value(game_display, coordinate, " ")
        else:
            replace_value(game_display, coordinate, str(coordinate_value))

    if all_visible:
        return game_display

    for coordinate in board_coords:
        if not get_coordinate_value(game["visible"], coordinate):
            replace_value(game_display, coordinate, "_")

    return game_display


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    # doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
