"""Rogue 5.4.4 misc.c:look() visibility helpers."""
from __future__ import annotations

from pyxel_rogue import rogue_io
from pyxel_rogue.rogue_map import TILE_CH, T_CORR, T_DOOR, T_VOID


def look_cell_visible(
    hero_tile: int,
    target_tile: int,
    dx: int,
    dy: int,
    side_y_tile: int,
    side_x_tile: int,
    hero_pass: bool | None = None,
    target_pass: bool | None = None,
) -> bool:
    """Return whether misc.c:look() would consider a nearby terrain cell."""
    if target_tile == T_VOID:
        return False
    hero_is_pass = _f_pass(hero_tile) if hero_pass is None else hero_pass
    target_is_pass = _f_pass(target_tile) if target_pass is None else target_pass
    if hero_tile != T_DOOR and target_tile != T_DOOR and hero_is_pass != target_is_pass:
        return False
    if (target_is_pass or target_tile == T_DOOR) and (hero_is_pass or hero_tile == T_DOOR):
        if dx != 0 and dy != 0 and not _step_ok(side_y_tile) and not _step_ok(side_x_tile):
            return False
    return True


def _f_pass(tile: int) -> bool:
    return tile == T_CORR


def _step_ok(tile: int) -> bool:
    return rogue_io.step_ok_tile(tile, TILE_CH)
