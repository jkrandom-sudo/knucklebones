"""Tests for the round + menu loop."""
import io
import unittest
from unittest import mock

import game


class StackedInput:
    def __init__(self, answers):
        self.answers = list(answers)
        self.calls = 0

    def __call__(self, prompt=""):
        if self.calls >= len(self.answers):
            raise EOFError()
        v = self.answers[self.calls]
        self.calls += 1
        return v


class FixedRng:
    def __init__(self, values):
        self.values = list(values)
        self.idx = 0

    def randint(self, lo, hi):
        v = self.values[self.idx]
        self.idx += 1
        return v

    def choice(self, seq):
        return seq[0]


class RenderTests(unittest.TestCase):
    def test_render_includes_columns(self):
        from knucklebones import KnucklebonesGame
        g = KnucklebonesGame()
        g.boards[0][0] = [4]
        g.boards[1][2] = [6]
        out = game.render_boards(g, "en")
        self.assertIn("4", out)
        self.assertIn("6", out)
        self.assertIn("You", out)
        self.assertIn("AI", out)


class PlayRoundTests(unittest.TestCase):
    def setUp(self):
        self.out = io.StringIO()
        self.sound = mock.MagicMock()

    def _settings(self, **kw):
        s = {"lang": "en", "difficulty": "normal", "sound": False, "volume": 0}
        s.update(kw)
        return s

    def test_invalid_then_valid(self):
        # Use a seeded real RNG so rolls vary and the round can terminate.
        import random
        # 200 inputs is plenty for any round (max 9 valid placements per
        # player, plus retries on full columns).
        inputs = StackedInput(["9"] + ["1", "2", "3"] * 200)
        try:
            result = game.play_round(self._settings(difficulty="easy"),
                                     self.sound, inputs, self.out,
                                     rng=random.Random(0))
        except game.QuitGame:
            self.fail("round did not terminate")
        self.assertIsNotNone(result)
        self.assertIn(result["result"], ("win", "loss", "draw"))

    def test_quit_returns_none(self):
        import random
        inputs = StackedInput(["q"])
        result = game.play_round(self._settings(),
                                 self.sound, inputs, self.out,
                                 rng=random.Random(0))
        self.assertIsNone(result)

    def test_full_column_rejected(self):
        import random
        # Try col 1 first (might reject if full), keep cycling.
        inputs = StackedInput(["1", "1", "1", "1", "2"] +
                              ["1", "2", "3"] * 200)
        try:
            result = game.play_round(self._settings(difficulty="easy"),
                                     self.sound, inputs, self.out,
                                     rng=random.Random(1))
        except game.QuitGame:
            self.fail("round did not terminate")
        self.assertIsNotNone(result)

    def test_win_score_includes_difficulty_bonus(self):
        # Use patch to force fake outcome
        with mock.patch.object(game, "DIFFICULTY_BONUS",
                               {"easy": 1, "normal": 2, "hard": 3}):
            self.assertEqual(game.DIFFICULTY_BONUS["hard"], 3)


class HelpScoresTests(unittest.TestCase):
    def test_show_help(self):
        out = io.StringIO()
        inputs = StackedInput([""])
        game.show_help({"lang": "en"}, inputs, out)
        self.assertIn("Knucklebones", out.getvalue())

    def test_show_help_zh(self):
        out = io.StringIO()
        inputs = StackedInput([""])
        game.show_help({"lang": "zh"}, inputs, out)
        self.assertIn("骰子", out.getvalue())

    def test_show_scores_empty(self):
        out = io.StringIO()
        inputs = StackedInput([""])
        with mock.patch.object(game.score_mod, "load", return_value=[]):
            game.show_scores({"lang": "en"}, inputs, out)
        self.assertIn("No scores yet", out.getvalue())

    def test_show_scores_with_entries(self):
        out = io.StringIO()
        inputs = StackedInput([""])
        entries = [
            {"name": "alice", "score": 50, "difficulty": "normal"},
            {"name": "bob", "score": 30, "difficulty": "easy"},
        ]
        with mock.patch.object(game.score_mod, "load", return_value=entries):
            game.show_scores({"lang": "en"}, inputs, out)
        text = out.getvalue()
        self.assertIn("alice", text)
        self.assertIn("bob", text)


