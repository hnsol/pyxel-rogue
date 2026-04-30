"""Rogue 5.4.4 command.c search helpers."""
from __future__ import annotations


def search_probinc(hallucinating: bool, blind: bool) -> int:
    """Rogue 5.4.4 command.c:search() probinc."""
    return (3 if hallucinating else 0) + (2 if blind else 0)


def reveals_secret_door(roll: int, probinc: int) -> bool:
    """Rogue 5.4.4 command.c:search() wall/secret door reveal gate."""
    return roll == 0


def reveals_trap(roll: int, probinc: int) -> bool:
    """Rogue 5.4.4 command.c:search() hidden trap reveal gate."""
    return roll == 0


def reveals_secret_passage(roll: int, probinc: int) -> bool:
    """Rogue 5.4.4 command.c:search() hidden passage reveal gate."""
    return roll == 0


def secret_feature_hidden(level: int, rng, denominator: int) -> bool:
    """Rogue 5.4.4 passages.c:door()/putpass() secret feature gate."""
    return rng.rnd(10) + 1 < level and rng.rnd(denominator) == 0
