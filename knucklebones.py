"""Knucklebones — core game logic.

Two players, each with a 3-column board (each column holds up to 3 dice).
Each turn:
  1. Active player rolls a single d6 (revealed before placement).
  2. They choose a column on their own board with free space.
  3. The die is placed there.
  4. **Disruption**: any of the opponent's dice in the SAME column with
     the SAME value are immediately removed from the opponent's board.
  5. Turn passes to the opponent.

The game ends as soon as either player's board is full (all 9 slots
filled). The player with the higher total score wins (tie possible).

Column scoring (per player, per column):
  - Group dice in the column by value.
  - Each group of `k` identical dice with value `v` contributes
    `k * v * k = v * k^2` (one v = v, two v = 4v, three v = 9v).
  - The column's score is the sum across all groups.

Total score is the sum of the three column scores.
"""
import random
from collections import Counter
from typing import List, Optional


COLUMNS = 3
ROWS = 3
DEFAULT_TARGET_PLAYERS = 2


class KnucklebonesError(Exception):
    pass


def column_score(dice: List[int]) -> int:
    """Score one column. Identical dice multiply by group size."""
    total = 0
    for value, count in Counter(dice).items():
        total += value * count * count
    return total


def board_score(board: List[List[int]]) -> int:
    return sum(column_score(col) for col in board)


def board_full(board: List[List[int]]) -> bool:
    return all(len(col) >= ROWS for col in board)


def empty_board() -> List[List[int]]:
    return [[] for _ in range(COLUMNS)]


def legal_columns(board: List[List[int]]) -> List[int]:
    return [i for i, col in enumerate(board) if len(col) < ROWS]


class KnucklebonesGame:
    def __init__(self, num_players: int = 2, starting_player: int = 0):
        if num_players != 2:
            raise ValueError("only two-player Knucklebones is supported")
        self.boards: List[List[List[int]]] = [empty_board()
                                               for _ in range(num_players)]
        self.current_player: int = starting_player % num_players
        self.pending_die: Optional[int] = None
        self.winner: Optional[int] = None
        self.is_draw: bool = False
        self.last_disruption: int = 0
        self.turn_count: int = 0

    @property
    def num_players(self) -> int:
        return len(self.boards)

    def roll(self, rng: Optional[random.Random] = None) -> int:
        if self.winner is not None or self.is_draw:
            raise KnucklebonesError("game already over")
        if self.pending_die is not None:
            raise KnucklebonesError("die already pending — place it first")
        if rng is None:
            rng = random.Random()
        v = rng.randint(1, 6)
        self.pending_die = v
        return v

    def place(self, player: int, column: int) -> dict:
        if self.winner is not None or self.is_draw:
            raise KnucklebonesError("game already over")
        if player != self.current_player:
            raise KnucklebonesError("not your turn")
        if self.pending_die is None:
            raise KnucklebonesError("no die rolled yet")
        if column < 0 or column >= COLUMNS:
            raise KnucklebonesError("column out of range")
        board = self.boards[player]
        if len(board[column]) >= ROWS:
            raise KnucklebonesError("column full")
        die = self.pending_die
        board[column].append(die)
        # Disruption: opponent's dice in same column with same value removed.
        opponent = 1 - player
        before = len(self.boards[opponent][column])
        self.boards[opponent][column] = [d for d in self.boards[opponent][column]
                                          if d != die]
        removed = before - len(self.boards[opponent][column])
        self.last_disruption = removed
        self.pending_die = None
        self.turn_count += 1
        # End-game check
        if board_full(board) or board_full(self.boards[opponent]):
            s0 = board_score(self.boards[0])
            s1 = board_score(self.boards[1])
            if s0 > s1:
                self.winner = 0
            elif s1 > s0:
                self.winner = 1
            else:
                self.is_draw = True
        else:
            self.current_player = opponent
        return {"placed": die, "column": column, "removed": removed}

    def scores(self) -> List[int]:
        return [board_score(b) for b in self.boards]

    def column_scores(self, player: int) -> List[int]:
        return [column_score(c) for c in self.boards[player]]

    def reset(self, starting_player: int = 0) -> None:
        self.boards = [empty_board() for _ in range(self.num_players)]
        self.current_player = starting_player % self.num_players
        self.pending_die = None
        self.winner = None
        self.is_draw = False
        self.last_disruption = 0
        self.turn_count = 0


def simulate_place(board: List[List[int]], column: int,
                   die: int) -> List[List[int]]:
    """Return a copy of `board` with `die` placed in `column`."""
    new = [list(c) for c in board]
    new[column] = list(new[column]) + [die]
    return new


def simulate_disrupt(board: List[List[int]], column: int,
                     value: int) -> List[List[int]]:
    new = [list(c) for c in board]
    new[column] = [d for d in new[column] if d != value]
    return new
