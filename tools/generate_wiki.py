"""Generate GitHub Wiki game-guide pages from the Pyxel Rogue source tables."""

from __future__ import annotations

import argparse
import html
import re
import sys
import types
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _install_pyxel_stub() -> None:
    try:
        import pyxel  # noqa: F401
    except ModuleNotFoundError:
        pyxel = types.ModuleType("pyxel")

        def _missing_attr(name):
            if name.startswith("KEY_") or name.startswith("GAMEPAD"):
                return 0
            raise AttributeError(name)

        pyxel.__getattr__ = _missing_attr
        pyxel.__file__ = str(REPO_ROOT / "pyxel" / "__init__.py")
        sys.modules["pyxel"] = pyxel


_install_pyxel_stub()

import rogue  # noqa: E402
from pyxel_rogue import rogue_dungeon, rogue_monsters, rogue_rings, rogue_scrolls, rogue_sticks, rogue_things  # noqa: E402
from pyxel_rogue.rogue_items import CAT_ARM, CAT_FOOD, CAT_POT, CAT_RING, CAT_SCR, CAT_STICK, CAT_WPN  # noqa: E402
from pyxel_rogue.rogue_lang import LANG_EN, LANG_JA  # noqa: E402
from pyxel_rogue.rogue_text import TextCatalog  # noqa: E402


LANGS = (LANG_JA, LANG_EN)
MONSTER_ORDER = tuple(rogue_monsters.LEVEL_MONSTERS)
TREASURE_ROOM_COUNT_DIST = {count: 1 / (rogue_dungeon.MAXTREAS - rogue_dungeon.MINTREAS) for count in range(rogue_dungeon.MINTREAS, rogue_dungeon.MAXTREAS)}
TERM_OVERRIDES = {(LANG_JA, "weapon", "spear"): "槍"}

POTION_MESSAGE_KEYS = {
    "confusion": "potions.wait_what_s_going_on_here_huh_what_who",
    "hallucination": "potions.oh_wow_everything_seems_so_cosmic",
    "poison": "potions.you_feel_very_sick_now",
    "gain strength": "potions.you_feel_stronger_now_what_bulging_muscles",
    "see invisible": "potions.this_potion_tastes_like_item_juice",
    "healing": "potions.you_begin_to_feel_better",
    "monster detection": "pyxel.sense_monsters",
    "magic detection": "pyxel.sense_magic",
    "raise level": "potions.you_suddenly_feel_much_more_skillful",
    "extra healing": "potions.you_begin_to_feel_much_better",
    "haste self": "potions.you_feel_yourself_moving_much_faster",
    "restore strength": "potions.hey_this_tastes_great_it_make_you_feel_warm_all_over",
    "blindness": "potions.a_cloak_of_darkness_falls_around_you",
    "levitation": "potions.you_start_to_float_in_the_air",
}

SCROLL_MESSAGE_KEYS = {
    "monster confusion": "scrolls.your_hands_begin_to_glow_color",
    "magic mapping": "scrolls.oh_now_this_scroll_has_a_map_on_it",
    "hold monster": "scrolls.the_monsters_around_you_freeze",
    "sleep": "scrolls.you_fall_asleep",
    "enchant armor": "scrolls.your_armor_glows_color_for_a_moment",
    "identify potion": "scrolls.this_scroll_is_an_item_scroll",
    "identify scroll": "scrolls.this_scroll_is_an_item_scroll",
    "identify weapon": "scrolls.this_scroll_is_an_item_scroll",
    "identify armor": "scrolls.this_scroll_is_an_item_scroll",
    "identify ring, wand or staff": "scrolls.this_scroll_is_an_item_scroll",
    "scare monster": "scrolls.you_hear_maniacal_laughter_in_the_distance",
    "food detection": "scrolls.your_nose_tingles_and_you_smell_food",
    "teleportation": "",
    "enchant weapon": "scrolls.your_color_glows_color2_for_a_moment",
    "create monster": "scrolls.you_hear_a_faint_cry_of_anguish_in_the_distance",
    "remove curse": "scrolls.you_feel_as_if_somebody_is_watching_over_you",
    "aggravate monsters": "scrolls.you_hear_a_high_pitched_humming_noise",
    "protect armor": "scrolls.your_armor_is_covered_by_a_shimmering_color_shield",
}

TRAP_SUMMARIES = {
    LANG_EN: {
        "trap door": "Drops the hero to the next level.",
        "arrow trap": "Fires an arrow attack.",
        "sleeping gas trap": "Puts the hero to sleep.",
        "bear trap": "Pins the hero in place.",
        "teleport trap": "Teleports the hero.",
        "dart trap": "Fires a poison dart.",
        "rust trap": "Rusts worn armor unless protected.",
        "mysterious trap": "Triggers one of several strange messages.",
    },
    LANG_JA: {
        "trap door": "次の階へ落とされる。",
        "arrow trap": "矢の攻撃を受ける。",
        "sleeping gas trap": "眠って行動不能になる。",
        "bear trap": "その場に足止めされる。",
        "teleport trap": "別の場所へ飛ばされる。",
        "dart trap": "毒矢の攻撃を受ける。",
        "rust trap": "防護なしの装備中よろいが錆びる。",
        "mysterious trap": "不思議なメッセージ効果が起きる。",
    },
}


