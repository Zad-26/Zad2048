"""
Zad 2048 - Game Logic Module
Handles all core 2048 game mechanics including board state,
tile merging, move validation, and win/lose detection.
"""

import random
import copy


class GameLogic:
    """
    Core 2048 game logic engine.
    Manages the board state, moves, scoring, and game conditions.
    """

    BOARD_SIZE = 4
    WIN_TILE = 2048

    def __init__(self):
        self.board = []
        self.score = 0
        self.previous_board = []
        self.previous_score = 0
        self.moved = False
        self.merged_positions = []  # Track which tiles merged this move
        self.new_tile_pos = None    # Track where new tile spawned
        self.reset()

    def reset(self):
        """Initialize or reset the board to a fresh game state."""
        self.board = [[0] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
        self.score = 0
        self.previous_board = copy.deepcopy(self.board)
        self.previous_score = 0
        self.merged_positions = []
        self.new_tile_pos = None
        # Spawn two starting tiles
        self.spawn_tile()
        self.spawn_tile()

    def spawn_tile(self):
        """
        Spawn a new tile (2 or 4) at a random empty position.
        Returns the position (row, col) where the tile was spawned.
        """
        empty_cells = [
            (r, c)
            for r in range(self.BOARD_SIZE)
            for c in range(self.BOARD_SIZE)
            if self.board[r][c] == 0
        ]
        if not empty_cells:
            return None

        pos = random.choice(empty_cells)
        # 90% chance for 2, 10% chance for 4
        self.board[pos[0]][pos[1]] = 2 if random.random() < 0.9 else 4
        self.new_tile_pos = pos
        return pos

    def _compress_row(self, row):
        """
        Compress a row by sliding non-zero tiles to the left.
        Returns the compressed row.
        """
        new_row = [val for val in row if val != 0]
        new_row += [0] * (self.BOARD_SIZE - len(new_row))
        return new_row

    def _merge_row(self, row):
        """
        Merge adjacent equal tiles in a row (left direction).
        Returns (merged_row, score_gained, merge_indices).
        """
        score_gained = 0
        merge_indices = []

        for i in range(self.BOARD_SIZE - 1):
            if row[i] != 0 and row[i] == row[i + 1]:
                row[i] *= 2
                score_gained += row[i]
                row[i + 1] = 0
                merge_indices.append(i)

        return row, score_gained, merge_indices

    def _process_row(self, row):
        """
        Full row processing: compress → merge → compress.
        Returns (processed_row, score_gained, merge_indices).
        """
        row = self._compress_row(row)
        row, score_gained, merge_indices = self._merge_row(row)
        row = self._compress_row(row)
        return row, score_gained, merge_indices

    def move_left(self):
        """Execute a left swipe move."""
        self._save_state()
        self.merged_positions = []
        self.moved = False

        for r in range(self.BOARD_SIZE):
            original = self.board[r][:]
            new_row, gained, merges = self._process_row(self.board[r][:])
            self.board[r] = new_row
            self.score += gained

            if new_row != original:
                self.moved = True

            for c in merges:
                self.merged_positions.append((r, c))

        if self.moved:
            self.spawn_tile()

        return self.moved

    def move_right(self):
        """Execute a right swipe move."""
        self._save_state()
        self.merged_positions = []
        self.moved = False

        for r in range(self.BOARD_SIZE):
            original = self.board[r][:]
            reversed_row = self.board[r][::-1]
            new_row, gained, merges = self._process_row(reversed_row)
            new_row = new_row[::-1]
            self.board[r] = new_row
            self.score += gained

            if new_row != original:
                self.moved = True

            for c in merges:
                actual_c = self.BOARD_SIZE - 1 - c
                self.merged_positions.append((r, actual_c))

        if self.moved:
            self.spawn_tile()

        return self.moved

    def move_up(self):
        """Execute an up swipe move."""
        self._save_state()
        self.merged_positions = []
        self.moved = False

        for c in range(self.BOARD_SIZE):
            original = [self.board[r][c] for r in range(self.BOARD_SIZE)]
            col = original[:]
            new_col, gained, merges = self._process_row(col)
            self.score += gained

            if new_col != original:
                self.moved = True

            for r in range(self.BOARD_SIZE):
                self.board[r][c] = new_col[r]

            for r in merges:
                self.merged_positions.append((r, c))

        if self.moved:
            self.spawn_tile()

        return self.moved

    def move_down(self):
        """Execute a down swipe move."""
        self._save_state()
        self.merged_positions = []
        self.moved = False

        for c in range(self.BOARD_SIZE):
            original = [self.board[r][c] for r in range(self.BOARD_SIZE)]
            col = original[::-1]
            new_col, gained, merges = self._process_row(col)
            new_col = new_col[::-1]
            self.score += gained

            if new_col != original:
                self.moved = True

            for r in range(self.BOARD_SIZE):
                self.board[r][c] = new_col[r]

            for r in merges:
                actual_r = self.BOARD_SIZE - 1 - r
                self.merged_positions.append((actual_r, c))

        if self.moved:
            self.spawn_tile()

        return self.moved

    def _save_state(self):
        """Save the current board and score for undo functionality."""
        self.previous_board = copy.deepcopy(self.board)
        self.previous_score = self.score

    def undo(self):
        """Restore the board to the previous state."""
        self.board = copy.deepcopy(self.previous_board)
        self.score = self.previous_score
        self.merged_positions = []
        self.new_tile_pos = None

    def is_game_over(self):
        """
        Check if the game is over (no valid moves remaining).
        Returns True if the game is over.
        """
        # Check for any empty cell
        for r in range(self.BOARD_SIZE):
            for c in range(self.BOARD_SIZE):
                if self.board[r][c] == 0:
                    return False

        # Check for any possible horizontal merge
        for r in range(self.BOARD_SIZE):
            for c in range(self.BOARD_SIZE - 1):
                if self.board[r][c] == self.board[r][c + 1]:
                    return False

        # Check for any possible vertical merge
        for r in range(self.BOARD_SIZE - 1):
            for c in range(self.BOARD_SIZE):
                if self.board[r][c] == self.board[r + 1][c]:
                    return False

        return True

    def has_won(self):
        """
        Check if the player has reached the 2048 tile.
        Returns True if the win condition is met.
        """
        for r in range(self.BOARD_SIZE):
            for c in range(self.BOARD_SIZE):
                if self.board[r][c] >= self.WIN_TILE:
                    return True
        return False

    def get_highest_tile(self):
        """Return the value of the highest tile on the board."""
        return max(max(row) for row in self.board)

    def get_board_copy(self):
        """Return a deep copy of the current board."""
        return copy.deepcopy(self.board)

    def get_empty_count(self):
        """Return the number of empty cells on the board."""
        return sum(
            1
            for r in range(self.BOARD_SIZE)
            for c in range(self.BOARD_SIZE)
            if self.board[r][c] == 0
        )