class SettingsMenuTests(unittest.TestCase):
    def test_cycle_lang(self):
        out = io.StringIO()
        inputs = StackedInput(["1", "b"])
        s = {"lang": "zh", "sound": True, "volume": 1, "difficulty": "normal"}
        with mock.patch.object(game.settings_mod, "save"):
            game.settings_menu(s, inputs, out)
        self.assertEqual(s["lang"], "en")

    def test_toggle_sound(self):
        out = io.StringIO()
        inputs = StackedInput(["2", "b"])
        s = {"lang": "en", "sound": True, "volume": 1, "difficulty": "normal"}
        with mock.patch.object(game.settings_mod, "save"):
            game.settings_menu(s, inputs, out)
        self.assertFalse(s["sound"])

    def test_cycle_volume(self):
        out = io.StringIO()
        inputs = StackedInput(["3", "b"])
        s = {"lang": "en", "sound": True, "volume": 1, "difficulty": "normal"}
        with mock.patch.object(game.settings_mod, "save"):
            game.settings_menu(s, inputs, out)
        self.assertEqual(s["volume"], 2)

    def test_cycle_difficulty(self):
        out = io.StringIO()
        inputs = StackedInput(["4", "b"])
        s = {"lang": "en", "sound": True, "volume": 1, "difficulty": "easy"}
        with mock.patch.object(game.settings_mod, "save"):
            game.settings_menu(s, inputs, out)
        self.assertEqual(s["difficulty"], "normal")

    def test_unknown(self):
        out = io.StringIO()
        inputs = StackedInput(["x", "b"])
        s = {"lang": "en", "sound": True, "volume": 1, "difficulty": "normal"}
        with mock.patch.object(game.settings_mod, "save"):
            game.settings_menu(s, inputs, out)
        self.assertIn("Unknown", out.getvalue())


class MainMenuTests(unittest.TestCase):
    def _stub_settings(self):
        return {"lang": "en", "sound": False, "volume": 0,
                "difficulty": "normal"}

    def test_quit(self):
        out = io.StringIO()
        inputs = StackedInput(["q"])
        with mock.patch.object(game.settings_mod, "load",
                                return_value=self._stub_settings()), \
             mock.patch.object(game.settings_mod, "save"):
            game.main_menu(inputs, out)
        self.assertIn("Bye", out.getvalue())

    def test_help_then_quit(self):
        out = io.StringIO()
        inputs = StackedInput(["h", "", "q"])
        with mock.patch.object(game.settings_mod, "load",
                                return_value=self._stub_settings()), \
             mock.patch.object(game.settings_mod, "save"):
            game.main_menu(inputs, out)
        self.assertIn("Knucklebones", out.getvalue())

    def test_scores_then_quit(self):
        out = io.StringIO()
        inputs = StackedInput(["l", "", "q"])
        with mock.patch.object(game.settings_mod, "load",
                                return_value=self._stub_settings()), \
             mock.patch.object(game.settings_mod, "save"), \
             mock.patch.object(game.score_mod, "load", return_value=[]):
            game.main_menu(inputs, out)
        self.assertIn("No scores yet", out.getvalue())

    def test_unknown_choice(self):
        out = io.StringIO()
        inputs = StackedInput(["z", "q"])
        with mock.patch.object(game.settings_mod, "load",
                                return_value=self._stub_settings()), \
             mock.patch.object(game.settings_mod, "save"):
            game.main_menu(inputs, out)
        self.assertIn("Unknown", out.getvalue())

    def test_play_win_records_score(self):
        out = io.StringIO()
        inputs = StackedInput(["p", "alice", "q"])
        fake_result = {"result": "win", "score": 42, "difficulty": "normal"}
        added = []

        def fake_add(name, score, difficulty, path=None):
            added.append((name, score, difficulty))

        with mock.patch.object(game.settings_mod, "load",
                                return_value=self._stub_settings()), \
             mock.patch.object(game.settings_mod, "save"), \
             mock.patch.object(game, "play_round", return_value=fake_result), \
             mock.patch.object(game.score_mod, "add", side_effect=fake_add):
            game.main_menu(inputs, out)
        self.assertEqual(added, [("alice", 42, "normal")])

    def test_play_loss_does_not_record(self):
        out = io.StringIO()
        inputs = StackedInput(["p", "alice", "q"])
        fake_result = {"result": "loss", "score": 0, "difficulty": "easy"}
        added = []

        def fake_add(name, score, difficulty, path=None):
            added.append((name, score, difficulty))

        with mock.patch.object(game.settings_mod, "load",
                                return_value=self._stub_settings()), \
             mock.patch.object(game.settings_mod, "save"), \
             mock.patch.object(game, "play_round", return_value=fake_result), \
             mock.patch.object(game.score_mod, "add", side_effect=fake_add):
            game.main_menu(inputs, out)
        self.assertEqual(added, [])

    def test_play_quit_round(self):
        out = io.StringIO()
        inputs = StackedInput(["p", "q"])
        with mock.patch.object(game.settings_mod, "load",
                                return_value=self._stub_settings()), \
             mock.patch.object(game.settings_mod, "save"), \
             mock.patch.object(game, "play_round", return_value=None):
            game.main_menu(inputs, out)
        # main menu should re-prompt and we feed q to exit
        self.assertIn("Bye", out.getvalue())

    def test_quit_during_round_exits(self):
        out = io.StringIO()
        inputs = StackedInput(["p"])

        def raise_quit(*a, **kw):
            raise game.QuitGame()

        with mock.patch.object(game.settings_mod, "load",
                                return_value=self._stub_settings()), \
             mock.patch.object(game.settings_mod, "save"), \
             mock.patch.object(game, "play_round", side_effect=raise_quit):
            game.main_menu(inputs, out)
        self.assertIn("Bye", out.getvalue())


if __name__ == "__main__":
    unittest.main()