def monster_prob_matrix() -> dict[int, dict[str, float]]:
    result = {}
    table = rogue_monsters.LEVEL_MONSTERS
    for level in range(1, 27):
        probs = {}
        for rnd10 in range(10):
            depth = level + rnd10 - 6
            if depth < 0:
                for d5 in range(5):
                    probs[table[d5]] = probs.get(table[d5], 0.0) + 0.02
            elif depth > 25:
                for d5 in range(5):
                    probs[table[21 + d5]] = probs.get(table[21 + d5], 0.0) + 0.02
            else:
                probs[table[depth]] = probs.get(table[depth], 0.0) + 0.1
        result[level] = probs
    return result


def average_damage_expr(expr: str) -> float:
    total = 0.0
    for count, sides in re.findall(r"(\d+)x(\d+)", expr):
        total += int(count) * (int(sides) + 1) / 2
    return total


def term(lang: str, cat: str, name: str) -> str:
    if (lang, cat, name) in TERM_OVERRIDES:
        return TERM_OVERRIDES[(lang, cat, name)]
    cat_map = {
        "potion": CAT_POT,
        "scroll": CAT_SCR,
        "weapon": CAT_WPN,
        "armor": CAT_ARM,
        "ring": CAT_RING,
        "stick": CAT_STICK,
        "food": CAT_FOOD,
    }
    return TextCatalog.item_kind(lang, cat_map[cat], name)


def msg(lang: str, key: str, **kw) -> str:
    return TextCatalog.msg(lang, key, **kw) if key else "-"


def other_lang(lang: str) -> str:
    return LANG_EN if lang == LANG_JA else LANG_JA


def pct(value: float, bold_threshold: float | None = None) -> str:
    if value <= 0:
        return "-"
    n = round(value * 100)
    text = f"{n}%"
    return f"**{text}**" if bold_threshold is not None and value >= bold_threshold else text


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def fmt1(value: float) -> str:
    return f"{value:.1f}"


def monster_name(lang: str, sym: str) -> str:
    spec = next(spec for spec in rogue.BESTIARY if spec.sym == sym)
    return TextCatalog.monster(lang, spec.name)


def monster_heatmap_svg(lang: str) -> str:
    matrix = monster_prob_matrix()
    cell_w = 38
    cell_h = 24
    left = 50
    top = 78
    width = left + cell_w * len(MONSTER_ORDER) + 44
    height = top + cell_h * 26 + 50
    title = "Monster Appearance Heatmap" if lang == LANG_EN else "フロア別モンスター出現率"
    subtitle = "Rogue 5.4.4 randmonster() theoretical values" if lang == LANG_EN else "Rogue 5.4.4 randmonster() 理論値"
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbf8ee"/>',
        f'<text x="24" y="32" font-family="Georgia, serif" font-size="22" fill="#222">{html.escape(title)}</text>',
        f'<text x="24" y="54" font-family="sans-serif" font-size="12" fill="#777">{html.escape(subtitle)}</text>',
    ]
    for i, sym in enumerate(MONSTER_ORDER):
        x = left + i * cell_w + cell_w / 2
        out.append(f'<text x="{x:.1f}" y="{top - 14}" text-anchor="middle" font-family="monospace" font-size="13" fill="#333">{sym}</text>')
        out.append(f'<text x="{x:.1f}" y="{top + cell_h * 26 + 20}" text-anchor="middle" font-family="monospace" font-size="13" fill="#333">{sym}</text>')
    for floor in range(1, 27):
        y = top + (floor - 1) * cell_h
        out.append(f'<text x="{left - 14}" y="{y + 16}" text-anchor="end" font-family="monospace" font-size="12" fill="#555">{floor}</text>')
        for i, sym in enumerate(MONSTER_ORDER):
            value = matrix[floor].get(sym, 0.0)
            if value <= 0:
                fill = "#f4efe1"
                label = ""
            else:
                intensity = min(1.0, value / 0.2)
                red = round(247 - intensity * 110)
                green = round(230 - intensity * 138)
                blue = round(188 - intensity * 152)
                fill = f"#{red:02x}{green:02x}{blue:02x}"
                label = f"{round(value * 100)}"
            x = left + i * cell_w
            out.append(f'<rect x="{x}" y="{y}" width="{cell_w - 1}" height="{cell_h - 1}" fill="{fill}"/>')
            if label:
                out.append(f'<text x="{x + cell_w / 2:.1f}" y="{y + 16}" text-anchor="middle" font-family="monospace" font-size="10" fill="#2b2118">{label}</text>')
    for boundary in (5, 10, 15, 20, 25):
        y = top + boundary * cell_h - 1
        out.append(f'<line x1="{left}" y1="{y}" x2="{left + cell_w * len(MONSTER_ORDER) - 1}" y2="{y}" stroke="#5a5347" stroke-width="2.2"/>')
    for boundary in (5, 9, 14, 19, 24):
        x = left + boundary * cell_w - 1
        out.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{top + cell_h * 26 - 1}" stroke="#d1c9b8" stroke-width="1.4"/>')
    out.append(f'<rect x="{left}" y="{top}" width="{cell_w * len(MONSTER_ORDER) - 1}" height="{cell_h * 26 - 1}" fill="none" stroke="#5a5347" stroke-width="1.2"/>')
    out.append('<text x="24" y="{0}" font-family="sans-serif" font-size="11" fill="#777">cell value = %, darker = more likely</text>'.format(height - 12))
    out.append("</svg>")
    return "\n".join(out) + "\n"


