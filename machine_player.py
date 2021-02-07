import copy

"""
    *
    *   Author: Diego Fernandez Sebastian
    *
    *   Script that contains a tic tac toe machine player which is able to perform roughly the optimal move.
    *   The Minmax algorithm enhanced with the alpha-beta-pruning has been used in order to reduce the evaluations
    *   the computer must perform to come up with the optimal solution.  
    *       Note:
    *           --> It does generate all the alternatives and afterwards the static evaluation is carried out. Thus,
    *               all the nodes are generated beforehand and only the evaluations get reduced. It could be enhanced
    *               through not generating those movements wont be evaluated due to the deep cutoffs. 
    *  
    *   
    *
"""


# source_board = [['_', '_', '_'], ['_', '_', '_'], ['_', '_', '_']]

class MachinePlayer:
    def __init__(self, board, machine_token, human_token, machine_turn=True):
        self._current_board = board
        self._machine_token = machine_token
        self._human_token = human_token
        self._machine_turn = machine_turn

    @property
    def current_board(self):
        return self._current_board

    def get_optimal_move(self):
        """
        Returns the coordinates in which the player must place the token
        :return:
        """
        # create the root state
        root = State(self.current_board, True, self._machine_token, self._human_token)
        # alpha-beta-pruning algorithm
        best_move = max_value_a_b(root, depth(root), -1000, 1000)
        # obtain the coordinates of the movement.
        for child in root.children:
            if child.value == best_move:
                return get_coordinates(root, child)

    """:param
        crear uno con su token y luego un atributo que sea la mejor opcion para jugar la cual ejecutará el 
        algortimo este para obtener la mejor alternativa
        Siempre va a maximizar
    """


class State:
    def __init__(self, board, machine_turn, machine="O", human="X", value=0):
        """ :param board: whatever valid configuration within the board possible.
            :param machine: Character used by the machine in the game
            :param human: Character used by the human in the game
            :param value: A predefined value is used to differentiate which node has been evaluated or not.
                the values used are the following:
                    --> 0: it's used as a predefined value for every node generated.
                    --> 1: it's used for the minimizing player
                    --> 2: it's used for a tie
                    --> 3: it's used for the maximizing player
            :children: It's the reference of the state's successors. Though it's not passed as a parameter
                it will store the following states in order to perform the static evaluation.
        """
        if board is not None:
            # the board will be none only for the "root" state.
            self._board = board
        else:
            self._board = [['_', '_', '_'], ['_', '_', '_'], ['_', '_', '_']]
        # given value to every state. It will be used to set which player has won / whether it's a tie and so on.
        # a predefined value is set to 0. It may change due to the static evaluation carried out.
        self._value = value
        # In order to distinguish between the players to yield the static evaluation, two more arguments were needed.
        self._machine = machine
        self._human = human
        # Furthermore, to be able to generate the proper children, two more attributes are needed.
        self._machine_turn = machine_turn

        # all the possible moves an specific state may carry out.
        self._children = []

    @property
    def board(self):
        return self._board

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

    @property
    def children(self):
        return self._children

    @property
    def machine_turn(self):
        return self._machine_turn

    @machine_turn.setter
    def machine_turn(self, update):
        self._machine_turn = update

    def generate_children(self):
        # loop over the board in order to obtain all the possible options.
        for i in range(0, len(self.board)):
            for j in range(0, len(self.board[0])):
                if check_board_position(self, i, j):
                    # it's possible to place a token, therefore the board must be copied.
                    child = copy.deepcopy(self)
                    if self.machine_turn:
                        # the machine is playing, therefore the token used is the machine one.
                        child.board[i][j] = self._machine
                        # change the turn
                        child.machine_turn = False
                    else:
                        # otherwise the human is playing
                        child.board[i][j] = self._human
                        # change the turn
                        child.machine_turn = True
                    # append it to the list of children.
                    self._children.append(child)

    def ending_state(self):
        """
        A ending state can be shaped in two ways:
        1-.) All the board has been fulfilled and thus, no further movements can be performed
        2-.) Anyone has won the match without fulfill the entire board with tokens.

        :return: True if any of this constraints are true, otherwise false.
        """
        # constraint 1:
        if check_board_cells(self):
            return True

        # constraint 2:
        value_mdh, token = self._check_main_diagonal(self._human)
        value_mdm, token = self._check_main_diagonal(self._machine)
        value_sdh, token = self._check_secondary_diagonal(self._human)
        value_sdm, token = self._check_secondary_diagonal(self._machine)
        value_rh, token = self._check_rows(self._human)
        value_rm, token = self._check_rows(self._machine)
        value_ch, token = self._check_cols(self._human)
        value_cm, token = self._check_cols(self._machine)
        if value_mdh or value_mdm or value_sdh or value_sdm or value_rh or value_rm or value_ch or value_cm:
            return True

        return False

    def static_evaluation(self):
        """ The machine is going to maximize every time.
            In order to come up with a fast move,
            """

        # check the main diagonals first
        value_i, token_i = self._check_main_diagonal(self._human)
        value_j, token_j = self._check_main_diagonal(self._machine)
        if value_i and token_i == self._human:
            return 1
        elif value_j and token_j == self._machine:
            return 3

        # check the secondary diagonals
        value_i, token_i = self._check_secondary_diagonal(self._human)
        value_j, token_j = self._check_secondary_diagonal(self._machine)
        if value_i and token_i == self._human:
            return 1
        elif value_j and token_j == self._machine:
            return 3

        # secondly check the columns
        value_i, token_i = self._check_rows(self._human)
        value_j, token_j = self._check_rows(self._machine)
        if value_i and token_i == self._human:
            return 1
        elif value_j and token_j == self._machine:
            return 3

        # lastly check the rows
        value_i, token_i = self._check_cols(self._human)
        value_j, token_j = self._check_cols(self._machine)
        if value_i and token_i == self._human:
            return 1
        elif value_j and token_j == self._machine:
            return 3

        # if no solution has been found, 2 Tie
        return 2

    def _check_main_diagonal(self, player_token):
        # Aux variable to count till 3. When it was a value of 3 the player will have won
        _counter = 0
        for i in range(0, len(self.board)):
            for j in range(0, len(self.board[0])):
                if i - j == 0 and self.board[i][j] == player_token:
                    _counter += 1
        # once the board has been looped over, check the value of the counter
        if _counter == 3:
            return True, player_token
        return False, None

    def _check_secondary_diagonal(self, player_token):
        # Aux variable to count till 3. When it was a value of 3 the player will have won
        _counter = 0
        for i in range(0, len(self.board)):
            for j in range(0, len(self.board[0])):
                if i + j == 2 and self.board[i][j] == player_token:
                    _counter += 1
        # once the board has been looped over, check the value of the counter
        if _counter == 3:
            return True, player_token
        return False, None

    def _check_rows(self, player_token):
        # Aux variable to count till 3. When it was a value of 3 the player will have won
        _counter = 0
        for i in range(0, len(self.board)):
            for j in range(0, len(self.board[0])):
                if self.board[i][j] == player_token:
                    _counter += 1
            if _counter == 3:
                return True, player_token
            _counter = 0
        return False, None

    def _check_cols(self, player_token):
        # Aux variable to count till 3. When it was a value of 3 the player will have won
        _counter = 0
        for i in range(0, len(self.board)):
            for j in range(0, len(self.board[0])):
                if self.board[j][i] == player_token:
                    _counter += 1
            if _counter == 3:
                return True, player_token
            _counter = 0
        return False, None


