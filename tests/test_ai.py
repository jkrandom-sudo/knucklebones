"""Tests for the AI."""
import random
import unittest

import ai
import knucklebones as kb


class GainDisruptTests(unittest.TestCase):
    def test_gain_empty_column(self):
        b = [[], [], []]
        self.assertEqual(ai._gain(b, 0, 4), 4)

    def test_gain_match(self):
        b = [[4], [], []]
        # before: 4; after [4,4]: 16; gain 12
        self.assertEqual(ai._gain(b, 0, 4), 12)

    def test_gain_three_match(self):
        b = [[4, 4], [], []]
        # before: 16; after [4,4,4]: 36; gain 20
        self.assertEqual(ai._gain(b, 0, 4), 20)

    def test_disruption(self):
        opp = [[4, 4], [], []]
        # remove both 4s: before 16, after 0 -> 16
        self.assertEqual(ai._disruption(opp, 0, 4), 16)

    def test_no_disruption(self):
        opp = [[3, 5], [], []]
        self.assertEqual(ai._disruption(opp, 0, 4), 0)


class EasyAITests(unittest.TestCase):
    def test_easy_returns_legal(self):
        rng = random.Random(0)
        boards = [[[], [], []], [[], [], []]]
        for _ in range(20):
            c = ai.choose_column(boards, 0, 3, "easy", rng)
            self.assertIn(c, (0, 1, 2))

    def test_easy_avoids_full(self):
        rng = random.Random(0)
        boards = [[[1, 2, 3], [], []], [[], [], []]]
        for _ in range(20):
            c = ai.choose_column(boards, 0, 3, "easy", rng)
            self.assertIn(c, (1, 2))


class NormalAITests(unittest.TestCase):
    def test_normal_picks_disruption(self):
        # opp has two 4s in col 1 — disruption value 16, gain only 4.
        # Putting a 4 in col 1 nets 4 + 16 = 20; col 0 nets 4 + 0 = 4.
        boards = [[[], [], []], [[], [4, 4], []]]
        c = ai.choose_column(boards, 0, 4, "normal", random.Random(0))
        self.assertEqual(c, 1)

    def test_normal_picks_stacking(self):
        # Own col 0 has 4,4 -> placing 4 there gains 20 (16 -> 36).
        # Disruption empty everywhere.
        boards = [[[4, 4], [], []], [[], [], []]]
        c = ai.choose_column(boards, 0, 4, "normal", random.Random(0))
        self.assertEqual(c, 0)

    def test_normal_skips_full_columns(self):
        boards = [[[1, 2, 3], [], []], [[], [], []]]
        c = ai.choose_column(boards, 0, 4, "normal", random.Random(0))
        self.assertIn(c, (1, 2))


class HardAITests(unittest.TestCase):
    def test_hard_returns_legal(self):
        rng = random.Random(0)
        boards = [[[], [], []], [[], [], []]]
        c = ai.choose_column(boards, 0, 3, "hard", rng)
        self.assertIn(c, (0, 1, 2))

    def test_hard_picks_disruption(self):
        # Big disruption beat: opp has [6,6,6] in col 0.
        # Placing a 6 in col 0 disrupts 54 points.
        boards = [[[], [], []], [[6, 6, 6], [], []]]
        c = ai.choose_column(boards, 0, 6, "hard", random.Random(0))
        self.assertEqual(c, 0)

    def test_hard_skips_full(self):
        boards = [[[1, 2, 3], [], []], [[], [], []]]
        c = ai.choose_column(boards, 0, 4, "hard", random.Random(0))
        self.assertIn(c, (1, 2))


class NoLegalTests(unittest.TestCase):
    def test_raises_when_no_legal(self):
        boards = [[[1, 2, 3], [4, 5, 6], [1, 2, 3]], [[], [], []]]
        with self.assertRaises(ValueError):
            ai.choose_column(boards, 0, 3, "normal", random.Random(0))


if __name__ == "__main__":
    unittest.main()
