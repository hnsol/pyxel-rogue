"""HUD text helpers."""

from __future__ import annotations

from pyxel_rogue.rogue_items import CAT_ARM, CAT_WPN
from pyxel_rogue.rogue_lang import LANG_EN, LANG_JA
from pyxel_rogue.rogue_palettes import ROLE_FLAG_OFF, ROLE_FLAG_ON, ROLE_STATUS_BAD, ROLE_STATUS_BUFF, ROLE_STATUS_MIND, ROLE_STATUS_WARN
from pyxel_rogue.rogue_text import TextCatalog


def hud_equip_name(item, lang, fallback_name):
    lang = lang if lang in (LANG_EN, LANG_JA) else LANG_EN
    if item.cat == CAT_WPN:
        nm = TextCatalog.hud_item_kind(lang, CAT_WPN, item.data["name"])
        prefix = f"{item.qty} " if item.stackable and item.qty > 1 else ""
        if not getattr(item, "known", True):
            return f"{prefix}{nm}"
        hp = signed(item.hit_plus)
        dp = signed(item.dam_plus)
        return f"{prefix}{hp},{dp} {nm}"
    if item.cat == CAT_ARM:
        nm = TextCatalog.hud_item_kind(lang, CAT_ARM, item.data["name"])
        if not getattr(item, "known", True):
            return nm
        return f"{signed(item.ench)} {nm}"
    return fallback_name(item)


def signed(value):
    return f"{'+' if value >= 0 else ''}{value}"


def hud_weapon_bonus(item):
    if not item:
        return "+0,+0"
    if not getattr(item, "known", True):
        return "?,?"
    return f"{signed(item.hit_plus)},{signed(item.dam_plus)}"


def hud_armor_bonus(item):
    if not item:
        return "+0"
    if not getattr(item, "known", True):
        return "?"
    return signed(item.ench)


def hud_weapon_empty_name(lang):
    return "素手" if lang == LANG_JA else "bare hands"


def hud_armor_empty_name(lang):
    return "防具なし" if lang == LANG_JA else "no armor"


def hud_condition_labels(player, lang, show_status_hud):
    if not show_status_hud:
        return []
    if lang == LANG_JA:
        names = {
            "hungry": "空腹",
            "weak": "衰弱",
            "faint": "失神",
            "confuse": "混乱",
            "blind": "盲目",
            "haste": "加速",
            "halu": "幻覚",
            "levit": "浮遊",
        }
    else:
        names = {
            "hungry": "Hungry",
            "weak": "Weak",
            "faint": "Faint",
            "confuse": "Confuse",
            "blind": "Blind",
            "haste": "Haste",
            "halu": "Halu",
            "levit": "Levit",
        }
    eff = []
    if player.state == "hungry":
        eff.append(names["hungry"])
    elif player.state == "weak":
        eff.append(names["weak"])
    elif player.state == "faint":
        eff.append(names["faint"])
    if player.confused > 0:
        eff.append(names["confuse"])
    if player.blind > 0:
        eff.append(names["blind"])
    if player.haste > 0:
        eff.append(names["haste"])
    if player.hallucinating > 0:
        eff.append(names["halu"])
    if player.levitating > 0:
        eff.append(names["levit"])
    return eff


def hud_condition_chips(player, lang, show_status_hud):
    if not show_status_hud:
        return []
    chips = []
    labels = hud_condition_labels(player, lang, show_status_hud)
    offset = 0
    if player.state == "hungry":
        chips.append((labels[0], ROLE_STATUS_WARN))
        offset = 1
    elif player.state == "weak":
        chips.append((labels[0], ROLE_STATUS_WARN))
        offset = 1
    elif player.state == "faint":
        chips.append((labels[0], ROLE_STATUS_BAD))
        offset = 1
    rest = labels[offset:]
    roles = []
    if player.confused > 0:
        roles.append(ROLE_STATUS_MIND)
    if player.blind > 0:
        roles.append(ROLE_STATUS_MIND)
    if player.haste > 0:
        roles.append(ROLE_STATUS_BUFF)
    if player.hallucinating > 0:
        roles.append(ROLE_STATUS_MIND)
    if player.levitating > 0:
        roles.append(ROLE_STATUS_BUFF)
    chips.extend(zip(rest, roles))
    return chips


def hud_mode_chips(auto_pickup, diag_assist):
    return (
        ("P", ROLE_FLAG_ON if auto_pickup else ROLE_FLAG_OFF),
        ("X", ROLE_FLAG_ON if diag_assist else ROLE_FLAG_OFF),
    )
