"""Rogue 5.4.4 misc.c:eat() food helpers."""
from __future__ import annotations


def eat_food(food_left: int, food_kind: int, rnd_400, rnd_100, hungertime: int, stomachsize: int):
    """Return (new_food_left, outcome, exp_gain) for Rogue 5.4.4 misc.c:eat()."""
    new_food = max(food_left, 0) + hungertime - 200 + rnd_400(400)
    if new_food > stomachsize:
        new_food = stomachsize
    if food_kind == 1:
        return new_food, "slime-mold", 0
    if rnd_100(100) > 70:
        return new_food, "awful", 1
    return new_food, "good", 0
