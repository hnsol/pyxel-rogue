"""Rogue 5.4.4 fight.c helpers."""
from __future__ import annotations

STR_PLUS = [-7, -6, -5, -4, -3, -2, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3]
ADD_DAM = [-7, -6, -5, -4, -3, -2, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 3, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6]


def _str_index(strength: int) -> int:
    return max(0, min(strength, len(STR_PLUS) - 1))


def str_hit_plus(strength: int) -> int:
    """Rogue 5.4.4 fight.c:str_plus[]."""
    return STR_PLUS[_str_index(strength)]


def str_dam_plus(strength: int) -> int:
    """Rogue 5.4.4 fight.c:add_dam[]."""
    return ADD_DAM[_str_index(strength)]


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


def leprechaun_gold_loss(level: int, magic_saved: bool, goldcalc) -> int:
    """Rogue 5.4.4 fight.c:attack() Leprechaun purse loss."""
    loss = goldcalc(level)
    if not magic_saved:
        loss += sum(goldcalc(level) for _ in range(4))
    return loss


def ice_freeze(no_command: int, bore_level: int, rnd):
    """Rogue 5.4.4 fight.c:attack() Ice monster freeze."""
    should_message = no_command <= 0
    no_command += rnd(2) + 2
    return no_command, should_message, no_command > bore_level


def venus_flytrap_hit(vf_hit: int):
    """Rogue 5.4.4 fight.c:attack() Venus Flytrap hold damage."""
    vf_hit += 1
    return vf_hit, f"{vf_hit}x1"


def venus_flytrap_miss_hp(player_hp: int, vf_hit: int) -> int:
    """Rogue 5.4.4 fight.c:attack() Venus Flytrap miss damage."""
    return player_hp - vf_hit


def poison_bite_strength(strength: int, poison_saved: bool, sustain_strength: bool):
    """Rogue 5.4.4 fight.c:attack() Rattlesnake poison bite."""
    if poison_saved:
        return strength, None
    if sustain_strength:
        return strength, "sustained"
    if strength <= 3:
        return strength, "floor"
    return strength - 1, "weakened"


def wraith_drain(level: int, exp: int, hp: int, max_hp: int, exp_table, roll_fewer):
    """Rogue 5.4.4 fight.c:attack() Wraith level drain."""
    if exp == 0:
        return level, exp, 0, max_hp, True
    level -= 1
    if level == 0:
        exp = 0
        level = 1
    else:
        exp = exp_table[level - 1] + 1
    fewer = roll_fewer()
    hp -= fewer
    max_hp -= fewer
    if hp <= 0:
        hp = 1
    return level, exp, hp, max_hp, max_hp <= 0


def max_hp_drain(hp: int, max_hp: int, roll_fewer):
    """Rogue 5.4.4 fight.c:attack() Vampire max HP drain."""
    fewer = roll_fewer()
    hp -= fewer
    max_hp -= fewer
    if hp <= 0:
        hp = 1
    return hp, max_hp, max_hp <= 0


def drain_hits(monster_sym: str, rnd) -> bool:
    """Rogue 5.4.4 fight.c:attack() Wraith/Vampire drain chance."""
    return rnd(100) < (15 if monster_sym == "W" else 30)


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
