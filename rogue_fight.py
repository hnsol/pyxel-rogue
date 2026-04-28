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


def set_mname(visible: bool, detected: bool, hallucinating: bool, real_name: str, random_name, unseen_name: str):
    """Rogue 5.4.4 fight.c:set_mname()."""
    if not (visible or detected):
        return unseen_name
    if hallucinating:
        return random_name()
    return real_name


def combat_message_key(keys, rnd):
    """Rogue 5.4.4 fight.c:hit()/miss() h_names/m_names family choice."""
    return keys[rnd(4)]


def prname(name: str | None, upper: bool = False) -> str:
    """Rogue 5.4.4 fight.c:prname()."""
    text = "you" if name is None else name
    if upper:
        return text[:1].upper() + text[1:]
    return text


def player_defense_armor(base_ac: int, armor_ac: int | None, protection_bonus: int) -> int:
    """Rogue 5.4.4 fight.c:roll_em() player def_arm branch."""
    def_arm = base_ac if armor_ac is None else armor_ac
    return def_arm - protection_bonus


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
    loss = leprechaun_gold_loss_after_first(goldcalc(level), level, magic_saved, goldcalc)
    return loss


def leprechaun_gold_loss_after_first(first_loss: int, level: int, magic_saved: bool, goldcalc) -> int:
    """Rogue 5.4.4 fight.c:attack() after the first purse -= GOLDCALC."""
    loss = first_loss
    if not magic_saved:
        loss += sum(goldcalc(level) for _ in range(4))
    return loss


def leprechaun_kill_gold(level: int, magic_saved: bool, goldcalc) -> int:
    """Rogue 5.4.4 fight.c:killed() Leprechaun dropped gold."""
    value = leprechaun_kill_gold_after_first(goldcalc(level), level, magic_saved, goldcalc)
    return value


def leprechaun_kill_gold_after_first(first_value: int, level: int, magic_saved: bool, goldcalc) -> int:
    """Rogue 5.4.4 fight.c:killed() after o_goldval = GOLDCALC."""
    value = first_value
    if magic_saved:
        value += sum(goldcalc(level) for _ in range(4))
    return value


def leprechaun_kill_gold_allowed(level: int, max_level: int, has_fallpos: bool) -> bool:
    """Rogue 5.4.4 fight.c:killed() Leprechaun gold creation gate."""
    return has_fallpos and level >= max_level


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


def venus_flytrap_release():
    """Rogue 5.4.4 fight.c:killed() Venus Flytrap release."""
    return 0, "0x0"


def poison_bite_strength(strength: int, poison_saved: bool, sustain_strength: bool):
    """Rogue 5.4.4 fight.c:attack() Rattlesnake poison bite."""
    if poison_saved:
        return strength, None
    if sustain_strength:
        return strength, "sustained"
    if strength <= 3:
        return strength, "weakened"
    return strength - 1, "weakened"


def poison_bite_message_key(result: str | None, terse: bool) -> str | None:
    """Rogue 5.4.4 fight.c:attack() Rattlesnake poison message branch."""
    if result == "weakened":
        return "fight.a_bite_has_weakened_you" if terse else "fight.you_feel_a_bite_in_your_leg_and_now_feel_weaker"
    if result == "sustained":
        return "fight.bite_has_no_effect" if terse else "fight.a_bite_momentarily_weakens_you"
    return None


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
        if "x" not in part:
            break
        n, sides = part.split("x", 1)
        total += roll(int(n), int(sides))
    return total


def roll_em_damage(damage_expr: str, swing, roll_part, dplus: int, add_dam: int):
    """Rogue 5.4.4 fight.c:roll_em() per-damage-part hit loop."""
    did_hit = False
    total = 0
    for part in damage_expr.split("/"):
        if swing():
            total += roll_em_part_damage(roll_part(part), dplus, add_dam)
            did_hit = True
    return did_hit, total


def roll_em_part_damage(proll: int, dplus: int, add_dam: int) -> int:
    """Rogue 5.4.4 fight.c:roll_em() max(0, damage)."""
    return max(0, proll + dplus + add_dam)


def hit_plus_vs_defender(hplus: int, defender_running: bool) -> int:
    """Rogue 5.4.4 fight.c:roll_em() !ISRUN hit bonus."""
    return hplus if defender_running else hplus + 4


def attack_hit_plus(hplus: int, defender_running: bool, strength: int) -> int:
    """Rogue 5.4.4 fight.c:roll_em() hplus + str_plus[s_str]."""
    return hit_plus_vs_defender(hplus, defender_running) + str_hit_plus(strength)


def attack_damage_plus(dplus: int, strength: int) -> int:
    """Rogue 5.4.4 fight.c:roll_em() dplus + add_dam[s_str]."""
    return dplus + str_dam_plus(strength)


def player_defender_running(no_command: int) -> bool:
    """Rogue 5.4.4 player ISRUN approximation for fight.c:roll_em()."""
    return no_command <= 0


def monster_attack_message_allowed(monster_sym: str) -> bool:
    """Rogue 5.4.4 fight.c:attack() skips hit()/miss() for Ice monster."""
    return monster_sym != "I"


def confusion_message_allowed(confused_by_hit: bool, blind: bool) -> bool:
    """Rogue 5.4.4 fight.c:fight() prints confusion only for CANHUH hits while not blind."""
    return confused_by_hit and not blind


def confusion_hit_effect(can_confuse_monster: bool):
    """Rogue 5.4.4 fight.c:fight() consumes CANHUH on a successful hit."""
    if can_confuse_monster:
        return False, True
    return False, False


def thrown_message_uses_weapon_name(item_category) -> bool:
    """Rogue 5.4.4 fight.c:thunk()/bounce() checks o_type == WEAPON."""
    return item_category == "wpn"


def thrown_message_key(item_category, hit: bool) -> str:
    """Rogue 5.4.4 fight.c:thunk()/bounce() message branch."""
    if thrown_message_uses_weapon_name(item_category):
        return "fight.thrown_weapon_hits" if hit else "fight.thrown_weapon_misses"
    return "fight.you_hit_target" if hit else "fight.you_missed_target"


def killed_message_key(pr: bool, has_hit: bool, terse: bool) -> str | None:
    """Rogue 5.4.4 fight.c:killed() defeated message branch."""
    if not pr:
        return None
    if has_hit:
        return "fight.defeated_target"
    if terse:
        return "fight.defeated_target"
    return "fight.you_have_defeated_target"


def killed_experience(player_exp: int, monster_exp: int) -> int:
    """Rogue 5.4.4 fight.c:killed() pstats.s_exp += monster exp."""
    return player_exp + monster_exp


def bare_attack_profile(damage_expr: str):
    """Rogue 5.4.4 fight.c:roll_em() weap == NULL profile."""
    return damage_expr, 0, 0


def non_weapon_profile(ring_hit_bonus: int, ring_damage_bonus: int):
    """Rogue 5.4.4 fight.c:roll_em() non-WEAPON o_damage profile."""
    return "0x0", ring_hit_bonus, ring_damage_bonus


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
