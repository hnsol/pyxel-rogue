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


def pick_one(weighted_items, roll100: int) -> int:
    """Rogue 5.4.4 things.c:pick_one()."""
    for index, (_, weight) in enumerate(weighted_items):
        if roll100 < weight:
            return index
        roll100 -= weight
    return 0


def new_thing_category(roll100: int, no_food: int = 0) -> str:
    """Rogue 5.4.4 things.c:new_thing() and extern.c:things[]."""
    if no_food > 3:
        return "food"
    return THING_CATEGORIES[pick_one(THING_CATEGORIES, roll100)][0]


def new_thing_category_roll(rnd, no_food: int = 0) -> str:
    """Rogue 5.4.4 things.c:new_thing() category roll."""
    if no_food > 3:
        return "food"
    return new_thing_category(rnd(100), no_food)


def no_food_after_new_level(no_food: int) -> int:
    """Rogue 5.4.4 new_level.c:new_level() increments no_food before put_things()."""
    return no_food + 1


def no_food_after_new_thing(category: str, no_food: int) -> int:
    """Rogue 5.4.4 things.c:new_thing() resets no_food only when FOOD is made."""
    return 0 if category == "food" else no_food