def top_monster_rows(lang: str) -> list[list[str]]:
    rows = []
    matrix = monster_prob_matrix()
    for floor in range(1, 27):
        top = sorted(matrix[floor].items(), key=lambda item: (-item[1], MONSTER_ORDER.index(item[0])))[:5]
        rows.append([
            str(floor),
            ", ".join(f"{sym} {round(prob * 100)}%" for sym, prob in top),
            ", ".join(monster_name(lang, sym) for sym, _ in top),
        ])
    return rows


def monster_section(lang: str) -> str:
    title = "フロア別モンスター出現率" if lang == LANG_JA else "Monster Appearance by Floor"
    note = (
        "Rogue 5.4.4 `randmonster()` と `LEVEL_MONSTERS` から計算した理論値。"
        if lang == LANG_JA
        else "Theoretical values from Rogue 5.4.4 `randmonster()` and `LEVEL_MONSTERS`."
    )
    names = ", ".join(f"{sym}: {monster_name(lang, sym)}" for sym in MONSTER_ORDER)
    image = "![Monster appearance heatmap](Monster-Appearance-ja.svg)" if lang == LANG_JA else "![Monster appearance heatmap](Monster-Appearance-en.svg)"
    return "\n\n".join((f"## {title}", note, image, names))


def weapon_role(row: dict) -> str:
    if row.get("launcher") is not None:
        return "missile"
    if row.get("missile"):
        return "throw"
    return "melee"


def weapon_sort_damage(row: dict) -> float:
    return average_damage_expr(row["hurl_damage"] if weapon_role(row) in {"throw", "missile"} else row["damage"])


def weapon_section(lang: str) -> str:
    title = "武器一覧（弱い順）" if lang == LANG_JA else "Weapons from Weak to Strong"
    note = (
        "主用途ごとに、期待ダメージが低いものから並べています。投擲武器は投擲平均で並べます。Rogue2.Official では mace は「ほこ」。spear は区別しやすいよう「槍」としています。"
        if lang == LANG_JA
        else "Sorted from lower to higher expected damage within each role. Thrown weapons use thrown average damage. Japanese names are shown for reference."
    )
    headers = (
        ["用途", "名前", "Name", "近接", "投擲", "近接平均", "投擲平均", "出現率", "価値"]
        if lang == LANG_JA
        else ["Role", "Name", "Japanese", "Melee", "Thrown", "Melee avg", "Thrown avg", "Chance", "Worth"]
    )
    role_label = {
        LANG_JA: {"melee": "近接", "throw": "投擲", "missile": "弾"},
        LANG_EN: {"melee": "melee", "throw": "throw", "missile": "missile"},
    }
    rows = []
    for row in sorted(rogue.WEAPONS, key=lambda r: ({"melee": 0, "throw": 1, "missile": 2}[weapon_role(r)], weapon_sort_damage(r), average_damage_expr(r["damage"]), r["name"])):
        rows.append([
            role_label[lang][weapon_role(row)],
            term(lang, "weapon", row["name"]),
            term(LANG_EN if lang == LANG_JA else LANG_JA, "weapon", row["name"]),
            row["damage"],
            row["hurl_damage"],
            f"{average_damage_expr(row['damage']):.1f}",
            f"{average_damage_expr(row['hurl_damage']):.1f}",
            pct(row["prob"] / 100),
            str(row["worth"]),
        ])
    return f"## {title}\n\n{note}\n\n" + markdown_table(headers, rows)


def armor_section(lang: str) -> str:
    title = "よろい一覧（弱い順）" if lang == LANG_JA else "Armors from Weak to Strong"
    headers = (
        ["名前", "Name", "AC", "出現率", "価値"]
        if lang == LANG_JA
        else ["Name", "Japanese", "AC", "Chance", "Worth"]
    )
    rows = [
        [
            term(lang, "armor", row["name"]),
            term(LANG_EN if lang == LANG_JA else LANG_JA, "armor", row["name"]),
            str(row["ac"]),
            pct(row["prob"] / 100),
            str(row["worth"]),
        ]
        for row in sorted(rogue.ARMORS, key=lambda r: r["ac"], reverse=True)
    ]
    return f"## {title}\n\n" + markdown_table(headers, rows)


def potion_section(lang: str) -> str:
    title = "ポーション一覧（価値の低い順）" if lang == LANG_JA else "Potions by Worth, Low to High"
    headers = (
        ["外見", "名前", "Name", "出現率", "価値", "使用メッセージ", "Use message"]
        if lang == LANG_JA
        else ["Appearance", "Name", "Japanese", "Chance", "Worth", "Use message", "使用メッセージ"]
    )
    rows = []
    colors = getattr(rogue, "POT_COLORS")
    for color, row in sorted(zip(colors, rogue.POTIONS), key=lambda pair: (pair[1]["worth"], -pair[1]["prob"])):
        name = row["name"]
        alt_lang = other_lang(lang)
        rows.append([
            TextCatalog.potion_color(lang, color),
            term(lang, "potion", name),
            term(alt_lang, "potion", name),
            pct(row["prob"] / 100),
            str(row["worth"]),
            msg(lang, POTION_MESSAGE_KEYS[name], item=term(lang, "food", "slime-mold")),
            msg(alt_lang, POTION_MESSAGE_KEYS[name], item=term(alt_lang, "food", "slime-mold")),
        ])
    return f"## {title}\n\n" + markdown_table(headers, rows)


