"""AI for Knucklebones.

Each strategy decides which legal column to place the pending die in.

  - easy:    picks a random legal column.
  - normal:  greedy — maximises (own_score_gain + opponent_disruption).
  - hard:    1-ply lookahead with random opponent rollout averaging,
             tie-breaking with raw greedy heuristic.
"""
import random
from typing import List, Optional

from knucklebones import (COLUMNS, ROWS, board_score, column_score,
                          legal_columns, simulate_disrupt, simulate_place)


DIFFICULTIES = ("easy", "normal", "hard")

# Validated difficulty aliases (for robustness)
DIFFICULTY_ALIASES = {
    "easy": "easy",
    "normal": "normal",
    "hard": "hard",
    "e": "easy",
    "n": "normal",
    "h": "hard",
}


def _gain(board: List[List[int]], column: int, die: int) -> int:
    """Score gained for `board` by placing `die` in `column`."""
    before = column_score(board[column])
    after = column_score(list(board[column]) + [die])
    return after - before


def _disruption(opp_board: List[List[int]], column: int,
                die: int) -> int:
    """Score lost by opponent if `die` is placed in `column`."""
    before = column_score(opp_board[column])
    after = column_score([d for d in opp_board[column] if d != die])
    return before - after


def choose_column(boards: List[List[List[int]]], player: int, die: int,
                  difficulty: str = "normal",
                  rng: Optional[random.Random] = None) -> int:
    if rng is None:
        rng = random.Random()
    my_board = boards[player]
    opp_board = boards[1 - player]
    legal = legal_columns(my_board)
    if not legal:
        raise ValueError("no legal column")

    # Validate and normalize difficulty
    normalized = DIFFICULTY_ALIASES.get(difficulty)
    if normalized is None:
        raise ValueError(f"invalid difficulty: {difficulty!r} "
                         f"(must be one of {DIFFICULTIES})")

    if normalized == "easy":
        return rng.choice(legal)

    scored = []
    for c in legal:
        gain = _gain(my_board, c, die)
        disrupt = _disruption(opp_board, c, die)
        scored.append((c, gain, disrupt))

    if normalized == "normal":
        # Maximise gain + disruption; tiebreak by gain alone, then disruption,
        # then prefer columns with fewer dice (preserves flexibility).
        def key(x):
            c, g, d = x
            return (-(g + d), -g, -d, len(my_board[c]))
        scored.sort(key=key)
        return scored[0][0]

    # hard: simulate one opponent reply (random die 1..6 averaged)
    def expected_opp_score(opp_board: List[List[int]],
                            my_board_after: List[List[int]]) -> float:
        opp_legal = legal_columns(opp_board)
        if not opp_legal:
            return board_score(opp_board)
        # Average over die values; for each die, opp picks max gain.
        total = 0.0
        for d in range(1, 7):
            best = float("-inf")
            for c in opp_legal:
                gain = _gain(opp_board, c, d)
                disrupt = _disruption(my_board_after, c, d)
                value = gain + disrupt * 0.5
                if value > best:
                    best = value
            total += best
        return total / 6.0

    best_score = float("-inf")
    best_column = legal[0]
    for c in legal:
        new_my = simulate_place(my_board, c, die)
        new_opp = simulate_disrupt(opp_board, c, die)
        net_gain = _gain(my_board, c, die) + _disruption(opp_board, c, die)
        opp_potential = expected_opp_score(new_opp, new_my)
        # Prefer high net_gain, then low opponent potential.
        score = net_gain * 2 - opp_potential
        if score > best_score:
            best_score = score
            best_column = c
    return best_column
