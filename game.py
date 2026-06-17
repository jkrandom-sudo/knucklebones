"""Knucklebones — main menu and round loop."""
import random
import sys
from typing import Optional

import ai as ai_mod
import score as score_mod
import settings as settings_mod
from i18n import t
from knucklebones import (COLUMNS, ROWS, KnucklebonesError,
                          KnucklebonesGame, column_score)
from sound import Sound


class QuitGame(Exception):
    pass


DIFFICULTY_BONUS = {"easy": 1, "normal": 2, "hard": 3}


def render_boards(game: KnucklebonesGame, lang: str) -> str:
    """Two boards side-by-side: AI on top (inverted), You on bottom."""
    ai_board = game.boards[1]
    you_board = game.boards[0]
    you_label = t(lang, "you_label")
    ai_label = t(lang, "ai_label")
    lines = []
    # AI board: rows from row 2 (deepest) to row 0 (most recent)
    # Actually we display top-down; the AI rolls into their board from
    # "below" in screen terms, but visually we treat their grid as 3x3.
    lines.append(f"  {ai_label}")
    lines.append("  +---+---+---+")
    for r in reversed(range(ROWS)):
        cells = []
        for c in range(COLUMNS):
            col = ai_board[c]
            if r < len(col):
                cells.append(f" {col[r]} ")
            else:
                cells.append("   ")
        lines.append("  |" + "|".join(cells) + "|")
    # Column scores for AI
    ai_scores = [column_score(c) for c in ai_board]
    lines.append("  " + "  ".join(f"{s:>3}" for s in ai_scores))
    lines.append("")
    # You board
    you_scores = [column_score(c) for c in you_board]
    lines.append("  " + "  ".join(f"{s:>3}" for s in you_scores))
    for r in range(ROWS):
        cells = []
        for c in range(COLUMNS):
            col = you_board[c]
            if r < len(col):
                cells.append(f" {col[r]} ")
            else:
                cells.append("   ")
        lines.append("  |" + "|".join(cells) + "|")
    lines.append("  +---+---+---+")
    lines.append("    1   2   3")
    lines.append(f"  {you_label}")
    return "\n".join(lines)


def play_round(s: dict, sound: Sound, input_func, output,
               rng=None) -> Optional[dict]:
    if rng is None:
        rng = random.Random()
    lang = s.get("lang", "zh")
    difficulty = s.get("difficulty", "normal")
    game = KnucklebonesGame(num_players=2, starting_player=0)

    def write(msg=""):
        output.write(msg + "\n")

    while game.winner is None and not game.is_draw:
        write(render_boards(game, lang))
        write(t(lang, "scoreboard",
                you=game.scores()[0], ai=game.scores()[1]))
        if game.current_player == 0:
            write(t(lang, "your_turn"))
            value = game.roll(rng)
            sound.roll()
            write(t(lang, "rolled", value=value))
            while True:
                try:
                    line = input_func(t(lang, "input_column"))
                except EOFError:
                    raise QuitGame()
                cmd = line.strip().lower()
                if cmd == "q":
                    return None
                if cmd not in ("1", "2", "3"):
                    write(t(lang, "invalid_column"))
                    sound.illegal()
                    continue
                col = int(cmd) - 1
                try:
                    res = game.place(0, col)
                except KnucklebonesError:
                    write(t(lang, "column_full"))
                    sound.illegal()
                    continue
                sound.place()
                write(t(lang, "you_placed", column=col + 1))
                if res["removed"] > 0:
                    sound.disrupt()
                    write(t(lang, "disruption", n=res["removed"],
                            value=value))
                break
        else:
            write(t(lang, "ai_turn"))
            value = game.roll(rng)
            sound.roll()
            write(t(lang, "ai_rolled", value=value))
            col = ai_mod.choose_column(game.boards, 1, value, difficulty,
                                       rng)
            res = game.place(1, col)
            sound.place()
            write(t(lang, "ai_placed", column=col + 1))
            if res["removed"] > 0:
                sound.disrupt()
                write(t(lang, "disruption", n=res["removed"], value=value))

    write(render_boards(game, lang))
    you, ai = game.scores()
    write(t(lang, "scoreboard", you=you, ai=ai))
    if game.winner == 0:
        score = you * DIFFICULTY_BONUS.get(difficulty, 1)
        write(t(lang, "you_win", you=you, ai=ai, score=score))
        sound.win()
        return {"result": "win", "score": score, "difficulty": difficulty}
    if game.winner == 1:
        write(t(lang, "you_lose", you=you, ai=ai))
        sound.lose()
        return {"result": "loss", "score": 0, "difficulty": difficulty}
    write(t(lang, "draw", score=you))
    return {"result": "draw", "score": 0, "difficulty": difficulty}