def scroll_rows(lang: str, rows_source: list[dict]) -> list[list[str]]:
    rows = []
    for row in sorted((r for r in rows_source if r["prob"] > 0), key=lambda r: (r["worth"], -r["prob"])):
        name = row["name"]
        base_name = "identify potion" if name == "identify" else name
        message_key = SCROLL_MESSAGE_KEYS.get(base_name, "")
        alt_lang = other_lang(lang)
        rows.append([
            term(lang, "scroll", name),
            term(alt_lang, "scroll", name),
            pct(row["prob"] / 100),
            str(row["worth"]),
            msg(
                lang,
                message_key,
                item=term(lang, "scroll", name),
                color=TextCatalog.color(lang, "red", "stem"),
                color2=TextCatalog.color(lang, "blue", "stem"),
            ),
            msg(
                alt_lang,
                message_key,
                item=term(alt_lang, "scroll", name),
                color=TextCatalog.color(alt_lang, "red", "stem"),
                color2=TextCatalog.color(alt_lang, "blue", "stem"),
            ),
        ])
    return rows


def scroll_section(lang: str) -> str:
    title = "巻き物一覧（価値の低い順）" if lang == LANG_JA else "Scrolls by Worth, Low to High"
    note = (
        "Normal は `identify` 巻き物を使う調整配列。0%の旧個別鑑定巻き物は表から省略します。Classic/Strict は Rogue 5.4.4 配列。"
        if lang == LANG_JA
        else "Normal uses the adjusted `identify` scroll table. Old 0% individual identify scrolls are omitted. Classic/Strict use the Rogue 5.4.4 table."
    )
    headers = (
        ["名前", "Name", "出現率", "価値", "使用メッセージ", "Use message"]
        if lang == LANG_JA
        else ["Name", "Japanese", "Chance", "Worth", "Use message", "使用メッセージ"]
    )
    normal = rogue_scrolls.active_scrolls(rogue.SCROLLS, "normal")
    return "\n\n".join((
        f"## {title}",
        note,
        "### Normal",
        markdown_table(headers, scroll_rows(lang, normal)),
        "### Classic / Strict",
        markdown_table(headers, scroll_rows(lang, rogue.SCROLLS)),
    ))


def ring_section(lang: str) -> str:
    title = "指輪一覧（価値の低い順）" if lang == LANG_JA else "Rings by Worth, Low to High"
    note = (
        "食糧消費補正は装備中の追加消費です。「低確率」はその割合で1消費、「節約」はその割合で1消費ぶん戻します。"
        if lang == LANG_JA
        else "Food-use modifier is extra hunger while worn. Chance means one extra use at that odds; saving means one use is refunded at that odds."
    )
    headers = (
        ["名前", "Name", "出現率", "価値", "食糧消費補正"]
        if lang == LANG_JA
        else ["Name", "Japanese", "Chance", "Worth", "Food-use modifier"]
    )
    rows = []
    for index, row in sorted(enumerate(rogue_rings.RINGS), key=lambda item: (item[1].worth, -item[1].prob)):
        rows.append([
            term(lang, "ring", row.name),
            term(LANG_EN if lang == LANG_JA else LANG_JA, "ring", row.name),
            pct(row.prob / 100),
            str(row.worth),
            ring_food_use_label(lang, index),
        ])
    return f"## {title}\n\n{note}\n\n" + markdown_table(headers, rows)


def ring_food_use_label(lang: str, index: int) -> str:
    value = rogue_rings._RING_EAT_USES[index]
    if index == rogue_rings.R_DIGEST:
        return "1/2節約" if lang == LANG_JA else "save 1/2"
    if value == 0:
        return "なし" if lang == LANG_JA else "none"
    if value > 0:
        return f"+{value}"
    return f"1/{abs(value)}低確率" if lang == LANG_JA else f"+1 at 1/{abs(value)}"


def stick_charge_range(index: int) -> str:
    if index == rogue_sticks.WS_LIGHT:
        return "10-19"
    return "3-7"


def stick_section(lang: str) -> str:
    title = "杖一覧（価値の低い順）" if lang == LANG_JA else "Wands and Staves by Worth, Low to High"
    headers = (
        ["名前", "Name", "出現率", "価値", "初期チャージ"]
        if lang == LANG_JA
        else ["Name", "Japanese", "Chance", "Worth", "Initial charges"]
    )
    rows = []
    for index, row in sorted(enumerate(rogue_sticks.STICKS), key=lambda item: (item[1].worth, -item[1].prob)):
        rows.append([
            term(lang, "stick", row.name),
            term(LANG_EN if lang == LANG_JA else LANG_JA, "stick", row.name),
            pct(row.prob / 100),
            str(row.worth),
            f"{row.name}: {stick_charge_range(index)}",
        ])
    return f"## {title}\n\n" + markdown_table(headers, rows)


