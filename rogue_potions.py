"""Rogue 5.4.4 potions.c / misc.c helpers."""
from __future__ import annotations


def is_magic_item(category: str, weapon_magic: bool, armor_magic: bool) -> bool:
    """Rogue 5.4.4 potions.c:is_magic()."""
    if category in {"potion", "scroll", "stick", "ring", "amulet", "pot", "scr"}:
        return True
    if category in {"weapon", "wpn"}:
        return weapon_magic
    if category in {"armor", "arm"}:
        return armor_magic
    return False


def add_str(strength: int, amount: int) -> int:
    """Rogue 5.4.4 misc.c:add_str()."""
    return max(3, min(31, strength + amount))


def gain_strength(strength: int, max_strength: int) -> tuple[int, int]:
    """Rogue 5.4.4 potions.c:P_STRENGTH via misc.c:chg_str(1)."""
    strength = add_str(strength, 1)
    return strength, max(max_strength, strength)


def poison_strength(strength: int, loss: int) -> int:
    """Rogue 5.4.4 potions.c:P_POISON via misc.c:chg_str(-(rnd(3)+1))."""
    return add_str(strength, -loss)


def restore_strength(strength: int, max_strength: int, add_strength_bonus: int) -> int:
    """Rogue 5.4.4 potions.c:P_RESTORE with R_ADDSTR temporarily removed."""
    base_strength = strength - add_strength_bonus
    base_max = max_strength - add_strength_bonus
    if base_strength < base_max:
        base_strength = base_max
    return add_str(base_strength, add_strength_bonus)


def healing_hp(hp: int, max_hp: int, amount: int) -> tuple[int, int]:
    """Rogue 5.4.4 potions.c:P_HEALING overflow sets hp to ++max_hp."""
    hp += amount
    if hp > max_hp:
        max_hp += 1
        hp = max_hp
    return hp, max_hp


def extra_healing_hp(hp: int, max_hp: int, level: int, amount: int) -> tuple[int, int]:
    """Rogue 5.4.4 potions.c:P_XHEAL may increment max_hp twice on large overflow."""
    hp += amount
    if hp > max_hp:
        if hp > max_hp + level + 1:
            max_hp += 1
        max_hp += 1
        hp = max_hp
    return hp, max_hp


def turn_see_state(turn_off: bool, duration: int) -> int:
    """Rogue 5.4.4 potions.c:turn_see() toggles SEEMONST."""
    return 0 if turn_off else duration
