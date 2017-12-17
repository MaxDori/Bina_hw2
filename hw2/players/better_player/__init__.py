# ===============================================================================
# Imports
# ===============================================================================

import abstract
from utils import INFINITY, run_with_limited_time, ExceededTimeError
from Reversi.consts import EM, OPPONENT_COLOR, BOARD_COLS, BOARD_ROWS
import time
import copy
from collections import defaultdict

# ===============================================================================
# consts
# ===============================================================================
REG_5 = 99
REG_4_C_SQUARE = -8
REG_4_X_SQUARE = -24
REG_2_FAR_FROM_CORNER = -3
REG_2_CLOSE_TO_CORNER = -4
REG_3_CLOSE_TO_CORNER = 8
REG_3_FAR_FROM_CORNER = 6
REG_1_CLOSE_TO_CORNER = 7
REG_1_FAR_FROM_CORNER = 4
REG_3_START = 0

BOARD_WEIGHT_SQUARE = {
    (0, 0): REG_5,     # region 5 - corners.
    (0, 7): REG_5,
    (7, 0): REG_5,
    (7, 7): REG_5,
    (0, 1): REG_4_C_SQUARE,     # region 4
    (1, 0): REG_4_C_SQUARE,
    (6, 0): REG_4_C_SQUARE,
    (7, 1): REG_4_C_SQUARE,
    (6, 7): REG_4_C_SQUARE,
    (7, 6): REG_4_C_SQUARE,
    (0, 6): REG_4_C_SQUARE,
    (1, 7): REG_4_C_SQUARE,
    (1, 1): REG_4_X_SQUARE,
    (6, 1): REG_4_X_SQUARE,
    (1, 6): REG_4_X_SQUARE,
    (6, 6): REG_4_X_SQUARE,
    (1, 2): REG_2_CLOSE_TO_CORNER,     # region 2
    (2, 1): REG_2_CLOSE_TO_CORNER,
    (5, 1): REG_2_CLOSE_TO_CORNER,
    (6, 2): REG_2_CLOSE_TO_CORNER,
    (1, 5): REG_2_CLOSE_TO_CORNER,
    (2, 6): REG_2_CLOSE_TO_CORNER,
    (6, 5): REG_2_CLOSE_TO_CORNER,
    (5, 6): REG_2_CLOSE_TO_CORNER,
    (1, 3): REG_2_FAR_FROM_CORNER,
    (3, 1): REG_2_FAR_FROM_CORNER,
    (4, 6): REG_2_FAR_FROM_CORNER,
    (4, 1): REG_2_FAR_FROM_CORNER,
    (6, 3): REG_2_FAR_FROM_CORNER,
    (6, 4): REG_2_FAR_FROM_CORNER,
    (3, 6): REG_2_FAR_FROM_CORNER,
    (1, 4): REG_2_FAR_FROM_CORNER,
    (0, 2): REG_3_CLOSE_TO_CORNER,      # region 3
    (2, 0): REG_3_CLOSE_TO_CORNER,
    (5, 0): REG_3_CLOSE_TO_CORNER,
    (7, 2): REG_3_CLOSE_TO_CORNER,
    (0, 5): REG_3_CLOSE_TO_CORNER,
    (2, 7): REG_3_CLOSE_TO_CORNER,
    (5, 7): REG_3_CLOSE_TO_CORNER,
    (7, 5): REG_3_CLOSE_TO_CORNER,
    (0, 3): REG_3_FAR_FROM_CORNER,
    (0, 4): REG_3_FAR_FROM_CORNER,
    (3, 0): REG_3_FAR_FROM_CORNER,
    (4, 0): REG_3_FAR_FROM_CORNER,
    (7, 3): REG_3_FAR_FROM_CORNER,
    (7, 4): REG_3_FAR_FROM_CORNER,
    (3, 7): REG_3_FAR_FROM_CORNER,
    (4, 7): REG_3_FAR_FROM_CORNER,
    (2, 2): REG_1_CLOSE_TO_CORNER,      # region 1
    (5, 2): REG_1_CLOSE_TO_CORNER,
    (2, 5): REG_1_CLOSE_TO_CORNER,
    (5, 5): REG_1_CLOSE_TO_CORNER,
    (2, 3): REG_1_FAR_FROM_CORNER,
    (2, 4): REG_1_FAR_FROM_CORNER,
    (3, 2): REG_1_FAR_FROM_CORNER,
    (4, 2): REG_1_FAR_FROM_CORNER,
    (5, 3): REG_1_FAR_FROM_CORNER,
    (5, 4): REG_1_FAR_FROM_CORNER,
    (4, 5): REG_1_FAR_FROM_CORNER,
    (3, 5): REG_1_FAR_FROM_CORNER,
    (3, 3): REG_3_START,
    (3, 4): REG_3_START,
    (4, 3): REG_3_START,
    (4, 4): REG_3_START

}