def item_expectation_by_floor(max_floor: int = 9) -> list[dict[str, float]]:
    state = {0: 1.0}
    rows = []

    def add_level_start(dist):
        next_dist = {}
        for no_food, prob in dist.items():
            new_state = min(no_food + 1, 4)
            next_dist[new_state] = next_dist.get(new_state, 0.0) + prob
        return next_dist

    def add_item_event(dist, weight, counts):
        next_dist = {}
        category_probs = dict(rogue_things.THING_CATEGORIES)
        for no_food, state_prob in dist.items():
            if no_food > 3:
                cats = {"food": 1.0}
            else:
                cats = {cat: prob / 100 for cat, prob in category_probs.items()}
            for cat, cat_prob in cats.items():
                p = state_prob * weight * cat_prob
                counts[cat] += p
                new_state = 0 if cat == "food" else no_food
                next_dist[new_state] = next_dist.get(new_state, 0.0) + p
        return next_dist

    def add_no_item(dist, weight):
        return {no_food: prob * weight for no_food, prob in dist.items()}

    def merge(*dists):
        merged = {}
        for dist in dists:
            for no_food, prob in dist.items():
                merged[no_food] = merged.get(no_food, 0.0) + prob
        return {k: v for k, v in merged.items() if v}

    for floor in range(1, max_floor + 1):
        state = add_level_start(state)
        counts = {cat: 0.0 for cat, _ in rogue_things.THING_CATEGORIES}
        no_treasure = {k: v * (1 - 1 / rogue_dungeon.TREAS_ROOM) for k, v in state.items()}
        treasure_states = []
        for treasure_count, treasure_prob in TREASURE_ROOM_COUNT_DIST.items():
            dist = {k: v * (1 / rogue_dungeon.TREAS_ROOM) * treasure_prob for k, v in state.items()}
            for _ in range(treasure_count):
                dist = add_item_event(dist, 1.0, counts)
            treasure_states.append(dist)
        state = merge(no_treasure, *treasure_states)
        for _ in range(rogue_dungeon.MAXOBJ):
            made = add_item_event(state, rogue_dungeon.PUT_THINGS_PROB / 100, counts)
            skipped = add_no_item(state, 1 - rogue_dungeon.PUT_THINGS_PROB / 100)
            state = merge(made, skipped)
        row = {"floor": float(floor), **counts}
        row["subtotal"] = sum(counts.values())
        row["gold"] = 3.75 * ((50 + 10 * floor - 1) / 2 + 2)
        rows.append(row)
    return rows


def drop_expectation_tables(lang: str) -> tuple[list[str], list[list[str]], list[list[str]]]:
    labels = (
        ["階", "武器", "鎧", "巻物", "薬", "指輪", "杖", "小計", "食料", "GOLD"]
        if lang == LANG_JA
        else ["Floor", "Weapon", "Armor", "Scroll", "Potion", "Ring", "Stick", "Subtotal", "Food", "GOLD"]
    )
    rows = item_expectation_by_floor(9)
    per_floor = []
    cumulative = []
    totals = {key: 0.0 for key in ("weapon", "armor", "scroll", "potion", "ring", "stick", "subtotal", "food", "gold")}
    for row in rows:
        per_floor.append([
            str(int(row["floor"])),
            fmt1(row["weapon"]),
            fmt1(row["armor"]),
            fmt1(row["scroll"]),
            fmt1(row["potion"]),
            fmt1(row["ring"]),
            fmt1(row["stick"]),
            fmt1(row["subtotal"]),
            fmt1(row["food"]),
            fmt1(row["gold"]),
        ])
        for key in totals:
            totals[key] += row[key]
        cumulative.append([
            f"{int(row['floor']) + 1}階" if lang == LANG_JA else f"Floor {int(row['floor']) + 1}",
            fmt1(totals["weapon"]),
            fmt1(totals["armor"]),
            fmt1(totals["scroll"]),
            fmt1(totals["potion"]),
            fmt1(totals["ring"]),
            fmt1(totals["stick"]),
            fmt1(totals["subtotal"]),
            fmt1(totals["food"]),
            fmt1(totals["gold"]),
        ])
    return labels, per_floor, cumulative


