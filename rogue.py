"""
PYXEL ROGUE
Rogue 5.4.4 fidelity build for Pyxel.

Current controls are documented in the in-game Help and docs/DESIGN.md.
"""

from __future__ import annotations
import pyxel
import random
import os
import sys
import time
from dataclasses import dataclass
from pyxel_rogue.rogue_rng import RogueRng
from pyxel_rogue import rogue_monsters
from pyxel_rogue import rogue_pack
from pyxel_rogue import rogue_potions
from pyxel_rogue import rogue_scrolls
from pyxel_rogue import rogue_rings
from pyxel_rogue import rogue_rooms
from pyxel_rogue import rogue_search
from pyxel_rogue import rogue_sticks
from pyxel_rogue import rogue_things
from pyxel_rogue import rogue_vision
from pyxel_rogue import rogue_dungeon
from pyxel_rogue import rogue_daemons
from pyxel_rogue import rogue_armor
from pyxel_rogue import rogue_chase
from pyxel_rogue import rogue_fight
from pyxel_rogue import rogue_food
from pyxel_rogue import rogue_init
from pyxel_rogue import rogue_io
from pyxel_rogue import rogue_levels
from pyxel_rogue import rogue_misc
from pyxel_rogue import rogue_move
from pyxel_rogue import rogue_passages
from pyxel_rogue import rogue_weapons
from pyxel_rogue import rogue_hud
from pyxel_rogue import rogue_input
from pyxel_rogue import rogue_sfx
from pyxel_rogue import rogue_online_scoreboard
from pyxel_rogue import rogue_online_state
from pyxel_rogue import rogue_online_text
from pyxel_rogue import rogue_save
from pyxel_rogue import rogue_variant
from pyxel_rogue.rogue_combat_text import (
    MONSTER_HIT_MESSAGE_KEYS,
    MONSTER_MISS_MESSAGE_KEYS,
    PLAYER_HIT_MESSAGE_KEYS,
    PLAYER_MISS_MESSAGE_KEYS,
)
from pyxel_rogue.rogue_bgm import DungeonBgmController
from pyxel_rogue.rogue_items import (
    CAT_AMULET,
    CAT_ARM,
    CAT_FOOD,
    CAT_GOLD,
    CAT_POT,
    CAT_RING,
    CAT_SCR,
    CAT_STICK,
    CAT_WPN,
    HALLU_THINGS,
    ICOL,
    ISYM,
)
from pyxel_rogue.rogue_lang import DEFAULT_LANG, LANG_EN, LANG_JA, Settings, load_settings, save_settings, settings_exists
from pyxel_rogue.rogue_difficulty import DIFF_NORMAL, DIFFICULTY_ORDER, profile as difficulty_profile
from pyxel_rogue.rogue_message_toast import (
    _dominant_msg_toast_dir,
    _sign,
    msg_toast_block_origin,
    msg_toast_color,
    msg_toast_home_block,
    pick_msg_toast_block,
)
from pyxel_rogue.rogue_text import TextCatalog
from pyxel_rogue.rogue_layout import (
    DEAD_ZONE_X,
    DEAD_ZONE_Y,
    FONT_ASCII_W,
    FONT_CJK_W,
    FONT_LINE_H,
    HUD_W,
    HUD_X,
    HUD_Y,
    MSG_COLS,
    MSG_LINES,
    MSG_TOAST_BRIGHT_TURNS,
    MSG_TOAST_DIM_TURNS,
    MSG_TOAST_FADE_COLORS,
    MSG_TOAST_GRID_COL_EDGES,
    MSG_TOAST_GRID_ROW_EDGES,
    MSG_TOAST_LINES,
    MSG_TOAST_SHADOW_COL,
    MSG_LINE_H,
    MSG_X,
    MSG_Y,
    SCR_H,
    SCR_W,
    TILE_H,
    TILE_W,
    ZV_COLS,
    ZV_PX_H,
    ZV_PX_W,
    ZV_ROWS,
    ZV_X,
    ZV_Y,
)
from pyxel_rogue.rogue_map import (
    GRID_C,
    GRID_R,
    MAP_H,
    MAP_W,
    MEMORY_TILE_COLOR,
    NUMCOLS,
    NUMLINES,
    PLAY_H,
    PLAY_Y_MAX,
    PLAY_Y_MIN,
    RM_MAX_H,
    RM_MAX_W,
    RM_MIN_H,
    RM_MIN_W,
    ROOM_DARK,
    ROOM_GONE,
    ROOM_MAZE,
    SEC_H,
    SEC_W,
    STATLINE,
    TILE_CH,
    T_CORR,
    T_DOOR,
    T_FLOOR,
    T_HWALL,
    T_STAIR,
    T_TRAP,
    T_VOID,
    T_VWALL,
    WALKABLE,
)
from pyxel_rogue.rogue_palettes import (
    DEFAULT_PALETTE,
    FLEXOKI_DARK_PALETTE,
    GBC_HIGH_CONTRAST_PALETTE,
    GBC_PALETTE,
    FLEXOKI_LIGHT_PALETTE,
    FLEXOKI_SYNTAX_DARK_PALETTE,
    FLEXOKI_SYNTAX_LIGHT_PALETTE,
    MCOL,
    MROLE,
    PALETTE_COLOR_LIMIT,
    PALETTE_FLEXOKI_DARK,
    PALETTE_FLEXOKI_LIGHT,
    PALETTE_FLEXOKI_SYNTAX_DARK,
    PALETTE_FLEXOKI_SYNTAX_LIGHT,
    PALETTE_GBC,
    PALETTE_GBC_HIGH_CONTRAST,
    PALETTE_IDS,
    PALETTE_LABELS,
    PALETTE_THEMES,
    PALETTES,
    REQUIRED_MONSTER_ROLES,
    REQUIRED_PALETTE_ROLES,
    ROLE_CORRIDOR,
    ROLE_DOOR,
    ROLE_FLOOR,
    ROLE_FLAG_OFF,
    ROLE_FLAG_ON,
    ROLE_GOLD,
    ROLE_HILITE,
    ROLE_HP_LOW_FRAME_DIM,
    ROLE_HP_LOW_FRAME_GLOW,
    ROLE_HP_LOW_FRAME_MID,
    ROLE_HP_LOW_FRAME_SHADOW,
    ROLE_MEMORY,
    ROLE_PLAYER,
    ROLE_SECTION,
    ROLE_STATUS_BAD,
    ROLE_STATUS_BUFF,
    ROLE_STATUS_MIND,
    ROLE_STATUS_WARN,
    ROLE_TEXT,
    ROLE_TRAP,
    ROLE_WALL,
    palette_monster_color,
    palette_role_color,
    palette_theme,
)
from pyxel_rogue.rogue_scores import (
    SCOREBOARD_PERIOD_LOCAL,
    SCOREBOARD_PERIOD_SEASON,
    SCOREBOARD_PERIOD_WEEKLY,
    USER_NAME_MAX,
    check_online_user,
    fetch_online_scores,
    build_score_entry,
    can_register_user_id,
    display_score_name,
    format_score_line,
    format_top_score_lines,
    get_period_scores,
    get_top_scores,
    link_online_user,
    load_online_score_cache,
    load_online_profile,
    load_score_entries,
    local_best_sync_entries,
    local_score_player_name_candidates,
    normalize_online_profile,
    record_guest_scoreboard_sync,
    register_online_user,
    sanitize_player_name,
    sanitize_user_id,
    save_player_name,
    save_local_only_profile,
    save_online_score_cache,
    save_online_profile,
    save_score_entry,
    score_period_keys,
    submit_online_score,
    sync_online_scoreboard,
    sync_missing_local_best,
    total_winner_item_worth,
    total_winner_score,
)
from pyxel_rogue.rogue_timing import (
    AMULET_LEVEL,
    BEARTIME,
    BOLT_LENGTH,
    BORE_LEVEL,
    DRAGONSHOT,
    HEALTIME,
    HUHDURATION,
    HUNGERTIME,
    LAMPDIST,
    MAX_TRAPS,
    MORETIME,
    SEEDURATION,
    SLEEPTIME,
    STARVETIME,
    STOMACHSIZE,
    VS_MAGIC,
    WANDERTIME,
)
from pyxel_rogue.rogue_ui import (
    AUX_ACTIONS,
    BACK_TAP_FRAMES,
    B_TAP_FRAMES,
    CALL_PRESETS,
    MENU_ACTIONS,
    PAD_ACTION_GRID,
    PACK_GRID_MAX_ROWS,
    action_index,
    pack_grid_move,
    pack_grid_pos,
    pack_grid_shape,
    pad_menu_initial_index,
    pad_menu_move,
    ST_AUX,
    ST_CALL,
    ST_DEAD,
    ST_DIFFICULTY,
    ST_DIR,
    ST_DISC,
    ST_HELP,
    ST_INVENTORY,
    ST_ITEM,
    ST_LOADING,
    ST_LOG,
    ST_LOGO,
    ST_LANGUAGE,
    ST_MENU,
    ST_NAME,
    ST_NYANDOR_BRIEF,
    ST_NYANDOR_GUIDE,
    ST_ONLINE_SCORE,
    ST_ONLINE_REGISTER,
    ST_ONLINE_PIN,
    ST_ONLINE_CONFIRM,
    ST_ONLINE_LOCAL_CONFIRM,
    ST_PLAY,
    ST_QUIT,
    ST_QUIT_CONFIRM,
    ST_READY,
    ST_SAVE_CONFIRM,
    ST_SCORE,
    ST_SETTINGS,
    ST_TITLE,
    ST_WIN,
)

RNG = RogueRng(random)
UI_BUILD = "260601_1810"
VARIANT_ROGUE = rogue_variant.VARIANT_ROGUE
VARIANT_NYANDOR = rogue_variant.VARIANT_NYANDOR
NYANDOR_TARGET_DEPTH = rogue_variant.NYANDOR_TARGET_DEPTH
NYANDOR_CAT_NAME = rogue_variant.NYANDOR_CAT_NAME
NYANDOR_CAT_NAME_JA = rogue_variant.NYANDOR_CAT_NAME_JA

def normalize_variant(value):
    return rogue_variant.normalize_variant(value)

GAME_VARIANT = normalize_variant(os.environ.get("PYXEL_ROGUE_VARIANT"))

def is_nyandor_variant():
    return rogue_variant.is_nyandor_variant(GAME_VARIANT)

def variant_fixed_difficulty():
    return rogue_variant.variant_fixed_difficulty(GAME_VARIANT)

def variant_title_lines():
    return rogue_variant.variant_title_lines(GAME_VARIANT)

def variant_window_title():
    return rogue_variant.variant_window_title(GAME_VARIANT)

def variant_title_background_path():
    return TITLE_BG_NYANDOR_PATH if is_nyandor_variant() else TITLE_BG_PATH

def variant_title_palette():
    return TITLE_BG_NYANDOR_PALETTE if is_nyandor_variant() else TITLE_BG_PALETTE

def variant_mission_brief_lines(lang):
    return rogue_variant.variant_mission_brief_lines(lang)

def variant_quick_guide_lines(lang):
    return rogue_variant.variant_quick_guide_lines(lang)

def is_nyandor_cat_item(item):
    return rogue_variant.is_nyandor_cat_item(item)

def nyandor_cat_name(lang):
    return rogue_variant.nyandor_cat_name(lang)

def variant_escape_message_key():
    return rogue_variant.variant_escape_message_key(GAME_VARIANT)

def variant_scoreboard_key():
    return rogue_variant.variant_scoreboard_key(GAME_VARIANT)

def score_entry_is_nyandor(entry):
    return rogue_variant.score_entry_is_nyandor(entry)

MSG_TOAST_INTENT_HISTORY = 4
MSG_TOAST_ROW_RETIRE_FRAMES = 20
DEATH_MINIMAP_W = 21
DEATH_MINIMAP_H = 7
DEATH_SHAKE_FRAMES = 10
DEATH_HITSTOP_FRAMES = 20
DEATH_FADE_OUT_FRAMES = 30
DEATH_FADE_IN_FRAMES = 40
DEATH_INPUT_LOCK_FRAMES = DEATH_SHAKE_FRAMES + DEATH_HITSTOP_FRAMES
DEATH_RIP_START_FRAMES = DEATH_INPUT_LOCK_FRAMES + DEATH_FADE_OUT_FRAMES
DEATH_INTRO_FRAMES = DEATH_RIP_START_FRAMES + DEATH_FADE_IN_FRAMES
DEATH_LOG_FRAMES_PER_TURN = 30
DEATH_LOG_RESTART_FRAMES = 45
MSG_KINSOKU_LINE_START = "、。！？"
HP_LOW_FRAME_ROLES = (
    ROLE_HP_LOW_FRAME_DIM,
    ROLE_HP_LOW_FRAME_DIM,
    ROLE_HP_LOW_FRAME_SHADOW,
    ROLE_HP_LOW_FRAME_MID,
    ROLE_HP_LOW_FRAME_GLOW,
    ROLE_HP_LOW_FRAME_GLOW,
    ROLE_HP_LOW_FRAME_GLOW,
    ROLE_HP_LOW_FRAME_MID,
    ROLE_HP_LOW_FRAME_SHADOW,
    ROLE_HP_LOW_FRAME_DIM,
)
HP_LOW_FRAME_PERIOD = 5
HP_LOW_FRAME_PROBE_FRAMES = tuple(range(0, len(HP_LOW_FRAME_ROLES) * HP_LOW_FRAME_PERIOD, HP_LOW_FRAME_PERIOD))
NAME_ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789 "
PIN_ALPHABET = "0123456789"
SCOREBOARD_PERIOD_ORDER = rogue_online_scoreboard.SCOREBOARD_PERIOD_ORDER
ONLINE_UI_TEXT = rogue_online_text.ONLINE_UI_TEXT
UI_TEXT_COL = 14
UI_SUBTEXT_COL = 4
UI_HILITE_COL = 11
UI_SECTION_COL = 15
UI_SELECTED_COL = UI_HILITE_COL
UI_RESTORED_CURSOR_COL = 12
SCOREBOARD_HILITE_COL = UI_HILITE_COL
SCOREBOARD_TEXT_COL = UI_TEXT_COL
SCOREBOARD_DIM_COL = UI_SUBTEXT_COL
UI_HEADING_SCREEN = "screen"
UI_HEADING_PANEL = "panel"
UI_HEADING_SECTION = "section"

from pyxel_rogue.rogue_title import (
    FONT_PATH,
    LOGO_ACCENT_COL,
    LOGO_BGM_DELAY_FRAMES,
    LOGO_FADE_FRAMES,
    LOGO_HOLD_FRAMES,
    LOGO_TEXT_COL,
    LOGO_TOTAL_FRAMES,
    TITLE_BG_NYANDOR_PALETTE,
    TITLE_BG_NYANDOR_PATH,
    TITLE_BG_PALETTE,
    TITLE_BG_PATH,
    TITLE_BGM_MMLS,
    TITLE_BGM_STOP_WAIT_FRAMES,
    TITLE_FADE_FRAMES,
    TITLE_LOGO_RIGHT_X,
    TITLE_MENU_BORDER_COL,
    TITLE_MENU_H,
    TITLE_MENU_SELECTED_COL,
    TITLE_MENU_TEXT_COL,
    TITLE_MENU_W,
    TITLE_MENU_X,
    TITLE_MENU_Y,
    TITLE_RESTORED_CURSOR_COL,
)


INV_MAX = 26
DASH_INTERVAL = 1                # frames between dash steps
DEST_PLAYER = "player"
DEST_GOLD = "gold"
HELP_HEADER_COL = UI_SECTION_COL
HELP_TEXT_COL = UI_TEXT_COL

# ===========================================================
#  Dice
# ===========================================================
def roll(s: str) -> int:
    n, d = s.split("d"); return RNG.roll(int(n), int(d))

def roll_damage_expr(expr: str) -> int:
    return rogue_fight.roll_damage_expr(expr, RNG.roll)

def rnd(n: int) -> int:
    return RNG.rnd(n)

def goldcalc(level: int) -> int:
    # C: rogue.h:GOLDCALC
    return rogue_fight.goldcalc(level, rnd)

def in_map(x: int, y: int) -> bool:
    return 0 <= x < MAP_W and 0 <= y < MAP_H

def in_play_area(x: int, y: int) -> bool:
    return 0 <= x < MAP_W and PLAY_Y_MIN <= y <= PLAY_Y_MAX

# ===========================================================
#  Item data  (Rogue 5.4.4)
# ===========================================================
POTIONS = [
    {"name":"confusion","prob":7,"worth":5},{"name":"hallucination","prob":8,"worth":5},
    {"name":"poison","prob":8,"worth":5},{"name":"gain strength","prob":13,"worth":150},
    {"name":"see invisible","prob":3,"worth":100},{"name":"healing","prob":13,"worth":130},
    {"name":"monster detection","prob":6,"worth":130},{"name":"magic detection","prob":6,"worth":105},
    {"name":"raise level","prob":2,"worth":250},{"name":"extra healing","prob":5,"worth":200},
    {"name":"haste self","prob":5,"worth":190},{"name":"restore strength","prob":13,"worth":130},
    {"name":"blindness","prob":5,"worth":5},
    {"name":"levitation","prob":6,"worth":75},
]
POT_COLORS = ["blue","red","green","grey","brown","clear",
              "pink","white","purple","yellow","plaid","amber",
              "black","orange"]

SCROLLS = [
    {"name":"monster confusion","prob":7,"worth":140},
    {"name":"magic mapping","prob":4,"worth":150},{"name":"hold monster","prob":2,"worth":180},
    {"name":"sleep","prob":3,"worth":5},{"name":"enchant armor","prob":7,"worth":160},
    {"name":"identify potion","prob":10,"worth":80},{"name":"identify scroll","prob":10,"worth":80},
    {"name":"identify weapon","prob":6,"worth":80},{"name":"identify armor","prob":7,"worth":100},
    {"name":"identify ring, wand or staff","prob":10,"worth":115},
    {"name":"scare monster","prob":3,"worth":200},{"name":"food detection","prob":2,"worth":60},
    {"name":"teleportation","prob":5,"worth":165},{"name":"enchant weapon","prob":8,"worth":150},
    {"name":"create monster","prob":4,"worth":75},{"name":"remove curse","prob":7,"worth":105},
    {"name":"aggravate monsters","prob":3,"worth":20},{"name":"protect armor","prob":2,"worth":250},
]
SCR_SYLS = [
    "a", "ab", "ag", "aks", "ala", "an", "app", "arg",
    "arze", "ash", "bek", "bie", "bit", "bjor", "blu", "bot",
    "bu", "byt", "comp", "con", "cos", "cre", "dalf", "dan",
    "den", "do", "e", "eep", "el", "eng", "er", "ere",
    "erk", "esh", "evs", "fa", "fid", "fri", "fu", "gan",
    "gar", "glen", "gop", "gre", "ha", "hyd", "i", "ing",
    "ip", "ish", "it", "ite", "iv", "jo", "kho", "kli",
    "klis", "la", "lech", "mar", "me", "mi", "mic", "mik",
    "mon", "mung", "mur", "nej", "nelg", "nep", "ner", "nes",
    "nes", "nih", "nin", "o", "od", "ood", "org", "orn",
    "ox", "oxy", "pay", "ple", "plu", "po", "pot", "prok",
    "re", "rea", "rhov", "ri", "ro", "rog", "rok", "rol",
    "sa", "san", "sat", "sef", "seh", "shu", "ski", "sna",
    "sne", "snik", "sno", "so", "sol", "sri", "sta", "sun",
    "ta", "tab", "tem", "ther", "ti", "tox", "trol", "tue",
    "turs", "u", "ulk", "um", "un", "uni", "ur", "val",
    "viv", "vly", "vom", "wah", "wed", "werg", "wex", "whon",
    "wun", "xo", "y", "yot", "yu", "zant", "zeb", "zim",
    "zok", "zon", "zum",
]
SCR_SYLS_JA = [
    "あ", "あぶ", "あぐ", "あくす", "あら", "あん", "あぷ", "あるぐ",
    "あるぜ", "あしゅ", "べく", "びえ", "びと", "びょる", "ぶる", "ぼと",
    "ぶ", "びと", "こんぷ", "こん", "こす", "くれ", "だるふ", "だん",
    "でん", "ど", "え", "えぷ", "える", "えんぐ", "える", "えれ",
    "えるく", "えしゅ", "えぶす", "ふぁ", "ふぃど", "ふり", "ふ", "がん",
    "がる", "ぐれん", "ごぷ", "ぐれ", "は", "ひど", "い", "いんぐ",
    "いぷ", "いす", "いと", "いて", "いぶ", "じょ", "こ", "くり",
    "くりす", "ら", "れち", "まる", "め", "み", "みく", "みく",
    "もん", "むんぐ", "むる", "ねじ", "ねるぐ", "ねぷ", "ねる", "ねす",
    "ねす", "にひ", "にん", "お", "おど", "おど", "おるぐ", "おるん",
    "おくす", "おくし", "ぺい", "ぷれ", "ぷる", "ぽ", "ぽと", "ぷろく",
    "れ", "れあ", "ろぶ", "り", "ろ", "ろぐ", "ろく", "ろる",
    "さ", "さん", "さと", "せふ", "せ", "しゅ", "すき", "すな",
    "すね", "すにく", "すの", "そ", "そる", "すり", "すた", "すん",
    "た", "たぶ", "てむ", "てる", "てぃ", "とくす", "とろる", "とぅえ",
    "とぅるす", "う", "うるく", "うむ", "うん", "うに", "うる", "ばる",
    "びぶ", "ぶり", "ぼむ", "わ", "うぇど", "うぇるぐ", "うぇくす", "ほん",
    "うん", "ぞ", "い", "よと", "ゆ", "ざんと", "ぜぶ", "じむ",
    "ぞく", "ぞん", "ずむ",
]

FOODS = [{"name":"food ration","nut":900},{"name":"slime-mold","nut":700}]

WEAPONS = [
    rogue_weapons.apply_init_dam({"name":"mace","prob":11,"worth":8,"wield":True}, 0),
    rogue_weapons.apply_init_dam({"name":"long sword","prob":11,"worth":15,"wield":True}, 1),
    rogue_weapons.apply_init_dam({"name":"short bow","prob":12,"worth":15,"wield":True}, 2),
    rogue_weapons.apply_init_dam({"name":"arrow","prob":12,"worth":1,"wield":False}, 3),
    rogue_weapons.apply_init_dam({"name":"dagger","prob":8,"worth":3,"wield":True}, 4),
    rogue_weapons.apply_init_dam({"name":"two-handed sword","prob":10,"worth":75,"wield":True}, 5),
    rogue_weapons.apply_init_dam({"name":"dart","prob":12,"worth":2,"wield":False}, 6),
    rogue_weapons.apply_init_dam({"name":"shuriken","prob":12,"worth":5,"wield":False}, 7),
    rogue_weapons.apply_init_dam({"name":"spear","prob":12,"worth":5,"wield":True}, 8),
]

STR_PLUS = rogue_fight.STR_PLUS
ADD_DAM = rogue_fight.ADD_DAM

ARMORS = [
    {"name":"leather armor","prob":20,"worth":5,"ac":8},{"name":"ring mail","prob":15,"worth":30,"ac":7},
    {"name":"studded leather","prob":15,"worth":15,"ac":7},{"name":"scale mail","prob":13,"worth":3,"ac":6},
    {"name":"chain mail","prob":12,"worth":75,"ac":5},{"name":"splint mail","prob":10,"worth":80,"ac":4},
    {"name":"banded mail","prob":10,"worth":90,"ac":4},{"name":"plate mail","prob":5,"worth":150,"ac":3},
]
RINGS = [{"name":r.name,"prob":r.prob,"worth":r.worth} for r in rogue_rings.RINGS]
STICKS = [{"name":s.name,"prob":s.prob,"worth":s.worth} for s in rogue_sticks.STICKS]

TRAPS = [
    {"name":"trap door"}, {"name":"arrow trap"},
    {"name":"sleeping gas trap"}, {"name":"bear trap"},
    {"name":"teleport trap"}, {"name":"dart trap"},
    {"name":"rust trap"}, {"name":"mysterious trap"},
]
RAINBOW = ["red","orange","yellow","green","blue","violet"]
SYMBOL_DESC_EN = {
    "|": "wall of a room", "-": "wall of a room", "*": "gold",
    "%": "a staircase", "+": "door", ".": "room floor",
    "@": "you", "#": "passage", "^": "trap", "!": "potion",
    "?": "scroll", ":": "food", ")": "weapon", " ": "solid rock",
    "]": "armor", ",": "the Amulet of Yendor", "=": "ring",
    "/": "wand or staff",
}
SYMBOL_DESC_JA = {
    "|": "部屋の壁", "-": "部屋の壁", "*": "金貨",
    "%": "階段", "+": "扉", ".": "部屋の床",
    "@": "あなた", "#": "通路", "^": "わな", "!": "水薬",
    "?": "巻き物", ":": "食料", ")": "武器", " ": "岩",
    "]": "よろい", ",": "イェンダーの魔除け", "=": "指輪",
    "/": "杖",
}

# ===========================================================
#  Bestiary  (Rogue 5.4.4 extern.c:monsters[])
# ===========================================================
@dataclass(frozen=True)
class MonsterSpec:
    sym: str
    name: str
    level: int
    armor: int
    damage: str
    exp: int
    min_depth: int
    flags: str = ""
    carry: int = 0

BESTIARY = [
    MonsterSpec("A","aquator",5,2,"0x0/0x0",20,9,"rust,mean"),
    MonsterSpec("B","bat",1,3,"1x2",1,1,"erratic,fly"),
    MonsterSpec("C","centaur",4,4,"1x2/1x5/1x5",17,7,"", carry=15),
    MonsterSpec("D","dragon",10,-1,"1x8/1x8/3x10",5000,21,"mean", carry=100),
    MonsterSpec("E","emu",1,7,"1x2",2,1,"mean"),
    MonsterSpec("F","venus flytrap",8,3,"0x0",80,12,"hold,mean"),
    MonsterSpec("G","griffin",13,2,"4x3/3x5",2000,17,"fly,regen,mean", carry=20),
    MonsterSpec("H","hobgoblin",1,5,"1x8",3,1,"mean"),
    MonsterSpec("I","ice monster",1,9,"0x0",5,5,"freeze"),
    MonsterSpec("J","jabberwock",15,6,"2x12/2x4",3000,20,"", carry=70),
    MonsterSpec("K","kestrel",1,7,"1x4",1,1,"fly,mean"),
    MonsterSpec("L","leprechaun",3,8,"1x1",10,6,"steal_gold"),
    MonsterSpec("M","medusa",8,2,"3x4/3x4/2x5",200,18,"mean", carry=40),
    MonsterSpec("N","nymph",3,9,"0x0",37,9,"steal_item", carry=100),
    MonsterSpec("O","orc",1,6,"1x8",5,5,"greed", carry=15),
    MonsterSpec("P","phantom",8,3,"4x4",120,15,rogue_monsters.FLAG_INVISIBLE),
    MonsterSpec("Q","quagga",3,3,"1x5/1x5",15,8,"mean"),
    MonsterSpec("R","rattlesnake",2,3,"1x6",9,4,"poison,mean"),
    MonsterSpec("S","snake",1,5,"1x3",2,2,"mean"),
    MonsterSpec("T","troll",6,4,"1x8/1x8/2x6",120,13,"regen,mean", carry=50),
    MonsterSpec("U","black unicorn",7,-2,"1x9/1x9/2x9",190,18,"mean"),
    MonsterSpec("V","vampire",8,1,"1x10",350,16,"drain,regen,mean", carry=20),
    MonsterSpec("W","wraith",5,4,"1x6",55,14,"drain_level"),
    MonsterSpec("X","xeroc",7,7,"4x4",100,11,"mimic", carry=30),
    MonsterSpec("Y","yeti",4,6,"1x6/1x6",50,10,"", carry=30),
    MonsterSpec("Z","zombie",2,8,"1x8",6,7,"mean"),
]
# 8-direction vectors
DIR8 = {
    "N":(0,-1),"S":(0,1),"W":(-1,0),"E":(1,0),
    "NW":(-1,-1),"NE":(1,-1),"SW":(-1,1),"SE":(1,1),
}

# ===========================================================
#  Classes
# ===========================================================
class Room:
    def __init__(s,x,y,w,h,flags=None):
        s.x,s.y,s.w,s.h=x,y,w,h
        s.flags=set(flags or ())
        s.exits=[]
    @property
    def cx(s): return s.x+s.w//2
    @property
    def cy(s): return s.y+s.h//2
    @property
    def is_dark(s): return ROOM_DARK in s.flags
    @property
    def is_gone(s): return ROOM_GONE in s.flags
    @property
    def is_maze(s): return ROOM_MAZE in s.flags
    @property
    def usable(s): return not s.is_gone
    def inner(s):
        return RNG.randint(s.x+1,s.x+s.w-2),RNG.randint(s.y+1,s.y+s.h-2)

FLAG_ISKNOW = "ISKNOW"

class Item:
    _nid=0
    def __init__(s,cat,kind,ench=0,cursed=False,qty=1,hit_plus=None,dam_plus=None,charges=0,known=True,group=0):
        s.uid=Item._nid; Item._nid+=1
        s.cat=cat; s.kind=kind; s.cursed=cursed; s.qty=qty
        s.group=group
        s.charges=charges
        s.o_flags: set = set()
        s.o_label: str | None = None
        if known:
            s.o_flags.add(FLAG_ISKNOW)
        if cat==CAT_WPN:
            s.hit_plus = ench if hit_plus is None else hit_plus
            s.dam_plus = 0 if dam_plus is None else dam_plus
            s.ench = s.hit_plus
        else:
            s.ench=ench
            s.hit_plus = 0 if hit_plus is None else hit_plus
            s.dam_plus = 0 if dam_plus is None else dam_plus
        s.x=s.y=0
        s.picked_up=False
        s.protected=False
        s.variant_item=None
    @property
    def known(s):
        return FLAG_ISKNOW in s.o_flags
    @known.setter
    def known(s, v):
        if v: s.o_flags.add(FLAG_ISKNOW)
        else: s.o_flags.discard(FLAG_ISKNOW)
    @property
    def data(s):
        if s.cat==CAT_POT: return POTIONS[s.kind]
        if s.cat==CAT_SCR: return SCROLLS[s.kind]
        if s.cat==CAT_FOOD: return FOODS[s.kind]
        if s.cat==CAT_WPN: return WEAPONS[s.kind]
        if s.cat==CAT_ARM: return ARMORS[s.kind]
        if s.cat==CAT_RING: return RINGS[s.kind]
        if s.cat==CAT_STICK: return STICKS[s.kind]
        if s.cat==CAT_AMULET:
            if getattr(s, "variant_item", None) == "nyandor_cat":
                return {"name": NYANDOR_CAT_NAME}
            return {"name":"Amulet of Yendor"}
        return {}
    @property
    def stackable(s):
        return s.cat in (CAT_POT, CAT_SCR, CAT_FOOD) or (s.cat==CAT_WPN and (s.data.get("stack",False) or s.data.get("name")=="dagger"))
    @property
    def sym(s):
        if s.cat == CAT_AMULET and getattr(s, "variant_item", None) == "nyandor_cat":
            return "c"
        return ISYM.get(s.cat,"?")
    def plus_key(s):
        return (s.hit_plus,s.dam_plus) if s.cat==CAT_WPN else (s.ench,0)

class Monster:
    def __init__(s,x,y,sym,name,hp,level,armor,damage_expr,exp,fl):
        s.x,s.y,s.sym,s.name=x,y,sym,name
        s.disguise=sym
        s.hp=s.max_hp=hp
        s.level=level; s.armor=armor; s.damage_expr=damage_expr; s.exp=exp; s.strength=10
        s.flags=rogue_monsters.parse_flags(fl)
        s.held=s.scared=s.confused=0
        s.running=False; s.dest=DEST_PLAYER; s.turn=True
        s.mean=rogue_monsters.is_mean(s.flags); s.target=False; s.found=False; s.vf_hit=0
        s.pack=[]
    @property
    def alive(s): return s.hp>0

class Player:
    # Rogue 5.4.4 extern.c:e_levels[] with a leading level-1 sentinel for Pyxel indexing.
    EXP_T=[0,10,20,40,80,160,320,640,1300,2600,5200,13000,26000,
           50000,100000,200000,400000,800000,2000000,4000000,8000000]
    def __init__(s):
        s.x=s.y=0; s.hp=s.max_hp=12; s.st=s.max_st=16
        s.level=1; s.exp=0; s.gold=0; s.depth=0; s.food=HUNGERTIME
        s.state="normal"; s.ac=10; s.inv=[]; s.wpn=None; s.arm=None
        s.ring_l=None; s.ring_r=None
        s.confused=s.blind=s.haste=s.see_invisible=s.hallucinating=s.levitating=0
        s.see_monsters=0
        s.no_command=s.no_move=0
        s.held_by=None
        s.quiet=0
        s.facing=(0,1)
        s.can_confuse_monster=False
        s.has_amulet=False
    @property
    def alive(s): return s.hp>0
    @property
    def stuck(s):
        return max(s.no_command, s.no_move)
    @stuck.setter
    def stuck(s, v):
        s.no_command = max(s.no_command, v)
    def lvlup(s):
        s.level,s.hp,s.max_hp,changed=rogue_levels.check_level(s.level,s.exp,s.hp,s.max_hp,s.EXP_T,RNG)
        return changed
    def hunger(s):
        amulet_eat = 1 if s.has_amulet else 0
        food_cost = 1 + rogue_rings.ring_eat(s.ring_l, RNG) + rogue_rings.ring_eat(s.ring_r, RNG) - amulet_eat
        return rogue_daemons.stomach_tick(s, RNG, food_cost, MORETIME, STARVETIME)
    def heal_tick(s):
        rogue_daemons.doctor_tick(s, RNG, rogue_rings.regeneration_count(s))
    def recalc_ac(s):
        armor_ac = (s.arm.data["ac"]-s.arm.ench) if s.arm else None
        s.ac = rogue_fight.player_defense_armor(10, armor_ac, rogue_rings.protection_bonus(s))
    def str_hit_plus(s):
        return rogue_fight.str_hit_plus(s.st)
    def str_dam_plus(s):
        return rogue_fight.str_dam_plus(s.st)
    def inv_full(s): return len(s.inv)>=INV_MAX
    def add_item(s,it):
        if it.stackable:
            if it.cat != CAT_WPN and not rogue_pack.pack_room_allows(len(s.inv), INV_MAX):
                return False
            for i in s.inv:
                if i.cat==it.cat and i.kind==it.kind and (
                    it.cat != CAT_WPN or (it.group != 0 and i.group == it.group)
                ) and (it.cat == CAT_WPN or i.plus_key()==it.plus_key()):
                    i.picked_up = i.picked_up or it.picked_up
                    i.qty+=it.qty; return True
        if not rogue_pack.pack_room_allows(len(s.inv), INV_MAX):
            return False
        s.inv.insert(rogue_pack.add_pack_insert_index(s.inv, it), it); return True
    def rm_item(s,it):
        if it in s.inv: s.inv.remove(it)
        if s.wpn is it: s.wpn=None
        if s.arm is it: s.arm=None; s.recalc_ac()
        if s.ring_l is it or s.ring_r is it:
            was_cursed = it.cursed
            it.cursed = False
            rogue_rings.remove_ring(s,it)
            it.cursed = was_cursed
            s.recalc_ac()

class IdentTable:
    def __init__(s, lang=LANG_EN, scrolls=None):
        s.lang = lang
        s.scrolls = scrolls if scrolls is not None else SCROLLS
        s.easy_type_known = False
        s.pcol=RNG.sample(POT_COLORS,len(POTIONS))
        s.snam=[rogue_init.scroll_title_recipe(len(SCR_SYLS), RNG.rnd, syllables=SCR_SYLS) for _ in range(len(s.scrolls))]
        s.pk=[False]*len(POTIONS); s.sk=[False]*len(s.scrolls)
        s.pg=[None]*len(POTIONS); s.sg=[None]*len(SCROLLS)
        s.pf=[False]*len(POTIONS); s.sf=[False]*len(s.scrolls)
        s.rstones,s.rworth=rogue_rings.init_stones_and_worths(RNG)
        s.rk=[False]*len(RINGS)
        s.rg=[None]*len(RINGS)
        s.rf=[False]*len(RINGS)
        s.wtypes,s.wmades=rogue_sticks.init_materials(RNG)
        s.wk=[False]*len(STICKS)
        s.wg=[None]*len(STICKS)
        s.wf=[False]*len(STICKS)
    def set_lang(s, lang):
        s.lang = lang if lang in (LANG_EN, LANG_JA) else LANG_EN
    def name(s,it,lang=None):
        lang = s.lang if lang is None else lang
        if it.cat==CAT_POT:
            count_prefix = f"{it.qty} " if it.qty > 1 else ""
            type_name = "potions" if it.qty > 1 else "potion"
            if s.pk[it.kind] or s.easy_type_known:
                nm=TextCatalog.item_kind(lang, CAT_POT, POTIONS[it.kind]["name"])
                return f"{count_prefix}{type_name} of {nm}" if lang==LANG_EN else f"{count_prefix}{nm}水薬"
            if s.pg[it.kind] is not None:
                g=s.pg[it.kind]
                col=s.pcol[it.kind]
                return f"{count_prefix}{type_name} called {g}({col})" if lang==LANG_EN else f"{count_prefix}{TextCatalog.potion_color(lang,col)}水薬（{g}）"
            col=s.pcol[it.kind]
            return f"{count_prefix}{col} {type_name}" if lang==LANG_EN else f"{count_prefix}{TextCatalog.potion_color(lang,col)}水薬"
        if it.cat==CAT_SCR:
            count_prefix = f"{it.qty} " if it.qty > 1 else ""
            type_name = "scrolls" if it.qty > 1 else "scroll"
            if s.sk[it.kind] or s.easy_type_known:
                nm=TextCatalog.item_kind(lang, CAT_SCR, s.scrolls[it.kind]["name"])
                return f"{count_prefix}{type_name} of {nm}" if lang==LANG_EN else f"{count_prefix}{nm}巻き物"
            if s.sg[it.kind] is not None:
                g=s.sg[it.kind]
                return f"{count_prefix}{type_name} called {g}" if lang==LANG_EN else f"{count_prefix}巻き物（{g}）"
            syllables = SCR_SYLS_JA if lang == LANG_JA else SCR_SYLS
            title = rogue_init.render_scroll_title(s.snam[it.kind], syllables)
            return f"{count_prefix}{type_name} [{title}]" if lang==LANG_EN else f"{count_prefix}巻き物 [{title}]"
        if it.cat==CAT_FOOD:
            nm=TextCatalog.item_kind(lang, CAT_FOOD, it.data["name"])
            if it.qty>1 and lang==LANG_EN and not nm.endswith("s"):
                nm = f"{nm}s"
            prefix = f"{it.qty} " if it.qty>1 else ""
            return f"{prefix}{nm}"
        if it.cat==CAT_GOLD:
            return f"{it.qty} Gold pieces" if lang==LANG_EN else f"{it.qty}個の金塊"
        if it.cat==CAT_WPN:
            nm=TextCatalog.item_kind(lang, CAT_WPN, it.data["name"])
            if it.stackable and it.qty>1 and lang==LANG_EN and not nm.endswith("s"):
                nm = f"{nm}s"
            label = f" called {it.o_label}" if it.o_label else ""
            if not getattr(it, "known", True):
                prefix = f"{it.qty} " if it.stackable and it.qty>1 else ""
                return f"{prefix}{nm}{label}"
            hp = f"{'+' if it.hit_plus>=0 else ''}{it.hit_plus}"
            dp = f"{'+' if it.dam_plus>=0 else ''}{it.dam_plus}"
            prefix = f"{it.qty} " if it.stackable and it.qty>1 else ""
            return f"{prefix}{hp},{dp} {nm}{label}"
        if it.cat==CAT_ARM:
            e=it.ench; nm=TextCatalog.item_kind(lang, CAT_ARM, it.data["name"])
            label = f" called {it.o_label}" if it.o_label else ""
            if not getattr(it, "known", True):
                return f"{nm}{label}"
            protection = 10 - (it.data["ac"] - e)
            prot = TextCatalog.msg(lang, "item.protection", value=protection)
            return f"{'+' if e>=0 else ''}{e} {nm} [{prot}]{label}"
        if it.cat==CAT_RING:
            spec=RINGS[it.kind]
            if s.rk[it.kind] or s.easy_type_known:
                nm=TextCatalog.item_kind(lang, CAT_RING, spec["name"])
                num=rogue_rings.ring_num(it) if it.known else ""
                return f"ring of {nm}{num}" if lang==LANG_EN else f"{nm}指輪{num}"
            if s.rg[it.kind] is not None:
                g=s.rg[it.kind]; stone=s.rstones[it.kind]
                made=TextCatalog.material(lang, "ring", stone)
                return f"ring called {g}({stone})" if lang==LANG_EN else f"{made}の指輪（{g}）"
            stone=s.rstones[it.kind]
            made=TextCatalog.material(lang, "ring", stone)
            return f"{stone} ring" if lang==LANG_EN else f"{made}の指輪"
        if it.cat==CAT_STICK:
            spec=STICKS[it.kind]
            typ=s.wtypes[it.kind]
            made=s.wmades[it.kind]
            if s.wk[it.kind] or s.easy_type_known:
                nm=TextCatalog.item_kind(lang, CAT_STICK, spec["name"])
                charges=s.stick_charge_str(it, lang) if it.known else ""
                made_name=TextCatalog.material(lang, "stick", made)
                typ_name=TextCatalog.stick_type(lang, typ)
                return f"{typ} of {nm}{charges}({made})" if lang==LANG_EN else f"{nm}{typ_name}{charges}({made_name})"
            if s.wg[it.kind] is not None:
                g=s.wg[it.kind]
                made_name=TextCatalog.material(lang, "stick", made)
                typ_name=TextCatalog.stick_type(lang, typ)
                return f"{typ} called {g}({made})" if lang==LANG_EN else f"{made_name}の{typ_name}（{g}）"
            made_name=TextCatalog.material(lang, "stick", made)
            typ_name=TextCatalog.stick_type(lang, typ)
            return f"{made} {typ}" if lang==LANG_EN else f"{made_name}の{typ_name}"
        if it.cat==CAT_AMULET:
            if getattr(it, "variant_item", None) == "nyandor_cat":
                return nyandor_cat_name(lang)
            nm=TextCatalog.item_kind(lang, CAT_AMULET, it.data["name"])
            return f"the {nm}" if lang==LANG_EN else nm
        return "something" if lang==LANG_EN else "何者か"

    @staticmethod
    def stick_charge_str(it, lang):
        if lang == LANG_JA:
            return f" [{getattr(it, 'charges', 0)}回]"
        return rogue_sticks.charge_str(it)

# ===========================================================
#  Dungeon generator
# ===========================================================
class DGen:
    PASS_CONN = (
        (1, 3),
        (0, 2, 4),
        (1, 5),
        (0, 4, 6),
        (1, 3, 5, 7),
        (2, 4, 8),
        (3, 7),
        (4, 6, 8),
        (5, 7),
    )

    @staticmethod
    def gen(depth, with_hidden=False, room_callback=None):
        # C: new_level.c:new_level()
        tm=[[T_VOID]*MAP_W for _ in range(MAP_H)]; rooms=[]; sr={}
        hidden_tiles = {} if with_hidden else None
        gone=rogue_rooms.gone_room_indices(GRID_C*GRID_R, RNG)
        for i in range(GRID_C*GRID_R):
            gx,gy=i%GRID_C,i//GRID_C
            top_x,top_y=gx*SEC_W+1,gy*SEC_H
            flags=set()
            if i in gone:
                flags.add(ROOM_GONE)
            else:
                kind_flag = rogue_rooms.room_kind_flag(depth, RNG)
                if kind_flag == "maze":
                    flags.add(ROOM_MAZE)
                elif kind_flag == "dark":
                    flags.add(ROOM_DARK)
            if ROOM_GONE in flags:
                rx=top_x+rnd(SEC_W-2)+1
                ry=top_y+rnd(SEC_H-2)+1
                while not (0 < ry < MAP_H-1):
                    ry=top_y+rnd(SEC_H-2)+1
                rw,rh=1,1
            elif ROOM_MAZE in flags:
                rw,rh=SEC_W-1,SEC_H-1
                rx,ry=top_x,top_y
                if rx==1: rx=0
                if ry==0:
                    ry+=1; rh-=1
            else:
                while True:
                    rw=rnd(SEC_W-4)+4
                    rh=rnd(SEC_H-4)+4
                    rx=top_x+rnd(SEC_W-rw)
                    ry=top_y+rnd(SEC_H-rh)
                    if ry!=0:
                        break
            r=Room(rx,ry,rw,rh,flags); rooms.append(r); sr[(gx,gy)]=r
            if r.is_gone:
                continue
            if r.is_maze:
                DGen._maze_room(tm,r,depth=depth,hidden_tiles=hidden_tiles)
            else:
                DGen._room(tm,r)
            if room_callback is not None:
                room_callback(tm, rooms, r)
        for a,b in DGen._passage_edges():
            if with_hidden:
                DGen._conn(tm,rooms[a],rooms[b],abs(a-b)==1,depth=depth,hidden_tiles=hidden_tiles)
            else:
                DGen._conn(tm,rooms[a],rooms[b],abs(a-b)==1)
        if with_hidden:
            return tm, rooms, hidden_tiles
        return tm,rooms

    @staticmethod
    def _passage_edges(audit=False):
        """Rogue 5.4.4 passages.c: do_passages() room graph selection."""
        ingraph=[False]*(GRID_C*GRID_R)
        isconn=[[False]*(GRID_C*GRID_R) for _ in range(GRID_C*GRID_R)]
        tree_edges=[]; extra_edges=[]
        roomcount=1
        r1=rnd(GRID_C*GRID_R)
        ingraph[r1]=True
        while roomcount < GRID_C*GRID_R:
            picked=None; choices=0
            for i in DGen.PASS_CONN[r1]:
                if not ingraph[i]:
                    choices+=1
                    if rnd(choices)==0:
                        picked=i
            if choices==0:
                while True:
                    r1=rnd(GRID_C*GRID_R)
                    if ingraph[r1]:
                        break
            else:
                r2=picked
                ingraph[r2]=True
                tree_edges.append((r1,r2))
                isconn[r1][r2]=isconn[r2][r1]=True
                roomcount+=1
        for _ in range(rnd(5)):
            r1=rnd(GRID_C*GRID_R)
            picked=None; choices=0
            for i in DGen.PASS_CONN[r1]:
                if not isconn[r1][i]:
                    choices+=1
                    if rnd(choices)==0:
                        picked=i
            if choices!=0:
                r2=picked
                extra_edges.append((r1,r2))
                isconn[r1][r2]=isconn[r2][r1]=True
        edges=tree_edges+extra_edges
        if audit:
            return {"tree":tree_edges,"extra":extra_edges,"edges":edges}
        return edges
    @staticmethod
    def _room(t,r):
        if r.is_gone:
            return
        for y in range(r.y,r.y+r.h):
            for x in range(r.x,r.x+r.w):
                if in_play_area(x,y):
                    if y==r.y or y==r.y+r.h-1: t[y][x]=T_HWALL
                    elif x==r.x or x==r.x+r.w-1: t[y][x]=T_VWALL
                    else: t[y][x]=T_FLOOR
    @staticmethod
    def _maze_room(t,r,depth=None,hidden_tiles=None):
        for y in range(r.y,r.y+r.h):
            for x in range(r.x,r.x+r.w):
                if in_play_area(x,y):
                    t[y][x]=T_VOID
        if r.w <= 0 or r.h <= 0:
            return
        max_y=r.h-1
        max_x=r.w-1
        start_y=(RNG.rnd(r.h)//2)*2
        if r.y == PLAY_Y_MIN and r.h % 2 == 0:
            start_y = min(max_y, start_y + 1)
        start_x=(RNG.rnd(r.w)//2)*2

        def put(oy,ox):
            x,y=r.x+ox,r.y+oy
            if in_play_area(x,y):
                DGen._corr(t,(x,y),depth=depth,hidden_tiles=hidden_tiles)

        def is_pass(oy,ox):
            x,y=r.x+ox,r.y+oy
            return (
                in_play_area(x,y)
                and (t[y][x]==T_CORR or (hidden_tiles is not None and hidden_tiles.get((x,y)) == T_CORR))
            )

        def dig(oy,ox):
            # Rogue 5.4.4 rooms.c:dig() uses reservoir choice via rnd(++cnt).
            while True:
                cnt=0
                picked=None
                for dy,dx in ((2,0),(-2,0),(0,2),(0,-2)):
                    ny,nx=oy+dy,ox+dx
                    if ny < 0 or ny > max_y or nx < 0 or nx > max_x:
                        continue
                    if is_pass(ny,nx):
                        continue
                    cnt+=1
                    if RNG.rnd(cnt)==0:
                        picked=(ny,nx)
                if picked is None:
                    return
                ny,nx=picked
                if ny==oy:
                    put(oy, nx + 1 if nx - ox < 0 else nx - 1)
                else:
                    put(ny + 1 if ny - oy < 0 else ny - 1, ox)
                put(ny,nx)
                dig(ny,nx)

        put(start_y,start_x)
        dig(start_y,start_x)
    @staticmethod
    def _conn(t,r1,r2,horiz=None,depth=None,hidden_tiles=None):
        """Connect two rooms by choosing wall doors first, like Rogue's conn()."""
        if horiz is None:
            horiz = abs(r1.cx-r2.cx) >= abs(r1.cy-r2.cy)
        # C: passages.c:conn() normalizes r1/r2 to the lower sector before drawing right/down.
        if (horiz and r1.cx > r2.cx) or (not horiz and r1.cy > r2.cy):
            r1, r2 = r2, r1
        if horiz:
            if r1.cx <= r2.cx:
                d1,s=DGen._exit(t,r1,"R",outward=True,hidden_tiles=hidden_tiles)
                d2,e=DGen._exit(t,r2,"L",outward=True,hidden_tiles=hidden_tiles)
            else:
                d1,s=DGen._exit(t,r1,"L",outward=True,hidden_tiles=hidden_tiles)
                d2,e=DGen._exit(t,r2,"R",outward=True,hidden_tiles=hidden_tiles)
        else:
            if r1.cy <= r2.cy:
                d1,s=DGen._exit(t,r1,"D",outward=True,hidden_tiles=hidden_tiles)
                d2,e=DGen._exit(t,r2,"U",outward=True,hidden_tiles=hidden_tiles)
            else:
                d1,s=DGen._exit(t,r1,"U",outward=True,hidden_tiles=hidden_tiles)
                d2,e=DGen._exit(t,r2,"D",outward=True,hidden_tiles=hidden_tiles)
        turn_spot = DGen._passage_turn_spot(d1 or s, d2 or e, horiz)
        if d1 is not None:
            DGen._door(t,d1,r1,depth=depth,hidden_tiles=hidden_tiles)
        elif r1.is_gone:
            DGen._corr(t,s,depth=depth,hidden_tiles=hidden_tiles)
        if d2 is not None:
            DGen._door(t,d2,r2,depth=depth,hidden_tiles=hidden_tiles)
        elif r2.is_gone:
            DGen._corr(t,e,depth=depth,hidden_tiles=hidden_tiles)
        DGen._dig_pass(t,d1 or s,d2 or e,horiz,depth=depth,hidden_tiles=hidden_tiles,turn_spot=turn_spot)
    @staticmethod
    def _exit(t,r,side,outward=True,hidden_tiles=None):
        if r.is_gone:
            p=DGen._passage_side_point(r,side)
            return None,p
        if r.is_maze:
            p=DGen._maze_exit(t,r,side,hidden_tiles=hidden_tiles)
            DGen._record_exit(r,p)
            return None,p
        door=DGen._pick_wall_door(t,r,side)
        DGen._record_exit(r,door)
        x,y=door
        dx,dy={"L":(-1,0),"R":(1,0),"U":(0,-1),"D":(0,1)}[side]
        return door,(x+dx,y+dy) if outward else door
    @staticmethod
    def _record_exit(r,p):
        exits=getattr(r,"exits",None)
        if exits is None:
            r.exits=[]
            exits=r.exits
        if p not in exits:
            exits.append(p)
    @staticmethod
    def _passage_side_point(r,side):
        if side=="L": return r.x,r.cy
        if side=="R": return r.x+r.w-1,r.cy
        if side=="U": return r.cx,r.y
        return r.cx,r.y+r.h-1
    @staticmethod
    def _maze_exit(t,r,side,hidden_tiles=None):
        # Rogue 5.4.4 passages.c:conn() retries random side-wall
        # coordinates until an ISMAZE room coordinate already has F_PASS.
        if side in ("L","R"):
            limit = max(1, r.h - 2)
            x = r.x if side == "L" else r.x + r.w - 1
            while True:
                y = r.y + RNG.rnd(limit) + 1
                if in_play_area(x,y) and (t[y][x] == T_CORR or (hidden_tiles is not None and hidden_tiles.get((x,y)) == T_CORR)):
                    if hidden_tiles is None or hidden_tiles.get((x,y)) != T_CORR:
                        DGen._corr(t,(x,y))
                    return (x,y)
        else:
            limit = max(1, r.w - 2)
            y = r.y if side == "U" else r.y + r.h - 1
            while True:
                x = r.x + RNG.rnd(limit) + 1
                if in_play_area(x,y) and (t[y][x] == T_CORR or (hidden_tiles is not None and hidden_tiles.get((x,y)) == T_CORR)):
                    if hidden_tiles is None or hidden_tiles.get((x,y)) != T_CORR:
                        DGen._corr(t,(x,y))
                    return (x,y)
    @staticmethod
    def _pick_wall_door(t,r,side):
        # Rogue 5.4.4 passages.c:conn() selects a wall coordinate directly
        # with rnd(width/height - 2) + 1; it does not avoid adjacent doors.
        if side in ("L","R"):
            x = r.x if side=="L" else r.x+r.w-1
            return x, r.y + RNG.rnd(r.h - 2) + 1
        else:
            y = r.y if side=="U" else r.y+r.h-1
            return r.x + RNG.rnd(r.w - 2) + 1, y
    @staticmethod
    def _door(t,p,room=None,depth=None,hidden_tiles=None):
        x,y=p
        if not in_play_area(x,y):
            return
        if hidden_tiles is not None and depth is not None and rogue_search.secret_feature_hidden(depth, RNG, 5):
            hidden_tiles[(x,y)]=T_DOOR
            if room is not None and (y == room.y or y == room.y + room.h - 1):
                t[y][x]=T_HWALL
            elif room is not None:
                t[y][x]=T_VWALL
            else:
                t[y][x]=DGen._hidden_door_wall_tile(t,x,y)
            return
        t[y][x]=T_DOOR
    @staticmethod
    def _corr(t,p,depth=None,hidden_tiles=None):
        x,y=p
        if not in_play_area(x,y):
            return
        if hidden_tiles is not None and depth is not None and rogue_search.secret_feature_hidden(depth, RNG, 40):
            hidden_tiles[(x,y)]=T_CORR
            t[y][x]=T_VOID
            return
        t[y][x]=T_CORR
    @staticmethod
    def _hidden_door_wall_tile(t,x,y):
        left = 0<=x-1<MAP_W and t[y][x-1] in (T_FLOOR,T_CORR,T_STAIR)
        right = 0<=x+1<MAP_W and t[y][x+1] in (T_FLOOR,T_CORR,T_STAIR)
        return T_VWALL if left or right else T_HWALL
    @staticmethod
    def _passage_turn_spot(s,e,first_horiz):
        x,y=s; ex,ey=e
        distance=abs(x-ex)-1 if first_horiz else abs(y-ey)-1
        return RNG.rnd(distance - 1) + 1
    @staticmethod
    def _dig_pass(t,s,e,first_horiz,depth=None,hidden_tiles=None,turn_spot=None):
        # Rogue 5.4.4 passages.c:conn() moves one step at a time and
        # turns when the remaining straight-line distance reaches turn_spot.
        x,y=s; ex,ey=e
        if first_horiz:
            dx,dy=(1 if x < ex else -1),0
            tx,ty=0,(1 if y < ey else -1)
            distance=abs(x-ex)-1
            turn_distance=abs(y-ey)
        else:
            dx,dy=0,(1 if y < ey else -1)
            tx,ty=(1 if x < ex else -1),0
            distance=abs(y-ey)-1
            turn_distance=abs(x-ex)
        if turn_spot is None:
            turn_spot = RNG.rnd(distance - 1) + 1
        while distance > 0:
            x += dx
            y += dy
            if distance == turn_spot:
                while turn_distance > 0:
                    DGen._corr(t,(x,y),depth=depth,hidden_tiles=hidden_tiles)
                    x += tx
                    y += ty
                    turn_distance -= 1
            DGen._corr(t,(x,y),depth=depth,hidden_tiles=hidden_tiles)
            distance -= 1
    @staticmethod
    def _hl(t,x1,x2,y):
        if not(PLAY_Y_MIN<=y<=PLAY_Y_MAX): return
        for x in range(min(x1,x2),max(x1,x2)+1):
            if not(0<=x<MAP_W): continue
            v=t[y][x]
            if v==T_VOID or v==T_CORR: t[y][x]=T_CORR
    @staticmethod
    def _vl(t,y1,y2,x):
        if not(0<=x<MAP_W): return
        for y in range(min(y1,y2),max(y1,y2)+1):
            if not(PLAY_Y_MIN<=y<=PLAY_Y_MAX): continue
            v=t[y][x]
            if v==T_VOID or v==T_CORR: t[y][x]=T_CORR

# ===========================================================
#  Item factory
# ===========================================================
def wchoice(tbl):
    return rogue_things.pick_one([(e["name"], e["prob"]) for e in tbl], RNG.rnd(sum(e["prob"] for e in tbl)))

def make_item(depth, no_food=0, scrolls=None):
    scrolls = scrolls if scrolls is not None else SCROLLS
    cat=rogue_things.new_thing_category_roll(RNG.rnd, no_food)
    if cat=="potion": return Item(CAT_POT,wchoice(POTIONS))
    if cat=="scroll": return Item(CAT_SCR,wchoice(scrolls))
    if cat=="food": return Item(CAT_FOOD,rogue_things.new_thing_food_kind(RNG.rnd))
    if cat=="weapon":
        k=wchoice(WEAPONS)
        r=RNG.rnd(100)
        hit_plus,cursed=rogue_weapons.new_thing_weapon_enchant(r,RNG.rnd)
        q=rogue_weapons.initial_weapon_count(WEAPONS[k]["name"], WEAPONS[k].get("stack", False), RNG.rnd)
        group=rogue_weapons.initial_weapon_group(WEAPONS[k]["name"], WEAPONS[k].get("stack", False))
        return Item(CAT_WPN,k,hit_plus=hit_plus,dam_plus=0,cursed=cursed,qty=q,known=False,group=group)
    if cat=="armor":
        k=wchoice(ARMORS)
        r=RNG.rnd(100)
        e,cursed=rogue_armor.new_thing_armor_enchant(r,RNG.rnd)
        return Item(CAT_ARM,k,ench=e,cursed=cursed,known=False)
    if cat=="ring":
        ring=rogue_rings.make_ring(RNG, CAT_RING)
        return Item(CAT_RING,ring.kind,ench=ring.ench,cursed=ring.cursed,known=False)
    stick=rogue_sticks.make_stick(RNG, CAT_STICK)
    return Item(CAT_STICK,stick.kind,charges=stick.charges,known=False)

def start_inv():
    w=Item(CAT_WPN,0,hit_plus=1,dam_plus=1) # mace +1,+1
    a=Item(CAT_ARM,1,ench=1)        # ring mail +1
    ar=Item(CAT_WPN,3,hit_plus=0,dam_plus=0,qty=rogue_init.initial_arrow_count(RNG.rnd),group=rogue_weapons.initial_weapon_group(WEAPONS[3]["name"], WEAPONS[3].get("stack", False)))# arrows
    b=Item(CAT_WPN,2,hit_plus=1,dam_plus=0) # bow +1,+0
    f=Item(CAT_FOOD,0)              # ration
    return rogue_init.initial_pack_order(f,a,w,b,ar),w,a

# ===========================================================
#  GAME
# ===========================================================
class Game:
    def __init__(self):
        self.settings_missing = not settings_exists()
        self.settings = load_settings()
        fixed_difficulty = variant_fixed_difficulty()
        if fixed_difficulty:
            self.settings.difficulty = fixed_difficulty
        pyxel.init(SCR_W, SCR_H, title=variant_window_title(), fps=30, quit_key=pyxel.KEY_NONE)
        self.apply_palette()
        self.font = pyxel.Font(FONT_PATH)
        self.init_sfx()
        self.init_frontend_state()
        self.setup_title_bgm()
        self.start_title_bgm()
        self.load_title_background()
        pyxel.run(self.update, self.draw)

    def init_frontend_state(self):
        self.online_profile = self.startup_online_profile()
        self.player_name = self.online_profile.get("user_name", "guest")
        self.title_cursor = 0
        self.save_confirm_return_state = ST_PLAY
        self.name_chars = list(self.player_name[:8])
        self.name_pos = min(len(self.name_chars), 7)
        self.name_pick = 0
        self.language_cursor = 0 if self.ensure_settings().language == LANG_EN else 1
        self.logo_frames = 0
        self.online_period = SCOREBOARD_PERIOD_LOCAL
        self.online_scores = []
        self.online_score_cache = {}
        self.online_score_raw_cache = {}
        self.online_score_loaded = set()
        self.online_rank_cache = {}
        self.online_sync_pending = False
        self.online_syncing = False
        self.online_sync_wait = 0
        self.online_sync_force = False
        self.online_sync_periods = []
        self.online_sync_status = ""
        self.online_sync_result = ""
        self.online_register_prompt = False
        self.online_password_chars = []
        self.online_pending_user_name = ""
        self.online_original_user_name = ""
        self.online_name_candidates = []
        self.online_password_mode = "register"
        self.online_return_state = ST_TITLE
        self.title_bg = None
        self.title_fade_frames = 0
        self.b_button_state = rogue_input.TapButtonState()
        self.back_button_state = rogue_input.TapButtonState()
        self.b_menu_guard = False
        self.st = ST_LOGO
        self._loading_phase = 0
        self.title_bgm_loaded = False
        self.title_bgm_started = False
        self.title_bgm_stop_wait = 0
        self.title_save_error = ""

    def startup_online_profile(self):
        profile = normalize_online_profile(load_online_profile())
        if profile.get("server_token") and not profile.get("local_only", True):
            return profile
        return {
            "user_name": "guest",
            "local_only": True,
            "server_token": "",
            "last_sync_at": "",
            "next_sync_at": "",
            "profile_exists": True,
        }

    def setup_title_bgm(self):
        for i, mml in enumerate(TITLE_BGM_MMLS):
            pyxel.sounds[i].mml(mml)
        self.title_bgm_loaded = True

    def start_title_bgm(self):
        if getattr(self, "title_bgm_started", False):
            return
        if not getattr(self, "title_bgm_loaded", False):
            self.setup_title_bgm()
        for ch in range(len(TITLE_BGM_MMLS)):
            pyxel.play(ch, ch, loop=True)
        self.title_bgm_started = True

    def stop_title_bgm(self):
        if not getattr(self, "title_bgm_started", False):
            return
        for ch in range(len(TITLE_BGM_MMLS)):
            pyxel.stop(ch)
        self.title_bgm_started = False

    def init_sfx(self):
        path = os.path.join(os.path.dirname(__file__), "assets", "rpg-sepack.pyxres")
        enabled = rogue_sfx.load_se_pack(pyxel, path)
        self.sfx = rogue_sfx.SfxController(pyxel, enabled=enabled)

    def request_sfx(self, slot):
        if hasattr(self, "sfx"):
            self.sfx.request(slot)

    def request_hit_sfx(self):
        if hasattr(self, "sfx"):
            self.sfx.request_random_hit()

    def play_sfx_immediate(self, slot, *, stop_bgm=False):
        if hasattr(self, "sfx"):
            self.sfx.play_immediate(slot, stop_bgm=stop_bgm)

    def play_death_sfx(self):
        if hasattr(self, "sfx"):
            self.death_result_bgm_pending = True
            self.sfx.play_death()
            self.update_death_result_bgm()
        elif hasattr(self, "dungeon_bgm"):
            self.play_result_bgm()

    def update_death_result_bgm(self):
        if not getattr(self, "death_result_bgm_pending", False):
            return
        if hasattr(self, "sfx") and self.sfx.is_active():
            return
        self.death_result_bgm_pending = False
        self.play_result_bgm()

    def init_dungeon_bgm(self):
        if not hasattr(self, "sfx"):
            self.init_sfx()
        self.dungeon_bgm = DungeonBgmController(pyxel, sfx_active=self.sfx.is_active)
        self.sfx.bgm = self.dungeon_bgm

    def dungeon_bgm_enabled(self):
        return bool(self.ensure_settings().dungeon_bgm)

    def update_dungeon_bgm(self):
        if not hasattr(self, "dungeon_bgm"):
            self.init_dungeon_bgm()
        if not self.dungeon_bgm_enabled():
            self.dungeon_bgm.stop()
            return
        if getattr(self, "st", None) != ST_PLAY or not hasattr(self, "p"):
            return
        self.dungeon_bgm.play_exploration(
            depth=self.p.depth,
            hp=self.p.hp,
            max_hp=self.p.max_hp,
            hunger_state=self.p.state,
            enabled=True,
        )

    def play_result_bgm(self):
        if not hasattr(self, "dungeon_bgm"):
            return
        self.dungeon_bgm.play_result(enabled=self.dungeon_bgm_enabled())

    def stop_scoreboard_bgm(self):
        self.stop_title_bgm()
        if hasattr(self, "dungeon_bgm"):
            self.dungeon_bgm.stop()

    def load_title_background(self):
        self.title_bg = None
        try:
            self.apply_title_palette()
            img = pyxel.Image(SCR_W, SCR_H)
            img.load(0, 0, variant_title_background_path())
            self.title_bg = img
        except Exception:
            self.title_bg = None
        if getattr(self, "st", None) != ST_TITLE:
            self.apply_palette()

    def enter_title_screen(self, skip_fade=False, initial_fade=False):
        self.apply_title_palette()
        self.title_fade_frames = 0 if initial_fade and getattr(self, "title_bgm_started", False) and not skip_fade else TITLE_FADE_FRAMES
        self.st = ST_TITLE

    def enter_post_logo(self):
        profile = normalize_online_profile(getattr(self, "online_profile", None))
        if not (profile.get("server_token") and not profile.get("local_only", True)):
            self.online_profile = {
                "user_name": "guest",
                "local_only": True,
                "server_token": "",
                "last_sync_at": "",
                "next_sync_at": "",
                "profile_exists": True,
            }
            self.player_name = "guest"
        if getattr(self, "settings_missing", False):
            self.apply_palette()
            self.language_cursor = 0 if self.ensure_settings().language == LANG_EN else 1
            self.st = ST_LANGUAGE
            return
        self.enter_title_screen(initial_fade=True)

    def ensure_settings(self):
        if "settings" not in self.__dict__:
            self.settings = Settings()
        return self.settings

    def persist_settings(self):
        saved = save_settings(self.ensure_settings())
        if isinstance(saved, Settings):
            self.settings = saved

    @property
    def lang(self):
        return self.ensure_settings().language

    @lang.setter
    def lang(self, value):
        self.ensure_settings().language = value if value in (LANG_EN, LANG_JA) else LANG_EN

    @property
    def auto_pickup(self):
        return self.ensure_settings().auto_pickup

    @auto_pickup.setter
    def auto_pickup(self, value):
        self.ensure_settings().auto_pickup = bool(value)

    def apply_palette(self):
        palette = PALETTES.get(self.ensure_settings().palette, FLEXOKI_DARK_PALETTE)
        self.apply_palette_values(palette)

    def apply_title_palette(self):
        self.apply_palette_values(variant_title_palette())

    def apply_palette_values(self, palette):
        if not hasattr(pyxel, 'colors'):
            return
        for i, rgb in enumerate(palette):
            if i < len(pyxel.colors):
                pyxel.colors[i] = rgb
            elif hasattr(pyxel.colors, "append"):
                pyxel.colors.append(rgb)

    def run_step_interval(self):
        return DASH_INTERVAL if self.ensure_settings().show_run_steps else 1

    def current_player_name(self):
        if "online_profile" not in self.__dict__:
            return str(getattr(self, "player_name", "guest"))[:16] or "guest"
        profile = normalize_online_profile(getattr(self, "online_profile", None))
        if profile.get("local_only", True):
            return "guest"
        if profile.get("user_name"):
            return display_score_name(profile)
        return str(getattr(self, "player_name", "guest"))[:16] or "guest"

    def current_user_id(self):
        if "online_profile" not in self.__dict__:
            return sanitize_user_id(getattr(self, "player_name", "guest"))
        profile = normalize_online_profile(getattr(self, "online_profile", None))
        return sanitize_user_id(profile.get("user_name") or getattr(self, "player_name", "guest"))

    def current_score_player_name(self):
        if "online_profile" not in self.__dict__:
            return str(getattr(self, "player_name", "guest"))[:16]
        profile = normalize_online_profile(getattr(self, "online_profile", None))
        if profile.get("local_only", True):
            return "guest"
        return str(profile.get("user_name") or getattr(self, "player_name", "guest"))[:16]

    def is_online_mode(self):
        profile = normalize_online_profile(getattr(self, "online_profile", None))
        return bool(profile.get("server_token")) and not profile.get("local_only", True)

    def monster_color(self, sym):
        return palette_monster_color(self.ensure_settings().palette, sym)

    def random_thing_sym(self, depth=None):
        # Rogue 5.4.4 misc.c:rnd_thing() omits Amulet before AMULETLEVEL.
        depth = self.p.depth if depth is None else depth
        limit = len(HALLU_THINGS) if depth >= AMULET_LEVEL else len(HALLU_THINGS) - 1
        return HALLU_THINGS[rnd(limit)]

    def hallucination_thing_sym(self):
        return self.random_thing_sym()

    def visible_tile_sym(self, x, y, tile):
        # Rogue 5.4.4 misc.c:trip_ch() keeps STAIRS real after seenstairs is set.
        if self.p.hallucinating > 0 and tile == T_STAIR and not getattr(self, "seen_stairs", False):
            if (x, y) in self.hallu_tile_syms:
                return self.hallu_tile_syms[(x, y)]
            return self.hallucination_thing_sym()
        return TILE_CH.get(tile, (" ", 0))[0]

    def stairs_seen_on_map(self):
        # Rogue 5.4.4 potions.c:seen_stairs().
        if self.tm[self.p.y][self.p.x] == T_STAIR:
            return True
        for y, row in enumerate(self.tm):
            for x, tile in enumerate(row):
                if tile == T_STAIR and ((x, y) in self.visible or (x, y) in self.explored):
                    return True
        for monster in self.mons:
            if not getattr(monster, "alive", False) or self.tm[monster.y][monster.x] != T_STAIR:
                continue
            if self.monster_is_seen(monster) and getattr(monster, "running", False):
                return True
            if self.can_detect_monsters():
                return True
        return False

    def visible_item_sym(self, item):
        if self.p.hallucinating > 0:
            if id(item) in self.hallu_item_syms:
                return self.hallu_item_syms[id(item)]
            return self.hallucination_thing_sym()
        return item.sym

    def visible_monster_sym(self, monster):
        if self.p.hallucinating > 0:
            if id(monster) in self.hallu_monster_syms:
                return self.hallu_monster_syms[id(monster)]
            return chr(ord("A") + rnd(26))
        return getattr(monster, "disguise", monster.sym)

    def detected_monster_sym(self, monster):
        if self.p.hallucinating > 0:
            if id(monster) in self.hallu_detected_monster_syms:
                return self.hallu_detected_monster_syms[id(monster)]
            return chr(ord("A") + rnd(26))
        return monster.sym

    def toggle_palette(self):
        settings = self.ensure_settings()
        i = PALETTE_IDS.index(settings.palette) if settings.palette in PALETTE_IDS else 0
        settings.palette = PALETTE_IDS[(i + 1) % len(PALETTE_IDS)]
        self.apply_palette()
        self.persist_settings()
        self.msg("pyxel.palette_set", palette=PALETTE_LABELS[settings.palette])

    def txt(self, x, y, s, c):
        pyxel.text(x, y, str(s), c, self.font)

    def ui_text_width(self, s):
        width = 0
        for ch in str(s):
            width += FONT_ASCII_W if ord(ch) < 128 else FONT_CJK_W
        return width

    def ui_segments_width(self, segments):
        return sum(self.ui_text_width(text) for text, _col in segments)

    def txt_segments(self, x, y, segments):
        cur = x
        for text, col in segments:
            text = str(text)
            if text.strip():
                self.txt(cur, y, text, col)
            cur += self.ui_text_width(text)
        return cur

    def txt_segments_right(self, right_x, y, segments):
        return self.txt_segments(right_x - self.ui_segments_width(segments), y, segments)

    def ellipsize_to_width(self, text, max_width):
        text = str(text)
        if self.ui_text_width(text) <= max_width:
            return text
        ell = "."
        ell_w = self.ui_text_width(ell)
        if max_width <= ell_w:
            return ell if max_width >= ell_w else ""
        out = ""
        width = 0
        for ch in text:
            ch_w = FONT_ASCII_W if ord(ch) < 128 else FONT_CJK_W
            if width + ch_w + ell_w > max_width:
                break
            out += ch
            width += ch_w
        return out + ell

    def wrap_msg_toast_text(self, text):
        limit = MSG_COLS * FONT_ASCII_W
        rows = []
        line = ""
        width = 0
        last_space = -1
        text = str(text)
        if text.endswith("。"):
            text = text[:-1]
        use_space_wrap = all(ord(ch) < 128 for ch in text)
        for ch in text:
            ch_width = FONT_ASCII_W if ord(ch) < 128 else FONT_CJK_W
            if line and width + ch_width > limit:
                if ch in MSG_KINSOKU_LINE_START:
                    carry = line[-1] + ch
                    line = line[:-1]
                    if line:
                        rows.append(line)
                    line = carry
                    width = self.ui_text_width(line)
                elif use_space_wrap and last_space > 0:
                    rows.append(line[:last_space])
                    line = line[last_space + 1:] + ch
                    width = self.ui_text_width(line)
                else:
                    rows.append(line)
                    line = ch
                    width = ch_width
                last_space = line.rfind(" ") if use_space_wrap else -1
            else:
                line += ch
                width += ch_width
                if use_space_wrap and ch == " ":
                    last_space = len(line) - 1
        return rows + ([line] if line else [""])

    def item_name(self,it, describe=True):
        name=self.ident.name(it, self.lang)
        if describe and it is self.p.wpn: return f"{name} {TextCatalog.msg(self.lang, 'item.weapon_in_hand')}"
        if describe and it is self.p.arm: return f"{name} {TextCatalog.msg(self.lang, 'item.being_worn')}"
        if describe and it is self.p.ring_l: return f"{name} {TextCatalog.msg(self.lang, 'item.on_left_hand')}"
        if describe and it is self.p.ring_r: return f"{name} {TextCatalog.msg(self.lang, 'item.on_right_hand')}"
        return name

    def equip_name(self,it):
        return self.item_name(it, describe=False)

    def hud_equip_name(self,it):
        return rogue_hud.hud_equip_name(it, self.lang, self.equip_name)

    def hud_weapon_bonus(self, it):
        return rogue_hud.hud_weapon_bonus(it)

    def hud_armor_bonus(self, it):
        return rogue_hud.hud_armor_bonus(it)

    def hud_equip_line(self):
        w = self.hud_weapon_empty_name()
        a = self.hud_armor_empty_name()
        if self.p.wpn:
            w = self.hud_equip_name(self.p.wpn)
        if self.p.arm:
            a = self.hud_equip_name(self.p.arm)
        return f"W {w} A {a}"

    def hud_weapon_empty_name(self):
        return rogue_hud.hud_weapon_empty_name(self.lang)

    def hud_armor_empty_name(self):
        return rogue_hud.hud_armor_empty_name(self.lang)

    def hud_condition_labels(self):
        return rogue_hud.hud_condition_labels(self.p, self.lang, self.difficulty_profile().show_status_hud)

    def hud_condition_chips(self):
        return rogue_hud.hud_condition_chips(self.p, self.lang, self.difficulty_profile().show_status_hud)

    def hud_mode_chips(self):
        return rogue_hud.hud_mode_chips(self.auto_pickup, self.diag_assist)

    def ui_role_color(self, role):
        return palette_role_color(self.ensure_settings().palette, role)

    def expire_visible_msg_toast(self):
        if len(getattr(self, "msg_turns", [])) != len(self.msgs):
            self.msg_turns = [self.turn] * len(self.msgs)
        expired_turn = self.turn - MSG_TOAST_DIM_TURNS - 1
        self.msg_turns = [expired_turn] * len(self.msgs)
        self.msg_toast_visible_keys = ()
        self.msg_toast_expire_keys = ()
        self.msg_toast_expire_frame = getattr(pyxel, "frame_count", 0)
        self.msg_toast_expire_turn = self.turn
        self.msg_toast_block = None
        self.msg_toast_rows = 0
        self.msg_toast_reposition_needed = True

    # ---------- Init ----------
    def new_game(self):
        self.ensure_settings()
        self.p = Player()
        inv,w,a = start_inv()
        self.p.inv=inv; self.p.wpn=w; self.p.arm=a; self.p.recalc_ac()
        self.scrolls = rogue_scrolls.active_scrolls(SCROLLS, self.difficulty)
        self.ident = IdentTable(self.lang, self.scrolls)
        self.apply_initial_difficulty_knowledge()
        self.msgs = []; self.msg_turns = []; self.explored = set(); self.visible = set()
        self.gitems = []; self.mons = []; self.turn = 0
        self.traps = {}; self.hidden_tiles = {}
        self.st = ST_PLAY; self.mcur = 0; self.icur = 0; self.acur = 0
        self.save_confirm_return_state = ST_PLAY
        self.settings_cursor = 0
        self.cact = None; self.dact = None; self.fitems = []
        self.last_item_by_action = {}
        self.item_cursor_restored = False
        self.last_menu_action = None
        self.menu_cursor_restored = False
        self.message_ack_pending = False
        self.msg_toast_block = None
        self.msg_toast_rows = 0
        self.log_scroll = 0
        self.last_intent_dir = (0, 0)
        self.msg_toast_intent_history = []
        self.msg_toast_reposition_needed = True
        self.call_input = ""; self.call_preset_idx = 0; self.call_item = None
        self.identify_symbol_pending = False
        self.fight_kamikaze_pending = False
        self.fight_to_death = False
        self.fight_kamikaze = False
        self.fight_dir = (0, 0)
        self.fight_target = None
        self.fight_max_hit = 0
        self.repeat_state = rogue_input.RepeatState()
        self.count_input_state = rogue_input.CountInputState()
        self.dash_state = rogue_input.DashState()
        self.disc_scroll = 0
        self.turn_msg_start = 0
        self.throw_dir = None; self.zap_item = None; self.action_origin = ST_PLAY
        self.cam_x = self.cam_y = 0
        self.b_button_state = rogue_input.TapButtonState()
        self.back_button_state = rogue_input.TapButtonState()
        self.b_menu_guard = False
        self.diag_assist = False
        self.dir_pending = None
        self.dir_press_locked = None
        self.throw_anim = None
        self.turn_after_throw_anim = False
        self.last_hp_seen = None
        self.hp_damage_from = None
        self.hp_damage_turn = None
        self.death_cause = ""
        self.player_name = self.current_player_name()
        self.options = {"tombstone": True, "name": self.player_name}
        self.max_depth = 0
        self.no_food = 0
        self.seen_stairs = False
        self.hallu_item_syms = {}
        self.hallu_tile_syms = {}
        self.hallu_monster_syms = {}
        self.hallu_detected_monster_syms = {}
        self.wander_timer = 0
        self.wander_between = 0
        self.delayed_actions = rogue_daemons.DelayedActionTable()
        self.fuses = self.delayed_actions.fuses
        self.daemons = self.delayed_actions.daemons
        self.daemons.start("runners", rogue_daemons.AFTER)
        self.daemons.start("doctor", rogue_daemons.AFTER)
        self.init_dungeon_bgm()
        self.haste_half_turn = False
        self.haste_no_command_half_turn = False
        self.result_scores = []
        self.result_entry = None
        self.result_online_submitted = False
        self.result_outcome = None
        self.descend()
        self.fuses.fuse("swander", RNG.spread(WANDERTIME), rogue_daemons.AFTER)
        self.daemons.start("stomach", rogue_daemons.AFTER)
        self.wander_timer = self.fuses.remaining("swander")
        self.msg("pyxel.welcome_to_dungeons", name=self.player_name)
        self.turn_msg_start = len(self.msgs)

    def _json_rng_state(self):
        return self._json_value(RNG.getstate())

    def _restore_rng_state(self, state):
        if state is not None:
            RNG.setstate(self._tuple_value(state))

    def _json_value(self, value):
        if isinstance(value, tuple):
            return [self._json_value(v) for v in value]
        if isinstance(value, list):
            return [self._json_value(v) for v in value]
        if isinstance(value, set):
            return [self._json_value(v) for v in sorted(value)]
        if isinstance(value, dict):
            return {str(k): self._json_value(v) for k, v in value.items()}
        return value

    def _tuple_value(self, value):
        if isinstance(value, list):
            return tuple(self._tuple_value(v) for v in value)
        return value

    def _coord_key(self, coord):
        x, y = coord
        return f"{int(x)},{int(y)}"

    def _coord_from_key(self, key):
        x, y = str(key).split(",", 1)
        return int(x), int(y)

    def _item_state(self, item):
        return {
            "uid": item.uid,
            "cat": item.cat,
            "kind": item.kind,
            "ench": item.ench,
            "cursed": item.cursed,
            "qty": item.qty,
            "hit_plus": item.hit_plus,
            "dam_plus": item.dam_plus,
            "charges": item.charges,
            "group": item.group,
            "o_flags": sorted(item.o_flags),
            "o_label": item.o_label,
            "x": item.x,
            "y": item.y,
            "picked_up": item.picked_up,
            "protected": item.protected,
            "variant_item": item.variant_item,
        }

    def _item_from_state(self, data):
        item = Item(
            data["cat"],
            data["kind"],
            ench=data.get("ench", 0),
            cursed=data.get("cursed", False),
            qty=data.get("qty", 1),
            hit_plus=data.get("hit_plus", 0),
            dam_plus=data.get("dam_plus", 0),
            charges=data.get("charges", 0),
            known=False,
            group=data.get("group", 0),
        )
        item.uid = int(data["uid"])
        item.o_flags = set(data.get("o_flags", []))
        item.o_label = data.get("o_label")
        item.x = int(data.get("x", 0))
        item.y = int(data.get("y", 0))
        item.picked_up = bool(data.get("picked_up", False))
        item.protected = bool(data.get("protected", False))
        item.variant_item = data.get("variant_item")
        Item._nid = max(Item._nid, item.uid + 1)
        return item

    def _room_state(self, room):
        return {
            "x": room.x,
            "y": room.y,
            "w": room.w,
            "h": room.h,
            "flags": sorted(room.flags),
            "exits": [list(p) for p in getattr(room, "exits", [])],
        }

    def _room_from_state(self, data):
        room = Room(data["x"], data["y"], data["w"], data["h"], set(data.get("flags", [])))
        room.exits = [tuple(p) for p in data.get("exits", [])]
        return room

    def _monster_state(self, monster):
        return {
            "x": monster.x,
            "y": monster.y,
            "sym": monster.sym,
            "name": monster.name,
            "hp": monster.hp,
            "max_hp": monster.max_hp,
            "level": monster.level,
            "armor": monster.armor,
            "damage_expr": monster.damage_expr,
            "exp": monster.exp,
            "strength": monster.strength,
            "flags": sorted(monster.flags),
            "held": monster.held,
            "scared": monster.scared,
            "confused": monster.confused,
            "running": monster.running,
            "dest": list(monster.dest) if isinstance(monster.dest, tuple) else monster.dest,
            "turn": monster.turn,
            "mean": monster.mean,
            "target": monster.target,
            "found": monster.found,
            "vf_hit": monster.vf_hit,
            "disguise": monster.disguise,
            "pack": [self._item_state(item) for item in monster.pack],
        }

    def _monster_from_state(self, data):
        monster = Monster(
            data["x"],
            data["y"],
            data["sym"],
            data["name"],
            data["max_hp"],
            data["level"],
            data["armor"],
            data["damage_expr"],
            data["exp"],
            "",
        )
        monster.hp = data["hp"]
        monster.flags = set(data.get("flags", []))
        monster.strength = data.get("strength", 10)
        monster.held = data.get("held", 0)
        monster.scared = data.get("scared", 0)
        monster.confused = data.get("confused", 0)
        monster.running = data.get("running", False)
        dest = data.get("dest", DEST_PLAYER)
        monster.dest = tuple(dest) if isinstance(dest, list) else dest
        monster.turn = data.get("turn", True)
        monster.mean = data.get("mean", rogue_monsters.is_mean(monster.flags))
        monster.target = data.get("target", False)
        monster.found = data.get("found", False)
        monster.vf_hit = data.get("vf_hit", 0)
        monster.disguise = data.get("disguise", monster.sym)
        monster.pack = [self._item_from_state(item) for item in data.get("pack", [])]
        return monster

    def _player_state(self):
        p = self.p
        return {
            "x": p.x,
            "y": p.y,
            "hp": p.hp,
            "max_hp": p.max_hp,
            "st": p.st,
            "max_st": p.max_st,
            "level": p.level,
            "exp": p.exp,
            "gold": p.gold,
            "depth": p.depth,
            "food": p.food,
            "state": p.state,
            "ac": p.ac,
            "confused": p.confused,
            "blind": p.blind,
            "haste": p.haste,
            "see_invisible": p.see_invisible,
            "hallucinating": p.hallucinating,
            "levitating": p.levitating,
            "see_monsters": p.see_monsters,
            "no_command": p.no_command,
            "no_move": p.no_move,
            "quiet": p.quiet,
            "facing": list(p.facing),
            "can_confuse_monster": p.can_confuse_monster,
            "has_amulet": p.has_amulet,
            "inv": [self._item_state(item) for item in p.inv],
            "wpn": None if p.wpn is None else p.wpn.uid,
            "arm": None if p.arm is None else p.arm.uid,
            "ring_l": None if p.ring_l is None else p.ring_l.uid,
            "ring_r": None if p.ring_r is None else p.ring_r.uid,
        }

    def _restore_player(self, data):
        p = Player()
        for key in (
            "x", "y", "hp", "max_hp", "st", "max_st", "level", "exp", "gold", "depth",
            "food", "state", "ac", "confused", "blind", "haste", "see_invisible",
            "hallucinating", "levitating", "see_monsters", "no_command", "no_move",
            "quiet", "can_confuse_monster", "has_amulet",
        ):
            setattr(p, key, data.get(key, getattr(p, key)))
        p.facing = tuple(data.get("facing", p.facing))
        p.inv = [self._item_from_state(item) for item in data.get("inv", [])]
        by_uid = {item.uid: item for item in p.inv}
        p.wpn = by_uid.get(data.get("wpn"))
        p.arm = by_uid.get(data.get("arm"))
        p.ring_l = by_uid.get(data.get("ring_l"))
        p.ring_r = by_uid.get(data.get("ring_r"))
        p.recalc_ac()
        return p

    def _ident_state(self):
        ident = self.ident
        return {
            "easy_type_known": ident.easy_type_known,
            "pcol": ident.pcol,
            "snam": ident.snam,
            "pk": ident.pk,
            "sk": ident.sk,
            "pg": ident.pg,
            "sg": ident.sg,
            "pf": ident.pf,
            "sf": ident.sf,
            "rstones": ident.rstones,
            "rworth": ident.rworth,
            "rk": ident.rk,
            "rg": ident.rg,
            "rf": ident.rf,
            "wtypes": ident.wtypes,
            "wmades": ident.wmades,
            "wk": ident.wk,
            "wg": ident.wg,
            "wf": ident.wf,
        }

    def _restore_ident(self, data):
        ident = IdentTable(self.lang, self.scrolls)
        for key, value in data.items():
            if hasattr(ident, key):
                setattr(ident, key, value)
        ident.lang = self.lang
        ident.scrolls = self.scrolls
        return ident

    def save_state(self):
        return {
            "format": "pyxel-rogue-save-v1",
            "ui_build": UI_BUILD,
            "lang": self.lang,
            "difficulty": self.difficulty,
            "rng_state": self._json_rng_state(),
            "scrolls": self.scrolls,
            "ident": self._ident_state(),
            "player": self._player_state(),
            "tm": self.tm,
            "rooms": [self._room_state(room) for room in self.rooms],
            "gitems": [self._item_state(item) for item in self.gitems],
            "mons": [self._monster_state(monster) for monster in self.mons],
            "traps": {self._coord_key(k): v for k, v in self.traps.items()},
            "hidden_tiles": {self._coord_key(k): v for k, v in self.hidden_tiles.items()},
            "explored": [list(p) for p in sorted(self.explored)],
            "visible": [list(p) for p in sorted(self.visible)],
            "msgs": list(self.msgs),
            "msg_turns": list(self.msg_turns),
            "turn": self.turn,
            "max_depth": self.max_depth,
            "no_food": self.no_food,
            "seen_stairs": self.seen_stairs,
            "wander_timer": self.wander_timer,
            "wander_between": self.wander_between,
            "delayed_actions": self.delayed_actions.to_list(),
            "haste_half_turn": self.haste_half_turn,
            "haste_no_command_half_turn": self.haste_no_command_half_turn,
            "death_cause": self.death_cause,
            "player_name": self.player_name,
            "options": dict(self.options),
        }

    def restore_state(self, data):
        if data.get("format") != "pyxel-rogue-save-v1":
            raise rogue_save.SaveError("unsupported save data")
        existing = self.ensure_settings()
        self.settings = Settings(
            language=data.get("lang", existing.language),
            auto_pickup=existing.auto_pickup,
            palette=existing.palette,
            show_run_steps=existing.show_run_steps,
            difficulty=data.get("difficulty", existing.difficulty),
            dungeon_bgm=existing.dungeon_bgm,
        )
        self.scrolls = data.get("scrolls") or rogue_scrolls.active_scrolls(SCROLLS, self.difficulty)
        self.ident = self._restore_ident(data.get("ident", {}))
        self.p = self._restore_player(data["player"])
        self.tm = [list(row) for row in data["tm"]]
        self.rooms = [self._room_from_state(room) for room in data.get("rooms", [])]
        self.gitems = [self._item_from_state(item) for item in data.get("gitems", [])]
        self.mons = [self._monster_from_state(monster) for monster in data.get("mons", [])]
        self.traps = {self._coord_from_key(k): v for k, v in data.get("traps", {}).items()}
        self.hidden_tiles = {self._coord_from_key(k): v for k, v in data.get("hidden_tiles", {}).items()}
        self.explored = {tuple(p) for p in data.get("explored", [])}
        self.visible = {tuple(p) for p in data.get("visible", [])}
        self.msgs = list(data.get("msgs", []))
        self.msg_turns = list(data.get("msg_turns", []))
        self.turn = int(data.get("turn", 0))
        self.max_depth = int(data.get("max_depth", self.p.depth))
        self.no_food = int(data.get("no_food", 0))
        self.seen_stairs = bool(data.get("seen_stairs", False))
        self.wander_timer = int(data.get("wander_timer", 0))
        self.wander_between = int(data.get("wander_between", 0))
        self.delayed_actions = rogue_daemons.DelayedActionTable([dict(slot) for slot in data.get("delayed_actions", [])])
        self.fuses = self.delayed_actions.fuses
        self.daemons = self.delayed_actions.daemons
        self.haste_half_turn = bool(data.get("haste_half_turn", False))
        self.haste_no_command_half_turn = bool(data.get("haste_no_command_half_turn", False))
        self.death_cause = data.get("death_cause", "")
        self.player_name = data.get("player_name", self.current_player_name())
        self.options = dict(data.get("options", {"tombstone": True, "name": self.player_name}))
        self.st = ST_PLAY
        self.save_confirm_return_state = ST_PLAY
        self.mcur = self.icur = self.acur = 0
        self.cact = None
        self.dact = None
        self.fitems = []
        self.last_item_by_action = {}
        self.item_cursor_restored = False
        self.last_menu_action = None
        self.menu_cursor_restored = False
        self.message_ack_pending = False
        self.msg_toast_block = None
        self.msg_toast_rows = 0
        self.log_scroll = 0
        self.last_intent_dir = (0, 0)
        self.msg_toast_intent_history = []
        self.msg_toast_reposition_needed = True
        self.call_input = ""
        self.call_preset_idx = 0
        self.call_item = None
        self.identify_symbol_pending = False
        self.fight_kamikaze_pending = False
        self.fight_to_death = False
        self.fight_kamikaze = False
        self.fight_dir = (0, 0)
        self.fight_target = None
        self.fight_max_hit = 0
        self.repeat_state = rogue_input.RepeatState()
        self.count_input_state = rogue_input.CountInputState()
        self.dash_state = rogue_input.DashState()
        self.disc_scroll = 0
        self.turn_msg_start = len(self.msgs)
        self.throw_dir = None
        self.zap_item = None
        self.action_origin = ST_PLAY
        self.cam_x = self.cam_y = 0
        self.b_button_state = rogue_input.TapButtonState()
        self.back_button_state = rogue_input.TapButtonState()
        self.b_menu_guard = False
        self.diag_assist = False
        self.dir_pending = None
        self.dir_press_locked = None
        self.throw_anim = None
        self.turn_after_throw_anim = False
        self.last_hp_seen = None
        self.hp_damage_from = None
        self.hp_damage_turn = None
        self.result_scores = []
        self.result_entry = None
        self.result_online_submitted = False
        self.result_outcome = None
        self.clear_hallucination_visuals()
        self._restore_rng_state(data.get("rng_state"))
        self._center_cam()
        self.update_fov()
        self.init_dungeon_bgm()
        self.update_dungeon_bgm()

    def difficulty_profile(self):
        return difficulty_profile(self.difficulty)

    def apply_initial_difficulty_knowledge(self):
        if not self.difficulty_profile().easy_type_known:
            return
        self.ident.easy_type_known = True
        self.ident.pg = [None] * len(self.ident.pg)
        self.ident.sg = [None] * len(self.ident.sg)
        self.ident.rg = [None] * len(self.ident.rg)
        self.ident.wg = [None] * len(self.ident.wg)

    def result_level(self, outcome):
        return self.max_depth if outcome == "winner" else self.p.depth

    def result_flags(self, outcome):
        if outcome == "killed" and self.p.has_amulet:
            return "killed_with_amulet"
        return outcome

    def death_killer_name(self):
        # C: rip.c:killname()
        cause = (self.death_cause or "died").strip()
        special = {
            "hypothermia": "hypothermia",
            "starved to death": "starvation",
            "an arrow killed you": "arrow",
            "a poisoned dart killed you": "dart",
        }
        if cause in special:
            return special[cause]
        for prefix in ("killed by an ", "killed by a ", "killed by "):
            if cause.startswith(prefix):
                return cause[len(prefix):]
        return cause

    def death_killer_article(self, killer):
        if killer in ("hypothermia", "starvation"):
            return ""
        return "an" if killer and killer[0].lower() in "aeiou" else "a"

    def tombstone_killed_by_line(self, killer):
        lines = self.rogue_544_tombstone_lines("rogue", 0, killer, 1980)
        return lines[8]

    def rogue_544_tombstone_lines(self, name, gold, killer, year):
        # C: rip.c:rip[] and death() overlay whoami, purse, killer, article, year.
        lines = [
            "              __________",
            "             /          \\",
            "            /    REST    \\",
            "           /      IN      \\",
            "          /     PEACE      \\",
            "         /                  \\",
            "         |                  |",
            "         |                  |",
            "         |   killed by a    |",
            "         |                  |",
            "         |       1980       |",
            "        *|     *  *  *      | *",
            "________)/\\\\_//(\\/(/\\)/\\//\\/|_)_______",
        ]
        base_col = 9

        def center_col(text):
            return 28 - ((len(text) + 1) // 2) - base_col

        def put(row, col, text):
            chars = list(lines[row])
            end = col + len(text)
            if end > len(chars):
                chars.extend(" " for _ in range(end - len(chars)))
            for i, ch in enumerate(text):
                chars[col + i] = ch
            lines[row] = "".join(chars)

        put(6, center_col(name), name)
        gold_text = f"{gold} Au"
        put(7, center_col(gold_text), gold_text)
        article = self.death_killer_article(killer)
        if article == "":
            put(8, 32 - base_col, " ")
        elif article == "an":
            put(8, 33 - base_col, "n")
        put(9, center_col(killer), killer)
        put(10, 26 - base_col, f"{year:4d}")
        return lines

    def rogue2_tombstone_killer_line(self, killer):
        special = {
            "hypothermia": "寒さにより死す",
            "starvation": "飢えにより死す",
            "arrow": "矢により死す",
            "dart": "毒矢により死す",
        }
        if killer in special:
            return special[killer]
        subject = TextCatalog.monster(LANG_JA, killer)
        if subject == killer:
            subject = TextCatalog.bolt(LANG_JA, killer)
        return f"{subject}と戦いて死す"

    def tombstone_lines(self, name, gold, killer, year):
        if self.lang != LANG_JA:
            return self.rogue_544_tombstone_lines(name, gold, killer, year)
        return [
            "              __________",
            "             /          \\",
            "            /  安らかに  \\",
            "           /            \\",
            "          /              \\",
            "         /                  \\",
            f"         |      {name[:8]:<8}    |",
            f"         |   {gold}個の金塊   |",
            f"         | {self.rogue2_tombstone_killer_line(killer)} |",
            "         |                  |",
            f"         |       {year:4d}       |",
            "        *|     *  *  *      | *",
            "________)/\\\\_//(\\/(/\\)/\\//\\/|_)_______",
        ]

    def rogue2_tombstone_killer_lines(self, killer):
        line = self.rogue2_tombstone_killer_line(killer)
        suffix = "戦いて死す"
        if line.endswith(suffix) and self.ui_text_width(line) > FONT_ASCII_W * 18:
            return [line[: -len(suffix)], suffix]
        return [line]

    def japanese_tombstone_shell_lines(self):
        return [
            "        __________",
            "       /          \\",
            "      /            \\",
            "     /              \\",
            "    /                \\",
            "   /                  \\",
            "   |                  |",
            "   |                  |",
            "   |                  |",
            "   |                  |",
            "   |                  |",
            "  *|     *  *  *      | *",
            "__)/\\\\_//(\\/(/\\)/\\//\\/|_)_______",
        ]

    def txt_centered(self, cx, y, s, col):
        self.txt(cx - self.ui_text_width(s) // 2, y, s, col)

    def draw_japanese_tombstone(self, bx, by, bw, name, gold, killer, year):
        # Keep the Rogue 5.4.4 rip.c shell ASCII-only, then overlay CJK text.
        cx = bx + bw // 2
        y0 = by + 28
        line_h = 10
        shell = self.japanese_tombstone_shell_lines()
        top_left_cols = len(shell[0]) - len(shell[0].lstrip(" "))
        shell_x = cx - (top_left_cols + 5) * FONT_ASCII_W
        for i, line in enumerate(shell):
            self.txt(shell_x, y0 + i * line_h, line, UI_TEXT_COL)
        self.txt_centered(cx, y0 + 2 * line_h, "安らかに", UI_TEXT_COL)
        self.txt_centered(cx, y0 + 3 * line_h, "眠れ", UI_TEXT_COL)
        self.txt_centered(cx, y0 + 6 * line_h, name[:8], UI_TEXT_COL)
        self.txt_centered(cx, y0 + 7 * line_h, f"{gold}個の金塊", UI_TEXT_COL)
        killer_lines = self.rogue2_tombstone_killer_lines(killer)
        for i, line in enumerate(killer_lines[:2]):
            self.txt_centered(cx, y0 + (8 + i) * line_h, line, UI_TEXT_COL)
        self.txt_centered(cx, y0 + 10 * line_h, f"{year:4d}", UI_TEXT_COL)
        return y0 + len(shell) * line_h + 10

    def result_killer(self, outcome):
        if outcome in ("quit", "winner"):
            return ""
        return self.death_killer_name()

    def total_winner_item_data(self, it):
        data = it.data
        out = {
            "cat": it.cat,
            "qty": it.qty,
            "name": data.get("name"),
            "base_worth": data.get("worth", 0),
            "known": getattr(it, "known", False),
            "ench": getattr(it, "ench", 0),
            "hit_plus": getattr(it, "hit_plus", 0),
            "dam_plus": getattr(it, "dam_plus", 0),
            "charges": getattr(it, "charges", 0),
            "base_ac": data.get("ac", 10),
        }
        if it.cat == CAT_POT:
            out["type_known"] = self.ident.pk[it.kind]
        elif it.cat == CAT_SCR:
            out["type_known"] = self.ident.sk[it.kind]
        elif it.cat == CAT_RING:
            out["base_worth"] = self.ident.rworth[it.kind]
        return out

    def total_winner_score(self):
        # C: rip.c:total_winner()
        return total_winner_score(self.p.gold, [self.total_winner_item_data(it) for it in self.p.inv])

    def enter_result_state(self, outcome):
        self.result_outcome = outcome
        self.result_entry = build_score_entry(
            score=self.total_winner_score() if outcome == "winner" else 0,
            result_flags=self.result_flags(outcome),
            level=self.result_level(outcome),
            killer=self.result_killer(outcome),
            player_name=self.current_score_player_name(),
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            gold=self.p.gold,
            difficulty=self.difficulty,
            variant=variant_scoreboard_key(),
        )
        save_score_entry(self.result_entry)
        self.result_online_submitted = False
        self.result_scores = get_top_scores(load_score_entries(), limit=10, difficulty=self.difficulty)
        if outcome == "winner":
            self.st = ST_WIN
            self.play_result_bgm()
        elif outcome == "quit":
            self.st = ST_QUIT
            self.play_result_bgm()
        else:
            self.capture_death_snapshot()
            self.st = ST_DEAD
            self.play_death_sfx()

    def capture_death_snapshot(self):
        self.death_frame = getattr(pyxel, "frame_count", 0)
        self.death_intro_done = False
        self.death_minimap_tiles = self.death_minimap_snapshot(DEATH_MINIMAP_W, DEATH_MINIMAP_H)

    def death_intro_elapsed(self):
        if getattr(self, "death_intro_done", False):
            return DEATH_INTRO_FRAMES
        return max(0, getattr(pyxel, "frame_count", 0) - getattr(self, "death_frame", 0))

    def death_intro_accepts_input(self):
        return self.death_intro_elapsed() >= DEATH_INPUT_LOCK_FRAMES

    def death_intro_finished(self):
        return getattr(self, "death_intro_done", False) or self.death_intro_elapsed() >= DEATH_INTRO_FRAMES

    def finish_death_intro(self):
        if not getattr(self, "death_intro_done", False):
            now = getattr(pyxel, "frame_count", 0)
            natural_start = getattr(self, "death_frame", now) + DEATH_INTRO_FRAMES
            self.death_intro_done_frame = natural_start if now >= natural_start else now
        self.death_intro_done = True

    def death_log_elapsed(self):
        if getattr(self, "death_intro_done", False):
            start_frame = getattr(self, "death_intro_done_frame", None)
            if start_frame is None:
                return max(0, getattr(pyxel, "frame_count", 0) - getattr(self, "death_frame", 0) - DEATH_INTRO_FRAMES)
            return max(0, getattr(pyxel, "frame_count", 0) - start_frame)
        return max(0, getattr(pyxel, "frame_count", 0) - getattr(self, "death_frame", 0) - DEATH_INTRO_FRAMES)

    def death_minimap_snapshot(self, width, height):
        half_w = width // 2
        half_h = height // 2
        start_dx = -half_w + (0 if width % 2 else 1)
        return [
            [self.death_minimap_cell(self.p.x + dx, self.p.y + dy) for dx in range(start_dx, start_dx + width)]
            for dy in range(-half_h, half_h + 1)
        ]

    def death_minimap_cell(self, mx, my):
        if not in_map(mx, my):
            return (" ", 0)
        if (mx, my) == (self.p.x, self.p.y):
            return ("@", UI_TEXT_COL)
        if self.p.blind > 0:
            return (" ", 0)
        vis = (mx, my) in self.visible
        exp = (mx, my) in self.explored
        if vis:
            mo = self.mon_at(mx, my)
            if mo and (self.can_see_monster(mo) or self.can_detect_monsters()):
                sym = self.visible_monster_sym(mo) if self.can_see_monster(mo) else self.detected_monster_sym(mo)
                return (sym, self.monster_color(mo.sym))
            gi = self.gi_at(mx, my)
            if gi:
                return (self.visible_item_sym(gi), self.item_color(gi.cat))
            tile = self.tm[my][mx]
            return (self.visible_tile_sym(mx, my, tile), self.visible_tile_color(tile))
        if exp:
            tile = self.tm[my][mx]
            ch, _col = TILE_CH.get(tile, (" ", 0))
            if ch != " " and self.should_draw_memory_tile(mx, my, tile):
                col = self.memory_tile_color(tile)
            else:
                ch, col = " ", 0
            gi = self.gi_at(mx, my)
            if gi:
                return (gi.sym, self.item_color(gi.cat))
            return (ch, col)
        if self.can_detect_monsters():
            mo = self.mon_at(mx, my)
            if mo:
                return (self.detected_monster_sym(mo), self.monster_color(mo.sym))
        return (" ", 0)

    def death_display_gold(self):
        # C: rip.c:death() reduces purse before tombstone() and score().
        entry = getattr(self, "result_entry", None)
        if entry and entry.get("result_flags") in ("killed", "killed_with_amulet"):
            return int(entry.get("score", self.p.gold))
        return self.p.gold

    def set_lang(self, lang, persist=False):
        self.lang = lang if lang in (LANG_EN, LANG_JA) else LANG_EN
        if hasattr(self, "ident"):
            self.ident.set_lang(self.lang)
        if persist:
            self.persist_settings()

    def toggle_lang(self):
        self.set_lang(LANG_JA if self.lang == LANG_EN else LANG_EN, persist=True)
        self.msg("pyxel.language_japanese" if self.lang == LANG_JA else "pyxel.language_english")

    def toggle_online_language(self):
        self.set_lang(LANG_JA if self.lang == LANG_EN else LANG_EN, persist=True)

    def toggle_auto_pickup(self):
        self.auto_pickup = not self.auto_pickup
        self.persist_settings()

    def toggle_dungeon_bgm(self):
        settings = self.ensure_settings()
        settings.dungeon_bgm = not settings.dungeon_bgm
        self.persist_settings()
        self.update_dungeon_bgm()

    @property
    def difficulty(self):
        fixed = variant_fixed_difficulty()
        if fixed:
            return fixed
        return self.ensure_settings().difficulty

    @difficulty.setter
    def difficulty(self, value):
        fixed = variant_fixed_difficulty()
        if fixed:
            self.ensure_settings().difficulty = fixed
            return
        self.ensure_settings().difficulty = difficulty_profile(value).id

    def online_language_toggle_pressed(self):
        if self.key_lower(pyxel.KEY_L):
            return True
        if self.kp_back():
            self.back_used = True
            return True
        return False

    def descend(self, *, play_stairs_sfx=True):
        # C: new_level.c:new_level() clears ISHELD before generating the level.
        self.p.held_by = None
        old_depth = self.p.depth
        self.p.depth += 1
        if play_stairs_sfx and old_depth > 0:
            self.play_sfx_immediate(rogue_sfx.SFX_STAIRS, stop_bgm=True)
        self.max_depth = max(getattr(self, "max_depth", 0), self.p.depth)
        self.mons=[]; self.gitems=[]; self.traps={}; self.hidden_tiles={}
        def populate_room(tm, rooms, room):
            self.tm = tm
            self.rooms = rooms
            self._populate_initial_room(room)
        self.tm, self.rooms, level_hidden_tiles = DGen.gen(
            self.p.depth, with_hidden=True, room_callback=populate_room
        )
        self.hidden_tiles.update(level_hidden_tiles)
        self.no_food = rogue_things.no_food_after_new_level(getattr(self, "no_food", 0))
        usable_rooms = self.usable_rooms()
        self.visible=set(); self.explored=set()
        self.seen_stairs = False
        self.clear_hallucination_visuals()
        self.wander_timer=self.fuses.remaining("swander")
        self._spawn_items(); self._spawn_amulet()
        self._spawn_traps()
        stair_pos = self.find_floor_pos(
            None,
            monst=False,
            occupied={(i.x,i.y) for i in self.gitems},
        )
        if stair_pos is None:
            stair_pos = self.random_room_tile(RNG.choice(usable_rooms), WALKABLE)
        sx,sy=stair_pos
        self.tm[sy][sx]=T_STAIR
        hero_pos = self.find_floor_pos(
            None,
            monst=True,
            occupied={(m.x,m.y) for m in self.mons if m.alive},
        )
        if hero_pos is None:
            hero_pos = self.random_room_tile(RNG.choice(usable_rooms), WALKABLE)
        self.p.x,self.p.y = hero_pos
        self._center_cam(); self.update_fov()
        if self.p.hallucinating > 0:
            self.run_visuals()
        self.expire_visible_msg_toast()
        if hasattr(self, "dungeon_bgm"):
            self.update_dungeon_bgm()

    def usable_rooms(self):
        return [room for room in self.rooms if room.usable] or self.rooms

    def room_tiles(self, room, tiles):
        return [
            (x,y)
            for y in range(room.y+1,room.y+room.h-1)
            for x in range(room.x+1,room.x+room.w-1)
            if 0<=x<MAP_W and 0<=y<MAP_H and self.tm[y][x] in tiles
        ]

    def random_room_tile(self, room, tiles):
        cands=self.room_tiles(room, tiles)
        if cands:
            return RNG.choice(cands)
        return room.inner()

    def source_rnd_room(self):
        # C: new_level.c:rnd_room() / rooms.c:find_floor().
        rooms = self.rooms or []
        usable = [room for room in rooms if room.usable]
        if not rooms:
            return None
        if not usable:
            return rooms[0]
        while True:
            room = rooms[RNG.rnd(len(rooms))]
            if room.usable:
                return room

    def source_rnd_pos(self, room):
        # C: rooms.c:rnd_pos().
        if room.w <= 2 or room.h <= 2:
            return room.inner()
        return room.x + RNG.rnd(room.w - 2) + 1, room.y + RNG.rnd(room.h - 2) + 1

    def find_floor_has_candidate(self, room=None, monst=False, avoid=(), occupied=()):
        rooms = [room] if room is not None else self.usable_rooms()
        avoid = set(avoid or ())
        occupied = set(occupied or ())
        for test_room in rooms:
            if test_room is None:
                continue
            for y in range(test_room.y + 1, test_room.y + max(1, test_room.h - 1)):
                for x in range(test_room.x + 1, test_room.x + max(1, test_room.w - 1)):
                    if not in_map(x, y) or (x, y) in avoid:
                        continue
                    tile = self.tm[y][x]
                    if monst:
                        if (x, y) not in occupied and rogue_io.step_ok_tile(tile, TILE_CH):
                            return True
                    else:
                        compchar = T_CORR if test_room.is_maze else T_FLOOR
                        if tile == compchar and (x, y) not in occupied:
                            return True
        return False

    def find_floor_pos(self, room=None, limit=0, monst=False, avoid=(), occupied=()):
        # C: rooms.c:find_floor().
        pickroom = room is None
        avoid = set(avoid or ())
        occupied = set(occupied or ())
        count = limit
        if not limit and not self.find_floor_has_candidate(room, monst, avoid, occupied):
            return None
        while True:
            if limit:
                if count == 0:
                    return None
                count -= 1
            test_room = self.source_rnd_room() if pickroom else room
            if test_room is None:
                return None
            x, y = self.source_rnd_pos(test_room)
            if not in_map(x, y) or (x, y) in avoid:
                continue
            tile = self.tm[y][x]
            if monst:
                if (x, y) not in occupied and rogue_io.step_ok_tile(tile, TILE_CH):
                    return x, y
            else:
                compchar = T_CORR if test_room.is_maze else T_FLOOR
                if tile == compchar and (x, y) not in occupied:
                    return x, y

    def _center_cam(self):
        max_x = max(0, MAP_W - ZV_COLS)
        min_y = PLAY_Y_MIN
        max_y = max(min_y, PLAY_Y_MAX - ZV_ROWS + 1)
        self.cam_x = max(0, min(self.p.x - ZV_COLS//2, max_x))
        self.cam_y = max(min_y, min(self.p.y - ZV_ROWS//2, max_y))

    def _spawn_mons(self):
        # C: rooms.c:do_rooms()
        d=self.p.depth
        for rm in self.usable_rooms():
            self._spawn_mon_for_room(rm, d)

    def _populate_initial_room(self, room):
        # C: rooms.c:do_rooms() places room gold and monster before do_passages().
        self._spawn_room_gold_for_room(room)
        self._spawn_mon_for_room(room, self.p.depth)

    def _spawn_mon_for_room(self, room, depth):
        if not room.usable:
            return
        if not rogue_dungeon.should_place_room_monster(RNG, self.room_has_gold(room)):
            return
        pos = self.find_floor_pos(
            room,
            monst=True,
            avoid={(self.p.x,self.p.y)},
            occupied={(m.x,m.y) for m in self.mons if m.alive},
        )
        if pos is None:
            return
        mx,my=pos
        e=self.random_monster_spec(depth)
        monster=self.new_monster_from_spec(mx,my,e)
        self.give_pack(monster)
        self.mons.append(monster)

    def room_has_gold(self, room):
        return any(
            item.cat == CAT_GOLD
            and room.x <= item.x < room.x + room.w
            and room.y <= item.y < room.y + room.h
            for item in self.gitems
        )

    def spawn_wanderer(self):
        # C: monsters.c:wanderer()
        pos = self.wanderer_floor_pos()
        if pos is None:
            return False
        x,y=pos
        spec=self.monster_spec_for_sym(rogue_monsters.randmonster(self.p.depth, RNG.rnd, wander=True))
        monster=self.new_monster_from_spec(x,y,spec)
        self.mons.append(monster)
        self.runto(monster)
        return True

    def random_monster_spec(self, depth):
        return self.monster_spec_for_sym(rogue_monsters.randmonster(depth, RNG.rnd, wander=False))

    def new_monster_from_spec(self,x,y,spec,depth=None):
        # C: monsters.c:new_monster()
        if depth is None:
            depth=self.p.depth
        level,hp,armor,exp=rogue_monsters.new_monster_stats(
            spec.level,spec.armor,spec.exp,depth,AMULET_LEVEL,RNG.roll
        )
        monster=Monster(
            x, y, spec.sym, spec.name, hp,
            level, armor, spec.damage, exp, spec.flags
        )
        rogue_monsters.apply_deep_haste(monster, depth)
        self.set_monster_disguise(monster,depth=depth)
        if rogue_rings.is_wearing(self.p, rogue_rings.R_AGGR):
            self.runto(monster)
        return monster

    def set_monster_disguise(self,m,depth=None):
        m.disguise = rogue_monsters.initial_disguise(m.sym, lambda: self.random_thing_sym(depth))

    def give_pack(self,m,depth=None):
        # C: monsters.c:give_pack()
        spec=self.monster_spec_for_sym(m.sym)
        depth = self.p.depth if depth is None else depth
        if not spec:
            return
        if rogue_monsters.should_give_pack(depth, getattr(self, "max_depth", self.p.depth), spec.carry, RNG.rnd):
            m.pack.append(self.make_game_item(depth))

    def make_game_item(self, depth):
        # C: things.c:new_thing(); new_level.c tracks no_food globally.
        before = getattr(self, "no_food", 0)
        try:
            item = make_item(depth, before, self.scrolls)
        except TypeError:
            item = make_item(depth)
        self.no_food = rogue_things.no_food_after_new_thing(item.cat, before)
        return item

    def wanderer_floor_candidates(self):
        player_room=self.room_containing(self.p.x,self.p.y)
        return rogue_dungeon.find_floor_monster_candidates(
            self.tm,
            self.room_at,
            {(m.x,m.y) for m in self.mons if m.alive},
            (self.p.x,self.p.y),
            TILE_CH,
            excluded_room=player_room,
        )

    def wanderer_floor_pos(self):
        # C: monsters.c:wanderer() loops until roomin(cp) != proom.
        player_room = self.room_containing(self.p.x, self.p.y)
        occupied = {(m.x, m.y) for m in self.mons if m.alive}
        if not self.wanderer_floor_candidates():
            return None
        while True:
            pos = self.find_floor_pos(None, monst=True, occupied=occupied)
            if pos is None:
                return None
            if self.room_containing(pos[0], pos[1]) is not player_room:
                return pos

    def _spawn_items(self):
        # C: new_level.c:put_things()
        d=self.p.depth
        if not rogue_dungeon.should_put_things(self.p.has_amulet, d, getattr(self, "max_depth", d)):
            return
        if rogue_dungeon.should_place_treasure_room(RNG):
            self._spawn_treasure_room()
        for _ in range(rogue_dungeon.MAXOBJ):
            if not rogue_dungeon.should_put_thing_attempt(RNG):
                continue
            it=self.make_game_item(d)
            pos = self.find_floor_pos(
                None,
                monst=False,
                avoid={(self.p.x,self.p.y)},
                occupied={(i.x,i.y) for i in self.gitems},
            )
            if pos is not None:
                ix,iy=pos
                it.x,it.y=ix,iy; self.gitems.append(it)

    def _spawn_room_gold(self):
        # C: rooms.c:do_rooms()
        for rm in self.usable_rooms():
            self._spawn_room_gold_for_room(rm)

    def _spawn_room_gold_for_room(self, room):
        # C: rooms.c:do_rooms()
        if not room.usable:
            return
        d=self.p.depth
        if not rogue_dungeon.should_place_room_gold(RNG, self.p.has_amulet, d, getattr(self, "max_depth", d)):
            return
        qty=goldcalc(d)
        pos = self.find_floor_pos(
            room,
            monst=False,
            avoid={(self.p.x,self.p.y)},
            occupied={(i.x,i.y) for i in self.gitems},
        )
        if pos is not None:
            ix,iy=pos
            g=Item(CAT_GOLD,0); g.qty=qty; g.x,g.y=ix,iy
            self.gitems.append(g)

    def _spawn_treasure_room(self, room=None):
        # Rogue 5.4.4 new_level.c:treas_room().
        rooms=self.usable_rooms()
        room = room or RNG.choice(rooms)
        inner_area=max(0,(room.w-2)*(room.h-2))
        treasure_count, monster_count = rogue_dungeon.treasure_room_counts(inner_area,RNG)
        for _ in range(treasure_count):
            pos = self.find_floor_pos(
                room,
                limit=2 * rogue_dungeon.MAXTRIES,
                monst=False,
                avoid={(self.p.x,self.p.y)},
                occupied={(i.x,i.y) for i in self.gitems},
            )
            if pos is not None:
                ix,iy=pos
                it=self.make_game_item(self.p.depth); it.x,it.y=ix,iy; self.gitems.append(it)
        monster_depth=self.p.depth+1
        for _ in range(monster_count):
            pos = self.find_floor_pos(
                room,
                limit=rogue_dungeon.MAXTRIES,
                monst=True,
                avoid={(self.p.x,self.p.y)},
                occupied={(m.x,m.y) for m in self.mons if m.alive},
            )
            if pos is None:
                continue
            mx,my=pos
            spec=self.monster_spec_for_sym(rogue_monsters.randmonster(monster_depth, RNG.rnd, wander=False))
            monster=self.new_monster_from_spec(mx,my,spec,depth=monster_depth)
            rogue_monsters.force_mean(monster)
            self.give_pack(monster,depth=monster_depth)
            self.mons.append(monster)

    def _spawn_amulet(self):
        # Rogue 5.4.4 new_level.c: level >= AMULETLEVEL && !amulet.
        if is_nyandor_variant():
            if self.p.depth != NYANDOR_TARGET_DEPTH or self.p.has_amulet:
                return
        elif self.p.depth < AMULET_LEVEL or self.p.has_amulet:
            return
        if any(item.cat==CAT_AMULET for item in self.p.inv + self.gitems):
            return
        pos = self.find_floor_pos(
            None,
            monst=False,
            avoid={(self.p.x,self.p.y)},
            occupied={(i.x,i.y) for i in self.gitems},
        )
        if pos is None:
            return
        x,y=pos
        amulet=Item(CAT_AMULET,0)
        if is_nyandor_variant():
            amulet.variant_item = "nyandor_cat"
        amulet.x,amulet.y=x,y
        self.gitems.append(amulet)

    def _secret_chance(self, denom):
        # Rogue 5.4.4 passages.c: rnd(10)+1 < level, then a per-feature rnd().
        return rogue_search.secret_feature_hidden(self.p.depth, RNG, denom)

    def _hide_secret_features(self):
        for y in range(MAP_H):
            for x in range(MAP_W):
                tile=self.tm[y][x]
                if tile==T_DOOR and self._secret_chance(5):
                    self.hidden_tiles[(x,y)]=T_DOOR
                    self.tm[y][x]=self._hidden_door_wall_tile(x,y)
                elif tile==T_CORR and self._secret_chance(40):
                    self.hidden_tiles[(x,y)]=T_CORR
                    self.tm[y][x]=T_VOID

    def _hidden_door_wall_tile(self,x,y):
        left = 0<=x-1<MAP_W and self.tm[y][x-1] in (T_FLOOR,T_CORR,T_STAIR)
        right = 0<=x+1<MAP_W and self.tm[y][x+1] in (T_FLOOR,T_CORR,T_STAIR)
        return T_VWALL if left or right else T_HWALL

    def _spawn_traps(self):
        # Rogue 5.4.4 new_level.c: if rnd(10) < level, place rnd(level/4)+1 traps.
        n=rogue_dungeon.trap_count_for_level(self.p.depth, RNG)
        if n <= 0:
            return
        for _ in range(n):
            while True:
                pos = self.find_floor_pos(
                    None,
                    monst=False,
                    occupied={(i.x,i.y) for i in self.gitems},
                )
                if pos is None:
                    return
                x,y=pos
                if self.tm[y][x] == T_FLOOR:
                    self.traps[(x,y)]=rogue_dungeon.trap_kind(RNG)
                    break

    # ---------- Helpers ----------
    def mon_at(self,x,y):
        for m in self.mons:
            if m.alive and m.x==x and m.y==y: return m
        return None
    def gi_at(self,x,y):
        for i in self.gitems:
            if i.x==x and i.y==y: return i
        return None
    def trap_name(self,kind):
        if isinstance(kind,int):
            kind=TRAPS[kind]["name"] if 0<=kind<len(TRAPS) else "trap"
        return TextCatalog.trap(self.lang,kind)
    def visible_trap_at(self,x,y):
        if not (0<=x<MAP_W and 0<=y<MAP_H):
            return None
        if self.tm[y][x]!=T_TRAP:
            return None
        return self.traps.get((x,y),0)
    def reveal_hidden_at(self,x,y):
        tile=self.hidden_tiles.pop((x,y),None)
        if tile is None:
            return False
        self.tm[y][x]=tile
        self.explored.add((x,y))
        return True
    def reveal_trap_at(self,x,y):
        if (x,y) not in self.traps:
            return False
        self.tm[y][x]=T_TRAP
        self.explored.add((x,y))
        return True
    def levit_check(self):
        if self.p.levitating <= 0:
            return False
        self.msg("command.you_cant_you_re_floating_off_the_ground")
        return True
    def walkable(self,x,y):
        # C: move.c:turn_ok()
        return in_play_area(x,y) and self.tm[y][x] in WALKABLE
    def tile_has_pass_flag(self,x,y):
        # Rogue 5.4.4 stores terrain char and F_PASS separately. Maze cells can
        # keep F_PASS even when p_ch becomes STAIRS or restored FLOOR.
        if not in_play_area(x,y):
            return False
        tile = self.tm[y][x]
        return tile == T_CORR or (
            tile in (T_FLOOR, T_STAIR) and getattr(self.room_containing(x,y), "is_maze", False)
        )
    def diag_ok(self,sx,sy,ex,ey):
        # C: chase.c:diag_ok()
        return (
            rogue_chase.diag_ok(
                sx,
                sy,
                ex,
                ey,
                in_play_area,
                lambda x, y: in_play_area(x, y) and self.tm[y][x] in WALKABLE,
            )
            and self.tm[ey][ex] in WALKABLE
        )
    def room_at(self,x,y):
        for r in self.rooms:
            if r.x<x<r.x+r.w-1 and r.y<y<r.y+r.h-1: return r
        return None
    def room_containing(self,x,y):
        # C: chase.c:roomin()
        return rogue_chase.roomin(x, y, self.rooms)
    def is_passage_number_cell(self,x,y):
        # C: passages.c:numpass() numbers F_PASS cells and door/secret-door exits.
        if not (0<=x<MAP_W and 0<=y<MAP_H):
            return False
        if self.tile_has_pass_flag(x, y):
            return True
        return rogue_passages.is_number_cell(
            self.tm[y][x], self.hidden_tiles.get((x,y)), T_CORR, T_DOOR
        )
    def is_maze_passage_floor(self,x,y):
        # C: F_PASS remains set if chase.c:do_chase() restores a maze PASSAGE char to FLOOR.
        return self.tm[y][x] == T_FLOOR and getattr(self.room_containing(x, y), "is_maze", False)
    def is_passage_exit_cell(self,x,y):
        # C: passages.c:numpass() records DOOR and non-F_REAL '|'/'-' as exits.
        return 0<=x<MAP_W and 0<=y<MAP_H and rogue_passages.is_exit_cell(
            self.tm[y][x], self.hidden_tiles.get((x,y)), T_DOOR
        )
    def passage_component(self,x,y):
        # C: passages.c:numpass() / chase.c:roomin() passage identity.
        component = rogue_passages.passage_component(
            (x,y),
            lambda px, py: 0<=px<MAP_W and 0<=py<MAP_H,
            self.is_passage_number_cell,
        )
        if component is None:
            return None
        return ("passage", component)
    def room_for_ai(self,x,y,actor=False):
        if not (0<=x<MAP_W and 0<=y<MAP_H):
            return None
        tile=self.tm[y][x]
        if self.tile_has_pass_flag(x, y) or (actor and tile==T_DOOR):
            return self.passage_component(x,y) or "corridor"
        if tile==T_DOOR:
            return self.room_near_door(x,y) or "corridor"
        return self.room_containing(x,y)
    def room_near_door(self,x,y):
        for dx,dy in((-1,0),(1,0),(0,-1),(0,1)):
            r=self.room_at(x+dx,y+dy) or self.room_containing(x+dx,y+dy)
            if r: return r
        return None
    def room_exits(self,room):
        exits=list(getattr(room,"exits",[]))
        for x in range(room.x,room.x+room.w):
            for y in (room.y,room.y+room.h-1):
                if self.is_passage_exit_cell(x,y):
                    exits.append((x,y))
        for y in range(room.y,room.y+room.h):
            for x in (room.x,room.x+room.w-1):
                if self.is_passage_exit_cell(x,y):
                    exits.append((x,y))
        return list(dict.fromkeys(exits))
    def passage_exits(self,passage):
        if not (isinstance(passage, tuple) and len(passage) == 2 and passage[0] == "passage"):
            return []
        roots = []
        for room in self.rooms:
            roots.extend(getattr(room, "exits", []))
        return rogue_passages.passage_exits(
            passage[1],
            self.is_passage_exit_cell,
            roots,
            lambda px, py: 0<=px<MAP_W and 0<=py<MAP_H,
            self.is_passage_number_cell,
        )
    def dist2(self,a,b):
        # C: chase.c:dist()
        return rogue_chase.dist_points(a, b)
    def same_ai_room(self,a,b):
        return a is not None and a==b
    def _append_msg(self, text):
        if len(getattr(self, "msg_turns", [])) != len(self.msgs):
            self.msg_turns = [self.turn] * len(self.msgs)
        text = self.normalize_log_message(text)
        self.msgs.append(text)
        self.msg_turns.append(self.turn)
        if getattr(self, "msg_toast_block", None) is None or getattr(self, "msg_toast_reposition_needed", False):
            self.refresh_msg_toast_block()
        if len(self.msgs) > 100:
            drop = len(self.msgs) - 100
            self.msgs = self.msgs[drop:]
            self.msg_turns = self.msg_turns[drop:]
            self.turn_msg_start = max(0, self.turn_msg_start - drop)

    def normalize_log_message(self, text):
        text = str(text)
        if text.startswith("You "):
            text = "you " + text[4:]
        if text.endswith("。"):
            text = text[:-1]
        elif text.endswith(".") and not text.endswith("..."):
            text = text[:-1]
        return text

    def message_display_text(self, text):
        text = str(text)
        # Rogue 5.4.4 io.c:endmsg() uppercases message starts except pack letters.
        if text[:1].islower() and not (len(text) > 1 and text[1] == ")"):
            text = text[0].upper() + text[1:]
        return text

    def refresh_msg_toast_block(self):
        home = msg_toast_home_block(self.p.x, self.p.y)
        self.msg_toast_block = pick_msg_toast_block(home, getattr(self, "last_intent_dir", (0, 0)))
        self.msg_toast_reposition_needed = False

    def set_last_intent_dir(self, dx, dy):
        if dx or dy:
            step = (_sign(dx), _sign(dy))
            history = list(getattr(self, "msg_toast_intent_history", []))
            history.append(step)
            history = history[-MSG_TOAST_INTENT_HISTORY:]
            sx = sum(x for x, _ in history)
            sy = sum(y for _, y in history)
            if sx or sy:
                self.last_intent_dir = _dominant_msg_toast_dir(sx, sy)
            else:
                self.last_intent_dir = step
            self.msg_toast_intent_history = history
            self.msg_toast_reposition_needed = True

    def msg_toast_block_with_margin_contains_player(self, margin=2):
        block = getattr(self, "msg_toast_block", None)
        if block is None or not getattr(self, "msgs", None):
            return False
        col, row = block
        left = MSG_TOAST_GRID_COL_EDGES[col] - margin
        right = MSG_TOAST_GRID_COL_EDGES[col + 1] - 1 + margin
        top = PLAY_Y_MIN + MSG_TOAST_GRID_ROW_EDGES[row] - margin
        bottom = PLAY_Y_MIN + MSG_TOAST_GRID_ROW_EDGES[row + 1] - 1 + margin
        return left <= self.p.x <= right and top <= self.p.y <= bottom

    def move_msg_toast_if_player_enters_margin(self):
        if self.msg_toast_block_with_margin_contains_player():
            current = self.msg_toast_block
            home = msg_toast_home_block(self.p.x, self.p.y)
            self.msg_toast_block = pick_msg_toast_block(
                home,
                getattr(self, "last_intent_dir", (0, 0)),
                avoid=(current,),
            )
            self.msg_toast_reposition_needed = False

    def msg(self,t,**kw):
        self._append_msg(TextCatalog.msg(self.lang,t,**kw))

    def msg_text(self,t):
        self._append_msg(t)

    def msg_important(self,t,**kw):
        self.msg(t, **kw)
        self.message_ack_pending = True

    def msg_bad(self,t,**kw):
        self.request_sfx(rogue_sfx.SFX_ERROR)
        self.msg_important(t, **kw)

    def msg_alarm(self,t,**kw):
        self.request_sfx(rogue_sfx.SFX_ALARM)
        self.msg_important(t, **kw)

    def combat_monster_name(self,m,upper=False, article_for_something=False):
        def random_monster_name():
            spec = self.monster_spec_for_sym(chr(ord("A") + RNG.rnd(26)))
            return TextCatalog.monster(self.lang, spec.name if spec else m.name)
        name = rogue_fight.set_mname(
            self.monster_is_seen(m),
            self.can_detect_monsters(),
            self.p.hallucinating > 0,
            TextCatalog.monster(self.lang, m.name),
            random_monster_name,
            "something" if self.lang == LANG_EN else "何者か",
        )
        if self.lang==LANG_EN and (name != "something" or article_for_something):
            name=f"the {name}"
        if self.lang==LANG_EN:
            name=rogue_fight.prname(name, upper)
        return name

    def combat_message(self,keys,**kw):
        return TextCatalog.msg(self.lang,rogue_fight.combat_message_key(keys, RNG.rnd),**kw)

    # Rogue 5.4.4 fight.c:hit()/miss() message families.
    def player_hit_message(self,target):
        return self.combat_message(PLAYER_HIT_MESSAGE_KEYS,target=target)

    def player_miss_message(self,target):
        return self.combat_message(PLAYER_MISS_MESSAGE_KEYS,target=target)

    def monster_hit_message(self,subject):
        return self.combat_message(MONSTER_HIT_MESSAGE_KEYS,subject=subject)

    def monster_miss_message(self,subject):
        return self.combat_message(MONSTER_MISS_MESSAGE_KEYS,subject=subject)

    def defeated_message(self,target):
        key = rogue_fight.killed_message_key(pr=True, has_hit=False, terse=False)
        return TextCatalog.msg(self.lang,key,target=target)

    def thrown_hit_message(self,it,item,target):
        key = rogue_fight.thrown_message_key(it.cat, hit=True)
        return TextCatalog.msg(self.lang,key,item=item,target=target)

    def thrown_miss_message(self,it,item,target):
        key = rogue_fight.thrown_message_key(it.cat, hit=False)
        return TextCatalog.msg(self.lang,key,item=item,target=target)

    # ---------- Camera ----------
    def update_cam(self):
        max_x = max(0, MAP_W - ZV_COLS)
        min_y = PLAY_Y_MIN
        max_y = max(min_y, PLAY_Y_MAX - ZV_ROWS + 1)
        if max_x == 0:
            self.cam_x = 0
        if max_y == min_y:
            self.cam_y = min_y
        rx = self.p.x - self.cam_x
        ry = self.p.y - self.cam_y
        if max_x and rx < DEAD_ZONE_X:
            self.cam_x = max(0, self.p.x - DEAD_ZONE_X)
        elif max_x and rx >= ZV_COLS - DEAD_ZONE_X:
            self.cam_x = min(max_x, self.p.x - ZV_COLS + DEAD_ZONE_X + 1)
        if max_y and ry < DEAD_ZONE_Y:
            self.cam_y = max(min_y, self.p.y - DEAD_ZONE_Y)
        elif max_y and ry >= ZV_ROWS - DEAD_ZONE_Y:
            self.cam_y = min(max_y, self.p.y - ZV_ROWS + DEAD_ZONE_Y + 1)

    # ---------- FOV ----------
    def update_fov(self):
        self.visible = set()
        px,py = self.p.x,self.p.y
        if self.p.blind > 0:
            # Rogue 5.4.4 rooms.c:enter_room() and misc.c:look() reveal only the hero while blind.
            self.visible.add((px, py))
            self.explored |= self.visible
            return
        room = self.room_at(px,py)
        if room and room.usable and not (room.is_dark or room.is_maze):
            # Rogue 5.4.4 rooms.c:enter_room() lights only the room's own cells.
            # Corridor tiles beyond doors are revealed by the 3x3 look() below.
            for ry in range(room.y, room.y+room.h):
                for rx in range(room.x, room.x+room.w):
                    if 0<=rx<MAP_W and 0<=ry<MAP_H:
                        self.visible.add((rx,ry))
        for dy in range(-1,2):
            for dx in range(-1,2):
                nx,ny=px+dx,py+dy
                if not (0<=nx<MAP_W and 0<=ny<MAP_H):
                    continue
                if dx == 0 and dy == 0:
                    self.visible.add((nx,ny))
                    continue
                if rogue_vision.look_cell_visible(
                    self.tm[py][px],
                    self.tm[ny][nx],
                    dx,
                    dy,
                    self.tm[ny][px],
                    self.tm[py][nx],
                    self.tile_has_pass_flag(px, py),
                    self.tile_has_pass_flag(nx, ny),
                ):
                    self.visible.add((nx,ny))
        self.explored |= self.visible

    # ---------- Combat ----------
    def swing_hits(self, at_lvl, op_arm, wplus):
        # C: fight.c:swing()
        return rogue_fight.swing(at_lvl, op_arm, wplus, RNG.rnd)

    def player_weapon_profile(self, weap=None, thrown=False):
        if weap is None:
            return rogue_fight.bare_attack_profile("1x4")
        if weap.cat == CAT_WPN:
            data = weap.data
            return rogue_fight.weapon_profile(
                data,
                weap.hit_plus,
                weap.dam_plus,
                thrown,
                rogue_rings.weapon_hit_bonus(self.p, weap, thrown),
                rogue_rings.weapon_damage_bonus(self.p, weap, thrown),
                self.p.wpn.kind if self.p.wpn else None,
                self.p.wpn.hit_plus if self.p.wpn else 0,
                self.p.wpn.dam_plus if self.p.wpn else 0,
            )
        if weap.cat == CAT_STICK:
            damage, _ = rogue_sticks.stick_damage(self.ident.wtypes[weap.kind])
            return (
                damage,
                rogue_rings.weapon_hit_bonus(self.p, weap, thrown),
                rogue_rings.weapon_damage_bonus(self.p, weap, thrown),
            )
        return rogue_fight.non_weapon_profile(
            rogue_rings.weapon_hit_bonus(self.p, weap, thrown),
            rogue_rings.weapon_damage_bonus(self.p, weap, thrown),
        )

    def roll_player_attack(self, m, weap=None, thrown=False):
        # C: fight.c:roll_em()
        damage_expr, hplus, dplus = self.player_weapon_profile(weap, thrown)
        hplus = rogue_fight.attack_hit_plus(hplus, m.running, self.p.st)
        return rogue_fight.roll_em_damage(
            damage_expr,
            lambda: self.swing_hits(self.p.level, m.armor, hplus),
            roll_damage_expr,
            dplus,
            rogue_fight.attack_damage_plus(0, self.p.st),
        )

    def roll_monster_attack(self, m):
        # C: fight.c:roll_em()
        hplus = rogue_fight.attack_hit_plus(
            0, rogue_fight.player_defender_running(self.p.no_command), m.strength
        )
        return rogue_fight.roll_em_damage(
            m.damage_expr,
            lambda: self.swing_hits(m.level, self.p.ac, hplus),
            roll_damage_expr,
            0,
            rogue_fight.attack_damage_plus(0, m.strength),
        )

    def award_monster_kill(self, m, translated_name=None):
        # C: fight.c:killed()
        mn = translated_name or TextCatalog.monster(self.lang,m.name)
        self.p.exp = rogue_fight.killed_experience(self.p.exp, m.exp)
        if self.p.held_by is m:
            m.vf_hit, m.damage_expr = rogue_fight.venus_flytrap_release()
            self.p.held_by=None
        if m.sym == "L" and rogue_fight.leprechaun_kill_gold_allowed(
            self.p.depth, getattr(self, "max_depth", self.p.depth), True
        ):
            gold = Item(CAT_GOLD, 0)
            first_gold = goldcalc(self.p.depth)
            gold.qty = rogue_fight.leprechaun_kill_gold_after_first(first_gold, self.p.depth, self.save_vs_magic(), goldcalc)
            m.pack.append(gold)
        if self.p.lvlup():
            self.msg_important("misc.welcome_to_level_level", level=self.p.level)
            self.request_sfx(rogue_sfx.SFX_HEAL_LARGE)
        self.remove_monster(m, was_kill=True)
        return mn

    def p_attack(self, m):
        # C: fight.c:fight()
        self.dashing, self.p.quiet = rogue_fight.attack_activity_state()
        self.clear_running_count()
        self.runto(m)
        if self.reveal_xeroc_for_attack(m, thrown=False):
            return False
        mn=self.combat_monster_name(m)
        hit,dmg=self.roll_player_attack(m,self.p.wpn,False)
        if hit:
            m.hp-=dmg
            self.msg_text(self.player_hit_message(mn))
            self.request_hit_sfx()
            self.p.can_confuse_monster, confused_by_hit = rogue_fight.confusion_hit_effect(self.p.can_confuse_monster)
            if confused_by_hit:
                m.confused=1
                self.msg("fight.your_hands_stop_glowing_color", color=TextCatalog.color(self.lang, "red", "stem"))
            if not m.alive:
                self.msg_text(self.defeated_message(mn))
                self.award_monster_kill(m,mn)
            elif rogue_fight.confusion_message_allowed(confused_by_hit, self.p.blind > 0):
                self.msg("fight.subject_appears_confused", subject=mn)
            return True
        else:
            self.msg_text(self.player_miss_message(mn))
            self.request_sfx(rogue_sfx.SFX_HIT_MISS)
            return False

    def reveal_xeroc_for_attack(self,m,thrown=False):
        # Rogue 5.4.4 fight.c:attack() reveals a disguised Xeroc; melee returns FALSE.
        if not rogue_fight.attack_reveals_disguised_xeroc(
            rogue_monsters.is_disguised_xeroc(m), self.p.blind > 0
        ):
            return False
        rogue_monsters.reveal_disguise(m)
        self.msg("fight.heavy_that_s_a_nasty_critter" if self.p.hallucinating>0 else "fight.wait_that_s_a_xeroc")
        return rogue_fight.revealed_xeroc_stops_attack(thrown)

    def monster_has_magic_item_to_steal(self):
        return rogue_fight.magic_item_to_steal(
            self.p.inv,
            {self.p.wpn, self.p.arm, self.p.ring_l, self.p.ring_r},
            self.is_magic_item,
            rnd,
        )

    def remove_monster(self,m,was_kill=False):
        # C: fight.c:remove_mon()
        if getattr(m, "target", False):
            self.clear_fight_to_death()
        if rogue_fight.remove_monster_pack_should_fall(was_kill):
            for item in list(getattr(m, "pack", [])):
                pos=self.fall_position(m.x,m.y)
                if pos:
                    item.x,item.y=pos
                    self.gitems.append(item)
                m.pack.remove(item)
        else:
            m.pack=[]
        if m in self.mons:
            self.mons.remove(m)

    def runto(self,m,dest=None):
        # C: chase.c:runto()
        rogue_chase.runto(m, DEST_PLAYER if dest is None else dest)
        if dest is None:
            self.find_dest(m)

    def aggravate_monsters(self):
        # C: misc.c:aggravate()
        rogue_scrolls.aggravate_monsters(self.mons, self.runto)

    def wake_monster(self,m):
        # C: monsters.c:wake_monster()
        if not m.alive:
            return
        if (rogue_monsters.mean_wake_active(
                m,
                rogue_rings.is_wearing(self.p, rogue_rings.R_STEALTH),
                self.p.levitating > 0,
        ) and rnd(3)!=0):
            self.runto(m)
        player_room = self.room_at(self.p.x, self.p.y)
        medusa_visible = rogue_monsters.medusa_gaze_visible(
            bool(player_room and not player_room.is_dark),
            self.dist2((m.x, m.y), (self.p.x, self.p.y)),
            LAMPDIST,
        )
        if medusa_visible and rogue_monsters.medusa_gaze_can_try(m, self.p.blind > 0, self.p.hallucinating > 0):
            rogue_monsters.mark_found(m)
            if not self.save_vs_magic():
                duration = RNG.spread(HUHDURATION)
                if self.p.confused > 0:
                    self.fuses.lengthen("unconfuse", duration)
                else:
                    self.fuses.fuse("unconfuse", duration, rogue_daemons.AFTER)
                self.p.confused += duration
                mn=self.combat_monster_name(m)
                self.msg_important("pyxel.monster_gaze_confused", monster=mn)
        if rogue_monsters.is_greedy(m) and not m.running:
            self.runto(m,DEST_GOLD if self.room_gold_target(m) else DEST_PLAYER)

    def look_scan_allows_cell(self, x, y):
        # C: misc.c:look() 3x3 scan gates: bounds, blank cells, F_PASS, and diagonal passages.
        if not in_play_area(x, y):
            return False
        if self.p.blind <= 0 and x == self.p.x and y == self.p.y:
            return False
        tile = self.tm[y][x]
        if tile == T_VOID:
            return False
        hero_tile = self.tm[self.p.y][self.p.x]

        cell_pass = self.tile_has_pass_flag(x, y)
        hero_pass = self.tile_has_pass_flag(self.p.x, self.p.y)
        if hero_tile != T_DOOR and tile != T_DOOR and cell_pass != hero_pass:
            return False
        if (cell_pass or tile == T_DOOR) and (hero_pass or hero_tile == T_DOOR):
            if x != self.p.x and y != self.p.y:
                if not (
                    rogue_io.step_ok_tile(self.tm[y][self.p.x], TILE_CH)
                    or rogue_io.step_ok_tile(self.tm[self.p.y][x], TILE_CH)
                ):
                    return False
        return True

    def wake_look_monsters(self):
        for mo in self.mons:
            if abs(mo.x - self.p.x) > 1 or abs(mo.y - self.p.y) > 1:
                continue
            if not self.look_scan_allows_cell(mo.x, mo.y):
                continue
            if self.p.see_monsters > 0 and rogue_monsters.is_invisible(mo):
                continue
            self.wake_monster(mo)

    def wake_visible_monsters(self):
        # Kept for command-path compatibility; Rogue 5.4.4 misc.c:look(TRUE) wakes
        # monsters from its 3x3 scan, not from the whole Pyxel visible set.
        self.wake_look_monsters()

    def command_look(self):
        # C: command.c:command() calls misc.c:look(TRUE) once before dispatch.
        if getattr(self, "command_look_done", False):
            return
        self.wake_visible_monsters()
        self.command_look_done = True

    def can_see_monster(self, m):
        # C: chase.c:see_monst()
        return rogue_chase.see_monst(
            self.p.blind > 0,
            rogue_monsters.is_invisible(m),
            self.p.see_invisible > 0 or rogue_rings.is_wearing(self.p, rogue_rings.R_SEEINVIS),
        )

    def monster_is_seen(self, m):
        # C: chase.c:see_monst(); Pyxel visible supplies lamp/room geometry.
        return (m.x, m.y) in self.visible and self.can_see_monster(m)

    def can_detect_monsters(self):
        return getattr(self.p, "see_monsters", 0) > 0

    def save_vs_magic(self):
        which=VS_MAGIC-rogue_rings.protection_bonus(self.p)
        return rogue_monsters.save_throw(which,self.p.level,RNG.roll)

    def monster_save_throw(self, which, m):
        # Rogue 5.4.4 monsters.c:save_throw().
        return rogue_monsters.save_throw(which,m.level,RNG.roll)

    def m_attack(self,m):
        # C: fight.c:attack()
        self.dashing, self.p.quiet = rogue_fight.attack_activity_state()
        self.clear_running_count()
        if getattr(self, "fight_to_death", False) and not getattr(m, "target", False):
            self.clear_fight_to_death()
        if rogue_fight.attack_reveals_disguised_xeroc(
            rogue_monsters.is_disguised_xeroc(m), self.p.blind > 0
        ):
            rogue_monsters.reveal_disguise(m)
        mn=self.combat_monster_name(m,upper=True)
        old_hp = self.p.hp
        hit,dmg=self.roll_monster_attack(m)
        if hit:
            if dmg:
                self.p.hp-=dmg
            if rogue_fight.monster_attack_message_allowed(m.sym):
                self.msg_text(self.monster_hit_message(mn))
            self.request_hit_sfx()
            if self.p.hp<=0:
                if not self.death_cause:
                    self.death_cause=f"killed by a {m.name}"
                self.clamp_player_hp()
                return
            if getattr(self, "fight_to_death", False) and not getattr(self, "fight_kamikaze", False):
                loss = max(0, old_hp - self.p.hp)
                self.fight_max_hit = max(getattr(self, "fight_max_hit", 0), loss)
                if self.p.hp <= self.fight_max_hit:
                    self.fight_to_death = False
            if rogue_fight.attack_specials_allowed(rogue_monsters.is_cancelled(m)):
                if rogue_monsters.has_special(m, "rust") and self.can_rust_armor(self.p.arm):
                    self.rust_armor(important=True)
                if rogue_monsters.has_special(m, "steal_gold"):
                    old_gold = self.p.gold
                    first_loss = goldcalc(self.p.depth)
                    loss=rogue_fight.leprechaun_gold_loss_after_first(first_loss, self.p.depth, self.save_vs_magic(), goldcalc)
                    self.p.gold=max(0,self.p.gold-loss)
                    if self.p.gold != old_gold:
                        self.msg_important("fight.your_purse_feels_lighter")
                    self.remove_monster(m); return rogue_fight.attack_result(monster_removed=True)
                if rogue_monsters.has_special(m, "poison"):
                    self.p.st, poison_result = rogue_fight.poison_bite_strength(
                        self.p.st,
                        self.save_vs_poison(),
                        rogue_rings.is_wearing(self.p, rogue_rings.R_SUSTSTR),
                    )
                    poison_msg = rogue_fight.poison_bite_message_key(poison_result, terse=False)
                    if poison_msg:
                        self.msg_alarm(poison_msg)
                if rogue_monsters.has_special(m, "drain_level") and rogue_fight.drain_hits("W", rnd):
                    self.p.level, self.p.exp, self.p.hp, self.p.max_hp, died = rogue_fight.wraith_drain(
                        self.p.level,
                        self.p.exp,
                        self.p.hp,
                        self.p.max_hp,
                        self.p.EXP_T,
                        lambda: roll("1d10"),
                    )
                    if died:
                        self.p.hp = 0
                        self.death_cause = f"killed by a {m.name}"
                        return
                    self.msg_alarm("fight.you_suddenly_feel_weaker")
                if rogue_monsters.has_special(m, "drain") and rogue_fight.drain_hits("V", rnd):
                    self.p.hp, self.p.max_hp, died = rogue_fight.max_hp_drain(
                        self.p.hp, self.p.max_hp, lambda: roll("1d3")
                    )
                    if died:
                        self.p.hp = 0
                        self.death_cause = f"killed by a {m.name}"
                        return
                    self.msg_alarm("fight.you_suddenly_feel_weaker")
                if rogue_monsters.has_special(m, "freeze"):
                    self.p.no_command, should_message, hypothermia = rogue_fight.ice_freeze(
                        self.p.no_command, BORE_LEVEL, rnd
                    )
                    if hypothermia:
                        self.p.hp=0; self.death_cause="hypothermia"
                    if should_message:
                        self.msg_important("fight.you_are_frozen", subject=self.combat_monster_name(m, article_for_something=True))
                if rogue_monsters.has_special(m, "hold"):
                    m.vf_hit, m.damage_expr = rogue_fight.venus_flytrap_hit(m.vf_hit)
                    self.p.held_by=m
                    self.p.hp-=1
                    if self.p.hp<=0 and not self.death_cause:
                        self.death_cause=f"killed by a {m.name}"
                        self.clamp_player_hp()
                if rogue_monsters.has_special(m, "steal_item"):
                    t=self.monster_has_magic_item_to_steal()
                    if t:
                        self.p.rm_item(t); self.msg_important("fight.she_stole_target", target=self.ident.name(t))
                        self.remove_monster(m); return rogue_fight.attack_result(monster_removed=True)
        else:
            if m.sym == "F" and m.vf_hit > 0:
                self.p.hp = rogue_fight.venus_flytrap_miss_hp(self.p.hp, m.vf_hit)
                if self.p.hp<=0 and not self.death_cause:
                    self.death_cause=f"killed by a {m.name}"
                    self.clamp_player_hp()
            if rogue_fight.monster_attack_message_allowed(m.sym):
                self.msg_text(self.monster_miss_message(mn))
            self.request_sfx(rogue_sfx.SFX_HIT_MISS)
        return rogue_fight.attack_result(monster_removed=False)

    def m_turn(self,m):
        # C: chase.c (monster turn loop)
        rogue_chase.monster_turn(
            m,
            self.move_monst,
            lambda mo: self.dist2((mo.x, mo.y), (self.p.x, self.p.y)),
        )

    def move_monst(self,m):
        # C: chase.c:move_monst()
        return rogue_chase.move_monst(
            m,
            self.do_chase,
            rogue_monsters.chase_steps_for_turn,
            rogue_monsters.finish_chase_turn,
        )

    def do_chase(self,m):
        # C: chase.c:do_chase()
        dest=self.current_chase_dest(m)
        door = self.tm[m.y][m.x] == T_DOOR
        rer=self.room_for_ai(m.x,m.y,actor=False) if door else self.room_for_ai(m.x,m.y,actor=True)
        ree=rogue_chase.destination_room(
            dest == (self.p.x, self.p.y),
            self.room_for_ai(self.p.x,self.p.y,actor=False),
            self.room_for_ai(dest[0],dest[1],actor=False),
        )
        chase_dest=dest
        if rer!=ree:
            exits = self.room_exits(rer) if hasattr(rer,"x") else self.passage_exits(rer)
            if door:
                exits = exits + self.passage_exits(self.passage_component(m.x,m.y))
            chase_dest = rogue_chase.nearest_exit_to_dest(
                exits,
                dest,
                self.dist2,
            ) or chase_dest
        elif self.try_dragon_breath(m):
            return 0
        orig_pos=(m.x,m.y)
        moved_or_attack=self.chase(m,chase_dest)
        if moved_or_attack=="attack":
            return -1 if m not in self.mons else 0
        if moved_or_attack=="move" and m.sym=="F":
            m.x,m.y=orig_pos
            return 0
        if m.dest!=DEST_PLAYER and (m.x,m.y)==dest:
            self.collect_monster_dest(m,dest)
        return 0

    def current_chase_dest(self,m):
        # C: chase.c:do_chase() uses the existing t_dest; find_dest() is called by runto()/relocate().
        if rogue_monsters.is_greedy(m) and self.room_gold_target(m) is None:
            m.dest=DEST_PLAYER
        if isinstance(m.dest, tuple):
            return m.dest
        if rogue_monsters.is_greedy(m) and m.dest==DEST_GOLD:
            target=rogue_chase.greedy_destination(True, m.dest, self.room_gold_target(m), DEST_PLAYER)
            if target != DEST_PLAYER:
                m.dest=target
                return target
            m.dest=DEST_PLAYER
        return (self.p.x,self.p.y)

    def try_dragon_breath(self,m):
        # C: chase.c:do_chase() Dragon flame bolt gate.
        direction = rogue_chase.dragon_breath_direction(
            m.sym,
            (m.x, m.y),
            (self.p.x, self.p.y),
            self.dist2((m.x, m.y), (self.p.x, self.p.y)),
            BOLT_LENGTH,
            rogue_monsters.is_cancelled(m),
            RNG.rnd,
            DRAGONSHOT,
        )
        if direction is None:
            return False
        sx,sy=direction
        self.clear_running_count()
        self.p.quiet=0
        self.fire_bolt_from(m.x,m.y,sx,sy,"flame")
        if getattr(self, "fight_to_death", False) and not getattr(m, "target", False):
            self.clear_fight_to_death()
        return True

    def room_gold_target(self,m):
        mr=self.room_for_ai(m.x,m.y)
        gold=[]
        for it in self.gitems:
            if it.cat==CAT_GOLD and self.room_for_ai(it.x,it.y)==mr:
                gold.append((it.x,it.y))
        if not gold:
            return None
        return min(gold,key=lambda p:self.dist2((m.x,m.y),p))

    def find_dest(self,m):
        # C: chase.c:find_dest()
        if rogue_monsters.is_greedy(m) and m.dest==DEST_GOLD:
            target=rogue_chase.greedy_destination(True, m.dest, self.room_gold_target(m), DEST_PLAYER)
            if target != DEST_PLAYER:
                m.dest=target
                return target
            m.dest=DEST_PLAYER
        spec = self.monster_spec_for_sym(m.sym)
        carry_prob = spec.carry if spec else 0
        target = rogue_chase.find_dest(
            carry_prob,
            self.room_for_ai(m.x, m.y),
            self.room_for_ai(self.p.x, self.p.y, actor=True),
            (m.x, m.y) in self.visible and self.can_see_monster(m),
            self.gitems,
            {mo.dest for mo in self.mons},
            lambda item: self.room_for_ai(item.x, item.y),
            lambda item: (item.x, item.y),
            self.is_scare_monster,
            RNG.rnd,
        )
        if target:
            m.dest=(target.x, target.y)
            return m.dest
        m.dest=DEST_PLAYER
        return (self.p.x,self.p.y)

    def collect_monster_dest(self,m,dest):
        gi=self.gi_at(*dest)
        if gi:
            self.gitems.remove(gi)
            m.pack.append(gi)
            room = self.room_for_ai(m.x, m.y, actor=True)
            self.tm[dest[1]][dest[0]] = T_CORR if getattr(room, "is_gone", False) else T_FLOOR
            self.find_dest(m)
            return
        if m.sym!="F":
            m.running=False

    def random_monster_move(self,m):
        # C: move.c:rndmove()
        return rogue_move.rndmove(
            (m.x, m.y),
            rnd,
            lambda src, dst: self.can_monster_step(m, dst[0], dst[1])
            and self.diag_ok(src[0], src[1], dst[0], dst[1]),
        )

    def can_monster_step(self,m,x,y):
        # C: move.c:rndmove() gates random monster moves with winat()/step_ok().
        if not (0 <= x < MAP_W and 0 <= y < MAP_H):
            return False
        is_hero_pos = (x, y) == (self.p.x, self.p.y)
        ch = "@" if is_hero_pos else self.zap_winat_char(x, y)
        if not self.zap_step_ok_char(ch):
            return False
        if is_hero_pos:
            return True
        gi=self.gi_at(x,y)
        return not (gi and self.is_scare_monster(gi))

    def can_player_rndmove_step(self,x,y):
        # C: move.c:rndmove() checks winat()/step_ok() and rejects S_SCARE.
        if not (0 <= x < MAP_W and 0 <= y < MAP_H):
            return False
        ch = self.zap_winat_char(x, y)
        if not self.zap_step_ok_char(ch):
            return False
        gi=self.gi_at(x,y)
        return not (gi and self.is_scare_monster(gi))

    def chase(self,m,dest):
        # C: chase.c:chase()
        px,py=self.p.x,self.p.y
        if rogue_chase.should_random_move(m.confused, m.sym, rnd):
            nx,ny=self.random_monster_move(m)
            if (nx,ny)==(px,py):
                self.m_attack(m); return "attack"
            m.x,m.y=nx,ny
            if rogue_chase.confusion_clears_after_random_move(m.confused, rnd): m.confused=0
            return "move"
        cur=self.dist2((m.x,m.y),dest)
        best=(m.x,m.y); bestd=cur; ties=1
        for dx,dy in rogue_chase.chase_candidate_offsets():
            nx,ny=m.x+dx,m.y+dy
            diagonal_ok=self.diag_ok(m.x,m.y,nx,ny)
            if not diagonal_ok:
                continue
            is_hero_pos = (nx,ny)==(px,py)
            gi=self.gi_at(nx,ny)
            if not rogue_chase.is_chase_candidate(
                diagonal_ok,
                self.walkable(nx,ny) and not self.mon_at(nx,ny),
                bool(not is_hero_pos and gi and self.is_scare_monster(gi)),
                False,
            ):
                continue
            d=self.dist2((nx,ny),dest)
            best,bestd,ties=rogue_chase.choose_chase_step(best,bestd,ties,(nx,ny),d,rnd)
        if best==(px,py):
            self.m_attack(m); return "attack"
        if best!=(m.x,m.y):
            m.x,m.y=best
        return "move" if rogue_chase.chase_continues(bestd, best, (px, py)) else "arrived"

    # ---------- Item effects ----------
    def use_pot(self,it):
        # C: potions.c:quaff()
        if it.cat != CAT_POT:
            self.msg("potions.yuk_why_would_you_want_to_drink_that")
            return
        if it is self.p.wpn:
            self.p.wpn = None
        self.consume_pack_item(it)
        self.request_sfx(rogue_sfx.SFX_SPELL_USE)
        p=self.p; nm=POTIONS[it.kind]["name"]
        if nm=="healing":
            self.ident.pk[it.kind]=True
            h=RNG.roll(p.level,4)
            p.hp,p.max_hp=rogue_potions.healing_hp(p.hp,p.max_hp,h)
            self.sight()
            self.msg("potions.you_begin_to_feel_better")
            self.request_sfx(rogue_sfx.SFX_HEAL_SMALL)
        elif nm=="extra healing":
            self.ident.pk[it.kind]=True
            h=RNG.roll(p.level,8)
            p.hp,p.max_hp=rogue_potions.extra_healing_hp(p.hp,p.max_hp,p.level,h)
            self.sight()
            self.come_down()
            self.msg("potions.you_begin_to_feel_much_better")
            self.request_sfx(rogue_sfx.SFX_HEAL_SMALL)
        elif nm=="poison":
            self.ident.pk[it.kind]=True
            if rogue_rings.is_wearing(p, rogue_rings.R_SUSTSTR):
                self.msg("potions.you_feel_momentarily_sick")
            else:
                l=RNG.rnd(3)+1; p.st=rogue_potions.poison_strength(p.st,l); self.msg_alarm("potions.you_feel_very_sick_now")
                self.come_down()
        elif nm=="gain strength":
            self.ident.pk[it.kind]=True; p.st,p.max_st=rogue_potions.gain_strength(p.st,p.max_st); self.msg("potions.you_feel_stronger_now_what_bulging_muscles")
        elif nm=="restore strength":
            # Rogue 5.4.4 potions.c:P_RESTORE temporarily removes R_ADDSTR before restoring max_stats.s_str.
            addstr = sum(r.ench for r in (p.ring_l, p.ring_r) if rogue_rings.is_ring(r, rogue_rings.R_ADDSTR))
            p.st = rogue_potions.restore_strength(p.st, p.max_st, addstr)
            self.msg("potions.hey_this_tastes_great_it_make_you_feel_warm_all_over")
        elif nm=="confusion":
            self.ident.pk[it.kind] = rogue_potions.do_pot_known(
                self.ident.pk[it.kind], p.hallucinating <= 0
            )
            duration = RNG.spread(HUHDURATION)
            if rogue_potions.do_pot_fuse_action(p.confused > 0) == "lengthen":
                self.fuses.lengthen("unconfuse", duration)
            else:
                self.fuses.fuse("unconfuse", duration, rogue_daemons.AFTER)
            p.confused += duration
            self.msg_important("potions.what_a_tripy_feeling" if p.hallucinating > 0 else "potions.wait_what_s_going_on_here_huh_what_who")
        elif nm=="hallucination":
            self.ident.pk[it.kind] = rogue_potions.do_pot_known(self.ident.pk[it.kind], True)
            duration = RNG.spread(SEEDURATION)
            if rogue_potions.do_pot_fuse_action(p.hallucinating > 0) == "lengthen":
                self.fuses.lengthen("come_down", duration)
            else:
                self.seen_stairs = self.stairs_seen_on_map()
                if p.see_monsters > 0:
                    p.see_monsters = rogue_potions.turn_see_state(False, p.see_monsters)
                self.daemons.start("visuals", rogue_daemons.BEFORE)
                self.fuses.fuse("come_down", duration, rogue_daemons.AFTER)
            p.hallucinating += duration
            self.msg_important("potions.oh_wow_everything_seems_so_cosmic")
        elif nm=="blindness":
            self.ident.pk[it.kind] = rogue_potions.do_pot_known(self.ident.pk[it.kind], True)
            duration = RNG.spread(SEEDURATION)
            if rogue_potions.do_pot_fuse_action(p.blind > 0) == "lengthen":
                self.fuses.lengthen("sight", duration)
            else:
                self.fuses.fuse("sight", duration, rogue_daemons.AFTER)
            p.blind += duration
            self.update_fov()
            self.msg_important("potions.oh_bummer_everything_is_dark_help" if p.hallucinating > 0 else "potions.a_cloak_of_darkness_falls_around_you")
        elif nm=="haste self":
            self.ident.pk[it.kind]=True
            if self.add_haste(True):
                self.msg("potions.you_feel_yourself_moving_much_faster")
            self.ident.pg[it.kind] = rogue_potions.call_it_guess_after_use(
                self.ident.pk[it.kind], self.ident.pg[it.kind]
            )
            return False
        elif nm=="see invisible":
            self.ident.pk[it.kind] = rogue_potions.do_pot_known(self.ident.pk[it.kind], False)
            duration = RNG.spread(SEEDURATION)
            wearing_see_invis = rogue_rings.is_wearing(p, rogue_rings.R_SEEINVIS)
            if rogue_potions.do_pot_fuse_action(p.see_invisible > 0 or wearing_see_invis) == "lengthen":
                self.fuses.lengthen("unsee", duration)
            else:
                self.fuses.fuse("unsee", duration, rogue_daemons.AFTER)
            p.see_invisible = rogue_potions.see_invisible_duration(
                p.see_invisible, duration, wearing_see_invis
            )
            self.msg(
                "potions.this_potion_tastes_like_item_juice",
                item=TextCatalog.item_kind(self.lang, CAT_FOOD, "slime-mold"),
            )
            self.sight()
        elif nm=="raise level":
            self.ident.pk[it.kind]=True
            p.exp=rogue_levels.raise_level_exp(p.level,p.EXP_T)
            self.msg("potions.you_suddenly_feel_much_more_skillful")
            if p.lvlup():
                self.msg_important("misc.welcome_to_level_level", level=p.level)
                self.request_sfx(rogue_sfx.SFX_HEAL_LARGE)
        elif nm=="monster detection":
            if p.see_monsters > 0:
                self.fuses.fuse("turn_see", HUHDURATION, rogue_daemons.AFTER)
            else:
                self.fuses.fuse("turn_see", HUHDURATION, rogue_daemons.AFTER)
            add_new = rogue_potions.turn_see_adds_new(
                self.monster_is_seen(m) for m in self.mons
            )
            p.see_monsters = rogue_potions.turn_see_state(False, HUHDURATION)
            if add_new:
                self.msg("pyxel.sense_monsters")
            else:
                self.msg("potions.you_have_a_item_feeling_for_a_moment_then_it_passes",
                         item="normal" if p.hallucinating > 0 else "strange")
        elif nm=="magic detection":
            found = False
            if rogue_potions.magic_detection_can_scan(bool(self.gitems)):
                for i in self.gitems:
                    if self.is_magic_item(i):
                        found = True
                        self.visible.add((i.x,i.y)); self.explored.add((i.x,i.y))
                for mo in self.mons:
                    if any(self.is_magic_item(i) for i in mo.pack):
                        found = True
                        self.visible.add((mo.x,mo.y)); self.explored.add((mo.x,mo.y))
            if found:
                self.ident.pk[it.kind]=True
                self.msg("pyxel.sense_magic")
            else:
                self.msg("potions.you_have_a_item_feeling_for_a_moment_then_it_passes",
                         item="normal" if p.hallucinating > 0 else "strange")
        elif nm=="levitation":
            self.ident.pk[it.kind] = rogue_potions.do_pot_known(self.ident.pk[it.kind], True)
            duration = RNG.spread(HEALTIME)
            if rogue_potions.do_pot_fuse_action(p.levitating > 0) == "lengthen":
                self.fuses.lengthen("land", duration)
            else:
                self.fuses.fuse("land", duration, rogue_daemons.AFTER)
            p.levitating += duration
            self.msg("potions.oh_wow_you_re_floating_in_the_air" if p.hallucinating > 0 else "potions.you_start_to_float_in_the_air")
        self.ident.pg[it.kind] = rogue_potions.call_it_guess_after_use(
            self.ident.pk[it.kind], self.ident.pg[it.kind]
        )
        return True

    def add_haste(self, potion=True):
        # Rogue 5.4.4 misc.c:add_haste() and daemons.c:nohaste().
        result = rogue_misc.add_haste_result(self.p.haste > 0, potion, rnd)
        if not result.ok:
            self.p.no_command += result.no_command_add
            self.p.haste = 0
            self.haste_half_turn = False
            self.haste_no_command_half_turn = False
            self.fuses.extinguish("nohaste")
            self.msg_important("misc.you_faint_from_exhaustion")
            return False
        self.p.haste = 1
        self.haste_half_turn = False
        self.haste_no_command_half_turn = False
        if potion:
            self.p.haste = result.duration
            self.fuses.fuse("nohaste", result.duration, rogue_daemons.AFTER)
        return True

    def nohaste(self):
        # C: daemons.c:nohaste()
        self.p.haste, self.haste_half_turn, message_key = rogue_daemons.nohaste_state()
        self.haste_no_command_half_turn = False
        self.msg(message_key)

    def come_down(self):
        # C: daemons.c:come_down()
        should_clear, message_key = rogue_daemons.come_down_result(
            self.p.hallucinating > 0, self.p.blind > 0
        )
        if not should_clear:
            return
        self.daemons.kill("visuals")
        self.clear_hallucination_visuals()
        self.p.hallucinating = 0
        if message_key:
            self.msg(message_key)

    def land(self):
        # C: daemons.c:land()
        self.p.levitating, message_key = rogue_daemons.land_state(self.p.hallucinating > 0)
        self.msg(message_key)

    def unconfuse(self):
        # C: daemons.c:unconfuse()
        self.p.confused = 0
        self.msg(
            "daemons.you_feel_less_value_now",
            value=rogue_daemons.unconfuse_message_value(self.p.hallucinating > 0),
        )

    def sight(self):
        # C: daemons.c:sight()
        message_key = rogue_daemons.sight_result(self.p.blind > 0, self.p.hallucinating > 0)
        if message_key is None:
            return
        self.fuses.extinguish("sight")
        self.p.blind = 0
        self.update_fov()
        self.msg(message_key)

    def is_magic_item(self, it):
        # Rogue 5.4.4 potions.c:is_magic().
        return rogue_potions.is_magic_item(
            it.cat,
            it.cat == CAT_WPN and (it.hit_plus != 0 or it.dam_plus != 0),
            it.cat == CAT_ARM and (it.protected or it.ench != 0),
        )

    def type_known(self, it):
        if it.cat == CAT_POT:
            return self.ident.pk[it.kind] or self.ident.easy_type_known
        if it.cat == CAT_SCR:
            return self.ident.sk[it.kind] or self.ident.easy_type_known
        if it.cat == CAT_RING:
            return self.ident.rk[it.kind] or self.ident.easy_type_known
        if it.cat == CAT_STICK:
            return self.ident.wk[it.kind] or self.ident.easy_type_known
        return False

    def clear_type_guess(self, it):
        if it.cat == CAT_POT:
            self.ident.pg[it.kind] = None
        elif it.cat == CAT_SCR:
            self.ident.sg[it.kind] = None
        elif it.cat == CAT_RING:
            self.ident.rg[it.kind] = None
        elif it.cat == CAT_STICK:
            self.ident.wg[it.kind] = None
        return True

    def set_type_known(self, it, known=True):
        if it.cat == CAT_POT:
            self.ident.pk[it.kind] = bool(known)
            if known: self.ident.pf[it.kind] = True
            if known: self.clear_type_guess(it)
            return True
        if it.cat == CAT_SCR:
            self.ident.sk[it.kind] = bool(known)
            if known: self.ident.sf[it.kind] = True
            if known: self.clear_type_guess(it)
            return True
        if it.cat == CAT_RING:
            self.ident.rk[it.kind] = bool(known)
            if known: self.ident.rf[it.kind] = True
            if known: self.clear_type_guess(it)
            return True
        if it.cat == CAT_STICK:
            self.ident.wk[it.kind] = bool(known)
            if known: self.ident.wf[it.kind] = True
            if known: self.clear_type_guess(it)
            return True
        return False

    def mark_type_discovered(self, it):
        if it.cat == CAT_POT:
            self.ident.pf[it.kind] = True
            return True
        if it.cat == CAT_SCR:
            self.ident.sf[it.kind] = True
            return True
        if it.cat == CAT_RING:
            self.ident.rf[it.kind] = True
            return True
        if it.cat == CAT_STICK:
            self.ident.wf[it.kind] = True
            return True
        return False

    def set_instance_known(self, it, known=True):
        it.known = bool(known)
        return True

    def set_know(self, it):
        # Rogue 5.4.4 wizard.c:set_know().
        # Sets type-level oi_know, clears oi_guess, sets instance ISKNOW flag.
        if it.cat in (CAT_POT, CAT_SCR, CAT_RING, CAT_STICK):
            self.set_type_known(it)
            self.set_instance_known(it)
            return True
        if it.cat in (CAT_WPN, CAT_ARM):
            self.set_instance_known(it)
            return True
        return False

    def _call_it_apply(self, it, name: str):
        # misc.c:call_it() — oi_know なら oi_guess クリア、それ以外は name をセット（空文字はクリア）
        val = name.strip() if name else None
        if it.cat == CAT_POT:
            if self.ident.pk[it.kind]:
                self.ident.pg[it.kind] = None
            else:
                self.ident.pg[it.kind] = val
        elif it.cat == CAT_SCR:
            if self.ident.sk[it.kind]:
                self.ident.sg[it.kind] = None
            else:
                self.ident.sg[it.kind] = val
        elif it.cat == CAT_RING:
            if self.ident.rk[it.kind]:
                self.ident.rg[it.kind] = None
            else:
                self.ident.rg[it.kind] = val
        elif it.cat == CAT_STICK:
            if self.ident.wk[it.kind]:
                self.ident.wg[it.kind] = None
            else:
                self.ident.wg[it.kind] = val
        elif it.cat in (CAT_WPN, CAT_ARM):
            it.o_label = val

    def call_type_known(self, it):
        # Rogue 5.4.4 command.c:call() checks oi_know only for type-level items.
        return self.type_known(it)

    def call_result(self, it):
        return rogue_things.call_result(
            it.cat,
            self.call_type_known(it),
            (CAT_POT, CAT_SCR, CAT_RING, CAT_STICK),
            (CAT_FOOD, CAT_AMULET),
        )

    def apply_call_name(self, it, name: str):
        # Rogue 5.4.4 command.c:call() rejects known type-level items before call_it().
        result = self.call_result(it)
        if result == rogue_things.CALL_RESULT_UNCALLABLE:
            self.msg("command.you_cant_call_that_anything")
            return False
        if result == rogue_things.CALL_RESULT_KNOWN:
            self.msg("command.that_has_already_been_identified")
            return False
        self._call_it_apply(it, name)
        return True

    def _disc_lines(self, rnd_func=None):
        # things.c:print_disc(*) — 全カテゴリの発見済みアイテム名を (color, text) リストで返す
        nothing = TextCatalog.msg(self.lang, "misc.nothing_discovered")
        lang = self.lang
        result = []

        def section(label, cat, table, known_arr, guess_arr, found_arr):
            result.append((UI_SECTION_COL, f"-- {label} --"))
            found = 0
            order = rogue_things.discovery_order(len(table), rnd_func) if rnd_func else range(len(table))
            for i in order:
                easy_found = self.difficulty_profile().easy_type_known and found_arr[i]
                if known_arr[i] or (guess_arr[i] is not None) or easy_found:
                    dummy = Item(cat, i, known=False)
                    result.append((UI_TEXT_COL, self.ident.name(dummy)))
                    found += 1
            if found == 0:
                result.append((5, nothing))

        section("Potions" if lang == LANG_EN else "水薬",   CAT_POT,   POTIONS, self.ident.pk, self.ident.pg, self.ident.pf)
        result.append((0, ""))
        section("Scrolls" if lang == LANG_EN else "巻き物", CAT_SCR,   self.ident.scrolls, self.ident.sk, self.ident.sg, self.ident.sf)
        result.append((0, ""))
        section("Rings"   if lang == LANG_EN else "指輪",   CAT_RING,  RINGS,   self.ident.rk, self.ident.rg, self.ident.rf)
        result.append((0, ""))
        section("Sticks"  if lang == LANG_EN else "杖",     CAT_STICK, STICKS,  self.ident.wk, self.ident.wg, self.ident.wf)
        return result

    def open_discoveries(self):
        self.command_look()
        self.disc_scroll = 0
        self.disc_lines = self._disc_lines(RNG.rnd)
        self.disc_return_state = self.st if self.st == ST_MENU else ST_PLAY
        self.st = ST_DISC
        self.command_look_done = False

    def identify_item(self, it):
        # Backward-compat alias for set_know().
        return self.set_know(it)

    def needs_identify(self, it):
        if it.cat == CAT_POT:
            return not self.ident.pk[it.kind]
        if it.cat == CAT_SCR:
            return not self.ident.sk[it.kind]
        if it.cat in (CAT_WPN, CAT_ARM):
            return not getattr(it, "known", True)
        if it.cat == CAT_RING:
            return not self.ident.rk[it.kind] or not getattr(it, "known", True)
        if it.cat == CAT_STICK:
            return not self.ident.wk[it.kind] or not getattr(it, "known", True)
        return False

    def identify_scroll_target_cats(self, nm):
        # Rogue 5.4.4 scrolls.c:S_ID_* id_type[].
        return rogue_scrolls.identify_target_cats(nm, sys.modules[__name__], self.difficulty_profile().idscrl)

    def use_scr(self,it):
        # C: scrolls.c:read_scroll()
        if it.cat != CAT_SCR:
            self.msg("scrolls.there_is_nothing_on_it_to_read")
            return
        p=self.p
        if it is p.wpn:
            p.wpn = None
        self.consume_pack_item(it)
        self.request_sfx(rogue_sfx.SFX_SPELL_USE)
        nm=self.scrolls[it.kind]["name"]; self.ident.sk[it.kind]=nm not in ("monster confusion","scare monster","food detection","teleportation","enchant weapon","create monster","remove curse","aggravate monsters","protect armor","hold monster","enchant armor")
        if nm=="monster confusion":
            rogue_scrolls.monster_confusion(p)
            self.msg("scrolls.your_hands_begin_to_glow_color", color=TextCatalog.color(self.lang, "red", "stem"))
        elif nm == "identify" or nm.startswith("identify "):
            cats = self.identify_scroll_target_cats(nm)
            self.msg("scrolls.this_scroll_is_an_item_scroll", item=nm)
            unid=[i for i in p.inv if i.cat in cats and self.needs_identify(i)]
            if unid:
                # Interactive target selection (Rogue 5.4.4 wizard.c:whatis()).
                self.ident.sg[it.kind] = rogue_scrolls.call_it_guess_after_read(
                    self.ident.sk[it.kind], self.ident.sg[it.kind]
                )
                self.fitems=unid; self.icur=0; self.cact="Identify"; self.st=ST_ITEM
                return True  # Caller must NOT call close_menu()/end_turn() yet.
            else:
                self.msg("pyxel.feel_vaguely_uneasy")
                self.ident.sg[it.kind] = rogue_scrolls.call_it_guess_after_read(
                    self.ident.sk[it.kind], self.ident.sg[it.kind]
                )
                return False
        elif nm=="enchant weapon":
            if rogue_scrolls.enchant_weapon(p.wpn, RNG.rnd):
                self.msg(
                    "scrolls.your_color_glows_color2_for_a_moment",
                    color=TextCatalog.item_kind(self.lang, CAT_WPN, p.wpn.data["name"]),
                    color2=TextCatalog.color(self.lang, "blue", "stem"),
                )
            else: self.msg("scrolls.you_feel_a_strange_sense_of_loss")
        elif nm=="enchant armor":
            if rogue_scrolls.enchant_armor(p.arm):
                p.recalc_ac()
                self.msg(
                    "scrolls.your_armor_glows_color_for_a_moment",
                    color=TextCatalog.color(self.lang, "silver", "noun"),
                )
        elif nm=="remove curse":
            rogue_scrolls.remove_curse_equipment((p.arm, p.wpn, p.ring_l, p.ring_r))
            self.msg("scrolls.you_feel_in_touch_with_the_universal_onenes" if p.hallucinating > 0 else "scrolls.you_feel_as_if_somebody_is_watching_over_you")
        elif nm=="aggravate monsters":
            self.aggravate_monsters(); self.msg("scrolls.you_hear_a_high_pitched_humming_noise")
        elif nm=="scare monster":
            self.msg("scrolls.you_hear_maniacal_laughter_in_the_distance")
        elif nm=="sleep":
            rogue_scrolls.sleep_scroll(p, rnd, SLEEPTIME); self.dashing=False; self.msg_important("scrolls.you_fall_asleep")
        elif nm=="teleportation":
            old_room = self.room_at(p.x, p.y)
            self.teleport_player()
            if rogue_scrolls.teleport_identifies(old_room, self.room_at(p.x, p.y)):
                self.ident.sk[it.kind]=True
        elif nm=="create monster":
            candidates = []
            for dy in (-1,0,1):
                for dx in (-1,0,1):
                    if dx==0 and dy==0:
                        continue
                    nx,ny=p.x+dx,p.y+dy
                    ch = self.zap_winat_char(nx, ny)
                    if self.zap_step_ok_char(ch):
                        gi=self.gi_at(nx,ny)
                        if gi and self.is_scare_scroll(gi):
                            continue
                        candidates.append((nx, ny))
            pick = rogue_scrolls.choose_create_monster_pos(p, candidates, RNG.rnd)
            if pick:
                nx,ny=pick
                spec = self.monster_spec_for_sym(rogue_monsters.randmonster(p.depth, RNG.rnd, wander=False))
                if spec:
                    # C: monsters.c:new_monster() attach(mlist, tp) puts the new monster at list head.
                    self.mons.insert(0, self.new_monster_from_spec(nx,ny,spec))
            else:
                self.msg("scrolls.you_hear_a_faint_cry_of_anguish_in_the_distance")
        elif nm=="magic mapping":
            for (x,y),tile in rogue_scrolls.magic_mapping_targets(self.hidden_tiles, self.traps, T_TRAP):
                self.tm[y][x]=tile
                self.explored.add((x,y))
                self.hidden_tiles.pop((x,y),None)
            for y in range(MAP_H):
                for x in range(MAP_W):
                    if self.tm[y][x]!=T_VOID: self.explored.add((x,y))
            self.msg("scrolls.oh_now_this_scroll_has_a_map_on_it")
        elif nm=="hold monster":
            held_count = rogue_scrolls.hold_monsters(p, self.mons)
            if held_count:
                self.ident.sk[it.kind]=True
                self.msg("scrolls.the_monster_freezes" if held_count == 1 else "scrolls.the_monsters_around_you_freeze")
            else:
                self.msg("scrolls.you_feel_a_strange_sense_of_loss")
        elif nm=="food detection":
            positions = rogue_scrolls.food_detection_positions(self.gitems, CAT_FOOD)
            for pos in positions:
                self.visible.add(pos)
                self.explored.add(pos)
            found = bool(positions)
            if found:
                self.ident.sk[it.kind]=True
                self.msg("scrolls.your_nose_tingles_and_you_smell_food")
            else:
                self.msg("scrolls.your_nose_tingles")
        elif nm=="protect armor":
            if rogue_scrolls.protect_armor(p.arm):
                self.msg(
                    "scrolls.your_armor_is_covered_by_a_shimmering_color_shield",
                    color=TextCatalog.color(self.lang, "gold", "noun"),
                )
            else:
                self.msg("scrolls.you_feel_a_strange_sense_of_loss")
        elif nm=="blank paper": self.msg("pyxel.scroll_is_blank")
        self.ident.sg[it.kind] = rogue_scrolls.call_it_guess_after_read(
            self.ident.sk[it.kind], self.ident.sg[it.kind]
        )

    def zap_winat_char(self, x, y):
        # C: rogue.h:winat(y,x) returns t_disguise before chat(y,x).
        m = self.mon_at(x, y)
        if m:
            return getattr(m, "disguise", m.sym)
        if not (0 <= x < MAP_W and 0 <= y < MAP_H):
            return " "
        return TILE_CH.get(self.tm[y][x], (" ", 0))[0]

    def zap_step_ok_char(self, ch):
        # C: io.c:step_ok() rejects space, walls, and alphabetic monster glyphs.
        return rogue_io.step_ok_char(ch)

    def first_zap_target(self, dx, dy, stop_at_door=False):
        x,y=self.p.x,self.p.y
        for _ in range(max(MAP_W,MAP_H)):
            if stop_at_door:
                x,y=x+dx,y+dy
                if not (0<=x<MAP_W and 0<=y<MAP_H):
                    return None
                ch=self.zap_winat_char(x,y)
                if self.zap_step_ok_char(ch) and ch != TILE_CH[T_DOOR][0]:
                    continue
                return self.mon_at(x,y)
            if not (0<=x<MAP_W and 0<=y<MAP_H):
                return None
            ch=self.zap_winat_char(x,y)
            if not self.zap_step_ok_char(ch):
                return self.mon_at(x,y)
            x,y=x+dx,y+dy
        return None

    def monster_spec_for_sym(self, sym):
        for spec in BESTIARY:
            if spec.sym == sym:
                return spec
        return None

    def set_monster_from_spec(self, m, spec):
        # Rogue 5.4.4 monsters.c:new_monster() rebuilds monster stats from monsters[].
        level,hp,armor,exp=rogue_monsters.new_monster_stats(
            spec.level,spec.armor,spec.exp,self.p.depth,AMULET_LEVEL,RNG.roll
        )
        m.sym=spec.sym; m.name=spec.name
        m.level=level; m.armor=armor
        m.damage_expr=spec.damage; m.exp=exp
        m.hp=m.max_hp=hp
        m.flags=rogue_monsters.parse_flags(spec.flags)
        m.pack=[]
        m.held=m.scared=m.confused=0
        m.running=False; m.dest=DEST_PLAYER; m.turn=True
        m.mean=rogue_monsters.is_mean(m.flags); m.target=False; m.found=False; m.vf_hit=0
        self.set_monster_disguise(m)
        rogue_monsters.apply_deep_haste(m, self.p.depth)
        if rogue_rings.is_wearing(self.p, rogue_rings.R_AGGR):
            self.runto(m)

    def clear_player_hold(self):
        # Rogue 5.4.4 wizard.c:teleport() clears ISHELD/vf_hit after teleporting.
        if self.p.held_by is not None:
            self.p.held_by.vf_hit = 0
            self.p.held_by.damage_expr = "0x0"
            self.p.held_by = None

    def finish_teleport(self):
        # Rogue 5.4.4 wizard.c:teleport() clears ISHELD/vf_hit, no_move, count, running.
        self.clear_player_hold()
        self.p.no_move = 0
        self.clear_running_count()

    def clear_running_count(self):
        # C: running=FALSE/count=0 in fight.c, chase.c, daemons.c, wizard.c.
        self.dashing = False
        self.dash_steps = 0

    def polymorph_monster(self,m):
        # C: sticks.c:do_zap(WS_POLYMORPH) detach(tp), then monsters.c:new_monster()
        # attach(mlist, tp) puts the rebuilt monster at list head.
        pack=m.pack
        spec=self.monster_spec_for_sym(chr(RNG.rnd(26)+ord("A")))
        if spec:
            if m in self.mons:
                self.mons.remove(m)
                self.mons.insert(0,m)
            self.set_monster_from_spec(m,spec)
            m.pack=pack

    def random_monster_floor(self,avoid=None):
        # C: rooms.c:find_floor(NULL, ..., monst=TRUE), used by sticks.c:WS_TELAWAY.
        avoid=set(avoid or ())
        avoid.add((self.p.x,self.p.y))
        return self.find_floor_pos(
            None,
            monst=True,
            avoid=avoid,
            occupied={(m.x,m.y) for m in self.mons if m.alive},
        )

    def relocate_monster(self,m,pos):
        # C: chase.c:relocate()
        if pos and self.walkable(pos[0],pos[1]) and not self.mon_at(pos[0],pos[1]):
            m.x,m.y=pos

    def cancel_monster(self,m):
        # C: sticks.c (WS_CANCEL)
        rogue_monsters.cancel_monster(m)
        if self.p.held_by is m:
            self.p.held_by=None

    def drain_targets(self):
        # C: sticks.c:drain() uses proom, plus corp when hero stands on a door.
        proom=self.room_for_ai(self.p.x,self.p.y,actor=False)
        corp=self.passage_component(self.p.x,self.p.y) if self.tm[self.p.y][self.p.x]==T_DOOR else None
        targets=[]
        for m in self.mons:
            if not m.alive:
                continue
            mroom=self.room_for_ai(m.x,m.y,actor=True)
            if self.same_ai_room(mroom,proom) or (corp is not None and self.same_ai_room(mroom,corp)):
                targets.append(m)
        return targets

    def drain_life(self):
        if self.p.hp < 2:
            self.msg("sticks.you_are_too_weak_to_use_it")
            return False
        targets=self.drain_targets()
        if not targets:
            self.msg("sticks.you_have_a_tingling_feeling")
            return True
        self.p.hp,dmg=rogue_sticks.drain_life_split(self.p.hp, len(targets))
        for m in list(targets):
            m.hp-=dmg
            if m.alive:
                self.runto(m)
            else:
                self.award_monster_kill(m)
        return True

    def hit_monster_with_magic_missile(self,m):
        self.p.quiet = 0
        self.runto(m)
        self.reveal_xeroc_for_attack(m, thrown=True)
        weapon_dam = self.p.wpn.dam_plus if self.p.wpn else 0
        dmg=rogue_sticks.magic_missile_damage(RNG.roll(1,4), weapon_dam, self.p.str_dam_plus())
        m.hp-=dmg
        mn = self.combat_monster_name(m)
        self.msg_text(self.thrown_hit_message(
            Item(CAT_STICK, rogue_sticks.WS_MISSILE),
            TextCatalog.bolt(self.lang, "magic missile"),
            mn,
        ))
        self.p.can_confuse_monster, confused_by_hit = rogue_fight.confusion_hit_effect(self.p.can_confuse_monster)
        if confused_by_hit:
            m.confused = 1
            self.msg("fight.your_hands_stop_glowing_color", color=TextCatalog.color(self.lang, "red", "stem"))
        if not m.alive:
            self.msg_text(self.defeated_message(mn))
            self.award_monster_kill(m)
        elif rogue_fight.confusion_message_allowed(confused_by_hit, self.p.blind > 0):
            self.msg("fight.subject_appears_confused", subject=mn)

    def bolt_name(self, kind):
        if kind == rogue_sticks.WS_ELECT:
            return "bolt"
        if kind == rogue_sticks.WS_FIRE:
            return "flame"
        return "ice"

    def bolt_bounces_at(self, x, y):
        return (not in_play_area(x, y)) or self.tm[y][x] in (T_VOID, T_HWALL, T_VWALL, T_DOOR)

    def hit_monster_with_bolt(self, m, name):
        self.p.quiet = 0
        self.runto(m)
        self.reveal_xeroc_for_attack(m, thrown=True)
        dmg=RNG.roll(6,6)
        m.hp-=dmg
        mn = self.combat_monster_name(m)
        self.msg_text(self.thrown_hit_message(Item(CAT_WPN, 0), TextCatalog.bolt(self.lang, name), mn))
        self.p.can_confuse_monster, confused_by_hit = rogue_fight.confusion_hit_effect(self.p.can_confuse_monster)
        if confused_by_hit:
            m.confused = 1
            self.msg("fight.your_hands_stop_glowing_color", color=TextCatalog.color(self.lang, "red", "stem"))
        if not m.alive:
            self.msg_text(self.defeated_message(mn))
            self.award_monster_kill(m)
        elif rogue_fight.confusion_message_allowed(confused_by_hit, self.p.blind > 0):
            self.msg("fight.subject_appears_confused", subject=mn)

    def fire_bolt(self, dx, dy, name):
        # Rogue 5.4.4 sticks.c:fire_bolt() bounces from walls/doors and uses 6x6 damage.
        return self.fire_bolt_from(self.p.x,self.p.y,dx,dy,name)

    def fire_bolt_from(self, start_x, start_y, dx, dy, name):
        # Rogue 5.4.4 sticks.c:fire_bolt() hit_hero is true when start != &hero.
        x,y=start_x,start_y
        hit_hero=(start_x,start_y)!=(self.p.x,self.p.y)
        hero_started=not hit_hero
        source_monster=self.mon_at(start_x,start_y) if hit_hero else None
        changed=False
        steps=0
        used=False
        bounces=0
        while steps < BOLT_LENGTH and bounces < BOLT_LENGTH * 2:
            x+=dx; y+=dy
            if hit_hero and (x,y)==(self.p.x,self.p.y):
                hit_hero=False
                changed=not changed
                if not self.save_vs_magic():
                    self.p.hp-=RNG.roll(6,6)
                    if self.p.hp<=0 and not self.death_cause:
                        killer=rogue_sticks.bolt_death_cause(hero_started, source_monster.name if source_monster else None)
                        self.death_cause=f"killed by a {killer}"
                    used=True
                    self.clamp_player_hp()
                    self.msg("sticks.you_are_hit_by_the_value", value=TextCatalog.bolt(self.lang, name))
                    return True
                self.msg("sticks.the_value_whizzes_by_you", value=TextCatalog.bolt(self.lang, name))
            target=self.mon_at(x,y)
            if target:
                steps+=1
                if not hit_hero:
                    hit_hero=True
                    changed=not changed
                    if not self.monster_save_throw(VS_MAGIC,target):
                        if target.sym=="D" and name=="flame":
                            used=True
                            self.msg("sticks.the_flame_bounces")
                            return True
                        else:
                            self.hit_monster_with_bolt(target,name)
                            return True
                    wake_miss, show_miss = rogue_sticks.saved_monster_miss_feedback(
                        hero_started,
                        self.zap_winat_char(x, y),
                        getattr(target, "disguise", target.sym),
                    )
                    if wake_miss:
                        self.runto(target)
                    if show_miss:
                        self.msg(
                            "sticks.the_value_whizzes_past_value2",
                            value=TextCatalog.bolt(self.lang, name),
                            value2=self.combat_monster_name(target),
                        )
                continue
            if rogue_sticks.bolt_should_bounce(self.bolt_bounces_at(x,y), (x,y)==(self.p.x,self.p.y)):
                if not changed:
                    hit_hero=not hit_hero
                changed=False
                dx=-dx; dy=-dy
                bounces+=1
                self.msg("sticks.the_value_bounces", value=TextCatalog.bolt(self.lang, name))
                continue
            steps+=1
        return used

    def zap_stick(self,it,dx,dy):
        # C: sticks.c:do_zap()
        if it.cat != CAT_STICK:
            self.msg("sticks.you_cant_zap_with_that")
            return False
        if it.charges <= 0:
            self.msg("sticks.nothing_happens")
            return True
        kind=it.kind
        self.request_sfx(rogue_sfx.SFX_WAND_ZAP)
        if kind == rogue_sticks.WS_LIGHT:
            self.ident.wk[kind]=True
            room=self.room_at(self.p.x,self.p.y) or self.room_containing(self.p.x,self.p.y)
            if rogue_sticks.light_uses_room_branch(bool(room and room.usable)):
                room.flags.discard(ROOM_DARK)
                self.update_fov()
                self.msg("sticks.the_room_is_lit")
            else:
                self.msg("sticks.the_corridor_glows_and_then_fades")
        elif kind == rogue_sticks.WS_NOP:
            pass
        elif kind == rogue_sticks.WS_DRAIN:
            if not self.drain_life():
                return True
        elif kind == rogue_sticks.WS_MISSILE:
            self.ident.wk[kind]=True
            target=self.first_zap_target(dx,dy,stop_at_door=True)
            if target and not self.monster_save_throw(VS_MAGIC,target):
                self.hit_monster_with_magic_missile(target)
            else:
                self.msg("sticks.the_missle_vanishes_with_a_puff_of_smoke")
        elif kind in (rogue_sticks.WS_ELECT, rogue_sticks.WS_FIRE, rogue_sticks.WS_COLD):
            self.ident.wk[kind]=True
            if kind == rogue_sticks.WS_ELECT:
                self.request_sfx(rogue_sfx.SFX_ELECTRIC)
            elif kind == rogue_sticks.WS_COLD:
                self.request_sfx(rogue_sfx.SFX_ICE)
            self.fire_bolt(dx,dy,self.bolt_name(kind))
        else:
            target=self.first_zap_target(dx,dy)
            if target:
                if rogue_sticks.zap_releases_flytrap(kind) and target.sym=="F":
                    self.p.held_by=None
                if kind == rogue_sticks.WS_INVIS:
                    rogue_monsters.make_invisible(target)
                elif kind == rogue_sticks.WS_POLYMORPH:
                    self.polymorph_monster(target)
                    if rogue_sticks.polymorph_identifies((target.x,target.y) in self.visible, self.can_see_monster(target)):
                        self.ident.wk[kind]=True
                elif kind == rogue_sticks.WS_CANCEL:
                    self.cancel_monster(target)
                elif kind == rogue_sticks.WS_HASTE_M:
                    rogue_monsters.haste_monster(target)
                    self.runto(target)
                elif kind == rogue_sticks.WS_SLOW_M:
                    rogue_monsters.slow_monster(target)
                    self.runto(target)
                elif kind == rogue_sticks.WS_TELAWAY:
                    target.running = True
                    target.dest = DEST_PLAYER
                    self.relocate_monster(target,self.random_monster_floor({(target.x,target.y)}))
                elif kind == rogue_sticks.WS_TELTO:
                    target.running = True
                    target.dest = DEST_PLAYER
                    self.relocate_monster(target,rogue_sticks.teleport_to_position((self.p.x,self.p.y),(dx,dy)))
                else:
                    self.runto(target)
        it.charges-=1
        return True

    def eat(self,it):
        # C: misc.c:eat()
        if it.cat != CAT_FOOD:
            self.msg("misc.ugh_you_would_get_ill_if_you_ate_that")
            return
        self.p.food, outcome, exp_gain = rogue_food.eat_food(
            self.p.food, it.kind, RNG.rnd, RNG.rnd, HUNGERTIME, STOMACHSIZE
        )
        self.p.state="normal"
        if it is self.p.wpn:
            self.p.wpn = None
        if outcome == "slime-mold":
            self.msg("misc.my_that_was_a_yummy_value", value=TextCatalog.item_kind(self.lang, CAT_FOOD, "slime-mold"))
        elif outcome == "awful":
            self.p.exp += exp_gain
            self.msg("misc.value_this_food_tastes_awful", value=TextCatalog.msg(self.lang, "misc.yuk"))
            if self.p.lvlup():
                self.msg_important("misc.welcome_to_level_level", level=self.p.level)
        else:
            self.msg("misc.value_that_tasted_good", value=TextCatalog.msg(self.lang, "misc.yum"))
        self.consume_pack_item(it)

    def wield(self,it):
        # C: weapons.c:wield()
        result = rogue_weapons.wield_result(
            bool(self.p.wpn and self.p.wpn.cursed),
            it.cat == CAT_ARM,
            it is self.p.wpn,
        )
        if result == "cursed":
            self.request_sfx(rogue_sfx.SFX_ERROR)
            self.msg("things.you_cant_it_appears_to_be_cursed")
            return True
        if result == "armor":
            self.msg("weapons.you_cant_wield_armor")
            return False
        if result == "current":
            self.msg_text(self.is_current_message())
            return False
        self.p.wpn=it; self.msg("pyxel.wield_item", item=self.ident.name(it))
        return True

    def is_current_message(self):
        # Rogue 5.4.4 misc.c:is_current() emits addmsg("That's already ") + msg("in use").
        return TextCatalog.msg(self.lang, "misc.that_s_already") + TextCatalog.msg(self.lang, "misc.in_use")

    def consume_pack_item(self,it):
        # C: pack.c:leave_pack(obj, FALSE, FALSE).
        if it is self.p.wpn:
            self.p.wpn = None
        is_mult = it.cat in (CAT_POT, CAT_SCR, CAT_FOOD)
        remaining_qty, _ = rogue_pack.leave_pack_counts(it.qty, is_mult, False)
        if remaining_qty:
            it.qty = remaining_qty
        else:
            self.p.rm_item(it)

    def wear(self,it):
        # C: armor.c:wear()
        result = rogue_armor.wear_result(self.p.arm is not None, it.cat == CAT_ARM)
        if result == "already-wearing":
            msg = (
                TextCatalog.msg(self.lang, "armor.you_are_already_wearing_some")
                + TextCatalog.msg(self.lang, "armor.you_ll_have_to_take_it_off_first")
            )
            self.msg_text(msg)
            return False
        if result == "not-armor":
            self.msg("armor.you_cant_wear_that")
            return True
        it.known=True
        self.waste_time()
        self.p.arm=it; self.p.recalc_ac(); self.msg("pyxel.put_on_item", item=self.ident.name(it))
        return True

    def put_on_ring(self,it):
        # C: rings.c:ring_on()
        result = rogue_rings.ring_on_result(
            it.cat == CAT_RING,
            it is self.p.ring_l or it is self.p.ring_r,
            self.p.ring_l is not None and self.p.ring_r is not None,
        )
        if result == "not-ring":
            self.msg("rings.it_would_be_difficult_to_wrap_that_around_a_finger")
            return True
        if result == "current":
            self.msg_text(self.is_current_message())
            return True
        if result == "full":
            self.msg("pyxel.already_ring_each_hand")
            return True
        if rogue_rings.put_on_ring(self.p,it):
            self.p.recalc_ac()
            if it.kind == rogue_rings.R_AGGR:
                self.aggravate_monsters()
            self.msg("pyxel.now_wearing_item", item=self.ident.name(it))
            return True
        return False

    def remove_ring_item(self,it):
        # C: things.c:dropcheck() ring branch.
        if not rogue_rings.remove_ring(self.p,it):
            return False
        if it.kind == rogue_rings.R_SEEINVIS:
            self.p.see_invisible = 0
            self.fuses.extinguish("unsee")
        self.p.recalc_ac()
        return True

    def takeoff(self,it):
        # C: armor.c:take_off()
        if it is self.p.arm:
            if it.cursed: self.request_sfx(rogue_sfx.SFX_ERROR); self.msg("pyxel.its_cursed"); return
            self.waste_time()
            self.p.arm=None; self.p.recalc_ac()
        elif it is self.p.wpn:
            if it.cursed: self.request_sfx(rogue_sfx.SFX_ERROR); self.msg("pyxel.its_cursed"); return
            self.p.wpn=None
        elif it is self.p.ring_l or it is self.p.ring_r:
            result = rogue_rings.ring_off_result(True, it.cursed)
            if result == "cursed":
                self.request_sfx(rogue_sfx.SFX_ERROR)
                self.msg("pyxel.cant_appears_cursed")
                return True
            if not self.remove_ring_item(it):
                return True
        elif it.cat == CAT_RING:
            result = rogue_rings.ring_off_result(False, it.cursed)
            if result == "not-wearing":
                self.msg("rings.not_wearing_such_a_ring")
                return True
        self.msg("pyxel.remove_item", item=self.ident.name(it))
        return True

    def drop(self,it):
        # C: things.c:drop()
        if is_nyandor_cat_item(it):
            self.msg("pyxel.nyandor_cat_drop_blocked")
            return False
        if self.tm[self.p.y][self.p.x] not in (T_FLOOR, T_CORR) or self.gi_at(self.p.x, self.p.y):
            self.msg("things.there_is_something_there_already")
            return False
        if (it is self.p.wpn or it is self.p.arm or it is self.p.ring_l or it is self.p.ring_r) and it.cursed:
            self.request_sfx(rogue_sfx.SFX_ERROR)
            self.msg("things.you_cant_it_appears_to_be_cursed"); return True
        if it is self.p.arm:
            self.waste_time()
        if it is self.p.ring_l or it is self.p.ring_r:
            self.remove_ring_item(it)
        is_mult = it.cat in (CAT_POT, CAT_SCR, CAT_FOOD)
        remaining_qty, dropped_qty = rogue_pack.leave_pack_counts(it.qty, is_mult, not is_mult)
        dropped = it
        if remaining_qty:
            it.qty = remaining_qty
            dropped = Item(it.cat, it.kind, ench=it.ench, cursed=it.cursed, qty=dropped_qty,
                           hit_plus=it.hit_plus, dam_plus=it.dam_plus, charges=it.charges,
                           known=it.known, group=it.group)
            dropped.o_flags = set(it.o_flags)
            dropped.o_label = it.o_label
            dropped.protected = it.protected
            dropped.picked_up = it.picked_up
        else:
            self.p.rm_item(it)
        dropped.x,dropped.y=self.p.x,self.p.y
        if dropped.cat == CAT_AMULET:
            self.p.has_amulet = False
        self.gitems.append(dropped); self.msg("pyxel.drop_item", item=self.ident.name(dropped))
        return True

    def waste_time(self):
        # C: armor.c:waste_time().
        self.do_before_daemons()
        self.do_after_daemons()
        self.fuses.tick_each(rogue_daemons.AFTER, self.run_fuse)

    def is_scare_monster(self,it):
        return it.cat==CAT_SCR and SCROLLS[it.kind]["name"]=="scare monster"

    def fall_position(self,x,y):
        choice=None; cnt=0
        for yy in range(y-1,y+2):
            for xx in range(x-1,x+2):
                if not (0<=xx<MAP_W and 0<=yy<MAP_H): continue
                if self.gi_at(xx,yy): continue
                tile_name = "PASSAGE" if self.tm[yy][xx] == T_CORR else "FLOOR" if self.tm[yy][xx] == T_FLOOR else ""
                if not rogue_weapons.is_fallpos_candidate((xx,yy), (self.p.x,self.p.y), tile_name):
                    continue
                choice,cnt=rogue_weapons.choose_fallpos(choice,cnt,(xx,yy),RNG.rnd)
        return choice

    def drop_thrown(self,it,x,y,around=True):
        # C: weapons.c:fall()
        pos = self.fall_position(x,y) if around else ((x,y) if self.walkable(x,y) and not self.gi_at(x,y) else None)
        result,pos=rogue_weapons.fall_result(pos, it.cat==CAT_WPN)
        if result!="drop":
            if it.cat==CAT_WPN: self.msg("pyxel.item_vanishes_as_hits_ground", item=it.data["name"])
            return
        it.x,it.y=pos; self.gitems.append(it)

    def resolve_throw_anim(self, anim):
        outcome = anim.get("outcome")
        if not outcome:
            return
        if outcome["kind"] == "floor":
            self.request_sfx(rogue_sfx.SFX_HIT_MISS)
            self.drop_thrown(outcome["item"], outcome["x"], outcome["y"], around=outcome["around"])
            return
        if outcome["kind"] != "monster":
            return
        m = outcome["monster"]
        thrown = outcome["item"]
        tx, ty = outcome["x"], outcome["y"]
        self.p.quiet = 0
        self.runto(m)
        self.reveal_xeroc_for_attack(m, thrown=True)
        hit, dmg = self.roll_player_attack(m, thrown, True)
        mn = self.combat_monster_name(m)
        item = self.ident.name(thrown)
        if hit:
            m.hp -= dmg
            self.msg_text(self.thrown_hit_message(thrown, item, mn))
            self.request_sfx(rogue_sfx.SFX_THROW_HIT)
            self.p.can_confuse_monster, confused_by_hit = rogue_fight.confusion_hit_effect(self.p.can_confuse_monster)
            if confused_by_hit:
                m.confused = 1
                self.msg("fight.your_hands_stop_glowing_color", color=TextCatalog.color(self.lang, "red", "stem"))
            if not m.alive:
                self.msg_text(self.defeated_message(mn))
                self.award_monster_kill(m, mn)
            elif rogue_fight.confusion_message_allowed(confused_by_hit, self.p.blind > 0):
                self.msg("fight.subject_appears_confused", subject=mn)
        else:
            self.msg_text(self.thrown_miss_message(thrown, item, mn))
            self.request_sfx(rogue_sfx.SFX_HIT_MISS)
            self.drop_thrown(thrown, tx, ty)

    def throw(self,it,dx,dy):
        # C: weapons.c:missile()
        p=self.p
        is_equipped = it is p.wpn or it is p.arm or it is p.ring_l or it is p.ring_r
        if rogue_things.dropcheck_result(is_equipped, it.cursed) == "cursed":
            self.msg("things.you_cant_it_appears_to_be_cursed")
            return False
        if it is p.arm:
            self.waste_time()
        if it is p.ring_l or it is p.ring_r:
            self.remove_ring_item(it)
        if it is p.wpn:
            p.wpn = None
        if it.stackable and it.qty>1:
            thrown=Item(it.cat,it.kind,ench=it.ench,cursed=it.cursed,qty=1,
                        hit_plus=it.hit_plus,dam_plus=it.dam_plus,charges=it.charges,
                        known=it.known,group=it.group)
            thrown.o_flags = set(it.o_flags)
            thrown.o_label = it.o_label
            thrown.protected = it.protected
            thrown.picked_up = it.picked_up
            it.qty-=1
        else: p.rm_item(it); thrown=it
        self.request_sfx(rogue_sfx.SFX_THROW)
        tx,ty=p.x,p.y; path=[]
        for _ in range(max(MAP_W,MAP_H)):
            nx,ny=tx+dx,ty+dy
            if not (0<=nx<MAP_W and 0<=ny<MAP_H): break
            m=self.mon_at(nx,ny)
            if m:
                tx,ty=nx,ny; path.append((tx,ty))
                self.throw_anim={"path":path,"sym":thrown.sym,"col":ICOL.get(thrown.cat,7),"tick":0,"delay":2,
                                 "outcome":{"kind":"monster","monster":m,"item":thrown,"x":tx,"y":ty}}
                self.runto(m)
                return True
            if not self.walkable(nx,ny) or self.tm[ny][nx]==T_DOOR:
                tx,ty=nx,ny
                break
            tx,ty=nx,ny; path.append((tx,ty))
        self.throw_anim={"path":path,"sym":thrown.sym,"col":ICOL.get(thrown.cat,7),"tick":0,"delay":2,
                         "outcome":{"kind":"floor","item":thrown,"x":tx,"y":ty,"around":True}}
        if not path:
            self.resolve_throw_anim(self.throw_anim)
            self.throw_anim = None
        return bool(path)

    # ---------- Movement & turns ----------
    def try_move(self, dx, dy):
        # C: move.c:do_move()
        p = self.p
        if p.held_by and not p.held_by.alive:
            p.held_by=None
        self.command_look()
        if p.no_move>0:
            p.no_move-=1
            self.msg("move.you_are_still_stuck_in_the_bear_trap")
            self.end_turn()
            return True
        if rogue_move.confused_player_uses_random_move(p.confused > 0, rnd):
            nx, ny = rogue_move.rndmove(
                (p.x, p.y),
                rnd,
                lambda src, dst: self.diag_ok(src[0], src[1], dst[0], dst[1])
                and (dst == src or self.can_player_rndmove_step(dst[0], dst[1])),
            )
            if (nx, ny) == (p.x, p.y):
                self.dashing = False
                self.clear_to_death_only()
                self.command_look_done = False
                return False
            dx, dy = nx - p.x, ny - p.y
        if dx or dy:
            p.facing=(dx,dy)
        nx, ny = p.x+dx, p.y+dy
        if not self.diag_ok(p.x,p.y,nx,ny):
            self.dashing = False
            self.command_look_done = False
            return False
        m = self.mon_at(nx, ny)
        gi = self.gi_at(nx, ny)
        hidden_floor_trap = (
            m is None
            and gi is None
            and (nx, ny) in self.traps
            and self.tm[ny][nx] == T_FLOOR
        )
        target_is_flytrap = m is not None and m.sym == "F"
        if (
            not hidden_floor_trap
            and rogue_move.held_move_blocked(p.held_by is not None, target_is_flytrap)
        ):
            self.msg("move.you_are_being_held")
            self.end_turn()
            return True
        if m: self.p_attack(m); self.end_turn(); return True
        if self.walkable(nx, ny):
            if self.tm[ny][nx] in (T_DOOR, T_STAIR) or gi:
                self.dashing = False
            old_pos = (p.x, p.y)
            p.x, p.y = nx, ny
            self.set_last_intent_dir(dx, dy)
            self.move_msg_toast_if_player_enters_margin()
            if self.tm[ny][nx] == T_STAIR:
                self.seen_stairs = True
            trapped = gi is None and (nx,ny) in self.traps and self.tm[ny][nx] in (T_FLOOR, T_TRAP)
            if trapped and p.levitating <= 0:
                self.trigger_trap(nx, ny, arrow_origin=old_pos)
                if not self.p.alive or self.st!=ST_PLAY:
                    self.end_turn()
                    return True
            move_on = getattr(self, "move_on_once", False)
            if gi and move_on and not trapped:
                self.msg("pack.moved_onto_item", item=self.ident.name(gi))
            elif gi and self.auto_pickup and not trapped:
                self.pickup_at(nx,ny)
            elif gi and not trapped:
                self.msg("pyxel.see_item_here", item=self.ident.name(gi))
            self.update_fov()
            self.update_cam(); self.end_turn(); return True
        self.command_look_done = False
        return False

    def do_search(self, front_only=False, spend_turn=True, quiet_fail=False):
        # C: command.c:search()
        if spend_turn:
            self.command_look()
        p=self.p
        dirs=[p.facing] if front_only else list(DIR8.values())
        found=False
        probinc=rogue_search.search_probinc(p.hallucinating>0, p.blind>0)
        for dx,dy in dirs:
            nx,ny=p.x+dx,p.y+dy
            if 0<=nx<MAP_W and 0<=ny<MAP_H:
                hidden=self.hidden_tiles.get((nx,ny))
                if hidden==T_DOOR and rogue_search.reveals_secret_door(rnd(5+probinc), probinc):
                    found = self.reveal_hidden_at(nx,ny) or found
                    if found:
                        self.request_sfx(rogue_sfx.SFX_SECRET_DOOR)
                        self.msg("command.a_secret_door")
                elif hidden==T_CORR and rogue_search.reveals_secret_passage(rnd(3+probinc), probinc):
                    found = self.reveal_hidden_at(nx,ny) or found
                elif (
                    (nx,ny) in self.traps
                    and self.tm[ny][nx] == T_FLOOR
                    and not self.gi_at(nx, ny)
                    and rogue_search.reveals_trap(rnd(2+probinc), probinc)
                ):
                    trap = self.traps[(nx,ny)]
                    found = self.reveal_trap_at(nx,ny) or found
                    if found:
                        if p.hallucinating > 0:
                            trap = rnd(len(TRAPS))
                        self.msg_important("pyxel.have_found_trap", trap=self.trap_name(trap))
        if found:
            self.update_fov()
        if spend_turn:
            self.end_turn()

    def trap_hits(self, at_lvl):
        # C: move.c:be_trapped() uses pstats.s_arm, not cur_armor->o_arm.
        return self.swing_hits(at_lvl, 10, 1)

    def save_vs_poison(self):
        return rogue_monsters.save_throw(0,self.p.level,RNG.roll)

    def drop_arrow_at_player(self, origin=None):
        arrow=Item(CAT_WPN,3,qty=1)
        # C: move.c:T_ARROW falls via weapons.c:fall()/fallpos().
        x, y = origin if origin is not None else (self.p.x, self.p.y)
        self.drop_thrown(arrow, x, y)

    def teleport_player(self):
        # C: wizard.c:teleport() via scrolls.c:S_TELEP / move.c:T_TEL.
        pos = self.find_floor_pos(
            None,
            monst=True,
            occupied={(m.x,m.y) for m in self.mons if m.alive},
        )
        if pos is not None:
            self.p.x,self.p.y=pos
            self.update_fov(); self._center_cam()
            self.request_sfx(rogue_sfx.SFX_WARP)
            self.finish_teleport()

    def trigger_trap(self, x, y, arrow_origin=None):
        # C: move.c:be_trapped()
        self.reveal_trap_at(x,y)
        self.request_sfx(rogue_sfx.SFX_ALARM)
        kind=self.traps.get((x,y),0)
        name=TRAPS[kind]["name"] if 0<=kind<len(TRAPS) else ""
        self.clear_running_count()
        if name=="trap door":
            self.msg_alarm("move.you_fell_into_a_trap")
            self.descend(play_stairs_sfx=False)
        elif name=="bear trap":
            self.p.no_move=rogue_move.bear_trap_no_move(self.p.no_move, BEARTIME)
            self.msg_alarm("move.you_are_caught_in_a_bear_trap")
        elif name=="sleeping gas trap":
            self.p.no_command=rogue_move.sleep_trap_no_command(self.p.no_command, SLEEPTIME)
            self.msg_alarm("move.a_strange_white_mist_envelops_you_and_you_fall_asleep")
        elif name=="arrow trap":
            if self.trap_hits(self.p.level-1):
                self.p.hp-=roll("1d6")
                if self.p.hp<=0 and not self.death_cause:
                    self.death_cause="an arrow killed you"
                    self.msg_alarm("move.an_arrow_killed_you")
                    self.clamp_player_hp()
                else:
                    self.msg("move.oh_no_an_arrow_shot_you")
            else:
                self.drop_arrow_at_player(arrow_origin)
                self.msg("move.an_arrow_shoots_past_you")
        elif name=="teleport trap":
            self.teleport_player()
        elif name=="dart trap":
            if self.trap_hits(self.p.level+1):
                self.p.hp-=roll("1d4")
                if self.p.hp<=0 and not self.death_cause:
                    self.death_cause="a poisoned dart killed you"
                    self.msg_alarm("move.a_poisoned_dart_killed_you")
                    self.clamp_player_hp()
                    return
                poison_saved = self.save_vs_poison()
                self.p.st = rogue_move.dart_poison_strength(
                    self.p.st,
                    poison_saved,
                    rogue_rings.is_wearing(self.p, rogue_rings.R_SUSTSTR),
                )
                if poison_saved or rogue_rings.is_wearing(self.p, rogue_rings.R_SUSTSTR):
                    self.msg("move.a_small_dart_just_hit_you_in_the_shoulder")
                else:
                    self.msg_alarm("move.a_small_dart_just_hit_you_in_the_shoulder")
            else:
                self.msg("move.a_small_dart_whizzes_by_your_ear_and_vanishes")
        elif name=="rust trap":
            self.msg("move.a_gush_of_water_hits_you_on_the_head")
            self.rust_armor()
        elif name=="mysterious trap":
            self.mysterious_trap_msg()

    def rust_armor(self, important=False):
        # C: move.c:rust_armor()
        arm=self.p.arm
        if not self.can_rust_armor(arm):
            return
        result = rogue_move.rust_armor_result(
            arm.protected,
            rogue_rings.is_wearing(self.p, rogue_rings.R_SUSTARM),
        )
        if result == "vanish":
            if important:
                self.msg_alarm("move.the_rust_vanishes_instantly")
            else:
                self.msg("move.the_rust_vanishes_instantly")
            return
        arm.ench-=1
        self.p.recalc_ac()
        if important:
            self.msg_alarm("move.your_armor_weakens")
        else:
            self.msg("move.your_armor_weakens")

    def can_rust_armor(self, arm):
        # C: move.c:rust_armor() skips NULL, non-armor, LEATHER, and o_arm >= 9.
        return bool(arm) and rogue_move.can_rust_armor(
            arm.cat == CAT_ARM,
            arm.data["name"] == "leather armor",
            arm.data["ac"] - arm.ench,
        )

    def mysterious_trap_msg(self):
        key,arg=rogue_move.mysterious_trap_message(rnd(11))
        kw = {}
        if arg in ("color", "value"):
            color = RAINBOW[rnd(len(RAINBOW))]
            form = "adjective" if key == "move.a_color_light_flashes_in_your_eyes" else "noun"
            kw[arg] = TextCatalog.color(self.lang, color, form)
        self.msg(key,**kw)

    def inspect_trap(self,dx,dy):
        self.command_look()
        x,y=self.p.x+dx,self.p.y+dy
        trap=self.visible_trap_at(x,y)
        if trap is None:
            self.msg("command.no_trap_there")
        else:
            if self.p.hallucinating > 0:
                trap = rnd(len(TRAPS))
            self.msg_important("pyxel.have_found_trap", trap=self.trap_name(trap))
        self.command_look_done = False

    def open_help_command(self):
        self.command_look()
        self.help_return_state = ST_PLAY
        self.st = ST_HELP
        self.command_look_done = False

    def open_symbol_identify_command(self):
        self.command_look()
        self.msg("command.what_do_you_want_identified")
        self.identify_symbol_pending = True
        self.command_look_done = False

    def picky_inventory_line(self, it):
        return f"{self.pack_letter_for(it)}) {self.ident.name(it)}"

    def open_picky_inventory_command(self):
        # Rogue 5.4.4 pack.c:picky_inven() inventories one chosen pack item.
        self.command_look()
        if not self.p.inv:
            self.msg("pack.you_arent_carrying_anything")
            self.command_look_done = False
            return
        if len(self.p.inv) == 1:
            self.msg_text(self.picky_inventory_line(self.p.inv[0]))
            self.command_look_done = False
            return
        self.cact = "Picky inventory"
        self.fitems = list(self.p.inv)
        self.icur = 0
        self.st = ST_ITEM
        self.msg("pack.which_item_do_you_wish_to_inventory")
        self.command_look_done = False

    def symbol_description(self, ch):
        unknown = "知らない文字" if self.lang == LANG_JA else "unknown character"
        if len(ch) == 1 and "A" <= ch <= "Z":
            spec = self.monster_spec_for_sym(ch)
            return TextCatalog.monster(self.lang, spec.name) if spec else unknown
        table = SYMBOL_DESC_JA if self.lang == LANG_JA else SYMBOL_DESC_EN
        return table.get(ch, unknown)

    def symbol_identify_key_press(self):
        if self.kp(getattr(pyxel, "KEY_ESCAPE", None)):
            return ""
        if self.kp(getattr(pyxel, "KEY_SPACE", None)):
            return " "
        if self.kp(getattr(pyxel, "KEY_AT", None)):
            return "@"
        if self.kp(getattr(pyxel, "KEY_PERIOD", None)):
            return "."
        if self.kp(getattr(pyxel, "KEY_COMMA", None)):
            return ","
        if self.kp(getattr(pyxel, "KEY_MINUS", None)):
            return "-"
        if self.kp(getattr(pyxel, "KEY_EQUALS", None)):
            return "="
        if self.kp(getattr(pyxel, "KEY_RIGHTBRACKET", None)):
            return "]"
        if self.kp(getattr(pyxel, "KEY_0", None)) and self.shift_held():
            return ")"
        if self.kp(getattr(pyxel, "KEY_6", None)) and self.shift_held():
            return "^"
        if self.kp(getattr(pyxel, "KEY_QUESTION", None)):
            return "?"
        if self.key_lower(getattr(pyxel, "KEY_SLASH", None)):
            return "/"
        for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            key = getattr(pyxel, f"KEY_{c}", None)
            if key is not None and self.kp(key):
                return c if self.shift_held() else c.lower()
        return None

    def update_symbol_identify_prompt(self):
        ch = self.symbol_identify_key_press()
        if ch is None:
            return True
        self.identify_symbol_pending = False
        if ch == "":
            return True
        self.msg("command.value_value2_2", value=ch, value2=self.symbol_description(ch))
        return True

    def show_version_command(self):
        self.command_look()
        self.msg("command.version_version_mctesq_was_here", version=UI_BUILD)
        self.command_look_done = False

    def open_options_command(self):
        self.command_look()
        self.open_settings()
        self.command_look_done = False

    def start_move_on_command(self):
        self.command_look()
        self.cact = "Move"
        self.dact = "Move"
        self.st = ST_DIR
        self.dir_pending = None

    def execute_move_on(self, dx, dy):
        self.move_on_once = True
        try:
            return self.try_move(dx,dy)
        finally:
            self.move_on_once = False

    def pack_letter_for(self, it):
        try:
            idx = self.p.inv.index(it)
        except ValueError:
            return "?"
        return chr(ord("a") + idx)

    def append_current_message(self, cur, how_en, where_en=None, how_ja=None, where_ja=None):
        how = how_ja if self.lang == LANG_JA and how_ja else how_en
        where = where_ja if self.lang == LANG_JA and where_ja else where_en
        where = f" {where}" if where else ""
        if cur is None:
            value = f"you are {how} nothing" if self.lang == LANG_EN else f"{how} 何もない"
            self.msg("command.value_value2", value=value, value2=where)
            return
        letter = self.pack_letter_for(cur)
        if self.lang == LANG_EN:
            value = f"you are {how} ("
            value2 = f"{letter}) {self.ident.name(cur)}{where}"
        else:
            value = f"{how}（"
            value2 = f"{letter}）{self.ident.name(cur)}{where}"
        self.msg("command.value_value2", value=value, value2=value2)

    def current_item_command(self, cur, how_en, where_en=None, how_ja=None, where_ja=None):
        self.command_look()
        self.append_current_message(cur, how_en, where_en, how_ja, where_ja)
        self.command_look_done = False

    def current_rings_command(self):
        self.command_look()
        self.append_current_message(self.p.ring_l, "wearing", "on left hand", "装着中", "左手")
        self.append_current_message(self.p.ring_r, "wearing", "on right hand", "装着中", "右手")
        self.command_look_done = False

    def status_command(self):
        self.command_look()
        self.command_look_done = False

    def quit_command(self):
        self.command_look()
        self.st = ST_QUIT_CONFIRM
        self.command_look_done = False

    def save_command(self):
        self.command_look()
        self.save_confirm_return_state = ST_PLAY
        self.st = ST_SAVE_CONFIRM
        self.command_look_done = False

    def repeat_message_command(self):
        # C: command.c:command() CTRL('P') dispatches msg(huh), the previous message.
        last = self.msgs[-1] if self.msgs else ""
        self.command_look()
        self.msg_text(last)
        self.command_look_done = False

    def redraw_command(self):
        self.command_look()
        self.command_look_done = False

    def legal_space_command(self):
        self.command_look()
        self.command_look_done = False

    def ctrl_command_press(self):
        if not self.ctrl_held():
            return None
        if self.kp(getattr(pyxel, "KEY_P", None)):
            return "repeat"
        if self.kp(getattr(pyxel, "KEY_R", None)):
            return "redraw"
        return None

    def legal_space_command_press(self):
        return (
            self.kp(getattr(pyxel, "KEY_SPACE", None))
            and not self.start_held()
            and not self.ctrl_held()
            and not self.dir_held_any()
        )

    def illegal_command(self, command):
        self.command_look()
        self.request_sfx(rogue_sfx.SFX_ERROR)
        self.msg("command.illegal_command_command", command=command)
        self.command_look_done = False

    def illegal_command_press(self):
        for key_name, command in (("KEY_G", "g"),):
            key = getattr(pyxel, key_name, None)
            if key is not None and self.key_lower(key):
                return command
        return None

    def do_action(self):
        self.do_pickup()

    def do_pickup(self):
        self.command_look()
        p=self.p; px,py=p.x,p.y
        if self.tm[py][px]==T_STAIR:
            self.use_stairs(); return
        if self.pickup_at(px,py):
            self.end_turn()
        else:
            self.msg("pyxel.nothing_here")

    def use_stairs(self):
        p=self.p
        if self.levit_check():
            return
        if p.has_amulet:
            if p.depth <= 1:
                self.msg(variant_escape_message_key())
                self.enter_result_state("winner")
                return
            p.depth-=2
            self.descend()
            self.msg("pyxel.wrenching_sensation_gut")
            self.end_turn()
            return
        if is_nyandor_variant() and p.depth >= NYANDOR_TARGET_DEPTH:
            self.msg("pyxel.nyandor_depth_limit")
            return
        self.descend()
        self.end_turn()

    def stairs_down_command(self):
        # Rogue 5.4.4 command.c:d_level() goes down on stairs regardless of amulet.
        self.command_look()
        if self.levit_check():
            self.command_look_done = False
            return
        if self.tm[self.p.y][self.p.x] != T_STAIR:
            self.msg("command.i_see_no_way_down")
            self.command_look_done = False
            return
        if is_nyandor_variant() and self.p.depth >= NYANDOR_TARGET_DEPTH:
            self.msg("pyxel.nyandor_depth_limit")
            self.command_look_done = False
            return
        self.descend()
        self.command_look_done = False
        self.end_turn()

    def stairs_up_command(self):
        # Rogue 5.4.4 command.c:u_level() only goes up when carrying the amulet.
        self.command_look()
        if self.levit_check():
            self.command_look_done = False
            return
        if self.tm[self.p.y][self.p.x] != T_STAIR:
            self.msg("command.i_see_no_way_up")
            self.command_look_done = False
            return
        if not self.p.has_amulet:
            self.msg("command.your_way_is_magically_blocked")
            self.command_look_done = False
            return
        if self.p.depth <= 1:
            self.msg(variant_escape_message_key())
            self.command_look_done = False
            self.enter_result_state("winner")
            return
        self.p.depth -= 2
        self.descend()
        self.msg("pyxel.wrenching_sensation_gut")
        self.command_look_done = False
        self.end_turn()

    def pickup_at(self,x,y):
        # C: pack.c:pick_up()
        p=self.p
        gi=self.gi_at(x,y)
        if not gi:
            return False
        if self.levit_check():
            return False
        if gi.cat==CAT_GOLD:
            p.gold+=gi.qty; self.gitems.remove(gi); self.msg("pyxel.gold_pieces", gold=gi.qty)
            self.request_sfx(rogue_sfx.SFX_PICKUP)
            return True
        if self.is_scare_monster(gi):
            scare_result=rogue_pack.scare_scroll_pickup_result(gi.picked_up)
            if scare_result=="dust":
                self.gitems.remove(gi)
                self.ident.sk[gi.kind]=True
                self.msg("pack.the_scroll_turns_to_dust_as_you_pick_it_up")
                return True
        was_picked_up = gi.picked_up
        gi.picked_up=True
        if p.add_item(gi):
            if gi.cat==CAT_AMULET:
                p.has_amulet=True
            self.mark_type_discovered(gi)
            self.gitems.remove(gi)
            if is_nyandor_cat_item(gi):
                self.msg("pyxel.nyandor_cat_recovered")
            else:
                self.msg("pyxel.pick_up_item", item=self.ident.name(gi))
            self.request_sfx(rogue_sfx.SFX_PICKUP)
            return True
        gi.picked_up = was_picked_up
        self.msg_important("pyxel.pack_too_full")
        return True

    def do_wait(self):
        self.command_look()
        self.end_turn()

    def ring_after_turn(self):
        for hand in (rogue_rings.LEFT, rogue_rings.RIGHT):
            ring = rogue_rings.equipped_ring(self.p, hand)
            if rogue_rings.is_ring(ring, rogue_rings.R_SEARCH):
                self.do_search(spend_turn=False, quiet_fail=True)
            elif rogue_rings.is_ring(ring, rogue_rings.R_TELEPORT) and rnd(50)==0:
                self.teleport_player()

    def end_turn(self):
        self.command_look_done = False
        msg_start = min(getattr(self, "turn_msg_start", 0), len(self.msg_turns))
        if self.p.haste > 0 and not self.haste_half_turn:
            # Rogue 5.4.4 command.c:command() gives ISHASTE two player actions
            # before do_fuses(AFTER) and monster/daemon work advance.
            self.do_before_daemons()
            if self.p.no_command > 0:
                self.decrement_no_command()
                self.haste_no_command_half_turn = True
            self.haste_half_turn = True
            return
        skip_before_daemons = self.haste_half_turn
        self.haste_half_turn = False
        self.haste_no_command_half_turn = False
        self.turn+=1
        for i in range(msg_start, len(self.msg_turns)):
            self.msg_turns[i] = self.turn
        if not skip_before_daemons:
            self.do_before_daemons()
        self.decrement_no_command()
        if self.p.confused>0 and self.fuses.remaining("unconfuse")==0:
            self.p.confused-=1
        if self.p.blind>0 and self.fuses.remaining("sight")==0:
            self.p.blind-=1
        if self.p.see_invisible>0 and self.fuses.remaining("unsee")==0:
            self.p.see_invisible-=1
        if getattr(self.p, "see_monsters", 0)>0 and self.fuses.remaining("turn_see")==0:
            self.p.see_monsters-=1
        if self.p.hallucinating>0 and self.fuses.remaining("come_down")==0:
            self.p.hallucinating-=1
            if self.p.hallucinating==0:
                self.msg("daemons.everything_looks_so_boring_now")
        if self.p.levitating>0 and self.fuses.remaining("land")==0:
            self.p.levitating-=1
            if self.p.levitating==0:
                _, message_key = rogue_daemons.land_state(self.p.hallucinating > 0)
                self.msg(message_key)
        self.do_after_daemons()
        due_fuses = []
        self.fuses.tick_each(rogue_daemons.AFTER, lambda name: (due_fuses.append(name), self.run_fuse(name)))
        if "nohaste" not in due_fuses and self.p.haste>0:
            remaining = self.fuses.remaining("nohaste")
            if remaining:
                self.p.haste = remaining
            else:
                self.p.haste -= 1
                if self.p.haste == 0:
                    self.msg("daemons.you_feel_yourself_slowing_down")
        self.ring_after_turn()
        self.mons=[mo for mo in self.mons if mo.alive]
        if not self.p.alive:
            if not self.death_cause: self.death_cause="died"
            self.msg_important("pyxel.died_restart"); self.enter_result_state("killed")
        if self.st == ST_PLAY:
            self.update_dungeon_bgm()
        self.turn_msg_start = len(self.msgs)

    def decrement_no_command(self):
        # C: command.c:command() --no_command inside the per-action loop.
        if self.p.no_command > 0:
            self.p.no_command -= 1
            if self.p.no_command == 0:
                self.msg("command.you_can_move_again")

    def do_before_daemons(self):
        # Rogue 5.4.4 command.c calls do_daemons(BEFORE), then do_fuses(BEFORE).
        self.daemons.tick_each(rogue_daemons.BEFORE, self.run_daemon)
        self.fuses.tick_each(rogue_daemons.BEFORE, self.run_fuse)
        self.wander_timer = self.fuses.remaining("swander")

    def run_fuse(self, name):
        if name == "unconfuse":
            self.unconfuse()
        elif name == "sight":
            self.sight()
        elif name == "turn_see":
            self.p.see_monsters = rogue_potions.turn_see_state(True, HUHDURATION)
        elif name == "unsee":
            self.p.see_invisible = rogue_daemons.unsee_state()
        elif name == "come_down":
            self.come_down()
        elif name == "land":
            self.land()
        elif name == "nohaste":
            self.nohaste()
        elif name == "swander":
            self.swander()

    def swander(self):
        # C: daemons.c:swander()
        rogue_daemons.swander(self.delayed_actions)

    def roll_wanderer(self):
        # C: daemons.c:rollwand()
        self.wander_between = rogue_daemons.rollwand(
            self.delayed_actions,
            RNG,
            self.wander_between,
            lambda: RNG.spread(WANDERTIME),
            self.spawn_wanderer,
        )
        self.wander_timer=self.fuses.remaining("swander")

    def do_after_daemons(self):
        # Rogue 5.4.4 command.c calls do_daemons(AFTER) before do_fuses(AFTER).
        self.daemons.tick_each(rogue_daemons.AFTER, self.run_daemon)

    def run_daemon(self, name):
        if name == "rollwand":
            self.roll_wanderer()
        elif name == "doctor":
            self.p.heal_tick()
        elif name == "stomach":
            self.run_stomach()
        elif name == "runners":
            self.run_runners()
        elif name == "visuals":
            self.run_visuals()

    def run_runners(self):
        # C: chase.c:runners()
        rogue_chase.runners(self.mons, self.m_turn, self.clear_to_death_only)

    def clear_hallucination_visuals(self):
        self.hallu_item_syms = {}
        self.hallu_tile_syms = {}
        self.hallu_monster_syms = {}
        self.hallu_detected_monster_syms = {}

    def run_visuals(self):
        # C: daemons.c:visuals()
        self.clear_hallucination_visuals()
        if self.p.hallucinating <= 0:
            return
        can_see_cells = self.p.blind <= 0
        for item in self.gitems:
            if can_see_cells and (item.x, item.y) in self.visible:
                self.hallu_item_syms[id(item)] = self.hallucination_thing_sym()
        if can_see_cells and not getattr(self, "seen_stairs", False):
            for y, row in enumerate(self.tm):
                for x, tile in enumerate(row):
                    if tile == T_STAIR and (x, y) in self.visible:
                        self.hallu_tile_syms[(x, y)] = self.hallucination_thing_sym()
        for monster in self.mons:
            if self.monster_is_seen(monster):
                if monster.sym == "X" and getattr(monster, "disguise", monster.sym) != "X":
                    self.hallu_monster_syms[id(monster)] = self.hallucination_thing_sym()
                else:
                    self.hallu_monster_syms[id(monster)] = chr(ord("A") + rnd(26))
            elif self.can_detect_monsters():
                self.hallu_detected_monster_syms[id(monster)] = chr(ord("A") + rnd(26))

    def run_stomach(self):
        # C: daemons.c:stomach()
        old_state = self.p.state
        m=self.p.hunger()
        if m:
            self.msg_bad(m)
        if rogue_daemons.stomach_stops_running(old_state, self.p.state):
            self.clear_running_count()
            self.clear_to_death_only()
        if self.p.hp<=0 and not self.death_cause:
            self.death_cause="starved to death"
        self.clamp_player_hp()

    def clamp_player_hp(self):
        if hasattr(self, "p") and self.p.hp < 0:
            self.p.hp = 0

    # ---------- Dash ----------
    def dash_turn_ok(self,x,y):
        return 0<=x<MAP_W and 0<=y<MAP_H and (self.tm[y][x] == T_DOOR or self.tile_has_pass_flag(x,y))

    def dash_door_stop(self,dx,dy):
        if self.dash_steps<1 or not self.room_at(self.p.x,self.p.y):
            return False
        px,py=self.p.x,self.p.y
        for oy in (-1,0,1):
            for ox in (-1,0,1):
                if ox==0 and oy==0: continue
                x,y=px+ox,py+oy
                if not(0<=x<MAP_W and 0<=y<MAP_H): continue
                if self.tm[y][x]!=T_DOOR: continue
                if not self._dash_ahead(dx,dy,ox,oy): continue
                if dx and not dy and ox!=0: continue
                if dy and not dx and oy!=0: continue
                return True
        return False

    def _dash_ahead(self,dx,dy,ox,oy):
        if dx and dy:
            if dx==dy:
                return ox+oy == dx+dy
            return oy-ox == dy-dx
        if dx:
            return ox==dx or ox==0
        if dy:
            return oy==dy or oy==0
        return False

    def dash_look_ignore(self,dx,dy,ox,oy):
        if dx == -1 and dy == 0:
            return ox == 1
        if dx == 1 and dy == 0:
            return ox == -1
        if dx == 0 and dy == -1:
            return oy == 1
        if dx == 0 and dy == 1:
            return oy == -1
        if dx == -1 and dy == -1:
            return ox + oy >= 1
        if dx == 1 and dy == -1:
            return oy - ox >= 1
        if dx == 1 and dy == 1:
            return ox + oy <= -1
        if dx == -1 and dy == 1:
            return oy - ox <= -1
        return False

    def dash_look_stop(self,dx,dy):
        if self.dash_steps<1 or self.p.blind>0:
            return False
        px,py=self.p.x,self.p.y
        passcount=0
        for oy in (-1,0,1):
            for ox in (-1,0,1):
                if ox==0 and oy==0: continue
                if self.dash_look_ignore(dx,dy,ox,oy): continue
                x,y=px+ox,py+oy
                if not(0<=x<MAP_W and 0<=y<MAP_H): continue
                if not rogue_vision.look_cell_visible(
                    self.tm[py][px],
                    self.tm[y][x],
                    ox,
                    oy,
                    self.tm[y][px],
                    self.tm[py][x],
                    self.tile_has_pass_flag(px, py),
                    self.tile_has_pass_flag(x, y),
                ):
                    continue
                if (x,y) in self.visible and (self.gi_at(x,y) or self.mon_at(x,y)):
                    return True
                tile=self.tm[y][x]
                if tile==T_DOOR:
                    if x==px or y==py:
                        return True
                elif tile==T_CORR:
                    if x==px or y==py:
                        passcount+=1
                elif tile not in (T_FLOOR,T_HWALL,T_VWALL,T_VOID):
                    return True
        return passcount>1

    def next_dash_dir(self,dx,dy):
        if dx and dy: return None
        px,py=self.p.x,self.p.y
        if dx:
            opts=[(0,-1),(0,1)]
        elif dy:
            opts=[(-1,0),(1,0)]
        else:
            return None
        turns=[d for d in opts if self.dash_turn_ok(px+d[0],py+d[1])]
        return turns[0] if len(turns)==1 else None

    def dash_should_stop_here(self,dx,dy):
        px,py=self.p.x,self.p.y
        tile=self.tm[py][px]
        if tile in (T_DOOR,T_STAIR): return True
        if self.gi_at(px,py): return True
        if self.dash_look_stop(dx,dy): return True
        if self.dash_door_stop(dx,dy): return True
        if not self.tile_has_pass_flag(px,py): return False
        if dx and dy: return False
        fwd=self.dash_turn_ok(px+dx,py+dy)
        if dx:
            sides=[(0,-1),(0,1)]
        else:
            sides=[(-1,0),(1,0)]
        side_dirs=[d for d in sides if self.dash_turn_ok(px+d[0],py+d[1])]
        if fwd and side_dirs:
            return True
        if not fwd:
            nd=self.next_dash_dir(dx,dy)
            if nd:
                self.dash_d=nd
                return False
            return True
        return False

    def dash_step(self):
        dx,dy=self.dash_d
        nx,ny=self.p.x+dx,self.p.y+dy
        next_mon=self.mon_at(nx,ny)
        if not self.walkable(nx,ny) and not next_mon:
            nd=self.next_dash_dir(dx,dy)
            if not nd:
                self.dash_state.stop(); return
            self.dash_d=nd
            dx,dy=nd
        ox,oy=self.p.x,self.p.y
        moved=self.try_move(dx,dy)
        if not moved or (self.p.x,self.p.y)==(ox,oy) or self.st!=ST_PLAY or not self.p.alive:
            self.dash_state.stop(); return
        self.dash_steps += 1
        self.dashing = not self.dash_should_stop_here(dx,dy)
        if not self.dashing:
            self.dash_restart_guard = True

    # ---------- Menu logic ----------
    def restorable_menu_actions(self):
        return ("Quaff", "Read", "Eat", "Zap", "Throw")

    def get_item_actions(self):
        return ("Quaff", "Read", "Eat", "Wield", "Wear", "Put on", "Zap", "Throw", "Drop", "Call")

    def action_index_by_name(self, name):
        for i, (action_name, _cat) in enumerate(MENU_ACTIONS):
            if action_name == name:
                return i
        return None

    def open_menu(self):
        self.request_sfx(rogue_sfx.SFX_SELECT_HIGH)
        restored = getattr(self, "last_menu_action", None)
        restored_index = self.action_index_by_name(restored) if restored in self.restorable_menu_actions() else None
        self.st=ST_MENU
        self.mcur=restored_index if restored_index is not None else pad_menu_initial_index(MENU_ACTIONS)
        self.menu_cursor_restored=restored_index is not None
        self.dir_pending=None
        self.b_menu_guard=self.kh(pyxel.GAMEPAD1_BUTTON_B)
    def close_menu(self):
        self.st=ST_PLAY; self.mcur=self.icur=0; self.cact=None; self.dact=None; self.fitems=[]
        self.throw_dir=None; self.zap_dir=None; self.zap_item=None; self.action_origin=ST_PLAY
        self.call_item=None; self.call_input=""; self.call_preset_idx=0
        self.b_menu_guard=False; self.dir_pending=None; self.command_look_done=False
        self.menu_cursor_restored=False

    def menu_select(self):
        self.request_sfx(rogue_sfx.SFX_SELECT_HIGH)
        aname, _cat = MENU_ACTIONS[self.mcur]
        self.last_menu_action = aname if aname in self.restorable_menu_actions() else None
        if aname=="Discoveries":
            self.open_discoveries()
            return
        if aname=="Search":
            self.st = ST_PLAY
            self.do_search()
            return
        if aname=="Trap":
            self.start_trap_inspect()
            return
        if aname=="Quit":
            self.quit_command()
            return
        self.start_item_action(aname)

    def start_item_action(self, aname):
        if self.st in (ST_PLAY, ST_MENU):
            self.command_look()
        self.action_origin = self.st
        self.cact = aname; p = self.p
        if aname in ("Take off", "Take off armor"):
            self.fitems=[p.arm] if p.arm is not None else []
        elif aname=="Remove ring":
            self.fitems=[i for i in (p.ring_l, p.ring_r) if i is not None]
        elif aname in self.get_item_actions():
            self.fitems=list(p.inv)
        else:
            self.fitems=list(p.inv)
        if (
            not self.fitems
            and not p.inv
            and aname in self.get_item_actions()
        ):
            self.msg("pack.you_arent_carrying_anything"); self.close_menu(); return
        if aname in ("Take off", "Take off armor") and not self.fitems:
            self.msg("armor.you_arent_wearing_any_armor"); self.close_menu(); return
        if aname=="Remove ring" and not self.fitems:
            self.msg("rings.you_arent_wearing_any_rings"); self.close_menu(); return
        if aname in ("Throw", "Zap"):
            self.icur, self.item_cursor_restored = self.initial_item_cursor(aname)
            self.throw_dir=None
            self.zap_dir=None
            self.zap_item=None
            self.dact=aname
            self.st=ST_DIR
            return
        if not self.fitems:
            self.msg(self.nothing_to_action_msg_key(aname), action=TextCatalog.action(self.lang, aname)); self.close_menu(); return
        self.icur, self.item_cursor_restored = self.initial_item_cursor(aname)
        if aname=="Call":
            self.call_item=None; self.call_input=CALL_PRESETS[0]; self.call_preset_idx=0
            self.st=ST_CALL
        else:
            self.st=ST_ITEM

    def nothing_to_action_msg_key(self, aname):
        return {
            "Call": "pyxel.nothing_to_call",
            "Eat": "pyxel.nothing_to_eat",
            "Put on": "rings.no_rings",
            "Quaff": "pyxel.nothing_to_quaff",
            "Read": "scrolls.nothing_to_read",
            "Wear": "pyxel.nothing_to_wear",
            "Wield": "pyxel.nothing_to_wield",
            "Zap": "pyxel.nothing_to_zap",
        }.get(aname, "pyxel.nothing_to_action")

    def item_confirm(self):
        if not self.fitems: self.close_menu(); return
        self.confirm_item(self.fitems[self.icur])

    def initial_item_cursor(self, action):
        last = getattr(self, "last_item_by_action", {}).get(action)
        if last in self.fitems:
            return self.fitems.index(last), True
        return 0, False

    def remember_item_cursor(self, action, item):
        if not hasattr(self, "last_item_by_action"):
            self.last_item_by_action = {}
        self.last_item_by_action[action] = item

    def confirm_item(self, it):
        a=self.cact
        self.remember_repeat_item(it)
        if a=="Throw":
            if self.throw_dir:
                self.command_look()
                dx,dy=self.throw_dir
                self.p.facing=(dx,dy)
                self.remember_item_cursor(a, it)
                animating = self.throw(it,dx,dy)
                self.clear_repeat_item_if_gone(it)
                self.close_menu()
                if animating:
                    self.turn_after_throw_anim = True
                else:
                    self.end_turn()
            else:
                self.dact="Throw"; self.st=ST_DIR
            return
        if a=="Zap":
            if getattr(self, "zap_dir", None):
                self.command_look()
                dx,dy=self.zap_dir
                self.p.facing=(dx,dy)
                self.remember_item_cursor(a, it)
                self.zap_item=it
                spent_turn = self.zap_stick(it,dx,dy)
                self.clear_repeat_item_if_gone(it)
                self.close_menu()
                if spent_turn:
                    self.end_turn()
            else:
                self.dact="Zap"; self.st=ST_DIR
            return
        if a=="Identify":
            # Rogue 5.4.4 wizard.c:whatis() — player selected item to identify.
            self.set_know(it)
            self.msg("pyxel.it_is_item", item=self.ident.name(it))
            self.close_menu(); self.end_turn()
            return
        if a=="Picky inventory":
            self.msg_text(self.picky_inventory_line(it))
            self.close_menu()
            return
        self.command_look()
        if a=="Quaff":
            if self.use_pot(it) is False:
                self.close_menu()
                return
            self.remember_item_cursor(a, it)
        elif a=="Read":
            read_result = self.use_scr(it)
            if read_result:
                self.remember_item_cursor(a, it)
                return  # use_scr set up next picker state; don't close yet.
            if it.cat == CAT_SCR:
                self.remember_item_cursor(a, it)
        elif a=="Eat":
            self.eat(it)
            self.remember_item_cursor(a, it)
        elif a=="Wield":
            if self.wield(it) is False:
                self.close_menu()
                return
            self.remember_item_cursor(a, it)
        elif a=="Wear":
            if self.wear(it) is False:
                self.close_menu()
                return
            self.remember_item_cursor(a, it)
        elif a=="Put on":
            if self.put_on_ring(it) is False:
                self.close_menu()
                return
            self.remember_item_cursor(a, it)
        elif a in ("Take off", "Take off armor", "Remove ring"):
            if self.takeoff(it) is False:
                self.close_menu()
                return
            self.remember_item_cursor(a, it)
        elif a=="Drop":
            if self.drop(it) is False:
                self.close_menu()
                return
            self.remember_item_cursor(a, it)
        self.clear_repeat_item_if_gone(it)
        self.close_menu(); self.end_turn()

    def dir_confirm(self,dx,dy):
        if self.dact=="Trap":
            self.remember_repeat_dir(dx,dy)
            self.inspect_trap(dx,dy)
            self.st=ST_PLAY; self.dact=None; self.cact=None; self.dir_pending=None
            return
        if self.dact in ("Fight", "Fight to death"):
            self.remember_repeat_dir(dx,dy)
            kamikaze = self.dact == "Fight to death" or getattr(self, "fight_kamikaze_pending", False)
            self.fight_command_confirm(dx,dy,kamikaze)
            self.st=ST_PLAY; self.dact=None; self.cact=None; self.dir_pending=None
            return
        if self.dact=="Throw":
            self.remember_repeat_dir(dx,dy)
            self.throw_dir=(dx,dy)
            self.dact=None
            self.st=ST_ITEM
            return
        if self.dact=="Zap":
            if self.zap_item is None:
                if self.fitems:
                    self.remember_repeat_dir(dx,dy)
                    self.zap_dir=(dx,dy)
                    self.dact=None
                    self.st=ST_ITEM
                else:
                    self.remember_repeat_dir(dx,dy)
                    self.p.facing=(dx,dy)
                    self.command_look()
                    self.msg("pack.you_arent_carrying_anything")
                    self.close_menu()
                    self.end_turn()
                return
            if self.zap_item:
                self.remember_repeat_dir(dx,dy)
                self.p.facing=(dx,dy)
                self.command_look()
                spent_turn = self.zap_stick(self.zap_item,dx,dy)
                self.clear_repeat_item_if_gone(self.zap_item)
                self.close_menu()
                if spent_turn:
                    self.end_turn()
            return
        if self.dact=="Move":
            self.p.facing=(dx,dy)
            count = self.count_input_state.take_prefix()
            if count is not None:
                if count > 1:
                    self.count_input_state.start_repeat("move_on", count, (dx, dy))
                else:
                    self.record_repeat_command("move_on")
                    self.remember_repeat_dir(dx,dy)
            else:
                self.remember_repeat_dir(dx,dy)
            moved = self.execute_move_on(dx,dy)
            if not moved:
                self.command_look_done = False
            self.st=ST_PLAY; self.dact=None; self.cact=None; self.dir_pending=None
            return

    def start_trap_inspect(self):
        self.command_look()
        self.cact="Trap"; self.dact="Trap"; self.st=ST_DIR; self.dir_pending=None

    def start_fight_command(self, kamikaze=False):
        # C: command.c:'f'/'F' calls get_dir() after command.c:look(TRUE).
        self.command_look()
        self.fight_kamikaze_pending = kamikaze
        self.cact = "Fight to death" if kamikaze else "Fight"
        self.dact = self.cact
        self.st = ST_DIR
        self.dir_pending = None

    def fight_command_confirm(self, dx, dy, kamikaze=False):
        # C: command.c:'f'/'F' selects an adjacent visible/SEEMONST target, marks ISTARGET, then melee-dispatches dir_ch.
        self.command_look()
        self.fight_kamikaze_pending = False
        nx, ny = self.p.x + dx, self.p.y + dy
        m = self.mon_at(nx, ny)
        if m is None or (not self.monster_is_seen(m) and not self.can_detect_monsters()):
            self.msg("command.no_monster_there")
            self.command_look_done = False
            return
        m.target = True
        if self.diag_ok(self.p.x, self.p.y, nx, ny):
            self.fight_to_death = True
            self.fight_kamikaze = kamikaze
            self.fight_dir = (dx, dy)
            self.fight_target = m
            self.fight_max_hit = 0
            self.try_move(dx, dy)
        else:
            self.end_turn()

    def clear_fight_to_death(self):
        self.fight_to_death = False
        self.fight_kamikaze = False
        self.fight_dir = (0, 0)
        self.fight_target = None
        self.fight_max_hit = 0

    def clear_to_death_only(self):
        self.fight_to_death = False

    def continue_fight_to_death(self):
        # C: command.c reuses runch while to_death is set, before reading another command.
        if not getattr(self, "fight_to_death", False):
            return False
        target = getattr(self, "fight_target", None)
        dx, dy = getattr(self, "fight_dir", (0, 0))
        if target not in self.mons or not getattr(target, "alive", False) or not getattr(target, "target", False):
            self.clear_fight_to_death()
            return False
        if (target.x, target.y) != (self.p.x + dx, self.p.y + dy):
            self.clear_fight_to_death()
            return False
        moved = self.try_move(dx, dy)
        if not moved:
            self.clear_fight_to_death()
        return moved

    @property
    def last_repeat_command(self):
        return self.repeat_state.command

    @last_repeat_command.setter
    def last_repeat_command(self, value):
        self.repeat_state.command = value

    @property
    def last_repeat_dir(self):
        return self.repeat_state.direction

    @last_repeat_dir.setter
    def last_repeat_dir(self, value):
        self.repeat_state.direction = value

    @property
    def last_repeat_item(self):
        return self.repeat_state.item

    @last_repeat_item.setter
    def last_repeat_item(self, value):
        self.repeat_state.item = value

    @property
    def prev_repeat_command(self):
        return self.repeat_state.previous_command

    @prev_repeat_command.setter
    def prev_repeat_command(self, value):
        self.repeat_state.previous_command = value

    @property
    def prev_repeat_dir(self):
        return self.repeat_state.previous_dir

    @prev_repeat_dir.setter
    def prev_repeat_dir(self, value):
        self.repeat_state.previous_dir = value

    @property
    def prev_repeat_item(self):
        return self.repeat_state.previous_item

    @prev_repeat_item.setter
    def prev_repeat_item(self, value):
        self.repeat_state.previous_item = value

    @property
    def repeat_command_active(self):
        return self.repeat_state.active

    @repeat_command_active.setter
    def repeat_command_active(self, value):
        self.repeat_state.active = value

    @property
    def count_prefix_active(self):
        return self.count_input_state.prefix_active

    @count_prefix_active.setter
    def count_prefix_active(self, value):
        self.count_input_state.prefix_active = value

    @property
    def count_prefix_value(self):
        return self.count_input_state.prefix_value

    @count_prefix_value.setter
    def count_prefix_value(self, value):
        self.count_input_state.prefix_value = value

    @property
    def count_repeat_command(self):
        return self.count_input_state.repeat_command

    @count_repeat_command.setter
    def count_repeat_command(self, value):
        self.count_input_state.repeat_command = value

    @property
    def count_repeat_remaining(self):
        return self.count_input_state.repeat_remaining

    @count_repeat_remaining.setter
    def count_repeat_remaining(self, value):
        self.count_input_state.repeat_remaining = value

    @property
    def count_repeat_dir(self):
        return self.count_input_state.repeat_dir

    @count_repeat_dir.setter
    def count_repeat_dir(self, value):
        self.count_input_state.repeat_dir = value

    @property
    def dashing(self):
        return self.dash_state.active

    @dashing.setter
    def dashing(self, value):
        self.dash_state.active = value

    @property
    def dash_d(self):
        return self.dash_state.direction

    @dash_d.setter
    def dash_d(self, value):
        self.dash_state.direction = value

    @property
    def dash_t(self):
        return self.dash_state.timer

    @dash_t.setter
    def dash_t(self, value):
        self.dash_state.timer = value

    @property
    def dash_steps(self):
        return self.dash_state.steps

    @dash_steps.setter
    def dash_steps(self, value):
        self.dash_state.steps = value

    @property
    def dash_restart_guard(self):
        return self.dash_state.restart_guard

    @dash_restart_guard.setter
    def dash_restart_guard(self, value):
        self.dash_state.restart_guard = value

    @property
    def b_prev(self):
        return self.b_button_state.previous

    @b_prev.setter
    def b_prev(self, value):
        self.b_button_state.previous = value

    @property
    def b_frames(self):
        return self.b_button_state.frames

    @b_frames.setter
    def b_frames(self, value):
        self.b_button_state.frames = value

    @property
    def b_used(self):
        return self.b_button_state.used

    @b_used.setter
    def b_used(self, value):
        self.b_button_state.used = value

    @property
    def b_tap(self):
        return self.b_button_state.tap

    @b_tap.setter
    def b_tap(self, value):
        self.b_button_state.tap = value

    @property
    def back_prev(self):
        return self.back_button_state.previous

    @back_prev.setter
    def back_prev(self, value):
        self.back_button_state.previous = value

    @property
    def back_frames(self):
        return self.back_button_state.frames

    @back_frames.setter
    def back_frames(self, value):
        self.back_button_state.frames = value

    @property
    def back_used(self):
        return self.back_button_state.used

    @back_used.setter
    def back_used(self, value):
        self.back_button_state.used = value

    @property
    def back_tap(self):
        return self.back_button_state.tap

    @back_tap.setter
    def back_tap(self, value):
        self.back_button_state.tap = value

    def record_repeat_command(self, command):
        # C: command.c saves last_comm/last_dir/last_pick before dispatch, except while again.
        if getattr(self, "repeat_command_active", False):
            return
        self.count_input_state.take_prefix()
        self.repeat_state.record(command)

    def reset_repeat_command(self):
        # C: pack.c:reset_last() restores the previous command when get_dir/get_item aborts.
        self.repeat_state.reset()

    def remember_repeat_dir(self, dx, dy):
        self.repeat_state.remember_dir((dx, dy))

    def remember_repeat_item(self, it):
        self.repeat_state.remember_item(it)

    def clear_repeat_item_if_gone(self, it):
        self.repeat_state.clear_item_if_gone(it, self.p.inv)

    def repeat_last_command(self):
        # C: command.c:'a' repeats last_comm with again=TRUE.
        self.command_look()
        command = self.last_repeat_command
        if command is None:
            self.msg("command.you_havent_typed_a_command_yet")
            self.command_look_done = False
            return
        self.repeat_command_active = True
        try:
            self.dispatch_repeat_command(command)
        finally:
            self.repeat_command_active = False

    def repeat_dir_or_prompt(self):
        direction = self.last_repeat_dir
        if direction is None:
            self.st = ST_DIR
            return None
        return direction

    def repeat_item_or_ran_out(self):
        item = self.last_repeat_item
        if item is None or item not in self.p.inv:
            if self.p.inv:
                self.msg("pack.you_ran_out")
            else:
                self.msg("pack.you_arent_carrying_anything")
            self.last_repeat_item = None
            self.end_turn()
            return None
        return item

    def dispatch_repeat_command(self, command):
        if command == "search":
            self.do_search()
        elif command == "wait":
            self.do_wait()
        elif command == "move":
            direction = self.repeat_dir_or_prompt()
            if direction is not None:
                self.try_move(*direction)
        elif command == "move_on":
            direction = self.repeat_dir_or_prompt()
            if direction is not None:
                moved = self.execute_move_on(*direction)
                if not moved:
                    self.command_look_done = False
        elif command == "trap":
            direction = self.repeat_dir_or_prompt()
            if direction is not None:
                self.inspect_trap(*direction)
        elif command == "picky_inventory":
            self.open_picky_inventory_command()
        elif command == "inventory":
            self.command_look()
            self.st = ST_INVENTORY
            self.command_look_done = False
        elif command == "help":
            self.open_help_command()
        elif command == "symbol_identify":
            self.open_symbol_identify_command()
        elif command == "version":
            self.show_version_command()
        elif command == "options":
            self.open_options_command()
        elif command == "discoveries":
            self.open_discoveries()
        elif command == "stairs_down":
            self.stairs_down_command()
        elif command == "stairs_up":
            self.stairs_up_command()
        elif command == "current_weapon":
            self.current_item_command(self.p.wpn, "wielding", None, "手に持っている")
        elif command == "current_armor":
            self.current_item_command(self.p.arm, "wearing", None, "装着中")
        elif command == "current_rings":
            self.current_rings_command()
        elif command == "status":
            self.status_command()
        elif command == "repeat_message":
            self.repeat_message_command()
        elif command == "redraw":
            self.redraw_command()
        elif command == "legal_space":
            self.legal_space_command()
        elif command == "pickup":
            self.do_pickup()
        elif command == "quit":
            self.quit_command()
        elif command in ("fight", "fight_to_death"):
            direction = self.repeat_dir_or_prompt()
            if direction is not None:
                self.fight_command_confirm(*direction, kamikaze=(command == "fight_to_death"))
        elif isinstance(command, tuple) and command[0] == "illegal":
            self.illegal_command(command[1])
        elif isinstance(command, tuple) and command[0] == "item":
            self.repeat_item_command(command[1])

    def repeat_item_command(self, aname):
        item = self.repeat_item_or_ran_out()
        if item is None:
            return
        self.cact = aname
        self.fitems = [item]
        self.action_origin = ST_PLAY
        if aname in ("Throw", "Zap"):
            direction = self.repeat_dir_or_prompt()
            if direction is None:
                self.dact = aname
                self.st = ST_DIR
                if aname == "Zap":
                    self.zap_item = item
                return
            if aname == "Throw":
                self.throw_dir = direction
                self.confirm_item(item)
            else:
                self.zap_item = item
                self.dir_confirm(*direction)
            return
        self.confirm_item(item)

    # ---------- Input helpers ----------
    def kp(self,*ks): return any(k is not None and pyxel.btnp(k) for k in ks)
    def kh(self,*ks): return any(k is not None and pyxel.btn(k) for k in ks)

    def direction_input_labels(self, check, include_vi=True, include_hjkl=True, include_gamepad=True):
        labels = set()
        groups = [
            ("up", [pyxel.KEY_UP]),
            ("down", [pyxel.KEY_DOWN]),
            ("left", [pyxel.KEY_LEFT]),
            ("right", [pyxel.KEY_RIGHT]),
        ]
        if include_hjkl:
            groups[0][1].append(pyxel.KEY_K)
            groups[1][1].append(pyxel.KEY_J)
            groups[2][1].append(pyxel.KEY_H)
            groups[3][1].append(pyxel.KEY_L)
        if include_gamepad:
            groups[0][1].append(pyxel.GAMEPAD1_BUTTON_DPAD_UP)
            groups[1][1].append(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)
            groups[2][1].append(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)
            groups[3][1].append(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
        if include_vi:
            groups.extend([
                ("y", [pyxel.KEY_Y]),
                ("u", [pyxel.KEY_U]),
                ("b", [pyxel.KEY_B]),
                ("n", [pyxel.KEY_N]),
            ])
        for label, keys in groups:
            if check(*keys):
                labels.add(label)
        return labels

    def held_direction_input_labels(self, **kwargs):
        return self.direction_input_labels(self.kh, **kwargs)

    def pressed_direction_input_labels(self, **kwargs):
        return self.direction_input_labels(self.kp, **kwargs)

    def count_digit_press(self):
        pressed = set()
        for digit in rogue_input.DIGITS:
            key = getattr(pyxel, f"KEY_{digit}", None)
            if key is not None and self.kp(key):
                pressed.add(digit)
        return rogue_input.count_digit(pressed, self.shift_held(), self.ctrl_held())

    def countable_command(self, command):
        return command in ("search", "wait", "move")

    def start_count_prefix(self, digit):
        # C: command.c digit prefix is read after look(TRUE), before dispatch.
        self.command_look()
        self.count_input_state.start_prefix(digit)

    def record_counted_input_command(self, command, direction=None):
        # C: command.c decrements count before deciding whether last_comm is updated.
        if not self.count_input_state.record_counted(command, self.countable_command(command), direction):
            return False
        self.record_repeat_command(command)
        if command == "move" and direction is not None:
            self.remember_repeat_dir(*direction)
        return True

    def continue_counted_command(self):
        command = getattr(self, "count_repeat_command", None)
        if not command or self.count_repeat_remaining <= 0:
            return False
        if command == "again":
            self.count_repeat_remaining -= 1
            if self.count_repeat_remaining <= 0:
                self.count_repeat_command = None
            self.repeat_last_command()
            return True
        if self.count_repeat_remaining == 1:
            repeat_command = "move" if command == "move_on" else command
            self.record_repeat_command(repeat_command)
            if command in ("move", "move_on") and self.count_repeat_dir is not None:
                self.remember_repeat_dir(*self.count_repeat_dir)
        self.count_repeat_remaining -= 1
        if self.count_repeat_remaining <= 0:
            self.count_repeat_command = None
        if command == "search":
            self.do_search()
            return True
        if command == "wait":
            self.do_wait()
            return True
        if command == "move" and self.count_repeat_dir is not None:
            self.try_move(*self.count_repeat_dir)
            return True
        if command == "move_on" and self.count_repeat_dir is not None:
            self.execute_move_on(*self.count_repeat_dir)
            return True
        return False

    def ensure_tap_button_states(self):
        if not hasattr(self, "b_button_state"):
            self.b_button_state = rogue_input.TapButtonState()
        if not hasattr(self, "back_button_state"):
            self.back_button_state = rogue_input.TapButtonState()

    def ensure_dash_state(self):
        if not hasattr(self, "dash_state"):
            self.dash_state = rogue_input.DashState()

    def begin_input(self):
        self.ensure_tap_button_states()
        self.ensure_dash_state()
        self.diag_assist=self.start_held()
        b_now=self.kh(pyxel.GAMEPAD1_BUTTON_B)
        back_now=self.back_held()
        self.dash_state.update_release(self.dash_held())
        self.b_button_state.update(b_now, B_TAP_FRAMES)
        if b_now and (self.kh(pyxel.KEY_UP,pyxel.KEY_DOWN,pyxel.KEY_LEFT,pyxel.KEY_RIGHT,
                              pyxel.GAMEPAD1_BUTTON_DPAD_UP,pyxel.GAMEPAD1_BUTTON_DPAD_DOWN,
                              pyxel.GAMEPAD1_BUTTON_DPAD_LEFT,pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
                      or self.kh(pyxel.GAMEPAD1_BUTTON_A)):
            self.b_button_state.mark_used()
        self.back_button_state.update(back_now, BACK_TAP_FRAMES)
        if back_now and self.kh(pyxel.KEY_RETURN, pyxel.KEY_ESCAPE,
                                pyxel.GAMEPAD1_BUTTON_A, pyxel.GAMEPAD1_BUTTON_B):
            self.back_button_state.mark_used()
        if back_now and self.dir_held_any():
            self.back_button_state.mark_used()

    GP = pyxel.GAMEPAD1_BUTTON_DPAD_UP
    def _held_up(self): return self.kh(pyxel.KEY_UP, pyxel.KEY_K, pyxel.GAMEPAD1_BUTTON_DPAD_UP)
    def _held_dn(self): return self.kh(pyxel.KEY_DOWN, pyxel.KEY_J, pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)
    def _held_lt(self): return self.kh(pyxel.KEY_LEFT, pyxel.KEY_H, pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)
    def _held_rt(self): return self.kh(pyxel.KEY_RIGHT, pyxel.KEY_L, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)

    def dir_press(self):
        """Return (dx,dy) for direction pressed this frame (btnp), or None."""
        direction, self.dir_pending, self.dir_press_locked = rogue_input.direction_press_guarded(
            self.held_direction_input_labels(),
            self.pressed_direction_input_labels(),
            self.dir_pending,
            self.diag_assist,
            getattr(self, "dir_press_locked", None),
        )
        return direction

    def dir_prompt_press(self):
        return rogue_input.prompt_direction(
            self.held_direction_input_labels(),
            self.pressed_direction_input_labels(),
        )

    def held_dir(self):
        return rogue_input.held_direction(self.held_direction_input_labels(), self.diag_assist)

    def dir_held_any(self):
        return rogue_input.any_direction_held(self.held_direction_input_labels(include_vi=False))

    def menu_vertical_press(self):
        if self.kp(pyxel.KEY_UP, pyxel.KEY_K, pyxel.GAMEPAD1_BUTTON_DPAD_UP): return -1
        if self.kp(pyxel.KEY_DOWN, pyxel.KEY_J, pyxel.GAMEPAD1_BUTTON_DPAD_DOWN): return 1
        return 0

    def menu_horizontal_press(self):
        if self.kp(pyxel.KEY_LEFT, pyxel.KEY_H, pyxel.GAMEPAD1_BUTTON_DPAD_LEFT): return -1
        if self.kp(pyxel.KEY_RIGHT, pyxel.KEY_L, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT): return 1
        return 0

    def shift_held(self):
        return self.kh(pyxel.KEY_SHIFT, pyxel.KEY_LSHIFT, pyxel.KEY_RSHIFT)
    def ctrl_held(self):
        return self.kh(pyxel.KEY_CTRL, pyxel.KEY_LCTRL, pyxel.KEY_RCTRL)
    def btn_a(self): return self.kp(pyxel.KEY_RETURN, pyxel.GAMEPAD1_BUTTON_A)
    def held_a(self): return self.kh(pyxel.KEY_RETURN, pyxel.GAMEPAD1_BUTTON_A)
    def btn_b(self): return self.kp(pyxel.KEY_ESCAPE) or getattr(self, "b_tap", False)
    def btn_cancel(self): return self.kp(pyxel.KEY_ESCAPE, pyxel.GAMEPAD1_BUTTON_B)
    def btn_overlay_cancel(self):
        if self.kp(pyxel.KEY_ESCAPE): return True
        if getattr(self, "back_tap", False): return True
        b_now=self.kh(pyxel.GAMEPAD1_BUTTON_B)
        if getattr(self, "b_menu_guard", False):
            if not b_now:
                self.b_menu_guard=False
            return False
        if self.kp(pyxel.GAMEPAD1_BUTTON_B):
            self.b_used=True
            return True
        return getattr(self, "b_tap", False)
    def btn_menu(self): return self.kp(pyxel.KEY_ESCAPE) or getattr(self, "b_tap", False)
    def btn_wait(self):
        return self.kp(pyxel.KEY_PERIOD) or (
            self.kh(pyxel.GAMEPAD1_BUTTON_A) and self.kh(pyxel.GAMEPAD1_BUTTON_B)
            and (self.kp(pyxel.GAMEPAD1_BUTTON_A) or self.kp(pyxel.GAMEPAD1_BUTTON_B))
            and not self.dir_held_any()
        ) or (
            self.kh(pyxel.KEY_RETURN) and self.kh(pyxel.KEY_ESCAPE)
            and (self.kp(pyxel.KEY_RETURN) or self.kp(pyxel.KEY_ESCAPE))
            and not self.dir_held_any()
        )
    def key_lower(self, key):
        return self.kp(key) and not self.shift_held()
    def key_upper(self, key):
        return self.kp(key) and self.shift_held()
    def pack_letter_press(self):
        # Rogue 5.4.4 pack.c:get_item() accepts a typed o_packch directly.
        for idx, ch in enumerate("abcdefghijklmnopqrstuvwxyz"):
            key = getattr(pyxel, f"KEY_{ch.upper()}", None)
            if key is not None and pyxel.btnp(key):
                if self.shift_held():
                    return ch.upper(), None
                return ch, self.p.inv[idx] if idx < len(self.p.inv) else None
        return None
    def invalid_pack_letter(self, ch):
        self.request_sfx(rogue_sfx.SFX_ERROR)
        self.msg("pack.item_is_not_a_valid_item", item=ch)
    def invalid_picky_inventory_letter(self, ch):
        self.request_sfx(rogue_sfx.SFX_ERROR)
        self.msg("pack.item_not_in_pack", item=ch)
    def cancel_item_prompt(self):
        # Rogue 5.4.4 pack.c:get_item() ESC aborts the command with after=FALSE.
        if not getattr(self, "repeat_command_active", False):
            self.reset_repeat_command()
        if self.cact=="Throw" and self.throw_dir is not None:
            self.st=ST_DIR
            self.dact="Throw"
            self.throw_dir=None
        elif self.cact=="Zap" and getattr(self, "zap_dir", None) is not None:
            self.st=ST_DIR
            self.dact="Zap"
            self.zap_dir=None
        elif self.action_origin==ST_MENU:
            self.st=ST_MENU
        else:
            self.close_menu()
        if self.st != ST_DIR:
            self.throw_dir=None
            self.zap_dir=None
    def cancel_call_prompt(self):
        # Rogue 5.4.4 command.c:call() returns without changing guesses on ESC.
        if (
            self.call_item is None
            and self.action_origin == ST_PLAY
            and not getattr(self, "repeat_command_active", False)
        ):
            self.reset_repeat_command()
        self.call_item=None; self.call_input=""; self.call_preset_idx=0
        if self.action_origin==ST_MENU:
            self.st=ST_MENU
        else:
            self.close_menu()
    def cancel_dir_prompt(self):
        # Rogue 5.4.4 misc.c:get_dir() ESC aborts direction commands with after=FALSE.
        if not getattr(self, "repeat_command_active", False):
            self.reset_repeat_command()
        if self.dact=="Trap":
            self.st=ST_PLAY
            self.dact=None
        elif self.dact in ("Throw", "Zap"):
            self.dact=None
            self.zap_dir=None
            self.zap_item=None
            if self.action_origin==ST_MENU:
                self.st=ST_MENU
            else:
                self.close_menu()
        elif self.dact in ("Fight", "Fight to death"):
            self.st=ST_PLAY
            self.dact=None
            self.cact=None
            self.fight_kamikaze_pending=False
            self.command_look_done=False
        elif self.dact=="Move":
            self.st=ST_PLAY
            self.dact=None
            self.cact=None
            self.command_look_done=False
        else:
            self.st=ST_ITEM
    def btn_search(self): return self.key_lower(pyxel.KEY_S)
    def btn_trap_inspect(self):
        return self.shift_held() and self.kp(getattr(pyxel,"KEY_6",None))
    def btn_inventory(self): return self.key_lower(pyxel.KEY_I)
    def start_held(self): return self.kh(getattr(pyxel,"KEY_SPACE",None), pyxel.GAMEPAD1_BUTTON_START)
    def btn_start_tap(self): return self.kp(getattr(pyxel,"KEY_SPACE",None), pyxel.GAMEPAD1_BUTTON_START)
    def kp_back(self): return self.kp(pyxel.KEY_TAB, pyxel.GAMEPAD1_BUTTON_BACK)
    def back_held(self): return self.kh(pyxel.KEY_TAB, pyxel.GAMEPAD1_BUTTON_BACK)
    def btn_back(self): return self.back_tap
    def btn_select_a(self):
        hit = (self.back_held() and self.btn_a()) or (self.kp_back() and self.held_a())
        if hit:
            self.back_used=True; self.b_used=True
        return hit
    def btn_select_b(self):
        hit = (self.back_held() and self.kp(pyxel.KEY_ESCAPE, pyxel.GAMEPAD1_BUTTON_B)) or (
            self.kp_back() and self.kh(pyxel.KEY_ESCAPE, pyxel.GAMEPAD1_BUTTON_B)
        )
        if hit:
            self.back_used=True; self.b_used=True
        return hit
    def select_dir_press(self):
        direction = rogue_input.select_direction(
            self.held_direction_input_labels(include_vi=False, include_hjkl=False),
            self.pressed_direction_input_labels(include_vi=False, include_hjkl=False),
            self.back_held(),
        )
        if direction:
            self.back_used=True
            return direction
        return None
    def btn_r(self):
        return self.kp(pyxel.KEY_QUESTION) or (
            self.kp(getattr(pyxel, "KEY_SLASH", None)) and self.shift_held()
        )
    def btn_any_key(self):
        """Return True if any meaningful key or gamepad button was pressed this frame.
        Used to dismiss help/info overlays."""
        if self.kp(pyxel.KEY_SPACE, pyxel.KEY_RETURN, pyxel.KEY_ESCAPE, pyxel.KEY_TAB,
                   pyxel.KEY_BACKSPACE, pyxel.KEY_PERIOD, pyxel.KEY_COMMA,
                   pyxel.KEY_SLASH, pyxel.KEY_QUESTION, pyxel.KEY_MINUS,
                   pyxel.KEY_UP, pyxel.KEY_DOWN, pyxel.KEY_LEFT, pyxel.KEY_RIGHT,
                   pyxel.GAMEPAD1_BUTTON_A, pyxel.GAMEPAD1_BUTTON_B,
                   pyxel.GAMEPAD1_BUTTON_START, pyxel.GAMEPAD1_BUTTON_BACK,
                   pyxel.GAMEPAD1_BUTTON_X, pyxel.GAMEPAD1_BUTTON_Y,
                   pyxel.GAMEPAD1_BUTTON_DPAD_UP, pyxel.GAMEPAD1_BUTTON_DPAD_DOWN,
                   pyxel.GAMEPAD1_BUTTON_DPAD_LEFT, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            return True
        for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            k = getattr(pyxel, f"KEY_{c}", None)
            if k is not None and pyxel.btnp(k):
                return True
        for i in range(10):
            k = getattr(pyxel, f"KEY_{i}", None)
            if k is not None and pyxel.btnp(k):
                return True
        return False
    def dash_held(self):
        return self.kh(pyxel.KEY_SHIFT, pyxel.KEY_LSHIFT, pyxel.KEY_RSHIFT, pyxel.GAMEPAD1_BUTTON_B)
    def dash_restart_dir_press(self):
        return self.kp(pyxel.KEY_UP, pyxel.KEY_DOWN, pyxel.KEY_LEFT, pyxel.KEY_RIGHT,
                       pyxel.KEY_H, pyxel.KEY_J, pyxel.KEY_K, pyxel.KEY_L,
                       pyxel.KEY_Y, pyxel.KEY_U, pyxel.KEY_B, pyxel.KEY_N,
                       pyxel.GAMEPAD1_BUTTON_DPAD_UP, pyxel.GAMEPAD1_BUTTON_DPAD_DOWN,
                       pyxel.GAMEPAD1_BUTTON_DPAD_LEFT, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)

    def rogue_command_action(self):
        if self.key_lower(getattr(pyxel, "KEY_T", None)): return "Throw"
        if self.key_lower(getattr(pyxel, "KEY_Q", None)): return "Quaff"
        if self.key_lower(pyxel.KEY_R): return "Read"
        if self.key_lower(getattr(pyxel, "KEY_E", None)): return "Eat"
        if self.key_lower(getattr(pyxel, "KEY_D", None)): return "Drop"
        if self.key_lower(getattr(pyxel, "KEY_W", None)): return "Wield"
        if self.key_lower(pyxel.KEY_Z): return "Zap"
        if self.key_upper(getattr(pyxel, "KEY_W", None)): return "Wear"
        if self.key_upper(getattr(pyxel, "KEY_T", None)): return "Take off"
        if self.key_upper(getattr(pyxel, "KEY_P", None)): return "Put on"
        if self.key_upper(getattr(pyxel, "KEY_R", None)): return "Remove ring"
        if self.key_lower(pyxel.KEY_C): return "Call"
        return None

    def prepare_title_new_game(self):
        self.player_name = self.current_player_name()
        self.stop_title_bgm()
        self.apply_palette()
        self.new_game()
        self.st = ST_PLAY

    def title_menu_items(self):
        items = []
        if rogue_save.exists():
            items.append("continue")
        items.extend(["dungeon", "scoreboard", "online"])
        return items

    def title_menu_label(self, item):
        online = self.is_online_mode()
        if getattr(self, "lang", LANG_EN) == LANG_JA:
            labels = {
                "continue": "つづきから",
                "dungeon": "運命の洞窟に入る",
                "scoreboard": "スコアボード",
                "online": "ゲストモード" if online else "オンラインモード",
            }
        else:
            labels = {
                "continue": "CONTINUE",
                "dungeon": "ENTER DUNGEON",
                "scoreboard": "SCOREBOARD",
                "online": "GUEST MODE" if online else "ONLINE MODE",
            }
        return labels[item]

    def load_saved_game_from_title(self):
        try:
            data = rogue_save.load()
            self.stop_title_bgm()
            self.restore_state(data)
            rogue_save.delete()
            self.apply_palette()
            self.title_save_error = ""
        except Exception:
            self.title_save_error = "ロードに失敗しました" if self.lang == LANG_JA else "Could not restore save"
            self.enter_title_screen(skip_fade=True)

    def request_title_new_game(self):
        if getattr(self, "title_bgm_stop_wait", 0) > 0:
            return
        self.stop_title_bgm()
        self.title_bgm_stop_wait = TITLE_BGM_STOP_WAIT_FRAMES

    def change_title_difficulty(self, delta):
        current = DIFFICULTY_ORDER.index(self.difficulty) if self.difficulty in DIFFICULTY_ORDER else 1
        self.difficulty = DIFFICULTY_ORDER[(current + delta) % len(DIFFICULTY_ORDER)]
        self.persist_settings()

    def enter_difficulty_select(self):
        if variant_fixed_difficulty():
            self.difficulty = variant_fixed_difficulty()
            self.st = ST_NYANDOR_BRIEF
            return
        self.difficulty_cursor = DIFFICULTY_ORDER.index(self.difficulty) if self.difficulty in DIFFICULTY_ORDER else 1
        self.difficulty_cursor_restored = True
        self.st = ST_DIFFICULTY

    def change_difficulty_cursor(self, delta):
        current = getattr(self, "difficulty_cursor", DIFFICULTY_ORDER.index(self.difficulty) if self.difficulty in DIFFICULTY_ORDER else 1)
        self.difficulty_cursor = (current + delta) % len(DIFFICULTY_ORDER)
        self.difficulty_cursor_restored = False

    def confirm_difficulty_select(self):
        cursor = getattr(self, "difficulty_cursor", DIFFICULTY_ORDER.index(self.difficulty) if self.difficulty in DIFFICULTY_ORDER else 1)
        self.difficulty = DIFFICULTY_ORDER[cursor % len(DIFFICULTY_ORDER)]
        self.persist_settings()
        self.request_title_new_game()

    def scoreboard_period_key(self, period, timestamp=None):
        return rogue_online_scoreboard.scoreboard_period_key(period, timestamp)

    def scoreboard_period_label(self, period, timestamp=None):
        return rogue_online_scoreboard.scoreboard_period_label(period, self.lang, timestamp)

    def format_utc_minute(self, value):
        return rogue_online_scoreboard.format_utc_minute(value)

    def format_utc_short_minute(self, value):
        return rogue_online_scoreboard.format_utc_short_minute(value)

    def scoreboard_period_end(self, period, now=None):
        return rogue_online_scoreboard.scoreboard_period_end(period, now)

    def scoreboard_period_ends_line(self, period, now=None):
        return rogue_online_scoreboard.scoreboard_period_ends_line(
            period,
            self.lang,
            now,
            local_line=self.online_sync_hint_line(),
        )

    def online_sync_hint_line(self):
        profile = normalize_online_profile(getattr(self, "online_profile", None))
        return rogue_online_scoreboard.online_sync_hint_line(profile, self.lang)

    def scoreboard_difficulty(self):
        fixed = variant_fixed_difficulty()
        if fixed:
            return fixed
        value = getattr(self, "scoreboard_difficulty_id", self.difficulty)
        return difficulty_profile(value).id

    def set_scoreboard_difficulty(self, value):
        self.scoreboard_difficulty_id = difficulty_profile(value).id

    def scoreboard_difficulty_profile(self):
        return difficulty_profile(self.scoreboard_difficulty())

    def change_scoreboard_difficulty(self, delta):
        fixed = variant_fixed_difficulty()
        if fixed:
            self.set_scoreboard_difficulty(fixed)
            return
        current = self.scoreboard_difficulty()
        index = DIFFICULTY_ORDER.index(current) if current in DIFFICULTY_ORDER else DIFFICULTY_ORDER.index(DIFF_NORMAL)
        self.set_scoreboard_difficulty(DIFFICULTY_ORDER[(index + delta) % len(DIFFICULTY_ORDER)])

    def online_score_cache_variant(self):
        return variant_scoreboard_key() or VARIANT_ROGUE

    def online_score_loaded_key(self, period, timestamp=None):
        key = "" if period == SCOREBOARD_PERIOD_LOCAL else self.scoreboard_period_key(period, timestamp)
        return (
            period,
            key,
            self.online_score_cache_variant(),
            self.scoreboard_difficulty(),
        )

    def online_score_is_loaded(self, period, timestamp=None):
        loaded = getattr(self, "online_score_loaded", set())
        return self.online_score_loaded_key(period, timestamp) in loaded or period in loaded

    def online_score_memory_key(self, period, timestamp=None):
        if period == SCOREBOARD_PERIOD_LOCAL:
            return SCOREBOARD_PERIOD_LOCAL
        return self.online_score_loaded_key(period, timestamp)

    def cached_online_scores(self, cache, period, default=None):
        memory_key = self.online_score_memory_key(period)
        if memory_key in cache:
            return cache[memory_key]
        return cache.get(period, [] if default is None else default)

    def store_online_score_cache(self, period, raw_entries, scores, timestamp=None):
        memory_key = self.online_score_memory_key(period, timestamp)
        self.online_score_raw_cache[memory_key] = raw_entries
        self.online_score_cache[memory_key] = scores
        self.online_score_raw_cache[period] = raw_entries
        self.online_score_cache[period] = scores

    def ensure_online_score_state(self):
        rogue_online_state.ensure_online_score_state(self)

    def online_text(self, key):
        return rogue_online_text.online_text(getattr(self, "lang", LANG_EN), key)

    def online_sync_due(self, profile):
        return rogue_online_state.online_sync_due(profile)

    def schedule_online_action(self, action):
        rogue_online_state.schedule_online_action_state(self, action)

    def run_pending_online_action(self):
        action = rogue_online_state.pop_ready_online_action(self)
        if not action:
            return False
        if action == "waiting":
            return True
        if action == "check_user":
            self.perform_online_user_check()
        elif action in ("register_user", "link_user"):
            self.perform_online_password_submit(action)
        return True

    def request_online_period_scores(self, force=False):
        self.ensure_online_score_state()
        profile = normalize_online_profile(getattr(self, "online_profile", None))
        return rogue_online_state.begin_online_period_score_request(
            self,
            post_allowed=self.online_sync_due(profile),
            force=force,
        )

    def cancel_online_sync(self):
        rogue_online_state.cancel_online_sync_state(self)

    def submit_result_online_score(self):
        entry = getattr(self, "result_entry", None)
        if not entry or getattr(self, "result_online_submitted", False):
            return
        if submit_online_score(entry):
            self.result_online_submitted = True

    def enter_online_register(self, reset_to_default=False):
        self.apply_palette()
        if getattr(self, "st", ST_TITLE) not in (ST_ONLINE_REGISTER, ST_ONLINE_PIN, ST_ONLINE_LOCAL_CONFIRM):
            self.online_register_return_state = getattr(self, "st", ST_TITLE)
        profile = normalize_online_profile(getattr(self, "online_profile", None))
        user_name = "" if reset_to_default or profile.get("local_only", True) else profile.get("user_name", "")
        self.online_pending_user_name = user_name
        self.online_original_user_name = user_name
        self.online_name_candidates = local_score_player_name_candidates(load_score_entries(), limit=3)
        self.name_chars = list(user_name[:USER_NAME_MAX])
        self.name_pos = min(len(self.name_chars), USER_NAME_MAX - 1)
        self.online_sync_result = ""
        self.online_sync_status = ""
        self.st = ST_ONLINE_REGISTER

    def confirm_online_user_id(self):
        raw_name = "".join(getattr(self, "name_chars", [])).strip()
        if not raw_name:
            self.online_sync_result = "Enter a name."
            return
        user_name = sanitize_user_id(raw_name)
        if not can_register_user_id(user_name):
            self.online_sync_result = "That user name is already registered."
            return
        self.online_pending_user_name = user_name
        self.online_sync_status = "checking user..."
        self.online_sync_result = ""
        self.schedule_online_action("check_user")

    def perform_online_user_check(self):
        user_name = getattr(self, "online_pending_user_name", "rogue54")
        result = check_online_user(user_name, variant=variant_scoreboard_key())
        if not result.get("ok"):
            self.online_sync_result = "Could not check user. Try again."
            return
        self.online_password_chars = ["0"] * 6
        self.name_pos = 0
        self.online_password_mode = "link" if result.get("exists") else "register"
        self.online_sync_result = ""
        self.st = ST_ONLINE_PIN

    def save_local_only_online_profile(self):
        self.online_profile = save_local_only_profile("guest")
        self.player_name = self.online_profile["user_name"]
        self.online_register_prompt = False
        if getattr(self, "online_register_return_state", ST_TITLE) == ST_ONLINE_SCORE:
            self.st = ST_ONLINE_SCORE
        else:
            self.enter_title_screen(skip_fade=True)

    def switch_to_guest_mode(self):
        self.online_profile = save_local_only_profile("guest")
        self.player_name = "guest"
        self.online_register_prompt = False
        self.online_sync_pending = False
        self.online_syncing = False
        self.online_sync_result = ""
        self.enter_title_screen(skip_fade=True)

    def enter_guest_mode_confirm(self):
        self.apply_palette()
        self.online_local_confirm_mode = "guest_switch"
        self.st = ST_ONLINE_LOCAL_CONFIRM

    def online_register_name_changed(self):
        current = sanitize_user_id("".join(getattr(self, "name_chars", [])))
        original = sanitize_user_id(getattr(self, "online_original_user_name", current))
        return current != original

    def cancel_or_confirm_local_only_name(self):
        profile = normalize_online_profile(getattr(self, "online_profile", None))
        if profile.get("local_only", True):
            self.online_profile = {
                "user_name": "guest",
                "local_only": True,
                "server_token": "",
                "last_sync_at": "",
                "next_sync_at": "",
                "profile_exists": True,
            }
            self.player_name = "guest"
            self.enter_title_screen(skip_fade=True)
        elif self.online_register_name_changed():
            self.st = ST_ONLINE_LOCAL_CONFIRM
        else:
            self.enter_title_screen()

    def online_name_candidate_count(self):
        return len(getattr(self, "online_name_candidates", [])[:3])

    def online_name_candidate_index(self):
        pos = getattr(self, "name_pos", 0)
        if pos <= USER_NAME_MAX:
            return -1
        idx = pos - USER_NAME_MAX - 1
        if idx >= self.online_name_candidate_count():
            return -1
        return idx

    def apply_online_name_candidate(self):
        idx = self.online_name_candidate_index()
        if idx < 0:
            return False
        name = self.online_name_candidates[idx]
        self.name_chars = list(name[:USER_NAME_MAX])
        self.name_pos = USER_NAME_MAX
        self.online_sync_result = ""
        return True

    def upd_online_local_confirm(self):
        if self.online_language_toggle_pressed():
            self.toggle_online_language()
            return
        if self.btn_a() or self.btn_start_tap():
            if getattr(self, "online_local_confirm_mode", "") == "guest_switch":
                self.online_local_confirm_mode = ""
                self.switch_to_guest_mode()
                return
            self.save_local_only_online_profile()
            return
        if self.btn_b():
            if getattr(self, "online_local_confirm_mode", "") == "guest_switch":
                self.online_local_confirm_mode = ""
                self.enter_title_screen(skip_fade=True)
                return
            self.st = ST_ONLINE_REGISTER
            return

    def decline_online_registration(self):
        self.online_profile = save_local_only_profile("guest")
        self.player_name = self.online_profile["user_name"]
        self.online_register_prompt = False
        self.enter_title_screen(skip_fade=True)

    def finish_online_password(self):
        if getattr(self, "online_password_mode", "register") == "link":
            self.online_sync_status = "linking user..."
            self.schedule_online_action("link_user")
        else:
            self.online_sync_status = "registering user..."
            self.schedule_online_action("register_user")
        self.online_sync_result = ""

    def perform_online_password_submit(self, action):
        pin = "".join(getattr(self, "online_password_chars", []))
        user_name = getattr(self, "online_pending_user_name", "rogue54")
        if action == "link_user":
            result = link_online_user(user_name, pin, variant=variant_scoreboard_key())
        else:
            result = register_online_user(user_name, pin, variant=variant_scoreboard_key())
            if result.get("status") in ("exists", "name_used"):
                self.online_password_mode = "link"
                self.online_sync_result = "Name exists. Enter its 6-digit PIN."
                return
        if result.get("ok"):
            if not result.get("server_token", ""):
                self.online_sync_result = "Registration failed."
                return
            self.online_profile = save_online_profile({
                "user_name": result.get("user_name", user_name),
                "local_only": False,
                "server_token": result.get("server_token", ""),
                "last_sync_at": result.get("last_sync_at", ""),
                "next_sync_at": result.get("next_sync_at", ""),
                "profile_exists": True,
            })
            self.player_name = self.online_profile["user_name"]
            self.online_register_prompt = False
            self.online_sync_pending = False
            self.online_syncing = False
            self.enter_title_screen(skip_fade=True)
            return
        if getattr(self, "online_password_mode", "register") == "link" and result.get("status") == "auth_failed":
            self.online_sync_result = "That name belongs to another player."
            return
        self.online_sync_result = str(result.get("message") or result.get("status") or "Registration failed.")

    def enter_online_scoreboard(self, auto_sync=False, difficulty=None):
        self.stop_scoreboard_bgm()
        self.apply_palette()
        self.ensure_online_score_state()
        if not hasattr(self, "online_profile"):
            self.online_profile = load_online_profile()
        if difficulty is not None:
            self.set_scoreboard_difficulty(difficulty)
        elif not hasattr(self, "scoreboard_difficulty_id"):
            self.set_scoreboard_difficulty(self.difficulty)
        self.online_period = SCOREBOARD_PERIOD_LOCAL
        local_entries = self.local_entries_for_current_scoreboard_variant()
        user_local_entries = self.current_user_local_score_entries()
        self.online_score_raw_cache[SCOREBOARD_PERIOD_LOCAL] = local_entries
        self.online_score_cache[SCOREBOARD_PERIOD_LOCAL] = get_top_scores(
            local_entries,
            limit=10,
            difficulty=self.scoreboard_difficulty(),
        )
        guest_mode = normalize_online_profile(getattr(self, "online_profile", None)).get("local_only", True)
        for period in (SCOREBOARD_PERIOD_WEEKLY, SCOREBOARD_PERIOD_SEASON):
            loaded_key = self.online_score_loaded_key(period)
            if self.online_score_is_loaded(period):
                continue
            key = self.scoreboard_period_key(period)
            cached = load_online_score_cache(
                period,
                key,
                variant=self.online_score_cache_variant(),
                difficulty=self.scoreboard_difficulty(),
            )
            if not cached:
                continue
            entries = cached if guest_mode else cached + user_local_entries
            scores = get_period_scores(
                entries,
                period,
                key,
                limit=10,
                difficulty=self.scoreboard_difficulty(),
            )
            self.store_online_score_cache(period, cached, scores)
            self.online_score_loaded.add(loaded_key)
        if getattr(self, "online_sync_result", "") in (
            "No local scores yet.",
            "Ranking updated. No local scores yet.",
            "Ranking refreshed. No local scores yet.",
            "Ranking refreshed. POST once per hour.",
            "Score posted. Ranking refreshed.",
        ):
            self.online_sync_result = ""
        self.online_return_state = ST_TITLE
        self.st = ST_ONLINE_SCORE
        self.online_register_prompt = False
        return

    def enter_result_scoreboard(self):
        entry = getattr(self, "result_entry", None) or {}
        self.set_scoreboard_difficulty(entry.get("difficulty", self.difficulty))
        self.enter_online_scoreboard()

    def load_online_period_scores(self, period=None, force=False):
        self.ensure_online_score_state()
        period = period or getattr(self, "online_period", SCOREBOARD_PERIOD_LOCAL)
        if period == SCOREBOARD_PERIOD_LOCAL:
            local_entries = self.local_entries_for_current_scoreboard_variant()
            self.online_score_raw_cache[SCOREBOARD_PERIOD_LOCAL] = local_entries
            scores = get_top_scores(
                local_entries,
                limit=10,
                difficulty=self.scoreboard_difficulty(),
            )
            self.online_score_cache[SCOREBOARD_PERIOD_LOCAL] = scores
            return scores
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        score_variant = variant_scoreboard_key()
        key = self.scoreboard_period_key(period, now)
        online = fetch_online_scores(
            period,
            timestamp=now,
            variant=score_variant or None,
            difficulty=self.scoreboard_difficulty(),
        )
        if online is None:
            self.online_score_load_result = "failed"
            online = load_online_score_cache(
                period,
                key,
                variant=self.online_score_cache_variant(),
                difficulty=self.scoreboard_difficulty(),
            )
            online = self.online_dedicated_variant_entries(online)
            scores = []
            if online:
                scores = get_period_scores(online, period, key, limit=10, difficulty=self.scoreboard_difficulty())
        elif online:
            online = self.online_dedicated_variant_entries(online)
            save_online_score_cache(
                period,
                key,
                online,
                variant=self.online_score_cache_variant(),
                difficulty=self.scoreboard_difficulty(),
            )
            scores = get_period_scores(online, period, key, limit=10, difficulty=self.scoreboard_difficulty())
        else:
            self.online_score_load_result = ""
            online = load_online_score_cache(
                period,
                key,
                variant=self.online_score_cache_variant(),
                difficulty=self.scoreboard_difficulty(),
            )
            online = self.online_dedicated_variant_entries(online)
            scores = []
            if online:
                scores = get_period_scores(online, period, key, limit=10, difficulty=self.scoreboard_difficulty())
        self.online_scores = scores
        self.store_online_score_cache(period, online or [], scores, now)
        self.online_score_loaded.add(self.online_score_loaded_key(period, now))
        return scores

    def online_dedicated_variant_entries(self, entries):
        score_variant = variant_scoreboard_key()
        if not score_variant:
            return entries
        return [
            {**entry, "variant": str(entry.get("variant") or score_variant)}
            for entry in entries
        ]

    def local_entries_for_current_scoreboard_variant(self):
        score_variant = variant_scoreboard_key()
        return [
            entry for entry in load_score_entries()
            if score_entry_is_nyandor(entry) == bool(score_variant)
        ]

    def current_user_local_score_entries(self):
        player_name = self.current_score_player_name().lower()
        return [
            entry for entry in self.local_entries_for_current_scoreboard_variant()
            if str(entry.get("player_name", "")).lower() == player_name
        ]

    def display_online_period_scores(self, period):
        scores = self.cached_online_scores(self.online_score_cache, period)
        if period == SCOREBOARD_PERIOD_LOCAL:
            return self.load_online_period_scores(SCOREBOARD_PERIOD_LOCAL)
        if period in (SCOREBOARD_PERIOD_WEEKLY, SCOREBOARD_PERIOD_SEASON):
            key = self.scoreboard_period_key(period)
            loaded_key = self.online_score_loaded_key(period)
            if not self.online_score_is_loaded(period):
                cached = load_online_score_cache(
                    period,
                    key,
                    variant=self.online_score_cache_variant(),
                    difficulty=self.scoreboard_difficulty(),
                )
                if cached:
                    cached = self.online_dedicated_variant_entries(cached)
                    scores = get_period_scores(
                        cached,
                        period,
                        key,
                        limit=10,
                        difficulty=self.scoreboard_difficulty(),
                    )
                    self.store_online_score_cache(period, cached, scores)
                    self.online_score_loaded.add(loaded_key)
            profile = normalize_online_profile(getattr(self, "online_profile", None))
            scores = self.cached_online_scores(self.online_score_raw_cache, period, scores)
            if not profile.get("local_only", True):
                scores = list(scores) + self.current_user_local_score_entries()
            return get_period_scores(
                self.online_dedicated_variant_entries(scores),
                period,
                key,
                limit=10,
                difficulty=self.scoreboard_difficulty(),
            )
        return scores

    def current_local_best_score_for_period(self, period, online_scores=None):
        if period not in (SCOREBOARD_PERIOD_WEEKLY, SCOREBOARD_PERIOD_SEASON):
            return None
        key = self.scoreboard_period_key(period)
        local_entries = self.current_user_local_score_entries()
        scores = get_period_scores(local_entries, period, key, limit=1, difficulty=self.scoreboard_difficulty())
        if not scores:
            return None
        best = scores[0]
        for online in online_scores or []:
            best_id = str(best.get("score_id", ""))
            online_id = str(online.get("score_id", ""))
            if best_id and best_id == online_id:
                return None
            if (
                str(best.get("player_name", "")).lower() == str(online.get("player_name", "")).lower()
                and int(best.get("score", 0)) == int(online.get("score", 0))
            ):
                return None
        return best

    def refresh_online_scoreboard_periods(self):
        ok = True
        periods = getattr(self, "online_sync_periods", []) or [SCOREBOARD_PERIOD_WEEKLY, SCOREBOARD_PERIOD_SEASON]
        original_difficulty = self.scoreboard_difficulty()
        difficulties = [variant_fixed_difficulty()] if variant_fixed_difficulty() else list(DIFFICULTY_ORDER)
        try:
            for period in periods:
                for difficulty in difficulties:
                    self.set_scoreboard_difficulty(difficulty)
                    try:
                        self.load_online_period_scores(period, force=True)
                        if getattr(self, "online_score_load_result", "") == "failed":
                            ok = False
                            break
                    except Exception:
                        ok = False
                        break
                if not ok:
                    break
        finally:
            self.set_scoreboard_difficulty(original_difficulty)
        self.online_score_load_result = ""
        return ok

    def perform_online_scoreboard_sync(self):
        self.ensure_online_score_state()
        profile = normalize_online_profile(getattr(self, "online_profile", None))
        if profile.get("local_only", True) or not profile.get("server_token", ""):
            self.online_sync_result = "Ranking refreshed. Guest mode."
            self.online_score_load_result = ""
            self.online_sync_status = "loading scoreboard..."
            try:
                record_guest_scoreboard_sync(variant=variant_scoreboard_key())
            except Exception:
                pass
            if not self.refresh_online_scoreboard_periods():
                self.online_sync_result = "Refresh failed. No local scores yet."
            return {"ok": True, "status": "guest_refresh", "posted_count": 0}
        self.online_sync_status = "posting local scores..."
        user_name = str(profile.get("user_name", "")).lower()
        entries = local_best_sync_entries(self.local_entries_for_current_scoreboard_variant(), player_name=user_name)
        entries = [
            entry for entry in entries
            if str(entry.get("player_name", "")).lower() == user_name
        ]
        post_allowed = bool(getattr(self, "online_sync_post_allowed", True))
        if not entries or not post_allowed:
            if entries:
                self.online_sync_result = "Ranking refreshed. POST once per hour."
            else:
                self.online_sync_result = "Ranking refreshed. No local scores yet."
            self.online_score_load_result = ""
            self.online_sync_status = "loading scoreboard..."
            if not self.refresh_online_scoreboard_periods():
                self.online_sync_result = "Refresh failed. POST once per hour." if entries else "Refresh failed. No local scores yet."
            status = "cooldown_refresh" if entries else "no_local_scores"
            return {"ok": True, "status": status, "posted_count": 0}
        result = sync_online_scoreboard(
            getattr(self, "online_profile", None),
            entries,
            variant=variant_scoreboard_key(),
        )
        status = str(result.get("status", "success" if result.get("ok") else "failed"))
        if result.get("ok"):
            self.online_sync_result = "Score posted. Ranking refreshed." if entries else "Ranking refreshed. No local scores yet."
        elif status == "cooldown":
            self.online_sync_result = "Ranking refreshed. POST once per hour."
            self.online_score_load_result = ""
            self.online_sync_status = "loading scoreboard..."
            if not self.refresh_online_scoreboard_periods():
                self.online_sync_result = "Refresh failed. POST once per hour."
        elif status == "auth_failed":
            self.online_sync_result = "Authentication failed. Register again."
            self.online_register_prompt = True
        else:
            self.online_sync_result = f"POST failed. {status}."
        if result.get("last_sync_at") or result.get("next_sync_at"):
            profile["last_sync_at"] = result.get("last_sync_at", profile.get("last_sync_at", ""))
            profile["next_sync_at"] = result.get("next_sync_at", profile.get("next_sync_at", ""))
            self.online_profile = save_online_profile(profile)
        self.online_score_load_result = ""
        if result.get("ok"):
            self.online_sync_status = "loading scoreboard..."
            if not self.refresh_online_scoreboard_periods():
                self.online_sync_result = "Score posted. Ranking refresh failed."
        return result

    def format_score_line_for_board(self, rank, entry, period):
        return rogue_online_scoreboard.format_score_line_for_board(rank, entry, self.lang)

    def format_score_line_for_board_ja(self, rank, entry):
        return rogue_online_scoreboard.format_score_line_for_board_ja(rank, entry)

    def is_current_result_score(self, entry):
        return rogue_online_scoreboard.is_current_result_score(entry, getattr(self, "result_entry", None))

    def mark_current_score_line(self, line):
        return rogue_online_scoreboard.mark_current_score_line(line)

    def online_result_lines(self, message, limit=27):
        return rogue_online_scoreboard.online_result_lines(message, self.lang, limit)

    def online_sync_box_lines(self):
        return rogue_online_scoreboard.online_sync_box_lines(
            getattr(self, "online_sync_post_allowed", True),
            self.lang,
        )

    def confirm_name_input(self):
        name = "".join(getattr(self, "name_chars", [])).strip()
        self.player_name = save_player_name(name)
        self.online_profile = save_local_only_profile(self.player_name)
        self.name_chars = list(self.player_name)
        self.name_pos = min(len(self.name_chars), 7)
        self.enter_title_screen(initial_fade=True)

    def open_name_input(self):
        self.enter_online_register()

    def upd_online_confirm(self):
        if self.online_language_toggle_pressed():
            self.toggle_online_language()
            return
        if self.btn_a() or self.btn_start_tap():
            self.enter_online_register(reset_to_default=True)
            return
        if self.btn_b():
            self.decline_online_registration()
            return

    def confirm_language_select(self):
        settings = self.ensure_settings()
        settings.language = LANG_JA if getattr(self, "language_cursor", 0) == 1 else LANG_EN
        self.settings = save_settings(settings)
        self.settings_missing = False
        self.enter_title_screen()

    def upd_language_select(self):
        d = self.menu_vertical_press()
        if d:
            self.language_cursor = (getattr(self, "language_cursor", 0) + d) % 2
        if self.btn_a() or self.btn_start_tap():
            self.confirm_language_select()
            return

    def upd_logo(self):
        self.start_title_bgm()
        self.logo_frames = getattr(self, "logo_frames", 0) + 1
        if self.btn_any_key():
            self.enter_post_logo()
            return
        if self.logo_frames >= LOGO_TOTAL_FRAMES:
            self.enter_post_logo()

    def upd_title(self):
        if getattr(self, "title_bgm_stop_wait", 0) > 0:
            self.title_bgm_stop_wait -= 1
            if self.title_bgm_stop_wait <= 0:
                self.prepare_title_new_game()
            return
        if getattr(self, "title_fade_frames", TITLE_FADE_FRAMES) < TITLE_FADE_FRAMES:
            if self.btn_any_key():
                self.title_fade_frames = TITLE_FADE_FRAMES
                return
            else:
                self.title_fade_frames = min(TITLE_FADE_FRAMES, getattr(self, "title_fade_frames", 0) + 1)
        d = self.menu_vertical_press()
        items = self.title_menu_items()
        if d:
            self.title_cursor = (getattr(self, "title_cursor", 0) + d) % len(items)
        if self.btn_a() or self.btn_start_tap():
            action = items[getattr(self, "title_cursor", 0) % len(items)]
            if action == "continue":
                self.load_saved_game_from_title()
                return
            if action == "dungeon":
                self.enter_difficulty_select()
            elif action == "scoreboard":
                self.stop_title_bgm()
                self.enter_online_scoreboard()
            elif self.is_online_mode():
                self.stop_title_bgm()
                self.enter_guest_mode_confirm()
            else:
                self.stop_title_bgm()
                self.enter_online_register(reset_to_default=True)

    def upd_difficulty_select(self):
        if getattr(self, "title_bgm_stop_wait", 0) > 0:
            self.title_bgm_stop_wait -= 1
            if self.title_bgm_stop_wait <= 0:
                self.prepare_title_new_game()
            return
        d = self.menu_vertical_press() or self.menu_horizontal_press()
        if d:
            self.change_difficulty_cursor(d)
            return
        if self.btn_overlay_cancel():
            self.st = ST_TITLE
            return
        if self.btn_a() or self.btn_start_tap():
            self.confirm_difficulty_select()

    def upd_nyandor_brief(self):
        if getattr(self, "title_bgm_stop_wait", 0) > 0:
            self.title_bgm_stop_wait -= 1
            if self.title_bgm_stop_wait <= 0:
                self.prepare_title_new_game()
            return
        if self.btn_overlay_cancel():
            self.st = ST_TITLE
            return
        if self.btn_a() or self.btn_start_tap():
            self.st = ST_NYANDOR_GUIDE

    def upd_nyandor_guide(self):
        if getattr(self, "title_bgm_stop_wait", 0) > 0:
            self.title_bgm_stop_wait -= 1
            if self.title_bgm_stop_wait <= 0:
                self.prepare_title_new_game()
            return
        if self.btn_overlay_cancel():
            self.st = ST_NYANDOR_BRIEF
            return
        if self.btn_a() or self.btn_start_tap():
            self.request_title_new_game()

    def upd_name(self):
        if self.btn_start_tap():
            self.confirm_name_input()
            return
        if self.btn_b():
            if getattr(self, "name_chars", []):
                self.name_chars.pop()
                self.name_pos = max(0, len(self.name_chars) - 1)
            else:
                self.enter_title_screen()
            return
        if self.kp(pyxel.KEY_LEFT, pyxel.KEY_H, pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            self.name_pos = max(0, getattr(self, "name_pos", 0) - 1)
        if self.kp(pyxel.KEY_RIGHT, pyxel.KEY_L, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            self.name_pos = min(8, getattr(self, "name_pos", 0) + 1)
        d = self.menu_vertical_press()
        if d:
            chars = getattr(self, "name_chars", [])
            pos = min(getattr(self, "name_pos", 0), 7)
            while len(chars) <= pos:
                chars.append(" ")
            idx = NAME_ALPHABET.index(chars[pos]) if chars[pos] in NAME_ALPHABET else 0
            chars[pos] = NAME_ALPHABET[(idx - d) % len(NAME_ALPHABET)]
            self.name_chars = chars[:8]
        if self.btn_a():
            if getattr(self, "name_pos", 0) >= 8:
                self.confirm_name_input()
            else:
                self.name_pos = min(8, getattr(self, "name_pos", 0) + 1)

    def upd_online_register(self):
        if self.run_pending_online_action():
            return
        if self.online_language_toggle_pressed():
            self.toggle_online_language()
            return
        if self.btn_b():
            self.cancel_or_confirm_local_only_name()
            return
        if self.btn_start_tap():
            if self.apply_online_name_candidate():
                return
            self.confirm_online_user_id()
            return
        if self.kp(pyxel.KEY_LEFT, pyxel.KEY_H, pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            self.name_pos = max(0, getattr(self, "name_pos", 0) - 1)
        if self.kp(pyxel.KEY_RIGHT, pyxel.KEY_L, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            max_pos = USER_NAME_MAX + self.online_name_candidate_count()
            self.name_pos = min(max_pos, getattr(self, "name_pos", 0) + 1)
        d = self.menu_vertical_press()
        if d and self.online_name_candidate_index() >= 0:
            idx = max(0, min(self.online_name_candidate_count() - 1, self.online_name_candidate_index() + d))
            self.name_pos = USER_NAME_MAX + 1 + idx
            return
        if d and getattr(self, "name_pos", 0) < USER_NAME_MAX:
            chars = getattr(self, "name_chars", [])
            pos = min(getattr(self, "name_pos", 0), USER_NAME_MAX - 1)
            while len(chars) <= pos:
                chars.append(" ")
            idx = NAME_ALPHABET.index(chars[pos]) if chars[pos] in NAME_ALPHABET else 0
            chars[pos] = NAME_ALPHABET[(idx - d) % len(NAME_ALPHABET)]
            self.name_chars = chars[:USER_NAME_MAX]
        if self.btn_a():
            if self.apply_online_name_candidate():
                return
            if getattr(self, "name_pos", 0) >= USER_NAME_MAX:
                self.confirm_online_user_id()
            else:
                self.name_pos = min(USER_NAME_MAX, getattr(self, "name_pos", 0) + 1)

    def upd_online_pin(self):
        if self.run_pending_online_action():
            return
        if self.online_language_toggle_pressed():
            self.toggle_online_language()
            return
        if self.btn_b():
            self.enter_online_register()
            return
        if self.btn_start_tap():
            self.finish_online_password()
            return
        if self.kp(pyxel.KEY_LEFT, pyxel.KEY_H, pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            self.name_pos = max(0, getattr(self, "name_pos", 0) - 1)
        if self.kp(pyxel.KEY_RIGHT, pyxel.KEY_L, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            self.name_pos = min(6, getattr(self, "name_pos", 0) + 1)
        d = self.menu_vertical_press()
        if d:
            chars = getattr(self, "online_password_chars", ["0"] * 6)
            pos = min(getattr(self, "name_pos", 0), 5)
            idx = PIN_ALPHABET.index(chars[pos]) if chars[pos] in PIN_ALPHABET else 0
            chars[pos] = PIN_ALPHABET[(idx - d) % len(PIN_ALPHABET)]
            self.online_password_chars = chars[:6]
        if self.btn_a():
            if getattr(self, "name_pos", 0) >= 6:
                self.finish_online_password()
            else:
                self.name_pos = min(6, getattr(self, "name_pos", 0) + 1)

    def upd_online_score(self):
        if getattr(self, "online_register_prompt", False):
            if self.btn_a() or self.btn_start_tap() or self.btn_back():
                self.enter_online_register()
                return
            if self.btn_b():
                self.online_profile = save_local_only_profile("guest")
                self.online_register_prompt = False
                self.online_sync_result = "Local only."
                return
        if self.btn_b():
            self.cancel_online_sync()
            self.enter_title_screen()
            return
        self.ensure_online_score_state()
        pending_sync = rogue_online_state.advance_online_pending_sync(self)
        if pending_sync == "waiting":
            return
        if pending_sync == "ready":
            self.perform_online_scoreboard_sync()
            rogue_online_state.finish_online_pending_sync(self)
            return
        if self.online_syncing:
            return
        dy = self.menu_vertical_press()
        if dy:
            self.change_scoreboard_difficulty(dy)
            return
        if self.kp(pyxel.KEY_LEFT, pyxel.KEY_H, pyxel.KEY_RIGHT, pyxel.KEY_L,
                   pyxel.GAMEPAD1_BUTTON_DPAD_LEFT, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            d = -1 if self.kp(pyxel.KEY_LEFT, pyxel.KEY_H, pyxel.GAMEPAD1_BUTTON_DPAD_LEFT) else 1
            self.online_period = rogue_online_scoreboard.cycle_scoreboard_period(
                getattr(self, "online_period", SCOREBOARD_PERIOD_LOCAL),
                d,
            )
            return
        if pyxel.btnp(pyxel.KEY_R) or self.btn_back():
            profile = normalize_online_profile(getattr(self, "online_profile", None))
            if profile.get("local_only", True) or getattr(self, "online_register_prompt", False):
                self.request_online_period_scores(force=True)
                return
            self.request_online_period_scores(force=True)
            return

    # ---------- Update ----------
    def update(self):
        if hasattr(self, "sfx"):
            self.sfx.update()
        self.update_death_result_bgm()
        if self.st in (ST_LOGO, ST_LANGUAGE, ST_TITLE, ST_DIFFICULTY, ST_NYANDOR_BRIEF, ST_NYANDOR_GUIDE, ST_NAME, ST_ONLINE_SCORE, ST_ONLINE_REGISTER, ST_ONLINE_PIN, ST_ONLINE_CONFIRM, ST_ONLINE_LOCAL_CONFIRM):
            self.begin_input()
            if self.st == ST_LOGO: self.upd_logo()
            elif self.st == ST_LANGUAGE: self.upd_language_select()
            elif self.st == ST_TITLE: self.upd_title()
            elif self.st == ST_DIFFICULTY: self.upd_difficulty_select()
            elif self.st == ST_NYANDOR_BRIEF: self.upd_nyandor_brief()
            elif self.st == ST_NYANDOR_GUIDE: self.upd_nyandor_guide()
            elif self.st == ST_NAME: self.upd_name()
            elif self.st == ST_ONLINE_SCORE: self.upd_online_score()
            elif self.st == ST_ONLINE_REGISTER: self.upd_online_register()
            elif self.st == ST_ONLINE_PIN: self.upd_online_pin()
            elif self.st == ST_ONLINE_CONFIRM: self.upd_online_confirm()
            elif self.st == ST_ONLINE_LOCAL_CONFIRM: self.upd_online_local_confirm()
            return
        if self.st == ST_LOADING:
            if self._loading_phase == 0:
                self._loading_phase = 1  # let draw() show loading screen first
            else:
                self.new_game()
                self.st = ST_PLAY
            return
        self.begin_input()
        if self.throw_anim:
            self.throw_anim["tick"] += 1
            if self.throw_anim["tick"] >= len(self.throw_anim["path"]) * self.throw_anim["delay"]:
                anim = self.throw_anim
                self.throw_anim = None
                self.resolve_throw_anim(anim)
                if self.turn_after_throw_anim:
                    self.turn_after_throw_anim = False
                    self.end_turn()
            return
        if self.st==ST_DEAD:
            if not self.death_intro_finished():
                if self.death_intro_accepts_input() and (self.btn_a() or self.btn_start_tap() or pyxel.btnp(pyxel.KEY_R)):
                    self.finish_death_intro()
                return
            self.finish_death_intro()
            if self.btn_a() or self.btn_start_tap() or pyxel.btnp(pyxel.KEY_R): self.enter_result_scoreboard()
            return
        if self.st==ST_WIN:
            if self.btn_a() or self.btn_start_tap() or pyxel.btnp(pyxel.KEY_R): self.enter_result_scoreboard()
            return
        if self.st==ST_QUIT:
            if self.btn_a() or self.btn_start_tap() or pyxel.btnp(pyxel.KEY_R): self.enter_result_scoreboard()
            return
        if self.st==ST_SCORE:
            if self.btn_a() or self.btn_start_tap() or pyxel.btnp(pyxel.KEY_R) or self.kp(
                pyxel.KEY_LEFT, pyxel.KEY_H, pyxel.KEY_RIGHT, pyxel.KEY_L,
                pyxel.GAMEPAD1_BUTTON_DPAD_LEFT, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT
            ) or self.btn_back():
                self.enter_online_scoreboard()
            return
        if self.st==ST_QUIT_CONFIRM:
            if self.btn_overlay_cancel():
                self.st=ST_PLAY
                return
            if self.btn_a() or self.btn_start_tap():
                self.enter_result_state("quit")
                return
            return
        if self.st==ST_PLAY:   self.upd_play()
        elif self.st==ST_MENU: self.upd_menu()
        elif self.st==ST_ITEM: self.upd_item()
        elif self.st==ST_CALL: self.upd_call()
        elif self.st==ST_DISC: self.upd_disc()
        elif self.st==ST_DIR:  self.upd_dir()
        elif self.st==ST_AUX:  self.upd_aux()
        elif self.st==ST_INVENTORY:
            self.upd_info()
        elif self.st==ST_LOG:
            self.upd_log()
        elif self.st==ST_SETTINGS:
            self.upd_settings()
        elif self.st==ST_SAVE_CONFIRM:
            self.upd_save_confirm()
        elif self.st==ST_HELP:
            self.upd_help()

    def upd_play(self):
        if getattr(self, "message_ack_pending", False):
            if self.btn_a() or self.btn_start_tap():
                self.message_ack_pending = False
            return

        if getattr(self, "identify_symbol_pending", False):
            if self.update_symbol_identify_prompt():
                return

        if self.p.no_command>0:
            self.wake_visible_monsters()
            self.msg("pyxel.unable_to_move")
            self.end_turn()
            return

        if self.continue_fight_to_death():
            return

        # Dash continuation
        if self.dashing:
            if not self.dash_held():
                self.dash_state.stop(restart_guard=False); return
            self.b_used=True
            if self.dash_state.tick(self.run_step_interval()):
                self.dash_step()
            return

        if self.continue_counted_command():
            return

        # Overlays
        sd=self.select_dir_press()
        if sd:
            self.inspect_trap(*sd)
            self.dir_pending=None
            return
        if self.btn_select_a():
            self.start_item_action("Throw")
            self.dir_pending=None
            return
        if self.btn_select_b():
            self.do_search()
            self.dir_pending=None
            return
        if self.btn_inventory():
            self.record_repeat_command("inventory")
            self.command_look(); self.st=ST_INVENTORY; self.command_look_done=False; return
        if self.btn_back():
            self.command_look(); self.st=ST_INVENTORY; self.command_look_done=False; return
        if self.btn_r():
            self.record_repeat_command("help")
            self.open_help_command(); return
        if self.kp(getattr(pyxel, "KEY_SLASH", None)):
            self.record_repeat_command("symbol_identify")
            self.open_symbol_identify_command(); return
        if self.key_upper(getattr(pyxel, "KEY_I", None)):
            self.record_repeat_command("picky_inventory")
            self.open_picky_inventory_command(); return
        if self.key_upper(getattr(pyxel, "KEY_PERIOD", None)):
            self.record_repeat_command("stairs_down")
            self.stairs_down_command(); return
        if self.key_upper(getattr(pyxel, "KEY_COMMA", None)):
            self.record_repeat_command("stairs_up")
            self.stairs_up_command(); return
        if self.key_lower(getattr(pyxel, "KEY_COMMA", None)):
            self.record_repeat_command("pickup")
            self.do_pickup(); return
        if self.key_lower(getattr(pyxel, "KEY_V", None)):
            self.record_repeat_command("version")
            self.show_version_command(); return
        if self.key_lower(getattr(pyxel, "KEY_O", None)):
            self.record_repeat_command("options")
            self.open_options_command(); return
        if self.key_lower(getattr(pyxel, "KEY_M", None)):
            if not self.count_prefix_active:
                self.record_repeat_command("move_on")
            self.start_move_on_command(); return
        if self.key_lower(getattr(pyxel, "KEY_F", None)):
            self.record_repeat_command("fight")
            self.start_fight_command(False); return
        if self.key_upper(getattr(pyxel, "KEY_F", None)):
            self.record_repeat_command("fight_to_death")
            self.start_fight_command(True); return
        if self.key_upper(getattr(pyxel, "KEY_Q", None)):
            self.record_repeat_command("quit")
            self.quit_command(); return
        if self.key_upper(getattr(pyxel, "KEY_S", None)):
            self.save_command(); return
        if self.key_upper(getattr(pyxel, "KEY_0", None)):
            self.record_repeat_command("current_weapon")
            self.current_item_command(self.p.wpn, "wielding", None, "手に持っている")
            return
        if self.kp(getattr(pyxel, "KEY_RIGHTBRACKET", None)):
            self.record_repeat_command("current_armor")
            self.current_item_command(self.p.arm, "wearing", None, "装着中")
            return
        if self.kp(getattr(pyxel, "KEY_EQUALS", None)):
            self.record_repeat_command("current_rings")
            self.current_rings_command()
            return
        if self.kp(getattr(pyxel, "KEY_AT", None)):
            self.record_repeat_command("status")
            self.status_command()
            return
        ctrl_command = self.ctrl_command_press()
        if ctrl_command == "repeat":
            self.record_repeat_command("repeat_message")
            self.repeat_message_command()
            return
        if ctrl_command == "redraw":
            self.record_repeat_command("redraw")
            self.redraw_command()
            return
        if self.legal_space_command_press():
            self.record_repeat_command("legal_space")
            self.legal_space_command()
            return
        count_digit = self.count_digit_press()
        if count_digit is not None:
            self.start_count_prefix(count_digit)
            return
        if self.key_lower(getattr(pyxel, "KEY_A", None)):
            count = self.count_input_state.take_prefix()
            if count is not None and count > 1:
                self.count_input_state.start_repeat("again", count)
            self.repeat_last_command()
            return
        if self.btn_wait():
            if self.kp(getattr(pyxel, "KEY_PERIOD", None)):
                self.record_counted_input_command("wait")
            self.do_wait(); return
        if self.btn_search():
            self.record_counted_input_command("search")
            self.do_search(); return
        if self.btn_trap_inspect():
            self.record_repeat_command("trap")
            self.start_trap_inspect(); return
        if self.key_upper(getattr(pyxel, "KEY_D", None)):
            self.record_repeat_command("discoveries")
            self.open_discoveries(); return
        aname = self.rogue_command_action()
        if aname:
            if aname == "Zap" and not self.p.inv:
                # C: command.c:'z' asks for direction before sticks.c:do_zap() asks for an item.
                self.record_repeat_command(("item", aname))
                self.command_look()
                self.action_origin = ST_PLAY
                self.cact = aname
                self.dact = aname
                self.zap_item = None
                self.st = ST_DIR
                self.dir_pending = None
                return
            self.record_repeat_command(("item", aname))
            self.start_item_action(aname)
            return
        illegal = self.illegal_command_press()
        if illegal:
            self.record_repeat_command(("illegal", illegal))
            self.illegal_command(illegal)
            return

        # Dash start: B/Shift held + direction
        if self.dash_state.can_start(self.dash_held(), self.dash_restart_dir_press()):
            d = self.held_dir()
            if d:
                self.dash_state.start(d)
                self.b_used=True
                self.dash_step()
                return

        # Normal direction
        d = self.dir_press()
        if d:
            self.record_counted_input_command("move", d)
            self.try_move(*d)
            return

        if self.btn_a(): self.do_action(); return
        if self.btn_menu(): self.open_menu(); return

    def upd_menu(self):
        dx=self.menu_horizontal_press()
        if dx:
            self.mcur=pad_menu_move(self.mcur,dx,0,MENU_ACTIONS)
            self.menu_cursor_restored=False
            self.request_sfx(rogue_sfx.SFX_SELECT_LOW)
            return
        dy=self.menu_vertical_press()
        if dy:
            self.mcur=pad_menu_move(self.mcur,0,dy,MENU_ACTIONS)
            self.menu_cursor_restored=False
            self.request_sfx(rogue_sfx.SFX_SELECT_LOW)
            return
        if self.btn_a(): self.menu_select(); return
        if self.btn_overlay_cancel(): self.close_menu(); return

    def upd_item(self):
        letter_press = self.pack_letter_press()
        if letter_press is not None:
            ch, letter_item = letter_press
            if letter_item is None:
                if self.cact == "Picky inventory":
                    self.invalid_picky_inventory_letter(ch)
                else:
                    self.invalid_pack_letter(ch)
                return
            self.confirm_item(letter_item)
            return
        dx=self.menu_horizontal_press()
        if dx and self.fitems:
            self.icur=pack_grid_move(self.icur,dx,0,len(self.fitems), self.pack_grid_max_rows(self.fitems)); self.item_cursor_restored=False; self.request_sfx(rogue_sfx.SFX_SELECT_LOW); return
        dy=self.menu_vertical_press()
        if dy and self.fitems: self.icur=pack_grid_move(self.icur,0,dy,len(self.fitems), self.pack_grid_max_rows(self.fitems)); self.item_cursor_restored=False; self.request_sfx(rogue_sfx.SFX_SELECT_LOW); return
        if self.btn_a(): self.item_confirm(); return
        if self.btn_overlay_cancel():
            self.cancel_item_prompt()
            return

    def upd_call(self):
        # Phase 1: アイテム選択
        if self.call_item is None:
            letter_press = self.pack_letter_press()
            if letter_press is not None:
                ch, letter_item = letter_press
                if letter_item is None:
                    self.invalid_pack_letter(ch)
                    return
                if self.call_result(letter_item) == rogue_things.CALL_RESULT_OK:
                    self.call_item = letter_item
                else:
                    self.apply_call_name(letter_item, "")
                    self.close_menu()
                return
            dy = self.menu_vertical_press()
            if dy and self.fitems:
                self.icur = (self.icur + dy) % len(self.fitems)
                return
            if self.btn_a():
                it = self.fitems[self.icur] if self.fitems else None
                if it is None:
                    self.close_menu(); return
                self.call_item = it
                return
            if self.btn_overlay_cancel():
                self.cancel_call_prompt(); return
            return
        # Phase 2: テキスト入力
        dy = self.menu_vertical_press()
        if dy:
            self.call_preset_idx = (self.call_preset_idx - dy) % len(CALL_PRESETS)
            self.call_input = CALL_PRESETS[self.call_preset_idx]
            return
        # キーボード文字入力
        for key_name, ch in (
            ("KEY_A","a"),("KEY_B","b"),("KEY_C","c"),("KEY_D","d"),
            ("KEY_E","e"),("KEY_F","f"),("KEY_G","g"),("KEY_H","h"),
            ("KEY_I","i"),("KEY_J","j"),("KEY_K","k"),("KEY_L","l"),
            ("KEY_M","m"),("KEY_N","n"),("KEY_O","o"),("KEY_P","p"),
            ("KEY_Q","q"),("KEY_R","r"),("KEY_S","s"),("KEY_T","t"),
            ("KEY_U","u"),("KEY_V","v"),("KEY_W","w"),("KEY_X","x"),
            ("KEY_Y","y"),("KEY_Z","z"),("KEY_SPACE"," "),
        ):
            k = getattr(pyxel, key_name, None)
            if k is not None and pyxel.btnp(k):
                c = ch.upper() if (ch.isalpha() and self.shift_held()) else ch
                self.call_input = (self.call_input + c)[:16]
                return
        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            self.call_input = self.call_input[:-1]
            return
        if self.btn_a() or pyxel.btnp(pyxel.KEY_RETURN):
            self.apply_call_name(self.call_item, self.call_input)
            self.close_menu()
            # ターン消費なし (misc.c:call_it() 準拠)
            return
        if self.btn_overlay_cancel():
            self.cancel_call_prompt(); return

    def upd_disc(self):
        lines = getattr(self, "disc_lines", None) or self._disc_lines()
        visible = 18
        max_scroll = max(0, len(lines) - visible)
        dy = self.menu_vertical_press()
        if dy:
            self.disc_scroll = max(0, min(self.disc_scroll + dy, max_scroll))
            return
        if self.btn_a() or self.btn_overlay_cancel():
            self.st = getattr(self, "disc_return_state", ST_PLAY); return

    def upd_dir(self):
        d=self.dir_prompt_press()
        if d: self.dir_confirm(*d); return
        if self.btn_overlay_cancel():
            self.cancel_dir_prompt()
            return

    def open_aux(self):
        self.open_settings()

    def log_visible_rows(self):
        return max(1, (SCR_H - 98) // 11)

    def open_log(self):
        self.st = ST_LOG
        self.dir_pending = None
        max_scroll = max(0, len(getattr(self, "msgs", [])) - self.log_visible_rows())
        self.log_scroll = max_scroll

    def open_settings(self):
        self.st = ST_SETTINGS
        self.dir_pending = None
        self.settings_focus = "row"
        self.settings_cursor = max(0, min(getattr(self, "settings_cursor", 0), len(self.settings_rows()) - 1))

    def info_tab_index(self):
        return {ST_INVENTORY: 0, ST_LOG: 1, ST_SETTINGS: 2, ST_HELP: 3}.get(self.st, 0)

    def set_info_tab_index(self, index):
        tabs = (ST_INVENTORY, ST_LOG, ST_SETTINGS, ST_HELP)
        previous = self.st
        self.st = tabs[index % len(tabs)]
        if self.st == ST_LOG:
            max_scroll = max(0, len(getattr(self, "msgs", [])) - self.log_visible_rows())
            if previous != ST_LOG:
                self.log_scroll = max_scroll
            else:
                self.log_scroll = max(0, min(getattr(self, "log_scroll", max_scroll), max_scroll))
        if self.st == ST_SETTINGS:
            self.settings_focus = "row"
            self.settings_cursor = max(0, min(getattr(self, "settings_cursor", 0), len(self.settings_rows()) - 1))

    def upd_info_common(self, allow_horizontal=True):
        dx = self.menu_horizontal_press()
        if dx and allow_horizontal:
            self.set_info_tab_index(self.info_tab_index() + dx)
            return True
        if self.btn_back():
            self.st = ST_PLAY
            return True
        if self.btn_r():
            self.st = ST_HELP
            return True
        if self.btn_a() or self.btn_overlay_cancel() or self.btn_inventory():
            self.st = ST_PLAY
            return True
        return False

    def upd_info(self):
        self.upd_info_common()

    def upd_log(self):
        if self.menu_horizontal_press():
            self.upd_info_common()
            return
        visible = self.log_visible_rows()
        max_scroll = max(0, len(getattr(self, "msgs", [])) - visible)
        dy = self.log_vertical_repeat()
        if dy:
            self.log_scroll = max(0, min(getattr(self, "log_scroll", 0) + dy, max_scroll))
            return
        self.log_scroll = max(0, min(getattr(self, "log_scroll", 0), max_scroll))
        self.upd_info_common()

    def log_vertical_repeat(self):
        if self.menu_vertical_press():
            self.log_repeat_frame = pyxel.frame_count
            return self.menu_vertical_press()
        held = -1 if self._held_up() else 1 if self._held_dn() else 0
        if not held:
            self.log_repeat_frame = pyxel.frame_count
            return 0
        last = getattr(self, "log_repeat_frame", pyxel.frame_count)
        if pyxel.frame_count - last >= 4:
            self.log_repeat_frame = pyxel.frame_count
            return held
        return 0

    def upd_help(self):
        self.upd_info_common()

    def settings_rows(self):
        return ("Auto pickup", "Dungeon BGM", "Language", "Palette", "Save and quit")

    def settings_row_index(self, name):
        return self.settings_rows().index(name)

    def setting_value_label(self, name):
        if name == "Auto pickup":
            return TextCatalog.msg(self.lang, "settings.on" if self.auto_pickup else "settings.off")
        if name == "Dungeon BGM":
            return TextCatalog.msg(self.lang, "settings.on" if self.ensure_settings().dungeon_bgm else "settings.off")
        if name == "Language":
            return "日本語" if self.lang == LANG_JA else "English"
        if name == "Palette":
            return PALETTE_LABELS[self.ensure_settings().palette]
        return ""

    def change_setting(self, delta):
        row = self.settings_rows()[getattr(self, "settings_cursor", 0)]
        if row == "Auto pickup":
            self.toggle_auto_pickup()
        elif row == "Dungeon BGM":
            self.toggle_dungeon_bgm()
        elif row == "Language":
            self.set_lang(LANG_JA if self.lang == LANG_EN else LANG_EN, persist=True)
        elif row == "Palette":
            settings = self.ensure_settings()
            i = PALETTE_IDS.index(settings.palette) if settings.palette in PALETTE_IDS else 0
            settings.palette = PALETTE_IDS[(i + delta) % len(PALETTE_IDS)]
            self.apply_palette()
            self.persist_settings()
        elif row == "Save and quit":
            self.save_confirm_return_state = ST_SETTINGS
            self.st = ST_SAVE_CONFIRM

    def upd_settings(self):
        if getattr(self, "settings_focus", "row") == "value" and self.btn_overlay_cancel():
            self.settings_focus = "row"
            return
        if self.btn_a():
            if self.settings_rows()[getattr(self, "settings_cursor", 0)] == "Save and quit":
                self.save_confirm_return_state = ST_SETTINGS
                self.st = ST_SAVE_CONFIRM
                return
            self.settings_focus = "row" if getattr(self, "settings_focus", "row") == "value" else "value"
            return
        dy = self.menu_vertical_press()
        if dy and getattr(self, "settings_focus", "row") == "row":
            self.settings_cursor = (getattr(self, "settings_cursor", 0) + dy) % len(self.settings_rows())
            self.request_sfx(rogue_sfx.SFX_SELECT_LOW)
            return
        dx = self.menu_horizontal_press()
        if dx and getattr(self, "settings_focus", "row") == "value":
            self.request_sfx(rogue_sfx.SFX_SELECT_HIGH)
            self.change_setting(dx)
            return
        self.upd_info_common(allow_horizontal=getattr(self, "settings_focus", "row") == "row")

    def save_and_quit(self):
        rogue_save.save(self.save_state())
        if sys.platform != "emscripten" and hasattr(pyxel, "quit"):
            pyxel.quit()
            return
        self.enter_title_screen(skip_fade=True)

    def upd_save_confirm(self):
        if self.btn_overlay_cancel():
            self.st = getattr(self, "save_confirm_return_state", ST_SETTINGS)
            return
        if self.btn_a() or self.btn_start_tap():
            try:
                self.save_and_quit()
            except Exception:
                self.msg("save.failed")
                self.st = getattr(self, "save_confirm_return_state", ST_SETTINGS)

    def upd_aux(self):
        dy=self.menu_vertical_press()
        if dy: self.acur=(self.acur+dy)%len(AUX_ACTIONS); return
        if self.btn_overlay_cancel(): self.st=ST_PLAY; return
        if not self.btn_a(): return
        act=AUX_ACTIONS[self.acur]
        if act=="Search":
            self.st=ST_PLAY
            self.do_search()
        elif act=="Trap":
            self.start_trap_inspect()
        elif act=="Pickup":
            self.toggle_auto_pickup()
            self.msg("pyxel.pickup_on" if self.auto_pickup else "pyxel.pickup_off")
            self.st=ST_PLAY
        elif act=="Language":
            self.toggle_lang()
            self.st=ST_PLAY
        elif act=="Palette":
            self.toggle_palette()
            self.st=ST_PLAY
        elif act=="Quit":
            self.quit_command()
        self.dir_pending=None

    # =====================================================
    #  DRAW
    # =====================================================
    def draw(self):
        pyxel.cls(0)
        if self.st == ST_LOGO:
            self.draw_logo_screen()
            return
        if self.st == ST_LANGUAGE:
            self.draw_language_select_screen()
            return
        if self.st == ST_TITLE:
            self.draw_title_screen()
            return
        if self.st == ST_DIFFICULTY:
            self.draw_difficulty_select_screen()
            return
        if self.st == ST_NYANDOR_BRIEF:
            self.draw_nyandor_brief_screen()
            return
        if self.st == ST_NYANDOR_GUIDE:
            self.draw_nyandor_guide_screen()
            return
        if self.st == ST_NAME:
            self.draw_name_input()
            return
        if self.st == ST_ONLINE_SCORE:
            self.draw_online_score_screen()
            return
        if self.st == ST_ONLINE_REGISTER:
            self.draw_online_register_screen()
            return
        if self.st == ST_ONLINE_PIN:
            self.draw_online_pin_screen()
            return
        if self.st == ST_ONLINE_LOCAL_CONFIRM:
            self.draw_online_local_confirm_screen()
            return
        if self.st == ST_ONLINE_CONFIRM:
            self.draw_online_confirm_screen()
            return
        if self.st == ST_LOADING:
            msg = TextCatalog.msg(self.lang, "ui.loading")
            self.txt(SCR_W // 2 - 30, SCR_H // 2, msg, 10)
            return
        if self.st == ST_DEAD:
            self.draw_death_transition()
            return
        self.draw_title()
        self.draw_zoom()
        self.draw_stat()
        self.draw_msgs()
        # Overlays
        self.draw_overlays()

    def draw_death_transition(self):
        elapsed = self.death_intro_elapsed()
        if elapsed < DEATH_RIP_START_FRAMES:
            if elapsed < DEATH_SHAKE_FRAMES:
                shake = max(0, DEATH_SHAKE_FRAMES - elapsed)
            else:
                shake = 0
            if shake:
                ox = (-1 if elapsed % 2 else 1) * min(2, shake)
                oy = 1 if elapsed % 3 == 0 else 0
                pyxel.camera(ox, oy)
            self.draw_title()
            self.draw_zoom()
            self.draw_stat()
            self.draw_msgs()
            if shake:
                pyxel.camera()
            fade = max(0, elapsed - DEATH_INPUT_LOCK_FRAMES)
            if fade > 0:
                pyxel.dither(min(1.0, fade / DEATH_FADE_OUT_FRAMES))
                pyxel.rect(0, 0, SCR_W, SCR_H, 0)
                pyxel.dither(1.0)
            return
        self.draw_title()
        self.draw_zoom()
        self.draw_stat()
        self.draw_dead()
        if not self.death_intro_finished():
            fade_in = elapsed - DEATH_RIP_START_FRAMES
            pyxel.dither(max(0.0, 1.0 - fade_in / DEATH_FADE_IN_FRAMES))
            pyxel.rect(0, 0, SCR_W, SCR_H, 0)
            pyxel.dither(1.0)

    def draw_logo_screen(self):
        self.apply_title_palette()
        frame = getattr(self, "logo_frames", 0)
        logo_frame = frame - LOGO_BGM_DELAY_FRAMES
        if logo_frame < 0:
            alpha = 0.0
        elif logo_frame < LOGO_FADE_FRAMES:
            alpha = max(0.0, min(1.0, logo_frame / LOGO_FADE_FRAMES))
        elif logo_frame < LOGO_FADE_FRAMES + LOGO_HOLD_FRAMES:
            alpha = 1.0
        elif logo_frame < LOGO_FADE_FRAMES + LOGO_HOLD_FRAMES + LOGO_FADE_FRAMES:
            fade_frame = logo_frame - LOGO_FADE_FRAMES - LOGO_HOLD_FRAMES
            alpha = max(0.0, min(1.0, (LOGO_FADE_FRAMES - fade_frame) / LOGO_FADE_FRAMES))
        else:
            alpha = 0.0
        lines = [
            ("ORIGINAL ROGUE 5.4.4", LOGO_ACCENT_COL),
            ("(C) 1980-1983, 1985, 1999", LOGO_TEXT_COL),
            ("MICHAEL TOY, KEN ARNOLD", LOGO_TEXT_COL),
            ("AND GLENN WICHMAN", LOGO_TEXT_COL),
            ("", LOGO_TEXT_COL),
            ("PYXEL VERSION", LOGO_ACCENT_COL),
            ("(C) 2026 HSL LABORATORY", LOGO_TEXT_COL),
        ]
        y = 92
        pyxel.dither(alpha)
        for i, (line, col) in enumerate(lines):
            if line:
                self.txt(SCR_W // 2 - len(line) * 3, y + i * 14, line, col)
        pyxel.dither(1.0)

    def draw_title_screen(self):
        self.apply_title_palette()
        if not hasattr(self, "title_bg"):
            self.load_title_background()
        title_alpha = 1.0
        if self.title_bg is not None:
            title_alpha = max(0.0, min(1.0, getattr(self, "title_fade_frames", TITLE_FADE_FRAMES) / TITLE_FADE_FRAMES))
            pyxel.dither(title_alpha)
            pyxel.blt(0, 0, self.title_bg, 0, 0, SCR_W, SCR_H)
            pyxel.dither(1.0)
        if title_alpha < 1.0:
            return
        if self.title_bg is None:
            title_lines = variant_title_lines()
            title_y = 42 if is_nyandor_variant() else 58
            for i, line in enumerate(title_lines):
                col = TITLE_MENU_SELECTED_COL if i == 0 else TITLE_MENU_TEXT_COL
                self.txt_centered(TITLE_LOGO_RIGHT_X // 2 + 34, title_y + i * 12, line, col)
        online = self.is_online_mode()
        menu_items = self.title_menu_items()
        if getattr(self, "lang", LANG_EN) == LANG_JA:
            mode_line = "モード: オンライン" if online else "モード: ゲスト"
            user_prefix = "ユーザ"
        else:
            mode_line = "MODE: ONLINE" if online else "MODE: GUEST"
            user_prefix = "USER"
        items = [self.title_menu_label(item) for item in menu_items]
        x = TITLE_MENU_X
        panel_h = TITLE_MENU_H + (28 if online else 16) + max(0, len(items) - 3) * 24
        y = min(TITLE_MENU_Y, SCR_H - panel_h + 10)
        pyxel.dither(0.8)
        pyxel.rect(x - 28, y - 10, TITLE_MENU_W, panel_h, 0)
        pyxel.dither(1.0)
        pyxel.rectb(x - 28, y - 10, TITLE_MENU_W, panel_h, TITLE_MENU_BORDER_COL)
        cur = getattr(self, "title_cursor", 0) % len(items)
        for i, item in enumerate(items):
            self.txt(x - 15, y + i * 24, ">" if i == cur else " ", TITLE_MENU_SELECTED_COL)
            self.txt(x, y + i * 24, item, TITLE_MENU_SELECTED_COL if i == cur else TITLE_MENU_TEXT_COL)
        status_y = y + len(items) * 24 - 2
        self.txt(x, status_y, mode_line, TITLE_MENU_SELECTED_COL)
        if online:
            self.txt(x, status_y + 12, f"{user_prefix}: {self.current_user_id()}", TITLE_MENU_SELECTED_COL)
        if getattr(self, "title_save_error", ""):
            self.txt(x, y + panel_h - 12, self.title_save_error, TITLE_MENU_SELECTED_COL)

    def draw_difficulty_select_screen(self):
        self.apply_title_palette()
        if not hasattr(self, "title_bg"):
            self.load_title_background()
        if self.title_bg is not None:
            pyxel.blt(0, 0, self.title_bg, 0, 0, SCR_W, SCR_H)
        bx, by, bw, bh = self.center_rect(392, 166)
        ja = getattr(self, "lang", LANG_EN) == LANG_JA
        title = "難易度を選ぶ" if ja else "Choose Your Rogue"
        hint = "A/Enter 決定  B/Esc 戻る" if ja else "A/Enter OK  B/Esc Back"
        self._box(bx, by, bw, bh, self.ui_heading(title, UI_HEADING_PANEL))
        previous = DIFFICULTY_ORDER.index(self.difficulty) if self.difficulty in DIFFICULTY_ORDER else 1
        current = getattr(self, "difficulty_cursor", previous)
        for i, diff_id in enumerate(DIFFICULTY_ORDER):
            diff = difficulty_profile(diff_id)
            y = by + 42 + i * 20
            selected = i == current
            restored = selected and getattr(self, "difficulty_cursor_restored", current == previous)
            col = TITLE_RESTORED_CURSOR_COL if restored else UI_SELECTED_COL if selected else UI_TEXT_COL
            self.txt(bx + 22, y, ">" if selected else " ", col if selected else UI_SUBTEXT_COL)
            self.txt(bx + 42, y, diff.label, col)
            if selected:
                desc = diff.description_ja if ja else diff.description_en
                self.txt(bx + 112, y, desc[:34], UI_SUBTEXT_COL)
        self.txt(bx + 18, by + 146, hint, UI_SUBTEXT_COL)

    def draw_nyandor_brief_screen(self):
        self.apply_title_palette()
        if not hasattr(self, "title_bg"):
            self.load_title_background()
        if self.title_bg is not None:
            pyxel.blt(0, 0, self.title_bg, 0, 0, SCR_W, SCR_H)
        bx, by, bw, bh = self.center_rect(392, 150)
        lines = variant_mission_brief_lines(getattr(self, "lang", LANG_EN))
        self._box(bx, by, bw, bh, self.ui_heading(lines[0], UI_HEADING_PANEL))
        for i, line in enumerate(lines[1:4]):
            self.txt(bx + 24, by + 34 + i * 22, line, UI_TEXT_COL)
        self.txt(bx + 24, by + 122, lines[4], UI_SUBTEXT_COL)

    def draw_nyandor_guide_screen(self):
        self.apply_title_palette()
        if not hasattr(self, "title_bg"):
            self.load_title_background()
        if self.title_bg is not None:
            pyxel.blt(0, 0, self.title_bg, 0, 0, SCR_W, SCR_H)
        bx, by, bw, bh = self.center_rect(392, 170)
        lines = variant_quick_guide_lines(getattr(self, "lang", LANG_EN))
        self._box(bx, by, bw, bh, self.ui_heading(lines[0], UI_HEADING_PANEL))
        for i, line in enumerate(lines[1:5]):
            self.txt(bx + 24, by + 32 + i * 22, line, UI_TEXT_COL)
        self.txt(bx + 24, by + 142, lines[5], UI_SUBTEXT_COL)

    def draw_language_select_screen(self):
        self.apply_palette()
        bx, by, bw, bh = self.center_rect(328, 150)
        self._box(bx, by, bw, bh, self.ui_heading(self.online_text("language_title"), UI_HEADING_SCREEN))
        self.txt(bx + 24, by + 30, self.online_text("language_prompt"), UI_TEXT_COL)
        options = [("English", LANG_EN), ("日本語", LANG_JA)]
        cur = getattr(self, "language_cursor", 0)
        for i, (label, _lang) in enumerate(options):
            y = by + 60 + i * 22
            col = UI_SELECTED_COL if i == cur else UI_TEXT_COL
            self.txt(bx + 44, y, ">" if i == cur else " ", UI_SELECTED_COL)
            self.txt(bx + 64, y, label, col)
        self.txt(bx + 24, by + 124, self.online_text("language_select_hint"), UI_SUBTEXT_COL)

    def draw_name_input(self):
        bx, by, bw, bh = self.center_rect(356, 210)
        self._box(bx, by, bw, bh, self.ui_heading(TextCatalog.msg(self.lang, "ui.name_entry"), UI_HEADING_SCREEN))
        self.txt(bx + 26, by + 26, TextCatalog.msg(self.lang, "ui.name_entry_label"), UI_SECTION_COL)
        chars = getattr(self, "name_chars", [])
        display = "".join(chars).ljust(8)[:8]
        base_x, y = bx + 104, by + 78
        for i, ch in enumerate(display):
            col = UI_SELECTED_COL if i == getattr(self, "name_pos", 0) else UI_TEXT_COL
            self.txt(base_x + i * 14, y, ch if ch != " " else "_", col)
        end_col = UI_SELECTED_COL if getattr(self, "name_pos", 0) >= 8 else UI_TEXT_COL
        self.txt(base_x + 126, y, TextCatalog.msg(self.lang, "ui.done"), end_col)
        self.txt(bx + 12, by + 152, TextCatalog.msg(self.lang, "ui.name_entry_move_hint"), UI_SUBTEXT_COL)
        self.txt(bx + 20, by + 168, TextCatalog.msg(self.lang, "ui.name_entry_ok_hint"), UI_SUBTEXT_COL)

    def draw_online_confirm_screen(self):
        bx, by, bw, bh = self.center_rect(348, 132)
        self._box(bx, by, bw, bh, self.ui_heading(self.online_text("confirm_title"), UI_HEADING_PANEL))
        self.txt(bx + 24, by + 26, self.online_text("confirm_prompt"), UI_TEXT_COL)
        self.txt(bx + 24, by + 48, self.online_text("confirm_register"), UI_HILITE_COL)
        self.txt(bx + 24, by + 66, self.online_text("confirm_local"), UI_TEXT_COL)
        self.txt(bx + 24, by + 90, self.online_text("confirm_mark"), SCOREBOARD_DIM_COL)
        self.draw_online_language_hint(bx + 24, by + 108)

    def draw_online_language_hint(self, x, y):
        self.txt(x, y, self.online_text("language_hint"), UI_HILITE_COL)

    def score_period_tab_label(self, period):
        return rogue_online_scoreboard.score_period_tab_label(period, self.lang)

    def draw_score_period_tabs(self, x, y, active_period):
        parts = [("-- ", UI_SECTION_COL)]
        periods = SCOREBOARD_PERIOD_ORDER
        for i, period in enumerate(periods):
            if i:
                parts.append((" | ", UI_TEXT_COL))
            col = UI_SELECTED_COL if period == active_period else UI_TEXT_COL
            parts.append((self.score_period_tab_label(period), col))
        parts.append((" --", UI_SECTION_COL))
        for text, col in parts:
            self.txt(x, y, text, col)
            x += self.ui_text_width(text)

    def draw_score_difficulty_tabs(self, x, y, active_difficulty):
        parts = [("-- ", UI_SECTION_COL)]
        for i, diff_id in enumerate(DIFFICULTY_ORDER):
            if i:
                parts.append((" | ", UI_TEXT_COL))
            col = UI_SELECTED_COL if diff_id == active_difficulty else UI_TEXT_COL
            parts.append((difficulty_profile(diff_id).label, col))
        parts.append((" --", UI_SECTION_COL))
        for text, col in parts:
            self.txt(x, y, text, col)
            x += self.ui_text_width(text)

    def draw_score_title_line(self, x, y, title, period):
        self.txt(x, y, title, UI_SECTION_COL)
        x += self.ui_text_width(f"{title} ")
        period_label = self.scoreboard_period_label(period)
        self.txt(x, y, period_label, UI_SUBTEXT_COL)
        x += self.ui_text_width(f"{period_label}  ")
        self.txt(x, y, self.scoreboard_difficulty_profile().label, UI_SUBTEXT_COL)

    def draw_online_score_screen(self):
        self.ensure_online_score_state()
        period = getattr(self, "online_period", SCOREBOARD_PERIOD_LOCAL)
        title = rogue_online_scoreboard.scoreboard_title(period, self.lang)
        bx, by, bw, bh = self.center_rect(416, 300)
        x = bx + 22
        bottom_y = by + bh - 56
        self._box(bx, by, bw, bh, self.ui_heading(self.online_text("score_title"), UI_HEADING_SCREEN))
        if not variant_fixed_difficulty():
            self.draw_score_difficulty_tabs(x, by + 28, self.scoreboard_difficulty())
            self.draw_score_period_tabs(x, by + 42, period)
            content_y = by + 56
        else:
            self.draw_score_period_tabs(x, by + 28, period)
            content_y = by + 42
        self.draw_score_title_line(x, content_y, title, period)
        content_y += 24
        scores = self.display_online_period_scores(period)
        self.txt(x, content_y, self.online_text("score_header"), SCOREBOARD_TEXT_COL)
        y = content_y + 14
        local_best = None
        for row in rogue_online_scoreboard.scoreboard_entry_rows(
            scores,
            period,
            self.lang,
            current_player_name=self.current_score_player_name(),
            current_entry=getattr(self, "result_entry", None),
        ):
            col = SCOREBOARD_HILITE_COL if row.highlight else SCOREBOARD_TEXT_COL
            self.txt(x, y, row.line[:56], col)
            y += 10
        if period in (SCOREBOARD_PERIOD_WEEKLY, SCOREBOARD_PERIOD_SEASON):
            local_best = self.current_local_best_score_for_period(period, scores)
            local_best_row = rogue_online_scoreboard.score_guest_local_best_row(local_best, period, self.lang)
            if local_best_row:
                y += 10
                if y + MSG_LINE_H * 2 <= bottom_y:
                    self.txt(x, y, local_best_row.line[:56], SCOREBOARD_HILITE_COL)
                y += 10
        if not scores and not local_best:
            self.txt(x, y, TextCatalog.msg(self.lang, "ui.no_scores_yet"), SCOREBOARD_DIM_COL)
            y += 16
        info_y = bottom_y - 14
        if getattr(self, "online_score_load_result", ""):
            self.txt(bx + 16, info_y, self.online_score_load_result[:58], SCOREBOARD_DIM_COL)
        if period != SCOREBOARD_PERIOD_LOCAL:
            self.txt(bx + 16, bottom_y, self.scoreboard_period_ends_line(period)[:72], SCOREBOARD_DIM_COL)
        hint = self.online_sync_hint_line()[:72]
        if hint:
            self.txt(bx + 16, bottom_y + 14, hint, SCOREBOARD_DIM_COL)
        if getattr(self, "online_sync_result", ""):
            for i, msg in enumerate(self.online_result_lines(self.online_sync_result)):
                self.txt(max(bx + 16, bx + bw - 10 - self.ui_text_width(msg)), by + 12 + i * 12, msg, SCOREBOARD_HILITE_COL)
        self.txt(bx + 16, bottom_y + 28, self.ellipsize_to_width(self.online_text("score_hint"), bw - 32), SCOREBOARD_DIM_COL)
        if getattr(self, "online_syncing", False):
            ox, oy = bx + (bw - 268) // 2, by + (bh - 82) // 2
            self._box(ox, oy, 268, 82, self.ui_heading(self.online_text("sync_title"), UI_HEADING_PANEL))
            lines = self.online_sync_box_lines()
            self.txt(ox + 28, oy + 30, lines[0][:34], SCOREBOARD_HILITE_COL)
            self.txt(ox + 28, oy + 44, lines[1][:34], SCOREBOARD_HILITE_COL)
        if getattr(self, "online_register_prompt", False):
            ox, oy = bx + (bw - 282) // 2, by + (bh - 92) // 2
            self._box(ox, oy, 282, 92, self.ui_heading(self.online_text("confirm_title"), UI_HEADING_PANEL))
            self.txt(ox + 20, oy + 22, self.online_text("score_register_prompt"), UI_TEXT_COL)
            self.txt(ox + 20, oy + 40, self.online_text("score_register_hint"), UI_SUBTEXT_COL)
            self.txt(ox + 20, oy + 58, self.online_text("score_register_mark"), UI_TEXT_COL)

    def draw_online_register_screen(self):
        bx, by, bw, bh = self.center_rect(356, 210)
        self._box(bx, by, bw, bh, self.ui_heading(self.online_text("register_title"), UI_HEADING_SCREEN))
        self.txt(bx + 26, by + 26, self.online_text("register_prompt"), UI_TEXT_COL)
        profile = normalize_online_profile(getattr(self, "online_profile", None))
        local_hint = profile.get("local_only", True) or self.online_register_name_changed()
        self.txt(bx + 26, by + 44, self.online_text("register_local" if local_hint else "register_cancel"), UI_TEXT_COL)
        chars = getattr(self, "name_chars", [])
        display = "".join(chars).ljust(USER_NAME_MAX)[:USER_NAME_MAX]
        base_x, y = bx + 62, by + 80
        for i, ch in enumerate(display):
            col = UI_SELECTED_COL if i == getattr(self, "name_pos", 0) else UI_TEXT_COL
            self.txt(base_x + i * 14, y, ch if ch != " " else "_", col)
        end_col = UI_SELECTED_COL if getattr(self, "name_pos", 0) >= USER_NAME_MAX else UI_TEXT_COL
        self.txt(base_x + 126, y, TextCatalog.msg(self.lang, "ui.done"), end_col)
        candidates = getattr(self, "online_name_candidates", [])[:3]
        if candidates:
            candidate_x = base_x + 182
            self.txt(base_x + 166, y, "->", UI_SUBTEXT_COL)
            self.txt(candidate_x, y, self.online_text("register_previous_names"), UI_SECTION_COL)
            for i, name in enumerate(candidates):
                selected = getattr(self, "name_pos", 0) == USER_NAME_MAX + 1 + i
                self.txt(
                    candidate_x + 8,
                    y + 16 + i * 12,
                    ("> " if selected else "  ") + name,
                    UI_SELECTED_COL if selected else UI_TEXT_COL,
                )
        self.txt(bx + 26, by + 170, self.online_text("register_hint" if local_hint else "register_cancel_hint"), UI_SUBTEXT_COL)
        self.draw_online_language_hint(bx + 26, by + 184)
        if getattr(self, "online_sync_status", "") and getattr(self, "online_pending_action", ""):
            self.txt(bx + 26, by + 198, self.online_text(self.online_sync_status)[:48], UI_HILITE_COL)
        if getattr(self, "online_sync_result", ""):
            self.txt(bx + 26, by + 198, self.online_text(self.online_sync_result)[:48], UI_HILITE_COL)

    def draw_online_pin_screen(self):
        is_link = getattr(self, "online_password_mode", "register") == "link"
        bx, by, bw, bh = self.center_rect(328, 210)
        self._box(bx, by, bw, bh, self.ui_heading(self.online_text("pin_link_title" if is_link else "pin_title"), UI_HEADING_SCREEN))
        user_name = getattr(self, "online_pending_user_name", "rogue54")
        self.txt(bx + 24, by + 26, TextCatalog.msg(self.lang, "ui.user_value", user=user_name), UI_TEXT_COL)
        self.txt(bx + 24, by + 46, self.online_text("pin_link_server" if is_link else "pin_server"), UI_TEXT_COL)
        self.txt(bx + 24, by + 60, self.online_text("pin_link_reuse" if is_link else "pin_reuse"), UI_TEXT_COL)
        chars = getattr(self, "online_password_chars", ["0"] * 6)
        base_x, y = bx + 80, by + 94
        for i, ch in enumerate(chars):
            col = UI_SELECTED_COL if i == getattr(self, "name_pos", 0) else UI_TEXT_COL
            self.txt(base_x + i * 18, y, ch, col)
        end_col = UI_SELECTED_COL if getattr(self, "name_pos", 0) >= 6 else UI_TEXT_COL
        self.txt(base_x + 122, y, TextCatalog.msg(self.lang, "ui.done"), end_col)
        self.txt(bx + 24, by + 168, self.online_text("pin_hint"), UI_SUBTEXT_COL)
        self.draw_online_language_hint(bx + 24, by + 182)
        if getattr(self, "online_sync_status", "") and getattr(self, "online_pending_action", ""):
            self.txt(bx + 24, by + 196, self.online_text(self.online_sync_status)[:46], UI_HILITE_COL)
        if getattr(self, "online_sync_result", ""):
            self.txt(bx + 24, by + 196, self.online_text(self.online_sync_result)[:46], UI_HILITE_COL)

    def draw_online_local_confirm_screen(self):
        guest_switch = getattr(self, "online_local_confirm_mode", "") == "guest_switch"
        title_key = "guest_confirm_title" if guest_switch else "local_confirm_title"
        bx, by, bw, bh = self.center_rect(356, 130)
        self._box(bx, by, bw, bh, self.ui_heading(self.online_text(title_key), UI_HEADING_PANEL))
        if guest_switch:
            self.txt(bx + 26, by + 26, self.online_text("guest_confirm_prompt"), UI_TEXT_COL)
            self.txt(bx + 26, by + 46, TextCatalog.msg(self.lang, "ui.name_value", name="guest"), UI_HILITE_COL)
            self.txt(bx + 26, by + 74, self.online_text("guest_confirm_ok"), UI_SUBTEXT_COL)
            self.txt(bx + 26, by + 92, self.online_text("guest_confirm_cancel"), UI_SUBTEXT_COL)
        else:
            self.txt(bx + 26, by + 26, self.online_text("local_confirm_prompt"), UI_TEXT_COL)
            self.txt(bx + 26, by + 46, TextCatalog.msg(self.lang, "ui.name_value", name="guest"), UI_HILITE_COL)
            self.txt(bx + 26, by + 74, self.online_text("local_confirm_ok"), UI_SUBTEXT_COL)
            self.txt(bx + 26, by + 92, self.online_text("local_confirm_cancel"), UI_SUBTEXT_COL)
        self.draw_online_language_hint(bx + 26, by + 110)

    def draw_title(self):
        pyxel.rect(0, 0, SCR_W, ZV_Y - 4, 1)
        self.txt(ZV_X, 6, self.difficulty_profile().label, UI_SUBTEXT_COL)

    def should_draw_memory_tile(self, mx, my, tile):
        room = self.room_at(mx, my)
        if tile == T_FLOOR and room and room.is_dark:
            return False
        return True

    def memory_tile_color(self, tile):
        if tile == T_STAIR:
            return TILE_CH[T_STAIR][1]
        return palette_role_color(self.ensure_settings().palette, ROLE_MEMORY)

    def visible_tile_color(self, tile):
        role_by_tile = {
            T_FLOOR: ROLE_FLOOR,
            T_HWALL: ROLE_WALL,
            T_VWALL: ROLE_WALL,
            T_DOOR: ROLE_DOOR,
            T_CORR: ROLE_CORRIDOR,
            T_TRAP: ROLE_TRAP,
        }
        role = role_by_tile.get(tile)
        if role is None:
            return TILE_CH.get(tile, (" ", 0))[1]
        return palette_role_color(self.ensure_settings().palette, role)

    def item_color(self, cat):
        if self.ensure_settings().palette == PALETTE_FLEXOKI_SYNTAX_LIGHT and cat == CAT_FOOD:
            return 8
        return ICOL.get(cat, 9)

    def hp_fill_color(self, hp_low):
        if hp_low:
            return 9
        return TILE_CH[T_STAIR][1]

    def hp_damage_color(self):
        if self.ensure_settings().palette == PALETTE_FLEXOKI_SYNTAX_LIGHT:
            return 11
        return 10

    def draw_zoom(self):
        cx,cy = self.cam_x, self.cam_y
        blind = self.p.blind > 0
        px,py = self.p.x, self.p.y

        for vy in range(ZV_ROWS):
            for vx in range(ZV_COLS):
                mx,my = cx+vx, cy+vy
                if not(0<=mx<MAP_W and 0<=my<MAP_H): continue
                sx = ZV_X + vx*TILE_W
                sy = ZV_Y + vy*TILE_H
                if blind and (mx, my) == (px, py):
                    self.txt(sx+1, sy+1, "@", UI_TEXT_COL)
                    continue
                vis = (mx,my) in self.visible and not blind
                exp = (mx,my) in self.explored and not blind

                if vis:
                    mo=self.mon_at(mx,my)
                    if mx==px and my==py:
                        self.txt(sx+1,sy+1,"@",UI_TEXT_COL)
                    elif mo and (self.can_see_monster(mo) or self.can_detect_monsters()):
                        sym = self.visible_monster_sym(mo) if self.can_see_monster(mo) else self.detected_monster_sym(mo)
                        self.txt(sx+1,sy+1,sym,self.monster_color(mo.sym))
                    else:
                        gi=self.gi_at(mx,my)
                        if gi:
                            self.txt(sx+1,sy+1,self.visible_item_sym(gi),self.item_color(gi.cat))
                        else:
                            tile=self.tm[my][mx]; ch=self.visible_tile_sym(mx,my,tile); col=self.visible_tile_color(tile)
                            if ch!=" ": self.txt(sx+1,sy+1,ch,col)
                elif exp:
                    tile=self.tm[my][mx]; ch,_=TILE_CH.get(tile,(" ",0))
                    if ch!=" " and self.should_draw_memory_tile(mx,my,tile):
                        self.txt(sx+1,sy+1,ch,self.memory_tile_color(tile))
                    gi=self.gi_at(mx,my)
                    if gi: self.txt(sx+1,sy+1,gi.sym,self.item_color(gi.cat))
                else:
                    mo=self.mon_at(mx,my)
                    if mo and self.can_detect_monsters():
                        self.txt(sx+1,sy+1,self.detected_monster_sym(mo),self.monster_color(mo.sym))

        if self.throw_anim and self.throw_anim["path"]:
            idx=min(self.throw_anim["tick"]//self.throw_anim["delay"],len(self.throw_anim["path"])-1)
            mx,my=self.throw_anim["path"][idx]
            if (mx,my) in self.visible and not blind:
                sx = ZV_X + (mx-cx)*TILE_W
                sy = ZV_Y + (my-cy)*TILE_H
                if ZV_X <= sx < ZV_X+ZV_PX_W and ZV_Y <= sy < ZV_Y+ZV_PX_H:
                    self.txt(sx+1,sy+1,self.throw_anim["sym"],self.throw_anim["col"])

    def draw_stat(self):
        self.clamp_player_hp()
        p=self.p
        hp_low = p.hp <= p.max_hp // 3
        pyxel.rect(0, SCR_H - 30, SCR_W, 30, 1)
        self.txt_segments_right(
            SCR_W - 16,
            6,
            (
                (TextCatalog.hud_label(self.lang, "depth"), UI_SUBTEXT_COL),
                (" ", UI_SUBTEXT_COL),
                (str(p.depth), UI_TEXT_COL),
                ("  ", UI_SUBTEXT_COL),
                (TextCatalog.hud_label(self.lang, "gold"), UI_SUBTEXT_COL),
                (" ", UI_SUBTEXT_COL),
                (str(p.gold), 11),
            ),
        )

        hp_y = SCR_H - 14
        equip_y = SCR_H - 26
        hp_label = TextCatalog.hud_label(self.lang, "hp")
        bw = 108
        bx = ZV_X + 18
        hp_label_x = max(0, bx - 6 - self.ui_text_width(hp_label))
        self.txt(hp_label_x, hp_y, hp_label, UI_SUBTEXT_COL)
        by = hp_y + 3
        hp_frame_col = self.hp_frame_color(hp_low)
        pyxel.rectb(bx - 1, by - 2, bw + 2, 9, hp_frame_col)
        pyxel.rect(bx, by - 1, bw, 7, 1)
        if p.max_hp>0:
            if self.last_hp_seen is not None and p.hp < self.last_hp_seen:
                self.hp_damage_from = min(self.last_hp_seen, p.max_hp)
                self.hp_damage_turn = self.turn
            cur_w=max(0,int(bw*p.hp/p.max_hp))
            if self.hp_damage_turn == self.turn and self.hp_damage_from is not None:
                old_w=max(cur_w,int(bw*self.hp_damage_from/p.max_hp))
                pyxel.rect(bx+cur_w,by - 1,old_w-cur_w,7,self.hp_damage_color())
            pyxel.rect(bx,by - 1,cur_w,7,self.hp_fill_color(hp_low))
            self.last_hp_seen = p.hp
        self.txt(bx + bw + 6, hp_y, f"{p.hp}({p.max_hp})", UI_TEXT_COL)
        stat_segments = (
            (TextCatalog.hud_label(self.lang, "strength"), UI_SUBTEXT_COL),
            (" ", UI_SUBTEXT_COL),
            (f"{p.st}({p.max_st})", UI_TEXT_COL),
            ("  ", UI_SUBTEXT_COL),
            (TextCatalog.hud_label(self.lang, "armor"), UI_SUBTEXT_COL),
            (" ", UI_SUBTEXT_COL),
            (str(p.ac), UI_TEXT_COL),
            ("  ", UI_SUBTEXT_COL),
            (TextCatalog.hud_label(self.lang, "experience"), UI_SUBTEXT_COL),
            (" ", UI_SUBTEXT_COL),
            (f"{p.level}/{p.exp}", UI_TEXT_COL),
        )
        self.txt_segments_right(SCR_W - 16, hp_y, stat_segments)
        equip_segments = (
            (TextCatalog.hud_label(self.lang, "weapon"), UI_SUBTEXT_COL),
            (" ", UI_SUBTEXT_COL),
            (self.hud_weapon_bonus(p.wpn), UI_SUBTEXT_COL),
            ("  ", UI_SUBTEXT_COL),
            (TextCatalog.hud_label(self.lang, "armor_slot"), UI_SUBTEXT_COL),
            (" ", UI_SUBTEXT_COL),
            (self.hud_armor_bonus(p.arm), UI_SUBTEXT_COL),
        )
        equip_left = SCR_W - 16 - self.ui_segments_width(equip_segments)
        mode_segments = [(text, self.ui_role_color(role)) for text, role in self.hud_mode_chips()]
        mode_w = self.ui_segments_width(mode_segments)
        mode_x = max(ZV_X, hp_label_x + self.ui_text_width(hp_label) - mode_w)
        if mode_segments:
            self.txt_segments(mode_x, equip_y, mode_segments)
        cond_segments = []
        for i, (text, role) in enumerate(self.hud_condition_chips()):
            if i:
                cond_segments.append((" ", UI_SUBTEXT_COL))
            cond_segments.append((text, self.ui_role_color(role)))
        cond_x = mode_x + mode_w + 8
        max_cond_w = max(0, equip_left - cond_x - 8)
        while cond_segments and self.ui_segments_width(cond_segments) > max_cond_w:
            cond_segments.pop()
        if cond_segments:
            self.txt_segments(cond_x, equip_y, cond_segments)
        self.txt_segments_right(SCR_W - 16, equip_y, equip_segments)

    def hp_frame_color(self, hp_low):
        if not hp_low:
            return UI_SUBTEXT_COL
        role = HP_LOW_FRAME_ROLES[(pyxel.frame_count // HP_LOW_FRAME_PERIOD) % len(HP_LOW_FRAME_ROLES)]
        return palette_role_color(self.ensure_settings().palette, role)

    def draw_msgs(self):
        rows=[]
        msg_turns = self.msg_turns if len(getattr(self, "msg_turns", [])) == len(self.msgs) else []
        last_index = len(self.msgs) - 1
        for src_i,m in enumerate(self.msgs):
            age = 0 if not msg_turns else max(0, self.turn - msg_turns[src_i])
            c = msg_toast_color(age, self.ensure_settings().palette)
            parts = self.wrap_msg_toast_text(self.message_display_text(m))
            for pi, part in enumerate(parts):
                rows.append((part, c, age, pi == 0, src_i))
        rows = rows[-MSG_TOAST_LINES:]
        row_keys = [(src_i, row_i) for row_i, (_m, _c, _age, _first_part, src_i) in enumerate(rows)]
        previous_visible_keys = set(getattr(self, "msg_toast_visible_keys", ()))
        retiring_keys = tuple(
            key
            for key, (_m, _c, age, _first_part, _src_i) in zip(row_keys, rows)
            if age > MSG_TOAST_DIM_TURNS and key in previous_visible_keys
        )
        if retiring_keys:
            now = getattr(pyxel, "frame_count", 0)
            old_expire_keys = tuple(getattr(self, "msg_toast_expire_keys", ()))
            old_expire_turn = getattr(self, "msg_toast_expire_turn", self.turn)
            if set(retiring_keys).issubset(set(old_expire_keys)):
                active_expire_keys = old_expire_keys if old_expire_turn == self.turn else ()
            else:
                active_expire_keys = retiring_keys
                self.msg_toast_expire_keys = active_expire_keys
                self.msg_toast_expire_frame = now
                self.msg_toast_expire_turn = self.turn
            elapsed = max(0, now - getattr(self, "msg_toast_expire_frame", now))
            retire_count = min(len(active_expire_keys), elapsed // MSG_TOAST_ROW_RETIRE_FRAMES)
            expired_seen = 0
            kept = []
            for key, row in zip(row_keys, rows):
                if row[2] > MSG_TOAST_DIM_TURNS:
                    if key in active_expire_keys and expired_seen >= retire_count:
                        kept.append((key, row))
                    if key in active_expire_keys:
                        expired_seen += 1
                else:
                    kept.append((key, row))
            keyed_rows = kept
        else:
            self.msg_toast_expire_keys = ()
            self.msg_toast_expire_frame = getattr(pyxel, "frame_count", 0)
            keyed_rows = [(key, row) for key, row in zip(row_keys, rows) if row[2] <= MSG_TOAST_DIM_TURNS]
        rows = [row for _key, row in keyed_rows]
        if not rows:
            self.msg_toast_visible_keys = ()
            self.msg_toast_rows = 0
            self.msg_toast_block = None
            self.msg_toast_reposition_needed = True
            return
        self.msg_toast_visible_keys = tuple(key for key, _row in keyed_rows)
        toast_rows = min(MSG_TOAST_LINES, max(getattr(self, "msg_toast_rows", 0), len(rows)))
        self.msg_toast_rows = toast_rows
        if getattr(self, "msg_toast_block", None) is None:
            self.refresh_msg_toast_block()
        x, y = msg_toast_block_origin(self.msg_toast_block, toast_rows)
        y += (toast_rows - len(rows)) * MSG_LINE_H
        ack_pending = getattr(self, "message_ack_pending", False)
        blink_on = (getattr(pyxel, "frame_count", 0) // 15) % 2 == 0
        for i,(m,c,age,first_part,src_i) in enumerate(rows):
            ty = y+i*MSG_LINE_H
            important_body = ack_pending and src_i == last_index
            important_marker = important_body and first_part
            marker = "!" if important_marker else (">" if age == 0 and first_part else "")
            text_col = UI_HILITE_COL if important_body else c
            marker_col = UI_HILITE_COL if important_marker else c
            text_x = x + 2 * FONT_ASCII_W
            if marker and (not important_marker or blink_on):
                self.txt(x + 1, ty + 1, marker, MSG_TOAST_SHADOW_COL)
                self.txt(x, ty, marker, marker_col)
            self.txt(text_x + 1, ty + 1, m, MSG_TOAST_SHADOW_COL)
            self.txt(text_x, ty, m, text_col)

    # ---------- Overlays ----------
    def ui_heading(self, label, level):
        if level == UI_HEADING_SCREEN:
            return f"=== {label} ==="
        if level == UI_HEADING_PANEL:
            return f"-- {label} --"
        if level == UI_HEADING_SECTION:
            return f"--- {label} ---"
        return str(label)

    def ui_heading_col(self, level):
        return UI_SECTION_COL

    def center_rect(self, w, h):
        return (SCR_W - w) // 2, (SCR_H - h) // 2, w, h

    def _box(self,x,y,w,h,title=""):
        pyxel.dither(1.0)
        pyxel.rect(x,y,w,h,0); pyxel.rectb(x,y,w,h,5)
        if title: self.txt(x+4,y+3,title,UI_SECTION_COL)

    def draw_overlays(self):
        if self.st==ST_MENU:
            self.draw_menu()
        elif self.st==ST_ITEM:
            if self.action_origin==ST_MENU:
                self.draw_menu()
            if self.cact=="Throw" and self.throw_dir is not None:
                self.draw_dirp("Throw")
            if self.cact=="Zap" and getattr(self, "zap_dir", None) is not None:
                self.draw_dirp("Zap")
            self.draw_isel()
        elif self.st==ST_CALL:
            if self.action_origin==ST_MENU:
                self.draw_menu()
            self.draw_call_input()
        elif self.st==ST_DISC:
            self.draw_disc()
        elif self.st==ST_DIR:
            if self.action_origin==ST_MENU:
                self.draw_menu()
                if self.dact=="Zap" and self.zap_item is not None:
                    self.draw_isel()
            self.draw_dirp()
        elif self.st==ST_AUX:
            self.draw_aux()
        elif self.st==ST_INVENTORY:
            self.draw_inventory()
        elif self.st==ST_LOG:
            self.draw_log()
        elif self.st==ST_SETTINGS:
            self.draw_settings()
        elif self.st==ST_SAVE_CONFIRM:
            self.draw_settings()
            self.draw_save_confirm()
        elif self.st==ST_HELP:
            self.draw_help()
        elif self.st==ST_DEAD:
            self.draw_dead()
        elif self.st==ST_WIN:
            self.draw_win()
        elif self.st==ST_QUIT:
            self.draw_quit()
        elif self.st==ST_QUIT_CONFIRM:
            self.draw_quit_confirm()
        elif self.st==ST_SCORE:
            self.draw_score_screen()

    def draw_menu(self):
        cell_w=82; cell_h=18
        bw=cell_w*3+10; bh=cell_h*len(PAD_ACTION_GRID)+24
        bx = 18
        by = ZV_Y + (ZV_PX_H - bh) // 2 - 18
        self._box(bx,by,bw,bh,self.ui_heading(TextCatalog.menu(self.lang, "Action"), UI_HEADING_PANEL))
        for gy,row in enumerate(PAD_ACTION_GRID):
            for gx,nm in enumerate(row):
                try:
                    idx=next(i for i,(an,_cat) in enumerate(MENU_ACTIONS) if an==nm)
                except StopIteration:
                    continue
                x=bx+5+gx*cell_w; y=by+17+gy*cell_h
                selected=idx==self.mcur
                if selected and getattr(self, "menu_cursor_restored", False):
                    c=UI_RESTORED_CURSOR_COL
                else:
                    c=UI_SELECTED_COL if selected else UI_TEXT_COL
                pre=">" if selected else " "
                self.txt(x,y,f"{pre}{self.menu_hint_label(nm)[:11]}",c)

    def menu_hint_label(self, name):
        hints = {
            "Zap": "z",
            "Throw": "t",
            "Quaff": "q",
            "Read": "r",
            "Eat": "e",
            "Wield": "w",
            "Wear": "W",
            "Take off": "T",
            "Remove ring": "R",
            "Drop": "d",
            "Call": "c",
            "Discoveries": "D",
            "Put on": "P",
            "Search": "s",
            "Trap": "^",
            "Quit": "Q",
        }
        label = TextCatalog.menu(self.lang, name)
        key = hints.get(name)
        return f"{key}){label}" if key else label

    def draw_isel(self):
        cell_w = min(264, max(180, (SCR_W - 24) // 2))
        bw, bh, cell_w = self.pack_grid_box_size(self.fitems, cell_w=cell_w)
        bx = min(SCR_W - bw - 4, max(0, (SCR_W - bw) // 2 + 20))
        by = min(SCR_H - bh - 4, max(ZV_Y, (SCR_H - bh) // 2 + 24))
        self.draw_pack_grid(
            bx,
            by,
            self.fitems,
            self.ui_heading(TextCatalog.menu(self.lang, self.cact), UI_HEADING_PANEL),
            self.icur,
            item_chars=40,
            cell_w=cell_w,
        )

    def draw_call_input(self):
        if self.call_item is None:
            self.draw_isel()
            return
        prompt = TextCatalog.msg(self.lang, "misc.what_to_call_it")
        bx, by = ZV_X + 20, ZV_Y + 60; bw = 240; bh = 36
        self._box(bx, by, bw, bh, self.ui_heading(TextCatalog.menu(self.lang, self.cact), UI_HEADING_PANEL))
        self.txt(bx + 4, by + 14, f"{prompt}", UI_TEXT_COL)
        cursor = "_" if (pyxel.frame_count // 15) % 2 == 0 else " "
        self.txt(bx + 4, by + 24, f"> {self.call_input}{cursor}", UI_SELECTED_COL)

    def draw_disc(self):
        bx, by = 20, 12; bw = SCR_W - 40; bh = SCR_H - 80
        title = TextCatalog.msg(self.lang, "misc.discoveries_title")
        hint  = TextCatalog.msg(self.lang, "misc.discoveries_hint")
        self._box(bx, by, bw, bh, self.ui_heading(title, UI_HEADING_SCREEN))
        lines = getattr(self, "disc_lines", None) or self._disc_lines()
        line_h = 11
        visible = (bh - 24) // line_h
        start = self.disc_scroll
        if len(lines) - start > visible:
            rows = visible
            col_w = (bw - 18) // 2
            shown = lines[start:start + rows * 2]
            for i, (col, text) in enumerate(shown):
                if not text:
                    continue
                cx = bx + 6 + (i // rows) * col_w
                cy = by + 16 + (i % rows) * line_h
                self.txt(cx, cy, text[:34], col if col else 9)
        else:
            for i, (col, text) in enumerate(lines[start:start + visible]):
                if not text:
                    continue
                self.txt(bx + 6, by + 16 + i * line_h, text[:60], col if col else 9)
        self.txt(bx + 4, by + bh - 10, hint, UI_TEXT_COL)

    def draw_dirp(self, action=None):
        action = action or self.dact
        title = TextCatalog.msg(
            self.lang,
            "ui.trap_direction_prompt" if action == "Trap" else "ui.direction_prompt",
        )
        bw = max(170, self.ui_text_width(title) + 12)
        bx, by = ZV_X + (ZV_PX_W - bw) // 2, ZV_Y + (ZV_PX_H - 20) // 2
        self._box(bx,by,bw,20,title)

    def draw_aux(self):
        bx,by=ZV_X+20,ZV_Y+8; bw=120; bh=len(AUX_ACTIONS)*14+18
        self._box(bx,by,bw,bh,self.ui_heading(TextCatalog.menu(self.lang, "Assist"), UI_HEADING_PANEL))
        for i,nm in enumerate(AUX_ACTIONS):
            ty=by+16+i*14; c=UI_SELECTED_COL if i==self.acur else UI_TEXT_COL
            pre=">" if i==self.acur else " "
            self.txt(bx+4,ty,f"{pre} {TextCatalog.menu(self.lang,nm)}",c)

    def draw_inventory(self):
        bx, by, bw, bh = self.info_window_rect()
        max_rows = self.inventory_pack_max_rows()
        cols, _rows = pack_grid_shape(len(self.p.inv), max_rows)
        cell_w = max(220, SCR_W - 24) if cols <= 1 else max(220, (SCR_W - 24) // cols)
        self._box(bx, by, bw, bh, self.ui_heading(self.info_title_label(), UI_HEADING_SCREEN))
        self.draw_info_tabs(bx + 8, by + 20, "Inventory")
        self.draw_pack_grid_lines(
            bx + 8,
            by + 40,
            self.p.inv,
            None,
            item_chars=40,
            cell_w=cell_w,
            max_rows=max_rows,
        )
        self.txt(bx + 8, by + bh - 16, self.info_guide_label(), UI_SUBTEXT_COL)

    def inventory_pack_max_rows(self):
        return 18

    def info_window_rect(self):
        return (20, 20, SCR_W - 40, SCR_H - 40)

    def info_tab_label(self, name):
        key = "info." + name.lower().replace(" ", "_")
        return TextCatalog.msg(self.lang, key)

    def info_title_label(self):
        return TextCatalog.msg(self.lang, "info.title")

    def info_guide_label(self, active=None):
        if active == "Log":
            return TextCatalog.msg(self.lang, "info.guide_log")
        if active == "Settings":
            return TextCatalog.msg(self.lang, "settings.guide")
        return TextCatalog.msg(self.lang, "info.guide_default")

    def draw_info_tabs(self, x, y, active):
        parts = [
            ("-- ", UI_SECTION_COL),
            (self.info_tab_label("Inventory"), UI_SELECTED_COL if active == "Inventory" else UI_TEXT_COL),
            (" | ", UI_TEXT_COL),
            (self.info_tab_label("Log"), UI_SELECTED_COL if active == "Log" else UI_TEXT_COL),
            (" | ", UI_TEXT_COL),
            (self.info_tab_label("Settings"), UI_SELECTED_COL if active == "Settings" else UI_TEXT_COL),
            (" | ", UI_TEXT_COL),
            (self.info_tab_label("Help"), UI_SELECTED_COL if active == "Help" else UI_TEXT_COL),
            (" --", UI_SECTION_COL),
        ]
        for text, col in parts:
            self.txt(x, y, text, col)
            x += self.ui_text_width(text)

    def draw_log(self):
        bx, by, bw, bh = self.info_window_rect()
        self._box(bx, by, bw, bh, self.ui_heading(self.info_title_label(), UI_HEADING_SCREEN))
        self.draw_info_tabs(bx + 8, by + 20, "Log")
        lines = list(getattr(self, "msgs", []))[-100:]
        visible = self.log_visible_rows()
        max_scroll = max(0, len(lines) - visible)
        self.log_scroll = max(0, min(getattr(self, "log_scroll", 0), max_scroll))
        if self.log_scroll > 0:
            self.txt(bx + bw - 16, by + 40, "^", UI_SUBTEXT_COL)
        if self.log_scroll < max_scroll:
            self.txt(bx + bw - 16, by + bh - 34, "v", UI_SUBTEXT_COL)
        visible_lines = lines[self.log_scroll:self.log_scroll + visible]
        for i, text in enumerate(visible_lines):
            self.txt(bx + 8, by + 40 + i * 11, self.message_display_text(text)[:72], self.log_line_color(self.log_scroll + i, len(lines)))
        self.draw_log_scrollbar(bx, by, bw, bh, len(lines), visible, max_scroll)
        self.txt(bx + 8, by + bh - 16, self.info_guide_label("Log"), UI_SUBTEXT_COL)

    def log_line_color(self, index, total_count):
        if index >= max(0, total_count - 10):
            return UI_TEXT_COL
        return UI_SUBTEXT_COL

    def draw_log_scrollbar(self, bx, by, bw, bh, total, visible, max_scroll):
        if total <= visible:
            return
        track_x = bx + bw - 8
        track_y = by + 40
        track_h = bh - 62
        pyxel.rect(track_x, track_y, 2, track_h, UI_SUBTEXT_COL)
        thumb_h = max(8, track_h * visible // max(visible, total))
        travel = max(1, track_h - thumb_h)
        thumb_y = track_y + (travel * self.log_scroll // max(1, max_scroll))
        pyxel.rect(track_x - 1, thumb_y, 4, thumb_h, UI_HILITE_COL)

    def draw_settings(self):
        bx, by, bw, bh = self.info_window_rect()
        self._box(bx, by, bw, bh, self.ui_heading(self.info_title_label(), UI_HEADING_SCREEN))
        self.draw_info_tabs(bx + 8, by + 20, "Settings")
        y = by + 44
        value_x = bx + 170
        focus_value = getattr(self, "settings_focus", "row") == "value"
        for i, row in enumerate(self.settings_rows()):
            selected = i == getattr(self, "settings_cursor", 0)
            col = UI_SELECTED_COL if selected else UI_TEXT_COL
            pre = ">" if selected else " "
            label = TextCatalog.msg(self.lang, "settings." + row.lower().replace(" ", "_"))
            value = self.setting_value_label(row)
            self.txt(bx + 8, y + i * 14, pre, col)
            self.txt(bx + 22, y + i * 14, label, col)
            if not value:
                continue
            value_col = UI_HILITE_COL if selected else UI_SUBTEXT_COL
            if selected and focus_value:
                self.txt(value_x - 14, y + i * 14, "<", UI_SUBTEXT_COL)
                self.txt(value_x + max(34, self.ui_text_width(value)) + 8, y + i * 14, ">", UI_SUBTEXT_COL)
            self.txt(value_x, y + i * 14, value, value_col)
        self.txt(bx + 8, by + bh - 16, self.info_guide_label("Settings"), UI_SUBTEXT_COL)

    def draw_save_confirm(self):
        title = TextCatalog.msg(self.lang, "save.confirm_title")
        line = TextCatalog.msg(self.lang, "save.confirm_body")
        bx, by, bw, bh = self.center_rect(236, 58)
        self._box(bx, by, bw, bh, self.ui_heading(title, UI_HEADING_PANEL))
        self.txt(bx + 8, by + 22, line, UI_TEXT_COL)
        self.txt(bx + 8, by + 40, TextCatalog.msg(self.lang, "save.confirm_hint"), UI_SUBTEXT_COL)

    def pack_grid_max_rows(self, items):
        return 13 if len(items) > 18 else PACK_GRID_MAX_ROWS

    def pack_grid_box_size(self, items, cell_w=264, max_rows=None):
        count = len(items)
        cols, rows = pack_grid_shape(count, self.pack_grid_max_rows(items) if max_rows is None else max_rows)
        bw = max(220, cols * cell_w + 12)
        bh = max(34, rows * 11 + 24)
        return bw, bh, cell_w

    def draw_pack_grid(self, bx, by, items, title, current_index=None, item_chars=38, cell_w=264):
        bw, bh, cell_w = self.pack_grid_box_size(items, cell_w)
        self._box(bx, by, bw, bh, title)
        self.draw_pack_grid_lines(
            bx + 8,
            by + 16,
            items,
            current_index,
            item_chars=item_chars,
            cell_w=cell_w,
            max_rows=self.pack_grid_max_rows(items),
        )

    def draw_pack_grid_lines(self, x0, y0, items, current_index=None, item_chars=24, cell_w=170, max_rows=PACK_GRID_MAX_ROWS):
        count = len(items)
        for ri, it in enumerate(items):
            gx, gy = pack_grid_pos(ri, count, max_rows)
            x = x0 + gx * cell_w
            y = y0 + gy * 11
            idx = self.p.inv.index(it) if it in self.p.inv else 0
            lt = chr(ord('a') + idx)
            ln = self.item_name(it)
            selected = current_index is not None and ri == current_index
            if selected and getattr(self, "item_cursor_restored", False):
                c = UI_RESTORED_CURSOR_COL
            elif selected:
                c = UI_SELECTED_COL
            else:
                c = UI_TEXT_COL
            max_text_width = max(0, cell_w - 12)
            if current_index is None:
                raw = f"{lt}) {ln[:item_chars]}"
                self.txt(x, y, self.ellipsize_to_width(raw, max_text_width), c)
            else:
                pre = ">" if selected else " "
                raw = f"{pre}{lt}) {ln[:item_chars]}"
                self.txt(x, y, self.ellipsize_to_width(raw, max_text_width), c)

    def draw_help(self):
        bx, by, bw, bh = self.info_window_rect()
        self._box(bx, by, bw, bh, self.ui_heading(self.info_title_label(), UI_HEADING_SCREEN))
        self.draw_info_tabs(bx + 8, by + 20, "Help")
        if self.lang == LANG_JA:
            basic_title = self.ui_heading("基本操作", UI_HEADING_SECTION)
            keys_title = self.ui_heading("キーボード専用", UI_HEADING_SECTION)
            basic_rows = [
                ("パッド", "キー", "動作"),
                ("D-pad", "Arrow", "移動"),
                ("Start", "Space", "斜め補助"),
                ("A", "Enter", "行動"),
                ("A+B", "Enter+Esc", "足踏み"),
                ("B", "Esc", "メニュー"),
                ("B+D-pad", "Shift+Arrow", "走る"),
                ("Select", "Tab", "情報"),
                ("Select+A", "Tab+Enter", "投げる"),
                ("Select+B", "Tab+Esc", "探す"),
                ("Select+D-pad", "Tab+Arrow", "罠"),
            ]
            key_rows = [
                ("HJKL/YUBN 移動/斜め", "", ""),
                (". 待機", ", 拾う", "</> 階段"),
                ("s 探す", "^ 罠", "t 投げる"),
                ("d 捨てる", "i 持ちもの", "I 詳細"),
                ("? ヘルプ", "/ 識別", "m 移動"),
                ("f 攻撃", "a 再実行", "R 外す"),
                ("q 飲む", "r 巻物を読む", "e 食べる"),
                ("z 杖を振る", "P 指輪", "o 設定"),
                ("Q 中止", "w 武器を持つ", ""),
                ("W よろいを着る", "T よろいを脱ぐ", ""),
            ]
        else:
            basic_title = self.ui_heading("Basic Controls", UI_HEADING_SECTION)
            keys_title = self.ui_heading("Keyboard Only", UI_HEADING_SECTION)
            basic_rows = [
                ("Pad", "Key", "Action"),
                ("D-pad", "Arrow", "Move"),
                ("Start", "Space", "Diag assist"),
                ("A", "Enter", "Action"),
                ("A+B", "Enter+Esc", "Wait"),
                ("B", "Esc", "Menu"),
                ("B+D-pad", "Shift+Arrow", "Dash"),
                ("Select", "Tab", "Info"),
                ("Select+A", "Tab+Enter", "Throw"),
                ("Select+B", "Tab+Esc", "Search"),
                ("Select+D-pad", "Tab+Arrow", "Trap"),
            ]
            key_rows = [
                ("HJKL/YUBN Move/Diag", "", ""),
                (". Wait", ", Pickup", "</> Stairs"),
                ("s Search", "^ Trap", "t Throw"),
                ("d Drop", "i Inventory", "I Item"),
                ("? Help", "/ Identify", "m Move"),
                ("f Fight", "a Again", "R Remove"),
                ("q Quaff", "r Read", "e Eat"),
                ("z Zap", "P Put on", "o Options"),
                ("Q Quit", "w Wield", "W Wear"),
                ("T Take off", "R Remove", ""),
            ]
        y=by+50
        line_h = FONT_LINE_H
        left_x = (bx + 8, bx + 84, bx + 154)
        right_x = (bx + 236, bx + 324, bx + 400)
        self.txt(left_x[0], y, basic_title, HELP_HEADER_COL)
        self.txt(right_x[0], y, keys_title, HELP_HEADER_COL)
        y += line_h
        for i in range(max(len(basic_rows), len(key_rows))):
            if i < len(basic_rows):
                for ci, (x, text) in enumerate(zip(left_x, basic_rows[i])):
                    right = left_x[ci + 1] - 4 if ci + 1 < len(left_x) else right_x[0] - 10
                    self.txt(x, y, self.ellipsize_to_width(text, max(0, right - x)), HELP_TEXT_COL)
            if i < len(key_rows):
                for ci, (x, text) in enumerate(zip(right_x, key_rows[i])):
                    if text:
                        tail = key_rows[i][ci + 1:]
                        right = right_x[ci + 1] - 4 if any(tail) and ci + 1 < len(right_x) else bx + bw - 8
                        self.txt(x, y, self.ellipsize_to_width(text, max(0, right - x)), HELP_TEXT_COL)
            y+=line_h
        self.txt(bx + 8, by + bh - 16, self.info_guide_label("Help"), UI_SUBTEXT_COL)

    def draw_top_scores(self, bx=412, by=30):
        bw=156; bh=144
        self._box(bx, by, bw, bh, self.ui_heading(TextCatalog.msg(self.lang, "ui.top_10"), UI_HEADING_PANEL))
        scores = self.result_scores or get_top_scores(load_score_entries(), limit=10, difficulty=self.difficulty)
        y = by + 16
        for i, entry in enumerate(scores[:10], start=1):
            name = str(entry.get("player_name", "rogue"))[:8]
            score = int(entry.get("score", 0))
            self.txt(bx + 6, y, f"{i:>2} {score:>5} {name}", 9 if i != 1 else 10)
            y += 12
        if not scores:
            self.txt(bx + 6, y, TextCatalog.msg(self.lang, "ui.no_scores_yet"), UI_TEXT_COL)

    def draw_score_screen(self):
        bx,by,bw,bh = self.center_rect(340, 220)
        self._box(bx, by, bw, bh, self.ui_heading(TextCatalog.msg(self.lang, "ui.top_10"), UI_HEADING_SCREEN))
        scores = self.result_scores or get_top_scores(load_score_entries(), limit=10, difficulty=self.difficulty)
        self.txt(bx + 12, by + 14, self.difficulty_profile().label, UI_SUBTEXT_COL)
        y = by + 30
        lines = format_top_score_lines(scores)
        if lines:
            lines[0] = TextCatalog.msg(self.lang, "ui.score_header")
        for i, line in enumerate(lines):
            self.txt(bx + 12, y, line, SCOREBOARD_HILITE_COL if i == 0 else SCOREBOARD_TEXT_COL)
            y += 14
        if not scores:
            self.txt(bx + 12, y, TextCatalog.msg(self.lang, "ui.no_scores_yet"), UI_TEXT_COL)
        self.txt(bx + 12, by + bh - 18, TextCatalog.msg(self.lang, "ui.press_confirm_new_game"), UI_HILITE_COL)

    def draw_death_summary(self, bx, by):
        p = self.p
        x = bx + 18
        y = by + 34
        self.txt(x, y, TextCatalog.msg(self.lang, "ui.death_epitaph"), UI_TEXT_COL); y += 22
        self.txt(x, y, TextCatalog.msg(self.lang, "ui.death_cause", cause=self.death_cause or "died"), UI_TEXT_COL); y += 18
        self.txt(x, y, TextCatalog.msg(self.lang, "ui.result_depth", depth=p.depth), UI_TEXT_COL); y += 14
        self.txt(x, y, TextCatalog.msg(self.lang, "ui.result_level", level=p.level), UI_TEXT_COL); y += 14
        self.txt(x, y, TextCatalog.msg(self.lang, "ui.result_gold", gold=self.death_display_gold()), UI_HILITE_COL); y += 14
        next_exp = p.EXP_T[min(p.level, len(p.EXP_T) - 1)]
        self.txt(x, y, TextCatalog.msg(self.lang, "ui.result_exp", exp=f"{p.exp}/{next_exp}"), UI_TEXT_COL); y += 14
        self.txt(x, y, TextCatalog.msg(self.lang, "ui.result_turn", turn=self.turn), UI_TEXT_COL)

    def draw_death_tombstone(self, bx, by, bw):
        x = bx + 18
        killer = self.death_killer_name()
        name = self.options.get("name", "rogue")
        year = time.localtime().tm_year
        if self.lang == LANG_JA:
            return self.draw_japanese_tombstone(bx, by, bw, name, self.death_display_gold(), killer, year)
        y = by + 24
        for line in self.tombstone_lines(name, self.death_display_gold(), killer, year):
            self.txt(x, y, line, UI_TEXT_COL)
            y += 10
        return y + 10

    def draw_death_minimap(self, x, y):
        rows = getattr(self, "death_minimap_tiles", None)
        if rows is None:
            rows = self.death_minimap_snapshot(DEATH_MINIMAP_W, DEATH_MINIMAP_H)
        for row_i, row in enumerate(rows):
            for col_i, (ch, col) in enumerate(row):
                if ch != " ":
                    self.txt(x + col_i * TILE_W + 1, y + row_i * TILE_H + 1, ch, col)

    def death_log_cycle_frames(self, row_count):
        if row_count <= 0:
            return 1
        turns = row_count + MSG_TOAST_DIM_TURNS + 1
        return turns * DEATH_LOG_FRAMES_PER_TURN + DEATH_LOG_RESTART_FRAMES

    def animated_death_log_rows(self, messages):
        count = len(messages)
        if count == 0:
            return []
        elapsed = self.death_log_elapsed()
        phase = elapsed % self.death_log_cycle_frames(count)
        active_span = (count + MSG_TOAST_DIM_TURNS + 1) * DEATH_LOG_FRAMES_PER_TURN
        if phase >= active_span:
            return []
        virtual_turn = phase // DEATH_LOG_FRAMES_PER_TURN
        all_rows = []
        palette = self.ensure_settings().palette
        for i, msg in enumerate(messages):
            if i > virtual_turn:
                continue
            age = virtual_turn - i
            for part in self.wrap_msg_toast_text(self.death_log_message_display_text(msg)):
                col = msg_toast_color(age, palette) if age <= MSG_TOAST_DIM_TURNS else None
                all_rows.append((part, col))
        window_start = max(0, len(all_rows) - MSG_TOAST_LINES)
        rows = []
        for slot, (part, col) in enumerate(all_rows[window_start:]):
            if col is not None:
                rows.append((slot, part, col))
        return rows

    def draw_death_log(self, x, y, w):
        rows = self.animated_death_log_rows(self.msgs[-MSG_TOAST_LINES:])
        for slot, text, col in rows:
            self.txt(x + FONT_ASCII_W, y + slot * MSG_LINE_H, text, col)

    def death_log_message_display_text(self, msg):
        text = self.message_display_text(msg)
        for marker in (" [A/Start]", "[A/Start]"):
            if marker in text:
                text = text.split(marker, 1)[0].rstrip()
        return text

    def draw_death_context_panel(self, x, y, w):
        map_y = y
        self.txt(x, map_y, f"-- {TextCatalog.msg(self.lang, 'ui.death_context')} --", UI_SECTION_COL)
        map_y += 18
        self.draw_death_minimap(x + FONT_ASCII_W, map_y)
        log_y = map_y + DEATH_MINIMAP_H * TILE_H + 18
        self.draw_death_log(x, log_y, w)

    def draw_dead(self):
        bx, by, bw, bh = 4, ZV_Y, SCR_W - 8, SCR_H - ZV_Y - 32
        div_x = min(bx + 300, bx + bw - 170)
        self._box(bx, by, bw, bh, self.ui_heading(TextCatalog.msg(self.lang, "ui.death_title"), UI_HEADING_SCREEN))
        pyxel.line(div_x, by + 14, div_x, by + bh - 12, UI_SECTION_COL)
        if self.options.get("tombstone", True):
            self.draw_death_tombstone(bx, by + 24, div_x - bx)
        else:
            self.draw_death_summary(bx, by)
        self.txt(bx + 18, by + bh - 18, TextCatalog.msg(self.lang, "ui.press_confirm_scores"), UI_HILITE_COL)
        right_x = div_x + 10
        self.draw_death_context_panel(right_x, by + 24, bx + bw - right_x - 10)

    def draw_win(self):
        bx,by,bw,bh = self.center_rect(334, 176)
        self._box(bx,by,bw,bh,self.ui_heading(TextCatalog.msg(self.lang, "ui.result_victory"), UI_HEADING_SCREEN))
        p=self.p; x=bx+18; y=by+26
        line_1 = "ui.nyandor_victory_line_1" if is_nyandor_variant() else "ui.victory_line_1"
        line_2 = "ui.nyandor_victory_line_2" if is_nyandor_variant() else "ui.victory_line_2"
        self.txt(x,y,TextCatalog.msg(self.lang, line_1),UI_HILITE_COL); y+=16
        self.txt(x,y,TextCatalog.msg(self.lang, line_2),UI_HILITE_COL); y+=24
        self.txt(x,y,TextCatalog.msg(self.lang, "ui.result_gold", gold=p.gold),UI_HILITE_COL); y+=14
        self.txt(x,y,TextCatalog.msg(self.lang, "ui.result_level", level=p.level),UI_TEXT_COL); y+=14
        self.txt(x,y,TextCatalog.msg(self.lang, "ui.result_exp", exp=p.exp),UI_TEXT_COL); y+=14
        self.txt(x,y,TextCatalog.msg(self.lang, "ui.result_turn", turn=self.turn),UI_TEXT_COL); y+=28
        self.txt(x,y,TextCatalog.msg(self.lang, "ui.press_confirm_scores"),UI_HILITE_COL)

    def draw_quit_confirm(self):
        bx,by,bw,bh = self.center_rect(224, 56)
        self._box(bx,by,bw,bh,self.ui_heading(TextCatalog.msg(self.lang, "ui.result_quit"), UI_HEADING_PANEL))
        self.txt(bx+12, by+20, TextCatalog.msg(self.lang, "main.really_quit"), UI_HILITE_COL)
        self.txt(bx+12, by+34, TextCatalog.msg(self.lang, "ui.quit_confirm_hint"), UI_SUBTEXT_COL)

    def draw_quit(self):
        bx,by,bw,bh = self.center_rect(300, 148)
        self._box(bx,by,bw,bh,self.ui_heading(TextCatalog.msg(self.lang, "ui.result_quit"), UI_HEADING_PANEL))
        p=self.p; x=bx+18; y=by+24
        self.txt(x,y,TextCatalog.msg(self.lang, "ui.you_quit_with_gold", gold=p.gold),UI_HILITE_COL); y+=24
        self.txt(x,y,TextCatalog.msg(self.lang, "ui.result_depth", depth=p.depth),UI_TEXT_COL); y+=14
        self.txt(x,y,TextCatalog.msg(self.lang, "ui.result_level", level=p.level),UI_TEXT_COL); y+=14
        self.txt(x,y,TextCatalog.msg(self.lang, "ui.result_turn", turn=self.turn),UI_TEXT_COL); y+=26
        self.txt(x,y,TextCatalog.msg(self.lang, "ui.press_confirm_scores"),UI_SUBTEXT_COL)

# ===========================================================
if __name__=="__main__":
    Game()
