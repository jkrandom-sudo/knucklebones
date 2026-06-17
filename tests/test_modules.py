"""Tests for i18n / settings / score / sound modules."""
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import i18n
import score
import settings
import sound


class I18nTests(unittest.TestCase):
    def test_basic_lookup(self):
        self.assertEqual(i18n.t("zh", "menu_quit")[0:2], "q)")
        self.assertIn("Quit", i18n.t("en", "menu_quit"))

    def test_format(self):
        s = i18n.t("en", "rolled", value=5)
        self.assertIn("5", s)

    def test_unknown_key(self):
        self.assertEqual(i18n.t("en", "doesnotexist"), "doesnotexist")

    def test_unknown_lang_falls_back(self):
        # Should not raise for an unknown language
        s = i18n.t("xx", "menu_quit")
        self.assertTrue(isinstance(s, str))

    def test_format_with_missing_kwarg(self):
        # missing kwargs should not raise — falls back to raw string
        s = i18n.t("en", "rolled")
        self.assertTrue(isinstance(s, str))

    def test_parity(self):
        zh = set(i18n.STRINGS["zh"].keys())
        en = set(i18n.STRINGS["en"].keys())
        self.assertEqual(zh, en, f"missing keys: zh-en={zh-en}, en-zh={en-zh}")


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.tmp.close()
        self.path = Path(self.tmp.name)
        os.unlink(self.path)

    def tearDown(self):
        if self.path.exists():
            os.unlink(self.path)

    def test_defaults_when_missing(self):
        s = settings.load(self.path)
        self.assertEqual(s["lang"], "zh")
        self.assertTrue(s["sound"])
        self.assertEqual(s["difficulty"], "normal")

    def test_round_trip(self):
        s = settings.load(self.path)
        s["lang"] = "en"
        s["sound"] = False
        settings.save(s, self.path)
        s2 = settings.load(self.path)
        self.assertEqual(s2["lang"], "en")
        self.assertFalse(s2["sound"])

    def test_invalid_lang_reverts(self):
        with open(self.path, "w") as f:
            json.dump({"lang": "fr", "sound": True}, f)
        s = settings.load(self.path)
        self.assertEqual(s["lang"], "zh")

    def test_invalid_volume_reverts(self):
        with open(self.path, "w") as f:
            json.dump({"volume": 99}, f)
        s = settings.load(self.path)
        self.assertEqual(s["volume"], 1)

    def test_corrupt_json(self):
        with open(self.path, "w") as f:
            f.write("not json{")
        s = settings.load(self.path)
        self.assertEqual(s["lang"], "zh")

    def test_cycle_lang(self):
        s = {"lang": "zh"}
        settings.cycle_lang(s)
        self.assertEqual(s["lang"], "en")
        settings.cycle_lang(s)
        self.assertEqual(s["lang"], "zh")

    def test_toggle_sound(self):
        s = {"sound": True}
        settings.toggle_sound(s)
        self.assertFalse(s["sound"])
        settings.toggle_sound(s)
        self.assertTrue(s["sound"])

    def test_cycle_volume(self):
        s = {"volume": 0}
        settings.cycle_volume(s)
        self.assertEqual(s["volume"], 1)
        for _ in range(3):
            settings.cycle_volume(s)
        self.assertEqual(s["volume"], 0)

    def test_cycle_difficulty(self):
        s = {"difficulty": "easy"}
        settings.cycle_difficulty(s)
        self.assertEqual(s["difficulty"], "normal")
        settings.cycle_difficulty(s)
        self.assertEqual(s["difficulty"], "hard")
        settings.cycle_difficulty(s)
        self.assertEqual(s["difficulty"], "easy")


class ScoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.tmp.close()
        self.path = Path(self.tmp.name)
        os.unlink(self.path)

    def tearDown(self):
        if self.path.exists():
            os.unlink(self.path)

    def test_load_missing(self):
        self.assertEqual(score.load(self.path), [])

    def test_add_and_load(self):
        score.add("alice", 50, "normal", self.path)
        score.add("bob", 70, "hard", self.path)
        scores = score.load(self.path)
        self.assertEqual(scores[0]["name"], "bob")
        self.assertEqual(scores[1]["name"], "alice")

    def test_top_10_only(self):
        for i in range(15):
            score.add(f"p{i}", i, "normal", self.path)
        scores = score.load(self.path)
        self.assertEqual(len(scores), 10)
        self.assertEqual(scores[0]["score"], 14)

    def test_corrupt_load(self):
        with open(self.path, "w") as f:
            f.write("garbage")
        self.assertEqual(score.load(self.path), [])

    def test_anon_name(self):
        score.add("", 5, "easy", self.path)
        scores = score.load(self.path)
        self.assertEqual(scores[0]["name"], "anon")

    def test_truncates_name(self):
        score.add("a" * 50, 5, "easy", self.path)
        scores = score.load(self.path)
        self.assertEqual(len(scores[0]["name"]), 12)


class SoundTests(unittest.TestCase):
    def test_disabled_silent(self):
        out = io.StringIO()
        snd = sound.Sound(enabled=False, volume=3, output=out)
        snd.roll(); snd.place(); snd.disrupt(); snd.win(); snd.lose()
        self.assertEqual(out.getvalue(), "")

    def test_zero_volume_silent(self):
        out = io.StringIO()
        snd = sound.Sound(enabled=True, volume=0, output=out)
        snd.roll()
        self.assertEqual(out.getvalue(), "")

    def test_volume_scales(self):
        out = io.StringIO()
        snd = sound.Sound(enabled=True, volume=2, output=out)
        snd.roll()  # base 1 * vol 2
        self.assertEqual(out.getvalue(), "\a\a")

    def test_disrupt_louder(self):
        out = io.StringIO()
        snd = sound.Sound(enabled=True, volume=1, output=out)
        snd.disrupt()
        self.assertEqual(out.getvalue(), "\a\a")

    def test_volume_clamped(self):
        out = io.StringIO()
        snd = sound.Sound(enabled=True, volume=99, output=out)
        snd.roll()  # clamped to 3
        self.assertEqual(len(out.getvalue()), 3)

    def test_negative_volume_clamped(self):
        out = io.StringIO()
        snd = sound.Sound(enabled=True, volume=-5, output=out)
        snd.roll()
        self.assertEqual(out.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