def drop_expectation_svg(lang: str) -> str:
    headers, per_floor, cumulative = drop_expectation_tables(lang)
    title = "Drop Rate Reference - Rogue V5" if lang == LANG_EN else "Drop Rate Reference - Rogue V5"
    subtitle = "Strict DP, no simulation, no carried monster drops" if lang == LANG_EN else "厳密 DP 版・シミュレーションなし・怪物所持なし"
    width = 980
    row_h = 26
    y = 86
    col_x = [54, 140, 225, 310, 395, 480, 565, 660, 760, 870]
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="860" viewBox="0 0 {width} 860">',
        '<rect width="100%" height="100%" fill="#fbf8ee"/>',
        f'<text x="54" y="44" font-family="Georgia, serif" font-size="28" fill="#222">{html.escape(title)}</text>',
        f'<text x="54" y="72" font-family="sans-serif" font-size="13" letter-spacing="2" fill="#aaa">{html.escape(subtitle)}</text>',
    ]

    def draw_table(section_y, section_title, rows):
        out.append(f'<text x="54" y="{section_y}" font-family="serif" font-size="18" fill="#333">◆ {html.escape(section_title)}</text>')
        head_y = section_y + 34
        out.append(f'<line x1="54" y1="{head_y + 10}" x2="{width - 54}" y2="{head_y + 10}" stroke="#333" stroke-width="1.2"/>')
        for x, h in zip(col_x, headers):
            out.append(f'<text x="{x}" y="{head_y}" text-anchor="middle" font-family="sans-serif" font-size="13" font-weight="700" fill="#555">{html.escape(h)}</text>')
        body_y = head_y + 30
        for r, row in enumerate(rows):
            yy = body_y + r * row_h
            out.append(f'<line x1="54" y1="{yy + 8}" x2="{width - 54}" y2="{yy + 8}" stroke="#eee8da" stroke-width="1"/>')
            for i, (x, value) in enumerate(zip(col_x, row)):
                weight = "700" if i in (7, 9) else "400"
                fill = "#765000" if i == 9 else "#333"
                out.append(f'<text x="{x}" y="{yy}" text-anchor="middle" font-family="monospace" font-size="14" font-weight="{weight}" fill="{fill}">{html.escape(value)}</text>')

    draw_table(y + 58, "各階ドロップ期待値" if lang == LANG_JA else "Per-floor expected drops", per_floor)
    draw_table(y + 410, "N階到達時点 累計期待値" if lang == LANG_JA else "Cumulative on arrival", cumulative)
    out.append("</svg>")
    return "\n".join(out) + "\n"


def drop_expectation_section(lang: str) -> str:
    title = "ドロップ期待値表" if lang == LANG_JA else "Drop Rate Reference"
    note = (
        "通常の床落ちと宝物部屋を含む理論期待値です。怪物の所持品・シミュレーションは含みません。各階と到達時累計は図にまとめています。"
        if lang == LANG_JA
        else "Theoretical expected values including normal floor drops and treasure rooms. Monster-carried items and simulation are not included. Per-floor and cumulative values are summarized in the figure."
    )
    image = "![Drop rate reference](Drop-Rate-Reference-ja.svg)" if lang == LANG_JA else "![Drop rate reference](Drop-Rate-Reference-en.svg)"
    return "\n\n".join((
        f"## {title}",
        note,
        image,
    ))


def beginner_guide_items(lang: str) -> tuple[list[tuple[str, str, str]], list[tuple[str, str, str]], list[tuple[str, str, str]]]:
    if lang == LANG_JA:
        controls = [
            ("MOVE", "D-pad", "8方向に移動。敵に向かえば攻撃。"),
            ("ACTION", "A", "決定、拾う、階段を使う。"),
            ("RUN", "B長押し + D-pad", "長い通路をラクに進む。"),
            ("SEARCH", "Select+B", "周囲8マスを探す。隠し扉・罠を見つける。"),
            ("WAIT", "A+B", "1ターン足踏み。安全ならHP回復待ち。"),
            ("INFO", "Select", "持ちもの、Log、設定、ヘルプを開く。"),
        ]
        stuck = [
            ("出口がない", "壁沿いを歩き、怪しい場所で Select+B を数回。", "1回で見つからないことは普通。"),
            ("通路が行き止まり", "先端や近くの壁を探す。", "隠し扉で続くことがある。"),
            ("階段が見つからない", "未探索の部屋、隠し扉、隠し通路を疑う。", "歩ける外周をもう一度なぞる。"),
            ("HPが減った", "敵が来ない場所で A+B。", "空腹が進むので待ちすぎない。"),
        ]
        goals = [
            ("1階", "見えるものは拾う。戦闘・拾得・階段に慣れる。", "まず流れを覚える。"),
            ("薬と巻物", "安全な時に試す。結果は Select の Log で確認。", "外見はプレイごとに変わる。"),
            ("走る", "長い直線を少ない入力で進む。", "止まったら周囲を確認。"),
            ("探す", "行き止まりや部屋の壁で使う。", "ターンと食料を使う。"),
        ]
        return controls, stuck, goals

    controls = [
        ("MOVE", "D-pad", "Move in 8 directions. Move into a monster to attack."),
        ("ACTION", "A", "Confirm, pick up items, or use stairs."),
        ("RUN", "Hold B + D-pad", "Move through long corridors with fewer inputs."),
        ("SEARCH", "Select+B", "Search all 8 neighboring tiles for secrets and traps."),
        ("WAIT", "A+B", "Wait one turn. Recover HP if the area is safe."),
        ("INFO", "Select", "Open inventory, Log, settings, and help."),
    ]
    stuck = [
        ("No exit", "Walk along walls and use Select+B several times.", "One search often fails."),
        ("Dead-end corridor", "Search the tip and nearby walls.", "A secret door may continue the route."),
        ("No staircase", "Check unexplored rooms, secret doors, and passages.", "Trace the reachable edge again."),
        ("Low HP", "Use A+B where monsters cannot reach you.", "Waiting still costs hunger."),
    ]
    goals = [
        ("Floor 1", "Pick up visible items and learn fighting, loot, stairs.", "Learn the rhythm first."),
        ("Potions & scrolls", "Try them when safe. Check results in Select > Log.", "Appearances change each run."),
        ("Running", "Use fewer inputs on long straight paths.", "When it stops, check nearby tiles."),
        ("Searching", "Use at dead ends, room walls, and suspicious gaps.", "It costs turns and food."),
    ]
    return controls, stuck, goals


