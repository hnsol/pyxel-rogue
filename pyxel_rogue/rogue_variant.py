"""Variant-specific rules and labels."""

from __future__ import annotations

from pyxel_rogue.rogue_difficulty import DIFF_NORMAL
from pyxel_rogue.rogue_items import CAT_AMULET
from pyxel_rogue.rogue_lang import LANG_JA

VARIANT_ROGUE = "rogue"
VARIANT_NYANDOR = "nyandor"
NYANDOR_TARGET_DEPTH = 5
NYANDOR_CAT_NAME = "The Cat (wearing the Amulet of Nyandor)"
NYANDOR_CAT_NAME_JA = "ねこ（ニャンダーの魔除けつき）"


def normalize_variant(value):
    value = str(value or VARIANT_ROGUE).strip().lower()
    return VARIANT_NYANDOR if value in (VARIANT_NYANDOR, "nyander", "cat") else VARIANT_ROGUE


def is_nyandor_variant(value):
    return normalize_variant(value) == VARIANT_NYANDOR


def variant_fixed_difficulty(value):
    return DIFF_NORMAL if is_nyandor_variant(value) else None


def variant_title_lines(value):
    if is_nyandor_variant(value):
        return (
            "ROGUE V5 ON PYXEL",
            "5F PLAYABLE BETA",
            "CAT AND AMULET OF NYANDOR",
        )
    return ("ROGUE V5 ON PYXEL",)


def variant_window_title(value):
    return "Cat and Amulet of Nyandor" if is_nyandor_variant(value) else "Pyxel Rogue"


def variant_mission_brief_lines(lang):
    if lang == LANG_JA:
        return (
            "ねこを回収せよ",
            "ギルドの大切なねこが地下5階で行方不明。",
            "ニャンダーの魔除けを首につけたねこを",
            "回収し、地上へ連れ戻せ。",
            "A/Enter 確認   B/Esc 戻る",
        )
    return (
        "CAT RECOVERY ORDER",
        "Guild property is missing on level 5.",
        "Recover the cat wearing the Amulet of Nyandor.",
        "Return to the surface with the asset.",
        "A/Enter acknowledge   B/Esc back",
    )


def variant_quick_guide_lines(lang):
    if lang == LANG_JA:
        return (
            "はじめての操作",
            "D-pad / 矢印: 移動",
            "A / Enter: 拾う・階段・調べる",
            "B / Esc: Actionメニュー",
            "Select / Tab: 持ちもの・ログ・ヘルプ",
            "A/Space/Enter 開始   B/Esc 戻る",
        )
    return (
        "QUICK START",
        "D-pad / Arrows: move",
        "A / Enter: pick up, stairs, inspect",
        "B / Esc: Action menu",
        "Select / Tab: Inventory, Log, Help",
        "A/Space/Enter start   B/Esc back",
    )


def is_nyandor_cat_item(item):
    return (
        item is not None
        and getattr(item, "cat", None) == CAT_AMULET
        and getattr(item, "variant_item", None) == "nyandor_cat"
    )


def nyandor_cat_name(lang):
    return NYANDOR_CAT_NAME_JA if lang == LANG_JA else NYANDOR_CAT_NAME


def variant_escape_message_key(value):
    return "pyxel.escaped_with_nyandor" if is_nyandor_variant(value) else "pyxel.escaped_with_amulet"


def variant_scoreboard_key(value):
    return VARIANT_NYANDOR if is_nyandor_variant(value) else None


def score_entry_is_nyandor(entry):
    return str(entry.get("variant", "")).lower() == VARIANT_NYANDOR
