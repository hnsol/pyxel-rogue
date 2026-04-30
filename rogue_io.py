"""Rogue 5.4.4 io.c helpers."""
from __future__ import annotations


def step_ok_char(ch: str) -> bool:
    """Rogue 5.4.4 io.c:step_ok()."""
    return ch not in (" ", "|", "-") and not ch.isalpha()


def step_ok_tile(tile: int, tile_ch: dict[int, tuple[str, int]]) -> bool:
    """Apply io.c:step_ok() to a Pyxel terrain tile via its Rogue glyph."""
    return step_ok_char(tile_ch.get(tile, (" ", 0))[0])