def beginner_guide_svg(lang: str) -> str:
    controls, stuck, goals = beginner_guide_items(lang)
    title = "First Steps in the Dungeon" if lang == LANG_EN else "はじめての探索"
    subtitle = (
        "The few controls that prevent early confusion."
        if lang == LANG_EN
        else "詰まりやすい操作だけ覚える。"
    )
    sections = [
        ("01", "Essential Controls" if lang == LANG_EN else "まず覚える操作", controls),
        ("02", "When You Get Stuck" if lang == LANG_EN else "詰まったら", stuck),
        ("03", "First Goals" if lang == LANG_EN else "最初の方針", goals),
    ]
    width, height = 1440, 680
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<defs>",
        '<linearGradient id="paper" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fbf7eb"/><stop offset="1" stop-color="#eee5d1"/></linearGradient>',
        '<filter id="softShadow" x="-5%" y="-5%" width="110%" height="110%"><feDropShadow dx="0" dy="8" stdDeviation="8" flood-color="#3a2a10" flood-opacity="0.18"/></filter>',
        "</defs>",
        '<rect width="1440" height="680" fill="#fbf7eb"/>',
        '<rect x="28" y="28" width="1384" height="624" rx="18" fill="url(#paper)" filter="url(#softShadow)"/>',
        '<rect x="54" y="54" width="1332" height="572" rx="12" fill="none" stroke="#2c2922" stroke-width="3"/>',
        '<line x1="84" y1="132" x2="1356" y2="132" stroke="#2c2922" stroke-width="4"/>',
        f'<text x="84" y="105" font-family="serif" font-size="46" fill="#27241e">{html.escape(title)}</text>',
        f'<text x="1356" y="103" text-anchor="end" font-family="serif" font-size="24" font-style="italic" fill="#a23631">Rogue V5</text>',
        f'<text x="84" y="162" font-family="sans-serif" font-size="20" fill="#777065">{html.escape(subtitle)}</text>',
    ]
    card_w, gap = 408, 26
    start_x, top_y = 84, 184
    for idx, (num, heading, items) in enumerate(sections):
        x = start_x + idx * (card_w + gap)
        out.extend([
            f'<rect x="{x}" y="{top_y}" width="{card_w}" height="410" rx="14" fill="#fffaf0" stroke="#ded4bf" stroke-width="2"/>',
            f'<text x="{x + 24}" y="{top_y + 42}" font-family="sans-serif" font-size="18" font-weight="700" fill="#b0322c">{num}</text>',
            f'<text x="{x + 70}" y="{top_y + 44}" font-family="sans-serif" font-size="24" font-weight="700" fill="#2c2922">{html.escape(heading)}</text>',
            f'<line x1="{x + 24}" y1="{top_y + 66}" x2="{x + card_w - 24}" y2="{top_y + 66}" stroke="#ded4bf" stroke-width="2"/>',
        ])
        row_y = top_y + 100
        for item_i, item in enumerate(items):
            y = row_y + item_i * (46 if idx == 0 else 72)
            if idx == 0:
                kicker, key, desc = item
                out.extend([
                    f'<text x="{x + 24}" y="{y}" font-family="sans-serif" font-size="15" font-weight="700" fill="#a23631">{html.escape(kicker)}</text>',
                    f'<text x="{x + 105}" y="{y}" font-family="sans-serif" font-size="20" font-weight="700" fill="#2c2922">{html.escape(key)}</text>',
                    f'<text x="{x + 105}" y="{y + 23}" font-family="sans-serif" font-size="15" fill="#5e574c">{html.escape(desc)}</text>',
                ])
            else:
                title_text, desc, sub = item
                out.extend([
                    f'<circle cx="{x + 32}" cy="{y - 7}" r="5" fill="#b0322c"/>',
                    f'<text x="{x + 50}" y="{y}" font-family="sans-serif" font-size="20" font-weight="700" fill="#2c2922">{html.escape(title_text)}</text>',
                    f'<text x="{x + 50}" y="{y + 24}" font-family="sans-serif" font-size="15" fill="#5e574c">{html.escape(desc)}</text>',
                    f'<text x="{x + 50}" y="{y + 46}" font-family="sans-serif" font-size="15" fill="#8a8375">{html.escape(sub)}</text>',
                ])
    out.extend([
        "</svg>",
    ])
    return "\n".join(out) + "\n"


def trap_section(lang: str) -> str:
    title = "罠一覧" if lang == LANG_JA else "Traps"
    headers = ["名前", "効果"] if lang == LANG_JA else ["Name", "Effect"]
    rows = [
        [TextCatalog.trap(lang, row["name"]), TRAP_SUMMARIES[lang][row["name"]]]
        for row in rogue.TRAPS
    ]
    return f"## {title}\n\n" + markdown_table(headers, rows)


def beginner_section(lang: str) -> str:
    if lang == LANG_JA:
        image = "![はじめての探索カード](Beginner-Guide-ja.svg)"
        return "\n\n".join((
            "## はじめての探索",
            "詰まりやすい操作だけ覚えるのがおすすめです。",
            image,
        ))

    image = "![First exploration card](Beginner-Guide-en.svg)"
    return "\n\n".join((
        "## First Exploration",
        "Learn the few actions that prevent early confusion.",
        image,
    ))


