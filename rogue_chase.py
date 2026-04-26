"""Rogue 5.4.4 chase.c helpers."""
from __future__ import annotations


def runners(monsters, monster_turn) -> None:
    """Rogue 5.4.4 chase.c:runners() ISHELD/ISRUN gate."""
    for monster in list(monsters):
        if getattr(monster, "held", 0) > 0 or not getattr(monster, "running", False):
            continue
        monster_turn(monster)


def monster_turn(monster, move_monst, distance_to_hero) -> None:
    """Rogue 5.4.4 chase.c:runners() per-monster move plus ISFLY extra move."""
    if not getattr(monster, "alive", False) or not getattr(monster, "running", False):
        return
    move_monst(monster)
    if getattr(monster, "alive", False) and "fly" in getattr(monster, "flags", set()) and distance_to_hero(monster) >= 3:
        move_monst(monster)


def move_monst(monster, do_chase, chase_steps_for_turn, finish_chase_turn) -> None:
    """Rogue 5.4.4 chase.c:move_monst() step loop."""
    if getattr(monster, "held", 0) > 0:
        monster.held -= 1
        return
    for _ in range(chase_steps_for_turn(monster)):
        if do_chase(monster) == -1:
            return
    finish_chase_turn(monster)


def runto(monster, dest) -> None:
    """Rogue 5.4.4 chase.c:runto()."""
    monster.running = True
    monster.held = 0
    monster.dest = dest


def diag_ok(sx, sy, ex, ey, in_bounds, step_ok) -> bool:
    """Rogue 5.4.4 chase.c:diag_ok()."""
    if not in_bounds(ex, ey):
        return False
    if sx == ex or sy == ey:
        return True
    return step_ok(sx, ey) and step_ok(ex, sy)


def dist(y1, x1, y2, x2) -> int:
    """Rogue 5.4.4 chase.c:dist()."""
    return ((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))


def dist_points(c1, c2) -> int:
    """Rogue 5.4.4 chase.c:dist_cp()."""
    return dist(c1[1], c1[0], c2[1], c2[0])