def check_board_position(state, board_row_position, board_col_position):
    """:param state: current node which represents a state.
       :param board_row_position: from the current board
       :param board_col_position: from the current board
        It checks whether the position is available to place a token. """
    return True if state.board[board_row_position][board_col_position] == '_' else False


def check_board_cells(state):
    for i in range(0, len(state.board)):
        for j in range(0, len(state.board[0])):
            if state.board[i][j] == '_':
                return False
    return True


def get_coordinates(parent, optimal_movement):
    for i in range(0, len(parent.board)):
        for j in range(0, len(parent.board[0])):
            if parent.board[i][j] != optimal_movement.board[i][j]:
                return i, j


def depth(state):
    """ it figures out the current depth"""
    current_depth = 0
    for i in range(0, len(state.board)):
        for j in range(0, len(state.board[0])):
            if state.board[i][j] == '_':
                current_depth += 1
    return current_depth


# ALPHA-BETA-PRUNING ALGORITHM
def max_value_a_b(state, depth, alpha, beta):
    if state.ending_state() or depth == 0:
        # perform the static evaluation
        state.value = state.static_evaluation()
        return state.value
    v = -1000
    # generate the following states.
    state.generate_children()
    # loop over the following states.
    for child in state.children:
        v = max(v, min_value_a_b(child, depth - 1, alpha, beta))
        alpha = max(alpha, v)
        # performs the cutoff if necessary
        if alpha >= beta:
            return alpha
    state.value = v
    return v


def min_value_a_b(state, depth, alpha, beta):
    if state.ending_state() or depth == 0:
        # perform the static evaluation
        state.value = state.static_evaluation()
        return state.value
    v = 1000
    # generate the following states.
    state.generate_children()
    # loop over the following states.
    for child in state.children:
        v = min(v, max_value_a_b(child, depth - 1, alpha, beta))
        beta = min(beta, v)
        # performs the cutoff if necessary
        if alpha >= beta:
            return beta
    state.value = v
    return v


source_board = [['o', '_', 'x'],
                ['x', 'o', 'o'],
                ['_', 'x', '_']]

source_board1 = [['o', '_', 'x'],
                 ['x', 'o', '_'],
                 ['o', '_', 'x']]

source_board2 = [['_', '_', '_'],
                 ['_', '_', '_'],
                 ['_', '_', '_']]
# the machine gives up
source_board3 = [['x', 'x', 'o'],
                 ['_', 'o', '_'],
                 ['_', '_', '_']]

# if the board is full of tokens, the optimal move gets None
player = MachinePlayer(source_board2, 'o', 'x')
obj = player.get_optimal_move()
print(obj)