def spoiler_warning_section(lang: str) -> str:
    if lang == LANG_JA:
        return "\n".join((
            "## 警告",
            "",
            "> [!WARNING]",
            "> **ここから先はネタバレです**",
            ">",
            "> フロア別の怪物、ドロップ期待値、アイテム効果など、探索中に自分で知る楽しみがある情報を含みます。",
            ">",
            "> まず自力で遊びたい場合は、ここで引き返しても大丈夫です。",
        ))
    return "\n".join((
        "## Warning",
        "",
        "> [!WARNING]",
        "> **Spoiler Warning**",
        ">",
        "> The sections below include monster floors, drop expectations, and item effects that you may prefer to discover during play.",
        ">",
        "> If you want a first blind run, this is a good place to stop.",
    ))


def generate(lang: str) -> str:
    if lang not in LANGS:
        raise ValueError(f"unsupported language: {lang}")
    title = "攻略ガイド" if lang == LANG_JA else "Game Guide"
    intro = (
        "このページはゲーム本体のテーブルから生成しています。数値は現在の実装と同期します。"
        if lang == LANG_JA
        else "This page is generated from the game source tables, so the values track the current implementation."
    )
    sections = [
        f"# {title}",
        intro,
        beginner_section(lang),
        spoiler_warning_section(lang),
        monster_section(lang),
        drop_expectation_section(lang),
        weapon_section(lang),
        armor_section(lang),
        potion_section(lang),
        scroll_section(lang),
        ring_section(lang),
        stick_section(lang),
        trap_section(lang),
    ]
    return "\n\n".join(sections).rstrip() + "\n"


def sidebar() -> str:
    return """# Rogue V5 on Pyxel

## 日本語

### 攻略情報
- [攻略ガイド](Game-Guide-ja)

### プロジェクトについて
- [Rogue V5の遊べる校訂復刻](Playable-Critical-Edition-ja)
- [校訂版アウトライン](Critical-Edition-Outline-ja)
- [近接メッセージログ](Proximity-Message-Log-ja)
- [ライフワークとしてのRogue](Rogue-as-Life-Work-ja)

## English

### Game Guide
- [Game Guide](Game-Guide-en)

### About the Project
- [A Playable Critical Edition](Playable-Critical-Edition-en)
- [Critical Edition Outline](Critical-Edition-Outline-en)
- [Proximity Message Log](Proximity-Message-Log-en)
- [Rogue as a Life Work](Rogue-as-Life-Work-en)

## Notes
- [Editorial Notes](Editorial-Notes)
"""


def home() -> str:
    return """# Rogue V5 on Pyxel Wiki

Rogue V5 on Pyxel の攻略情報、設計意図、実装方針、文化的背景をまとめる場所。

This wiki collects game-guide data, design intent, implementation policy, and cultural context for Rogue V5 on Pyxel.

## 日本語

- [攻略ガイド](Game-Guide-ja)
- [Rogue V5の遊べる校訂復刻](Playable-Critical-Edition-ja)
- [校訂版アウトライン](Critical-Edition-Outline-ja)
- [近接メッセージログ](Proximity-Message-Log-ja)
- [ライフワークとしてのRogue](Rogue-as-Life-Work-ja)

## English

- [Game Guide](Game-Guide-en)
- [A Playable Critical Edition](Playable-Critical-Edition-en)
- [Critical Edition Outline](Critical-Edition-Outline-en)
- [Proximity Message Log](Proximity-Message-Log-en)
- [Rogue as a Life Work](Rogue-as-Life-Work-en)

## Notes

- [Editorial Notes](Editorial-Notes)
"""


def write_wiki(wiki_dir: Path = REPO_ROOT / "wiki") -> None:
    wiki_dir.mkdir(parents=True, exist_ok=True)
    (wiki_dir / "Game-Guide-ja.md").write_text(generate(LANG_JA), encoding="utf-8")
    (wiki_dir / "Game-Guide-en.md").write_text(generate(LANG_EN), encoding="utf-8")
    (wiki_dir / "Beginner-Guide-ja.svg").write_text(beginner_guide_svg(LANG_JA), encoding="utf-8")
    (wiki_dir / "Beginner-Guide-en.svg").write_text(beginner_guide_svg(LANG_EN), encoding="utf-8")
    (wiki_dir / "Monster-Appearance-ja.svg").write_text(monster_heatmap_svg(LANG_JA), encoding="utf-8")
    (wiki_dir / "Monster-Appearance-en.svg").write_text(monster_heatmap_svg(LANG_EN), encoding="utf-8")
    (wiki_dir / "Drop-Rate-Reference-ja.svg").write_text(drop_expectation_svg(LANG_JA), encoding="utf-8")
    (wiki_dir / "Drop-Rate-Reference-en.svg").write_text(drop_expectation_svg(LANG_EN), encoding="utf-8")
    (wiki_dir / "_Sidebar.md").write_text(sidebar(), encoding="utf-8")
    (wiki_dir / "Home.md").write_text(home(), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wiki-dir", type=Path, default=REPO_ROOT / "wiki")
    args = parser.parse_args(argv)
    write_wiki(args.wiki_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