# ODD_REGION = '1'      #for potential use in future, in areas calculation.
# EVEN_REGION = '0'
PROCESSING_REGION = '*'
# ===============================================================================
# better player
# ===============================================================================

class Player(abstract.AbstractPlayer):

    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        abstract.AbstractPlayer.__init__(self, setup_time, player_color, time_per_k_turns, k)
        self.clock = time.time()

        # We are simply providing (remaining time / remaining turns) for each turn in round.
        # Taking a spare time of 0.05 seconds.
        self.turns_remaining_in_round = self.k
        self.time_remaining_in_round = self.time_per_k_turns
        self.time_for_current_move = self.time_remaining_in_round / self.turns_remaining_in_round - 0.05

    def get_move(self, game_state, possible_moves):
        self.clock = time.time()
        self.time_for_current_move = self.time_remaining_in_round / self.turns_remaining_in_round - 0.05
        if len(possible_moves) == 1:
            return possible_moves[0]

        # <old best move calc>
        best_move = possible_moves[0]
        next_state = copy.deepcopy(game_state)  # is preformed to leave the original game state unchanged.
        next_state.perform_move(best_move[0], best_move[1])
        # Choosing an arbitrary move
        # Get the best move according the utility function
        for move in possible_moves:
            new_state = copy.deepcopy(game_state)
            new_state.perform_move(move[0], move[1])
            if self.utility(new_state, move) > self.utility(next_state, move):
                next_state = new_state
                best_move = move
        # </old best move calc>

        if self.turns_remaining_in_round == 1:
            self.turns_remaining_in_round = self.k
            self.time_remaining_in_round = self.time_per_k_turns
        else:
            self.turns_remaining_in_round -= 1
            self.time_remaining_in_round -= (time.time() - self.clock)

        return best_move

    def utility(self, state, move):  # this is a greedy utility function- goes on the step where i'll have the most units.
        even_regions = 0

        # considering the regions of the new state- we strive for more even regions for the opponents move.
        if True:  # todo may be extend condition to lower bound of units on board
            heuristic_state = copy.deepcopy(state)
            even_regions = self.num_of_even_regions(heuristic_state)

        # considering the number of moves for oponent
        heuristic_state.curr_player = OPPONENT_COLOR[heuristic_state.curr_player]
        oponent_move_num = len(heuristic_state.get_possible_moves())

        #considering the static weight of every cell
        move_weight = BOARD_WEIGHT_SQUARE[(move[0], move[1])]
        return move_weight + even_regions - oponent_move_num  # + self.player_units_count(state)

    def num_of_even_regions(self, game_state):
        def aux_num_of_even_regions(regions_board, row, col, region_corr):
            if not(row >= 0 and row <= 7 and col >= 0 and col <=7) or regions_board[row][col] != EM:
                return
            regions_board[row][col] = PROCESSING_REGION
            region_corr.append((row, col))
            aux_num_of_even_regions(regions_board, row, col+1, region_corr)
            aux_num_of_even_regions(regions_board, row, col-1, region_corr)
            aux_num_of_even_regions(regions_board, row+1, col, region_corr)
            aux_num_of_even_regions(regions_board, row-1, col, region_corr)
            return

        num_odd_region = num_even_region = 0
        regions_board = copy.deepcopy(game_state.board)
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                if regions_board[i][j] != EM:
                    continue
                region_corr = []
                aux_num_of_even_regions(regions_board, i, j, region_corr)
                if len(region_corr) % 2 == 0:
                    ++num_even_region
                else:
                    ++num_odd_region
        return num_even_region      # optional return num_odd_region


    def player_units_count(self, state):
        if len(state.get_possible_moves()) == 0:  # todo I didn't get the meaning of this if.
            return INFINITY if state.curr_player != self.color else -INFINITY

        my_u = 0
        op_u = 0
        for x in range(BOARD_COLS):
            for y in range(BOARD_ROWS):
                if state.board[x][y] == self.color:
                    my_u += 1
                if state.board[x][y] == OPPONENT_COLOR[self.color]:
                    op_u += 1

        if my_u == 0:
            # I have no tools left
            return -INFINITY
        elif op_u == 0:
            # The opponent has no tools left
            return INFINITY
        else:
            return my_u - op_u

    def selective_deepening_criterion(self, state):
        # Simple player does not selectively deepen into certain nodes.
        return False

    def no_more_time(self):
        return (time.time() - self.clock) >= self.time_for_current_move

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'better')

# c:\python35\python.exe run_game.py 3 3 3 y simple_player random_player
