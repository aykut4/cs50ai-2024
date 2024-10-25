"""
Tic Tac Toe Player
"""

import copy
import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    x = 0
    o = 0
    for i in range(3):
        for j in range(3):
            if board[i][j] == X:
                x = x+1
            elif board[i][j] == O:
                o = o+1

    if x == o:
        return X
    return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                actions.add((i, j))
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action[0] < 0 or action[0] > 2 or action[1] < 0 or action[1] > 2 or board[action[0]][action[1]] != EMPTY:
        raise Exception
    new_board = copy.deepcopy(board)
    new_board[action[0]][action[1]] = player(new_board)
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    ret = utility(board)
    if ret == 0:
        return None
    elif ret == 1:
        return X
    else:
        return O


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    if utility(board) != 0:
        return True

    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                return False

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if board[0][0] == X and board[0][1] == X and board[0][2] == X:
        return 1
    if board[0][0] == O and board[0][1] == O and board[0][2] == O:
        return -1
    if board[1][0] == X and board[1][1] == X and board[1][2] == X:
        return 1
    if board[1][0] == O and board[1][1] == O and board[1][2] == O:
        return -1
    if board[2][0] == X and board[2][1] == X and board[2][2] == X:
        return 1
    if board[2][0] == O and board[2][1] == O and board[2][2] == O:
        return -1
    if board[0][0] == X and board[1][0] == X and board[2][0] == X:
        return 1
    if board[0][0] == O and board[1][0] == O and board[2][0] == O:
        return -1
    if board[0][1] == X and board[1][1] == X and board[2][1] == X:
        return 1
    if board[0][1] == O and board[1][1] == O and board[2][1] == O:
        return -1
    if board[0][2] == X and board[1][2] == X and board[2][2] == X:
        return 1
    if board[0][2] == O and board[1][2] == O and board[2][2] == O:
        return -1
    if board[0][0] == X and board[1][1] == X and board[2][2] == X:
        return 1
    if board[0][0] == O and board[1][1] == O and board[2][2] == O:
        return -1
    if board[0][2] == X and board[1][1] == X and board[2][0] == X:
        return 1
    if board[0][2] == O and board[1][1] == O and board[2][0] == O:
        return -1
    return 0


def minimax_recursive(board):

    if terminal(board):
        return utility(board), None

    if player(board) == X:
        max = -math.inf
        max_action = None
        for action in actions(board):
            res, _ = minimax_recursive(result(board, action))
            if res > max:
                max = res
                max_action = action

        return max, max_action

    else:
        min = math.inf
        min_action = None
        for action in actions(board):
            res, _ = minimax_recursive(result(board, action))
            if res < min:
                min = res
                min_action = action

        return min, min_action


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    minmax, action = minimax_recursive(board)
    return action

    """for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                return (i, j)"""
