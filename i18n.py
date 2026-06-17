"""Bilingual strings."""

STRINGS = {
    "zh": {
        "title": "骰子高手 / Knucklebones",
        "menu_play": "p) 开始游戏",
        "menu_help": "h) 帮助",
        "menu_scores": "l) 排行榜",
        "menu_settings": "s) 设置",
        "menu_quit": "q) 退出",
        "menu_choice": "请选择 > ",
        "bye": "再见!",
        "unknown": "未知选项: {choice}",
        "help_title": "帮助",
        "help_body": (
            "骰子高手 (Knucklebones): 双人骰子放置游戏。\n"
            "规则:\n"
            "  - 每位玩家拥有一个 3x3 的棋盘 (3 列, 每列最多 3 颗)。\n"
            "  - 轮到自己时, 先掷一颗骰子, 然后选择一列放入。\n"
            "  - 放置后, 对方棋盘同一列中所有相同点数的骰子都会被移除!\n"
            "  - 一方棋盘填满 (9 颗) 时立即结束。\n"
            "得分:\n"
            "  - 每列分数 = 各点数 × 该点数出现次数的平方。\n"
            "    例: 一颗 4 = 4; 两颗 4 = 4×4 = 16; 三颗 4 = 4×9 = 36。\n"
            "  - 总分 = 三列分数之和。\n"
            "  - 总分较高者胜。\n"
            "操作:\n"
            "  1, 2, 3 = 选择对应的列下骰\n"
            "  q = 放弃本局\n"
            "策略: 既要堆砌相同点数获取高分, 又要砸掉对方的高分组合!\n"
        ),
        "press_enter": "按回车继续...",
        "settings_title": "设置",
        "settings_lang": "1) 语言: {value}",
        "settings_sound": "2) 声音: {value}",
        "settings_volume": "3) 音量: {value}",
        "settings_difficulty": "4) AI 难度: {value}",
        "settings_back": "b) 返回",
        "scores_title": "排行榜 (Top 10)",
        "scores_empty": "暂无成绩",
        "scores_row": "{rank:>2}. {name:<12} {score:>4}  ({difficulty})",
        "name_prompt": "姓名(空= 不保存): ",
        "ai_label": "AI",
        "you_label": "你",
        "your_turn": ">>> 你的回合 <<<",
        "ai_turn": ">>> AI 回合 <<<",
        "rolled": "掷出: {value}",
        "ai_rolled": "AI 掷出: {value}",
        "input_column": "选择列 (1/2/3, q=退出) > ",
        "ai_placed": "AI 放在第 {column} 列",
        "you_placed": "你放在第 {column} 列",
        "disruption": "✦ 砸掉对方 {n} 颗 {value} 点!",
        "no_disruption": "",
        "scoreboard": "得分 — 你: {you}  AI: {ai}",
        "column_full": "该列已满, 请重新选择。",
        "invalid_column": "请输入 1, 2 或 3。",
        "you_win": "胜! 你 {you} 比 AI {ai}, 得 {score} 分。",
        "you_lose": "AI 赢! AI {ai} 比 你 {you}。",
        "draw": "平局! 双方都是 {score} 分。",
        "diff_easy": "简单",
        "diff_normal": "普通",
        "diff_hard": "困难",
        "lang_zh": "中文",
        "lang_en": "英文",
        "on": "开",
        "off": "关",
    },
    "en": {
        "title": "Knucklebones",
        "menu_play": "p) Play",
        "menu_help": "h) Help",
        "menu_scores": "l) Leaderboard",
        "menu_settings": "s) Settings",
        "menu_quit": "q) Quit",
        "menu_choice": "Choose > ",
        "bye": "Bye!",
        "unknown": "Unknown option: {choice}",
        "help_title": "Help",
        "help_body": (
            "Knucklebones: a two-player dice-placement game.\n"
            "Rules:\n"
            "  - Each player has a 3x3 board (3 columns × 3 slots).\n"
            "  - On your turn, roll a die, then choose a column to drop\n"
            "    it into on YOUR board.\n"
            "  - All of the OPPONENT's dice in the SAME column with the\n"
            "    SAME value are immediately removed.\n"
            "  - The game ends as soon as a board is full (9 dice).\n"
            "Scoring:\n"
            "  - Each column scores: sum over distinct values v of\n"
            "    v × (count of v)^2.\n"
            "  - One 4 = 4; two 4s = 4×4 = 16; three 4s = 4×9 = 36.\n"
            "  - Total = sum of all three columns.\n"
            "  - Higher total wins.\n"
            "Commands:\n"
            "  1, 2, 3 = drop the die into that column\n"
            "  q = quit round\n"
            "Strategy: build matching stacks for big multipliers — and\n"
            "smash the opponent's stacks before they pay off!\n"
        ),
        "press_enter": "Press Enter to continue...",
        "settings_title": "Settings",
        "settings_lang": "1) Language: {value}",
        "settings_sound": "2) Sound: {value}",
        "settings_volume": "3) Volume: {value}",
        "settings_difficulty": "4) AI difficulty: {value}",
        "settings_back": "b) Back",
        "scores_title": "Leaderboard (Top 10)",
        "scores_empty": "No scores yet",
        "scores_row": "{rank:>2}. {name:<12} {score:>4}  ({difficulty})",
        "name_prompt": "Name (empty = skip save): ",
        "ai_label": "AI",
        "you_label": "You",
        "your_turn": ">>> Your turn <<<",
        "ai_turn": ">>> AI turn <<<",
        "rolled": "Rolled: {value}",
        "ai_rolled": "AI rolled: {value}",
        "input_column": "Choose column (1/2/3, q=quit) > ",
        "ai_placed": "AI placed in column {column}",
        "you_placed": "You placed in column {column}",
        "disruption": "✦ Smashed {n} of opponent's {value}s!",
        "no_disruption": "",
        "scoreboard": "Score — You: {you}  AI: {ai}",
        "column_full": "Column full — pick another.",
        "invalid_column": "Enter 1, 2 or 3.",
        "you_win": "You win! You {you} vs AI {ai}, score {score}.",
        "you_lose": "AI wins. AI {ai} vs You {you}.",
        "draw": "Draw! Both at {score}.",
        "diff_easy": "easy",
        "diff_normal": "normal",
        "diff_hard": "hard",
        "lang_zh": "Chinese",
        "lang_en": "English",
        "on": "on",
        "off": "off",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    table = STRINGS.get(lang) or STRINGS["en"]
    s = table.get(key)
    if s is None:
        s = STRINGS["en"].get(key, key)
    if kwargs:
        try:
            return s.format(**kwargs)
        except Exception:
            return s
    return s
