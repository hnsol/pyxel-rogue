import os

from rogue_map import MAP_W, PLAY_H

DEFAULT_FONT_ID = "umplus_j10r"
FONT_IDS = ("umplus_j10r", "k8x12s")
FONT_METRICS = {
    "umplus_j10r": (6, 10, 12),
    "k8x12s": (4, 8, 12),
}


def normalize_font_id(value):
    font_id = str(value or DEFAULT_FONT_ID).lower()
    return font_id if font_id in FONT_IDS else DEFAULT_FONT_ID


FONT_ID = normalize_font_id(os.environ.get("PYXEL_ROGUE_FONT"))
FONT_ASCII_W, FONT_CJK_W, FONT_LINE_H = FONT_METRICS[FONT_ID]
SCR_W, SCR_H = 576, 300
TILE_W, TILE_H = 6, 12
ZV_COLS, ZV_ROWS = MAP_W, PLAY_H
ZV_PX_W = ZV_COLS * TILE_W
ZV_PX_H = ZV_ROWS * TILE_H
DEAD_ZONE_X = 8
DEAD_ZONE_Y = 5

ZV_X, ZV_Y = 4, 1
HUD_X = ZV_X + ZV_PX_W + 10
HUD_Y = ZV_Y
HUD_W = SCR_W - HUD_X - 4

MSG_LINES = 7
MSG_LINE_H = 10
MSG_X, MSG_Y = 4, SCR_H - MSG_LINES * MSG_LINE_H - 2
MSG_COLS = (SCR_W - MSG_X * 2) // FONT_ASCII_W
MSG_TOAST_LINES = 5
MSG_TOAST_BRIGHT_TURNS = 0
MSG_TOAST_DIM_TURNS = 5
