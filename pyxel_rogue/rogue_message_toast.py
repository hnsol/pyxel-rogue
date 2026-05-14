"""Message toast placement helpers."""

from __future__ import annotations

from pyxel_rogue.rogue_layout import (
    FONT_ASCII_W,
    MSG_TOAST_FADE_COLORS,
    MSG_TOAST_GRID_COL_EDGES,
    MSG_TOAST_GRID_ROW_EDGES,
    TILE_H,
    TILE_W,
    ZV_X,
    ZV_Y,
)
from pyxel_rogue.rogue_map import MAP_W, PLAY_H, PLAY_Y_MIN
from pyxel_rogue.rogue_palettes import (
    DEFAULT_PALETTE,
    PALETTE_FLEXOKI_LIGHT,
    PALETTE_FLEXOKI_SYNTAX_LIGHT,
    ROLE_MEMORY,
    palette_role_color,
)

UI_TEXT_COL = 14
UI_SUBTEXT_COL = 4


def msg_toast_color(age, palette_id=DEFAULT_PALETTE):
    if palette_id in (PALETTE_FLEXOKI_LIGHT, PALETTE_FLEXOKI_SYNTAX_LIGHT):
        if age <= 0:
            return UI_TEXT_COL
        if age <= 1:
            return UI_SUBTEXT_COL
        if age <= 3:
            return palette_role_color(palette_id, ROLE_MEMORY)
        return 3
    for max_age, color in MSG_TOAST_FADE_COLORS:
        if age <= max_age:
            return color
    return MSG_TOAST_FADE_COLORS[-1][1]


def _clamp_to_grid_index(value, edges):
    for i in range(len(edges) - 1):
        if value < edges[i + 1]:
            return i
    return len(edges) - 2


def msg_toast_home_block(x, y):
    col = _clamp_to_grid_index(max(0, min(MAP_W - 1, x)), MSG_TOAST_GRID_COL_EDGES)
    row_y = max(0, min(PLAY_H - 1, y - PLAY_Y_MIN))
    row = _clamp_to_grid_index(row_y, MSG_TOAST_GRID_ROW_EDGES)
    return (col, row)


def _sign(value):
    return (value > 0) - (value < 0)


def _valid_msg_toast_block(block):
    col, row = block
    return 0 <= col <= 2 and 0 <= row <= 2


def _dominant_msg_toast_dir(dx, dy):
    sx, sy = _sign(dx), _sign(dy)
    if not sx and not sy:
        return (0, 0)
    if abs(dx) > abs(dy):
        return (sx, 0)
    if abs(dy) > abs(dx):
        return (0, sy)
    if sx:
        return (sx, 0)
    return (0, sy)


def pick_msg_toast_block(home, last_intent_dir=(0, 0), avoid=()):
    dx, dy = last_intent_dir
    sx, sy = _dominant_msg_toast_dir(dx, dy)
    if sx:
        priority = (
            (home[0] + sx, home[1]),
            (home[0], home[1] + 1),
            (home[0], home[1] - 1),
        )
    elif sy:
        priority = (
            (home[0], home[1] + sy),
            (home[0] - 1, home[1]),
            (home[0] + 1, home[1]),
        )
    else:
        priority = (
            (home[0], home[1] + 1),
            (home[0], home[1] - 1),
            (home[0] - 1, home[1]),
            (home[0] + 1, home[1]),
        )
    avoid = set(avoid)
    for block in priority:
        if _valid_msg_toast_block(block) and block != home and block not in avoid:
            return block
    for row in range(3):
        for col in range(3):
            block = (col, row)
            if block != home and block not in avoid:
                return block
    raise RuntimeError("no valid message toast block")


def msg_toast_block_origin(block, rows=1):
    col, row = block
    start_col = MSG_TOAST_GRID_COL_EDGES[col]
    start_row = MSG_TOAST_GRID_ROW_EDGES[row]
    return (
        ZV_X + start_col * TILE_W + FONT_ASCII_W,
        ZV_Y + start_row * TILE_H + 2,
    )
