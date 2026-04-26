"""Rogue 5.4.4 init.c helpers."""
from __future__ import annotations


def initial_arrow_count(rnd) -> int:
    """Rogue 5.4.4 init.c:init_player() arrows use rnd(15)+25."""
    return rnd(15) + 25


def initial_pack_order(food, armor, mace, bow, arrows):
    """Rogue 5.4.4 init.c:init_player() add_pack order."""
    return [food, armor, mace, bow, arrows]
