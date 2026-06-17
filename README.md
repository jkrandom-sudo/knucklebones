# 骰子高手 / Knucklebones

A Python terminal implementation of the dice-placement game from
*Cult of the Lamb* (in turn inspired by the Witcher 3 minigame and
ancient Greek "knucklebones"). 100% pure standard library — no
third-party dependencies.

You vs. AI, 3×3 boards. Stack matching dice for column multipliers and
**smash** the opponent's stacks before they pay off.

## 规则 / Rules

- Each player has a 3×3 board (3 columns, each holding up to 3 dice).
- On your turn: roll a single d6, then choose a column to drop it into
  on YOUR board.
- **Disruption**: when you place a die, all of the opponent's dice in
  the SAME column with the SAME value are immediately removed from
  their board.
- The game ends as soon as either board is full (9 dice).

## 计分 / Scoring

Each column scores: for each distinct value `v` appearing `k` times,
add `v × k²`.

| Column contents      | Score                  |
| -------------------- | ---------------------- |
| `[4]`                | 4                      |
| `[4, 4]`             | 4 × 4 = **16**         |
| `[4, 4, 4]`          | 4 × 9 = **36**         |
| `[3, 2, 2]`          | 3 + (2 × 4) = **11**   |

Total = sum of all three columns. Higher total wins.

## 安装与运行 / Run

Requires only Python 3.8 or later — no external packages.

```bash
git clone https://github.com/jkrandom-sudo/knucklebones.git
cd knucklebones
python3 game.py
```

Then pick `p` from the main menu to start a round, or `s` to change
language, sound, volume or AI difficulty.

## 操作 / Controls

In the main menu:

- `p` — play a round
- `h` — help
- `l` — leaderboard (top 10)
- `s` — settings (language / sound / volume / difficulty)
- `q` — quit

In a round, after a roll is shown:

- `1`, `2`, `3` — drop the die into that column on your board
- `q` — abandon the current round

## 难度 / Difficulty

| Level | AI behaviour                                          | Win bonus |
| ----- | ----------------------------------------------------- | --------- |
| 简单 / easy   | Picks a random legal column.                  | ×1        |
| 普通 / normal | Greedy: maximises gain + opponent disruption. | ×2        |
| 困难 / hard   | 1-ply lookahead averaging opponent rolls.     | ×3        |

When you win, your final score is multiplied by the difficulty bonus
before being recorded on the leaderboard.

## 文件 / Files

- `game.py` — main menu, round loop, board rendering
- `knucklebones.py` — core game state and column-scoring logic
- `ai.py` — three AI strategies
- `i18n.py` — bilingual zh/en strings
- `settings.py` — persistent settings (`~/.knucklebones_settings.json`)
- `score.py`    — persistent leaderboard (`~/.knucklebones_scores.json`)
- `sound.py`    — terminal-bell SFX
- `tests/`      — 96 unit tests

## 测试 / Tests

```bash
python3 tests/run_tests.py
```

96 tests covering scoring, board state, disruption, end-game detection,
all three AI strategies, persistence, i18n parity, and the menu loop.

## 策略提示 / Strategy

- Stacking three of a kind is huge — `4×9 = 36` from a single column.
- But matching the opponent's stack lets you wipe it instantly. Sometimes
  smashing 16 points off them is better than gaining 16 yourself.
- The AI on `hard` will pre-empt your stacks. Diversify your columns or
  bait it into wasting placements.

## 授权 / License

MIT.