def show_help(s: dict, input_func, output) -> None:
    lang = s.get("lang", "zh")
    output.write("\n=== " + t(lang, "help_title") + " ===\n")
    output.write(t(lang, "help_body") + "\n")
    try:
        input_func(t(lang, "press_enter"))
    except EOFError:
        pass


def show_scores(s: dict, input_func, output) -> None:
    lang = s.get("lang", "zh")
    scores = score_mod.load()
    output.write("\n=== " + t(lang, "scores_title") + " ===\n")
    if not scores:
        output.write(t(lang, "scores_empty") + "\n")
    else:
        for i, e in enumerate(scores, 1):
            output.write(t(
                lang, "scores_row",
                rank=i, name=e.get("name", "")[:12],
                score=e.get("score", 0),
                difficulty=t(lang, f"diff_{e.get('difficulty', 'normal')}"),
            ) + "\n")
    try:
        input_func(t(lang, "press_enter"))
    except EOFError:
        pass


def settings_menu(s: dict, input_func, output) -> dict:
    while True:
        lang = s.get("lang", "zh")
        output.write("\n=== " + t(lang, "settings_title") + " ===\n")
        output.write(t(lang, "settings_lang", value=t(lang, f"lang_{lang}")) + "\n")
        output.write(t(lang, "settings_sound",
                       value=t(lang, "on" if s.get("sound") else "off")) + "\n")
        output.write(t(lang, "settings_volume", value=s.get("volume", 1)) + "\n")
        output.write(t(lang, "settings_difficulty",
                       value=t(lang, f"diff_{s.get('difficulty', 'normal')}")) + "\n")
        output.write(t(lang, "settings_back") + "\n")
        try:
            choice = input_func(t(lang, "menu_choice")).strip().lower()
        except EOFError:
            break
        if choice == "1":
            settings_mod.cycle_lang(s)
        elif choice == "2":
            settings_mod.toggle_sound(s)
        elif choice == "3":
            settings_mod.cycle_volume(s)
        elif choice == "4":
            settings_mod.cycle_difficulty(s)
        elif choice == "b":
            break
        else:
            output.write(t(lang, "unknown", choice=choice) + "\n")
    settings_mod.save(s)
    return s


def main_menu(input_func=None, output=None, rng=None) -> None:
    if input_func is None:
        input_func = input
    if output is None:
        output = sys.stdout
    if rng is None:
        rng = random.Random()
    s = settings_mod.load()
    settings_mod.save(s)
    while True:
        lang = s.get("lang", "zh")
        output.write("\n=== " + t(lang, "title") + " ===\n")
        output.write(t(lang, "menu_play") + "\n")
        output.write(t(lang, "menu_help") + "\n")
        output.write(t(lang, "menu_scores") + "\n")
        output.write(t(lang, "menu_settings") + "\n")
        output.write(t(lang, "menu_quit") + "\n")
        try:
            choice = input_func(t(lang, "menu_choice")).strip().lower()
        except EOFError:
            output.write(t(lang, "bye") + "\n")
            return
        if choice == "q":
            output.write(t(lang, "bye") + "\n")
            return
        if choice == "p":
            sound = Sound(enabled=bool(s.get("sound", True)),
                          volume=int(s.get("volume", 1)),
                          output=output)
            try:
                result = play_round(s, sound, input_func, output, rng=rng)
            except QuitGame:
                output.write(t(lang, "bye") + "\n")
                return
            if result is None:
                continue
            try:
                name = input_func(t(lang, "name_prompt")).strip()
            except EOFError:
                name = ""
            if name and result["score"] > 0 and result["result"] == "win":
                score_mod.add(name, result["score"], result["difficulty"])
        elif choice == "h":
            show_help(s, input_func, output)
        elif choice == "l":
            show_scores(s, input_func, output)
        elif choice == "s":
            settings_menu(s, input_func, output)
        else:
            output.write(t(lang, "unknown", choice=choice) + "\n")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print()
