"""Rogue 5.4.4 things.c helpers."""
from __future__ import annotations


def new_thing_food_kind(rnd) -> int:
    """Rogue 5.4.4 things.c:new_thing() food kind branch."""
    return 0 if rnd(10) != 0 else 1


THING_CATEGORIES = [
    ("potion", 26),
    ("scroll", 36),
    ("food", 16),
    ("weapon", 7),
    ("armor", 7),
    ("ring", 4),
    ("stick", 4),
]


def new_thing_category(roll100: int, no_food: int = 0) -> str:
    """Rogue 5.4.4 things.c:new_thing() and extern.c:things[]."""
    if no_food > 3:
        return "food"
    acc = 0
    for name, weight in THING_CATEGORIES:
        acc += weight
        if roll100 < acc:
            return name
    return THING_CATEGORIES[-1][0]
