"""Rogue 5.4.4 misc.c:look() visibility helpers."""
from __future__ import annotations

from rogue_map import T_CORR, T_DOOR, T_VOID, WALKABLE


def look_cell_visible(
    hero_tile: int,
    target_tile: int,
    dx: int,
    dy: int,
    side_y_tile: int,
    side_x_tile: int,
) -> bool:
    """Return whether misc.c:look() would consider a nearby terrain cell."""
    if target_tile == T_VOID:
        return False
    if hero_tile != T_DOOR and target_tile != T_DOOR and _f_pass(hero_tile) != _f_pass(target_tile):
        return False
    if (_f_pass(target_tile) or target_tile == T_DOOR) and (_f_pass(hero_tile) or hero_tile == T_DOOR):
        if dx != 0 and dy != 0 and not _step_ok(side_y_tile) and not _step_ok(side_x_tile):
            return False
    return True


def _f_pass(tile: int) -> bool:
    return tile == T_CORR


def _step_ok(tile: int) -> bool:
    return tile in WALKABLE
