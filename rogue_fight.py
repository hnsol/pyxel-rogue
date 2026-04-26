"""Rogue 5.4.4 fight.c helpers."""
from __future__ import annotations


def swing(at_lvl: int, op_arm: int, wplus: int, rnd) -> bool:
    """Rogue 5.4.4 fight.c:swing()."""
    need = (20 - at_lvl) - op_arm
    return rnd(20) + wplus >= need


def magic_item_to_steal(inventory, equipped_items, is_magic_item, rnd):
    """Rogue 5.4.4 fight.c:attack() Nymph steal selection."""
    steal = None
    nobj = 0
    for item in inventory:
        if item in equipped_items:
            continue
        if is_magic_item(item):
            nobj += 1
            if rnd(nobj) == 0:
                steal = item
    return steal


def goldcalc(level: int, rnd) -> int:
    """Rogue 5.4.4 rogue.h:GOLDCALC."""
    return rnd(50 + 10 * level) + 2


def roll_damage_expr(expr: str, roll) -> int:
    """Rogue 5.4.4 fight.c:roll_em() damage expression roll."""
    total = 0
    for part in expr.split("/"):
        sep = "x" if "x" in part else "d"
        n, sides = part.split(sep)
        total += roll(int(n), int(sides))
    return total


def roll_em_damage(damage_expr: str, swing, roll_part, dplus: int, add_dam: int):
    """Rogue 5.4.4 fight.c:roll_em() per-damage-part hit loop."""
    did_hit = False
    total = 0
    for part in damage_expr.split("/"):
        if swing():
            total += max(0, roll_part(part) + dplus + add_dam)
            did_hit = True
    return did_hit, total


def hit_plus_vs_defender(hplus: int, defender_running: bool) -> int:
    """Rogue 5.4.4 fight.c:roll_em() !ISRUN hit bonus."""
    return hplus if defender_running else hplus + 4


def weapon_profile(
    weapon,
    hit_plus: int,
    dam_plus: int,
    thrown: bool,
    ring_hit_bonus: int,
    ring_damage_bonus: int,
    launcher_kind=None,
    launcher_hit_plus: int = 0,
    launcher_dam_plus: int = 0,
):
    """Rogue 5.4.4 fight.c:roll_em() weapon/hurl profile."""
    hplus = hit_plus + ring_hit_bonus
    dplus = dam_plus + ring_damage_bonus
    damage = weapon["damage"]
    if thrown:
        launcher = weapon.get("launcher")
        if weapon.get("missile") and launcher is not None and launcher_kind == launcher:
            damage = weapon["hurl_damage"]
            hplus += launcher_hit_plus
            dplus += launcher_dam_plus
        elif launcher is None:
            damage = weapon["hurl_damage"]
    return damage, hplus, dplus
