"""Rogue 5.4.4 rooms.c helpers."""
from __future__ import annotations


def gone_room_indices(room_count: int, rng) -> set[int]:
    """Rogue 5.4.4 rooms.c:do_rooms() ISGONE room selection."""
    gone = set()
    for _ in range(rng.rnd(4)):
        gone.add(rng.rnd(room_count))
    return gone


def room_kind_flag(level: int, rng):
    """Rogue 5.4.4 rooms.c:do_rooms() ISDARK / ISMAZE selection."""
    if rng.rnd(10) >= level - 1:
        return None
    return "maze" if rng.rnd(15) == 0 else "dark"
