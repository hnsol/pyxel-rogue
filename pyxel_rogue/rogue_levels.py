"""Rogue 5.4.4 misc.c level helpers."""
from __future__ import annotations


def level_for_exp(exp: int, exp_thresholds: list[int]) -> int:
    """Rogue 5.4.4 misc.c:check_level() over extern.c:e_levels[]."""
    level = 1
    while level < len(exp_thresholds) and exp >= exp_thresholds[level]:
        level += 1
    return level


def check_level(level: int, exp: int, hp: int, max_hp: int, exp_thresholds: list[int], rng) -> tuple[int, int, int, bool]:
    """Rogue 5.4.4 misc.c:check_level() rolls delta d10 when mastery increases."""
    new_level = level_for_exp(exp, exp_thresholds)
    if new_level <= level:
        return level, hp, max_hp, False
    gain = rng.roll(new_level - level, 10)
    return new_level, hp + gain, max_hp + gain, True


def raise_level_exp(level: int, exp_thresholds: list[int]) -> int:
    """Rogue 5.4.4 potions.c:raise_level() sets exp=e_levels[level-1]+1."""
    index = min(level, len(exp_thresholds) - 1)
    return exp_thresholds[index] + 1
