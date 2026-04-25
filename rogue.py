"""
PYXEL ROGUE  Phase 3
Faithful Rogue 5.4.4 clone  ·  Shiren-style controls  ·  BDF font

Gamepad:                        Keyboard:
  D-pad        Move (8-dir)      Arrow / HJKL   Move
  Start tap    Diag assist       Space          Diag assist
  B + D-pad    Dash (run)        Shift+dir      Dash
  A            Action/Search     Enter          Action
  B tap        Menu/Cancel       Esc            Menu/Cancel
  A + B        Wait a turn       Enter+Esc/.    Wait
  Back         Assist menu       Tab            Assist menu
  Back + A     Search            Tab+Enter/s    Search
  Back + B     Quick throw       Tab+Esc/t      Quick throw
                                i              Inventory
                                ?              Help
"""

from __future__ import annotations
import pyxel
import json
import random
import os
import sys
import time
from dataclasses import dataclass
from rogue_rng import RogueRng
import rogue_monsters
import rogue_rings
import rogue_sticks
import rogue_dungeon
import rogue_daemons
from rogue_scores import build_score_entry, format_top_score_lines, get_top_scores, load_score_entries, save_score_entry

RNG = RogueRng(random)
UI_BUILD = "260425_2139"

LANG_EN = "en"
LANG_JA = "ja"
DEFAULT_LANG = os.environ.get("PYXEL_ROGUE_LANG", LANG_EN).lower()
if DEFAULT_LANG not in (LANG_EN, LANG_JA):
    DEFAULT_LANG = LANG_EN
PALETTE_GBC = "gbc"
PALETTE_GBC_HIGH_CONTRAST = "gbc_high_contrast"
PALETTE_FLEXOKI_LIGHT = "flexoki_light"
DEFAULT_PALETTE = PALETTE_GBC_HIGH_CONTRAST
PALETTE_IDS = (PALETTE_GBC, PALETTE_GBC_HIGH_CONTRAST, PALETTE_FLEXOKI_LIGHT)
PALETTE_LABELS = {
    PALETTE_GBC: "GBC",
    PALETTE_GBC_HIGH_CONTRAST: "GBC High Contrast",
    PALETTE_FLEXOKI_LIGHT: "Flexoki Light",
}


@dataclass
class Settings:
    language: str = DEFAULT_LANG
    auto_pickup: bool = True
    palette: str = DEFAULT_PALETTE
    show_run_steps: bool = True

    def __post_init__(self):
        if self.language not in (LANG_EN, LANG_JA):
            self.language = LANG_EN
        if self.palette not in PALETTE_IDS:
            self.palette = DEFAULT_PALETTE

# ===========================================================
#  Font
# ===========================================================
_pyxel_dir = os.path.dirname(pyxel.__file__)
FONT_PATH = os.path.join(_pyxel_dir, "examples", "assets", "umplus_j10r.bdf")

# ===========================================================
#  Map
# ===========================================================
NUMCOLS, NUMLINES = 80, 24
STATLINE = NUMLINES - 1
MAP_W, MAP_H = NUMCOLS, NUMLINES
PLAY_Y_MIN, PLAY_Y_MAX = 1, STATLINE - 1
PLAY_H = PLAY_Y_MAX - PLAY_Y_MIN + 1
GRID_C, GRID_R = 3, 3
SEC_W, SEC_H = MAP_W // GRID_C, MAP_H // GRID_R
RM_MIN_W, RM_MAX_W = 5, 12
RM_MIN_H, RM_MAX_H = 4, 7
ROOM_DARK = "dark"
ROOM_GONE = "gone"
ROOM_MAZE = "maze"

GBC_PALETTE = [
    0x050608, 0x10161C, 0x1A232C, 0x28323C,  # 0-3  深黒〜暗青灰
    0x34414C, 0x42515E, 0x536574, 0x677A89,  # 4-7  中青灰〜淡青灰
    0x8093A1, 0xA2B3BE, 0x1A2A21, 0x24382C,  # 8-11 淡青〜暗森緑
    0x2F4B3D, 0x3E6252, 0x4B7564, 0x6A8E7E,  # 12-15 森緑〜淡緑
    0x4A4034, 0x6A5A46, 0x90775E, 0xBCA58D,  # 16-19 暗土〜淡土
    0x5B1D1D, 0x8A2A25, 0xC7492E, 0xD7A33D,  # 20-23 極暗赤〜琥珀黄
    0x0F2F36, 0x1B4A56, 0x2A6D7A, 0x63A8B7,  # 24-27 極暗ティール〜シアン
    0x5E4B1C, 0xA06E1D, 0xD7DCCF, 0xF2F4EA,  # 28-31 暗琥珀〜近白
]
GBC_HIGH_CONTRAST_PALETTE = [
    0x020304, 0x18222B, 0x26333E, 0x344552,
    0x425663, 0x536978, 0x667D8E, 0x7D93A3,
    0x9BB0BE, 0xC3D1D8, 0x102018, 0x1F3528,
    0x31523E, 0x47725A, 0x5A8D72, 0x85B29A,
    0x3E3328, 0x6B5640, 0x9A7B58, 0xD5B98D,
    0x4C1212, 0x8D2020, 0xD94C2F, 0xF0B33F,
    0x06252C, 0x134A58, 0x237486, 0x72C8D8,
    0x6B4E10, 0xC98516, 0xE8EDE0, 0xFFFFFF,
]
FLEXOKI_LIGHT_PALETTE = [
    0xFFFCF0, 0xCECDC3, 0xB7B5AC, 0x878580,
    0x6F6E69, 0x575653, 0x403E3C, 0x282726,
    0x343331, 0x100F0F, 0xE6E4D9, 0xDAD8CE,
    0x66800B, 0x879A39, 0xA0AF54, 0xBEC97E,
    0xE6E4D9, 0xB7B5AC, 0xBC5215, 0xDA702C,
    0xD14D41, 0xAF3029, 0xD14D41, 0xAD8301,
    0x24837B, 0x3AA99F, 0x205EA6, 0x4385BE,
    0xAD8301, 0xBC5215, 0x1C1B1A, 0x100F0F,
]
PALETTES = {
    PALETTE_GBC: GBC_PALETTE,
    PALETTE_GBC_HIGH_CONTRAST: GBC_HIGH_CONTRAST_PALETTE,
    PALETTE_FLEXOKI_LIGHT: FLEXOKI_LIGHT_PALETTE,
}

# Tiles
T_VOID, T_FLOOR, T_HWALL, T_VWALL, T_DOOR, T_CORR, T_STAIR, T_TRAP = range(8)
TILE_CH = {
    T_VOID:  (" ",  0),
    T_FLOOR: (".", 12),
    T_HWALL: ("-",  4),
    T_VWALL: ("|",  3),
    T_DOOR:  ("+", 18),
    T_CORR:  ("#",  5),
    T_STAIR: ("%", 29),
    T_TRAP:  ("^", 28),
}
MEMORY_TILE_COLOR = 5
WALKABLE = {T_FLOOR, T_DOOR, T_CORR, T_STAIR, T_TRAP}

# ===========================================================
#  Screen layout  (BDF j10r: ASCII 6×~10 px)
# ===========================================================
SCR_W, SCR_H = 576, 360
TILE_W, TILE_H = 6, 12          # per-char cell in zoom view
ZV_COLS, ZV_ROWS = MAP_W, PLAY_H # Rogue 5.4.4 dungeon area: 80×22
ZV_PX_W = ZV_COLS * TILE_W      # 480
ZV_PX_H = ZV_ROWS * TILE_H      # 264
DEAD_ZONE_X = 8                  # camera edge zone; leaves ~50% center still
DEAD_ZONE_Y = 5

# Main view + right HUD
ZV_X, ZV_Y = 4, 1                # top-left pixel of full dungeon view
HUD_X = ZV_X + ZV_PX_W + 10
HUD_Y = ZV_Y
HUD_W = SCR_W - HUD_X - 4

# Messages
MSG_LINES = 7
MSG_LINE_H = 10
MSG_X, MSG_Y = 4, SCR_H - MSG_LINES * MSG_LINE_H - 2
MSG_COLS = (SCR_W - MSG_X * 2) // 6

INV_MAX = 26
DASH_INTERVAL = 2                # frames between dash steps
HUNGERTIME = 1300
MORETIME = 150
STOMACHSIZE = 2000
STARVETIME = 850
SEEDURATION = 850
HEALTIME = 30
MAX_TRAPS = 10
AMULET_LEVEL = 26
WANDERTIME = 70
BEARTIME = 3
SLEEPTIME = 5
BORE_LEVEL = 50
BOLT_LENGTH = 6
VS_MAGIC = 3
DEST_PLAYER = "player"
DEST_GOLD = "gold"
HUHDURATION = 20
HELP_HEADER_COL = 31
HELP_TEXT_COL = 30

PLAYER_HIT_MESSAGE_KEYS = (
    "fight.player_hit_excellent",
    "fight.player_hit",
    "fight.player_hit_injured",
    "fight.player_hit_swing",
)
PLAYER_MISS_MESSAGE_KEYS = (
    "fight.player_miss",
    "fight.player_miss_swing",
    "fight.player_miss_barely",
    "fight.player_miss_dont_hit",
)
MONSTER_HIT_MESSAGE_KEYS = (
    "fight.monster_hit_excellent",
    "fight.monster_hit",
    "fight.monster_hit_injured",
    "fight.monster_hit_swing",
)
MONSTER_MISS_MESSAGE_KEYS = (
    "fight.monster_miss",
    "fight.monster_miss_swing",
    "fight.monster_miss_barely",
    "fight.monster_miss_doesnt_hit",
)

# ===========================================================
#  UI states
# ===========================================================
ST_PLAY = 0; ST_MENU = 1; ST_ITEM = 2; ST_DIR = 3
ST_DEAD = 4; ST_INVENTORY = 5; ST_HELP = 6
ST_AUX = 7; ST_WIN = 8; ST_LOADING = 9
ST_QUIT = 10; ST_QUIT_CONFIRM = 11; ST_SCORE = 12
ST_CALL = 13; ST_DISC = 14

CALL_PRESETS = [
    "good", "bad",  "meh",  "skip",
    "try",  "use",  "id?",  "boo",
    "zap",  "hmm",  "ugh",  "yay",
    "wow",  "odd",  "???",  "!!!",
]


# ===========================================================
#  Item categories
# ===========================================================
CAT_POT = "pot"; CAT_SCR = "scr"; CAT_FOOD = "food"
CAT_WPN = "wpn"; CAT_ARM = "arm"; CAT_RING = "ring"; CAT_STICK = "stick"
CAT_GOLD = "gold"; CAT_AMULET = "amulet"
ISYM = {CAT_POT:"!",CAT_SCR:"?",CAT_FOOD:":",CAT_WPN:")",CAT_ARM:"]",CAT_RING:"=",CAT_STICK:"/",CAT_GOLD:"*",CAT_AMULET:","}
ICOL = {CAT_POT:27, CAT_SCR:9, CAT_FOOD:23, CAT_WPN:6, CAT_ARM:5, CAT_RING:14, CAT_STICK:26, CAT_GOLD:29, CAT_AMULET:29}
HALLU_THINGS = ["!","?","=","/",":",")","]","%","*",","]

# ===========================================================
#  Text catalog
# ===========================================================
POT_JA = {
    "healing":"体力が回復する", "extra healing":"体力がとても回復する",
    "poison":"毒の", "gain strength":"強さが増す",
    "restore strength":"強さが元にもどる", "confusion":"頭が混乱する",
    "blindness":"目が見えなくなる", "haste self":"素早くなる",
    "see invisible":"見えないものが見える", "raise level":"経験が増す",
    "monster detection":"遠くの怪物がわかる", "magic detection":"遠くのものがわかる",
    "hallucination":"幻覚の", "levitation":"空中浮遊",
}
SCR_JA = {
    "monster confusion":"怪物を混乱させる", "magic mapping":"魔法の地図の",
    "hold monster":"怪物を封じこめる", "sleep":"眠りにおちる",
    "enchant armor":"よろいに魔法をかける", "identify potion":"水薬がわかる",
    "identify scroll":"巻き物がわかる", "identify weapon":"武器がわかる",
    "identify armor":"よろいがわかる", "identify ring, wand or staff":"指輪や杖がわかる",
    "scare monster":"怪物を近寄せない", "food detection":"食料を探す",
    "teleportation":"テレポートする", "enchant weapon":"武器に魔法をかける",
    "create monster":"怪物を作りだす", "remove curse":"のろいを解く",
    "aggravate monsters":"怪物を怒らせる", "protect armor":"よろいを守る",
}
FOOD_JA = {"food ration":"食糧", "slime-mold":"こけもも"}
WEAPON_JA = {
    "mace":"ほこ", "long sword":"長い剣", "short bow":"弓", "arrow":"矢",
    "dagger":"短剣", "two-handed sword":"大きな剣", "dart":"投げ矢",
    "shuriken":"手裏剣", "spear":"ほこ",
}
ARMOR_JA = {
    "leather armor":"革のよろい", "ring mail":"かたびら",
    "studded leather":"鋲打ち革のよろい", "scale mail":"うろこのよろい",
    "chain mail":"鎖かたびら", "splint mail":"延金のよろい",
    "banded mail":"帯金のよろい", "plate mail":"鋼鉄のよろい",
}
HUD_WEAPON_SHORT = {
    LANG_EN: {
        "mace":"mace", "long sword":"long sw", "short bow":"bow", "arrow":"arrow",
        "dagger":"dagger", "two-handed sword":"2H sw", "dart":"dart",
        "shuriken":"shuriken", "spear":"spear",
    },
    LANG_JA: {
        "mace":"ほこ", "long sword":"長剣", "short bow":"弓", "arrow":"矢",
        "dagger":"短剣", "two-handed sword":"両手剣", "dart":"投げ矢",
        "shuriken":"手裏剣", "spear":"ほこ",
    },
}
HUD_ARMOR_SHORT = {
    LANG_EN: {
        "leather armor":"leather", "ring mail":"ring", "studded leather":"stud",
        "scale mail":"scale", "chain mail":"chain", "splint mail":"splint",
        "banded mail":"banded", "plate mail":"plate",
    },
    LANG_JA: {
        "leather armor":"革", "ring mail":"かたびら", "studded leather":"鋲革",
        "scale mail":"うろこ", "chain mail":"鎖", "splint mail":"延金",
        "banded mail":"帯金", "plate mail":"鋼鉄",
    },
}
RING_JA = {
    "protection":"守り", "add strength":"強さが増す", "sustain strength":"強さを保つ",
    "searching":"探索", "see invisible":"見えないものが見える", "adornment":"飾り",
    "aggravate monster":"怪物を怒らせる", "dexterity":"器用さ",
    "increase damage":"ダメージ増加", "regeneration":"回復", "slow digestion":"腹持ち",
    "teleportation":"テレポート", "stealth":"忍び足", "maintain armor":"よろいを保つ",
}
STICK_JA = {
    "light":"明かり", "invisibility":"見えなくする", "lightning":"稲妻",
    "fire":"火炎", "cold":"冷気", "polymorph":"変化",
    "magic missile":"魔法の矢", "haste monster":"怪物を速める",
    "slow monster":"怪物を遅くする", "drain life":"生命を吸い取る",
    "nothing":"何も起こらない", "teleport away":"遠くへ飛ばす",
    "teleport to":"近くへ飛ばす", "cancellation":"魔法を打ち消す",
}
MONSTER_JA = {
    "aquator":"水ごけの怪物", "bat":"大こうもり", "centaur":"ケンタウロス",
    "dragon":"ドラゴン", "emu":"大うずら", "venus flytrap":"はえとりぐさ",
    "griffin":"翼ライオン", "hobgoblin":"小鬼", "ice monster":"氷の怪物",
    "jabberwock":"巨大トカゲ", "kestrel":"大はやぶさ",
    "leprechaun":"金持ち妖精", "medusa":"メデューサ", "nymph":"ニンフ",
    "orc":"欲ばり鬼", "phantom":"幽霊", "quagga":"大つのじか",
    "rattlesnake":"がらがらへび", "snake":"へび", "troll":"巨人",
    "black unicorn":"一角獣", "vampire":"バンパイア", "wraith":"死霊",
    "xeroc":"物まねの怪物", "yeti":"雪男", "zombie":"ゾンビ",
}
POT_COLOR_JA = {
    "blue":"青い", "red":"赤い", "green":"緑の", "grey":"灰色の",
    "brown":"茶色の", "clear":"透明な", "pink":"ピンクの",
    "white":"白い", "purple":"紫の", "yellow":"黄色い",
    "plaid":"水色の", "amber":"琥珀色の", "black":"黒い",
    "orange":"橙色の",
}

class TextCatalog:
    _catalogs = None
    _missing_warned = set()

    @classmethod
    def _load_catalogs(cls):
        if cls._catalogs is not None:
            return cls._catalogs
        base = os.path.join(os.path.dirname(__file__), "assets", "messages")
        catalogs = {}
        try:
            if sys.platform == "emscripten":
                # Pyodide: open() won't find assets, fetch JSON directly from GitHub
                import pyodide.http as _ph
                _base = "https://raw.githubusercontent.com/hnsol/pyxel-rogue/master"
                for lang in (LANG_EN, LANG_JA):
                    resp = _ph.open_url(f"{_base}/assets/messages/{lang}.json")
                    catalogs[lang] = json.load(resp)
            else:
                for lang in (LANG_EN, LANG_JA):
                    path = os.path.join(base, f"{lang}.json")
                    with open(path, encoding="utf-8") as f:
                        catalogs[lang] = json.load(f)
        except Exception:
            from rogue_message_catalogs import EN_MESSAGES, JA_MESSAGES
            catalogs = {LANG_EN: EN_MESSAGES, LANG_JA: JA_MESSAGES}
        cls._catalogs = catalogs
        return cls._catalogs

    @classmethod
    def _warn_missing(cls, key):
        if key in cls._missing_warned:
            return
        cls._missing_warned.add(key)
        print(f"[TextCatalog] missing message key: {key}", file=sys.stderr)

    @staticmethod
    def msg(lang, key, **kw):
        catalogs = TextCatalog._load_catalogs()
        lang = lang if lang in (LANG_EN, LANG_JA) else LANG_EN
        s = catalogs.get(lang, {}).get(key)
        if s is None and lang != LANG_EN:
            s = catalogs.get(LANG_EN, {}).get(key)
        if s is None:
            TextCatalog._warn_missing(key)
            s = f"[missing:{key}]"
        return s.format(**kw) if kw else s

    @staticmethod
    def menu(lang, key):
        msg_key = "menu." + key.lower().replace(" ", "_")
        return TextCatalog.msg(lang, msg_key)

    @staticmethod
    def trap(lang, key):
        msg_key = "trap." + key.lower().replace(" ", "_")
        return TextCatalog.msg(lang, msg_key)

    @staticmethod
    def monster(lang, name):
        return MONSTER_JA.get(name, name) if lang == LANG_JA else name

    @staticmethod
    def hud_item_kind(lang, cat, name):
        lang = lang if lang in (LANG_EN, LANG_JA) else LANG_EN
        if cat == CAT_WPN:
            return HUD_WEAPON_SHORT.get(lang, HUD_WEAPON_SHORT[LANG_EN]).get(
                name,
                TextCatalog.item_kind(lang, cat, name),
            )
        if cat == CAT_ARM:
            return HUD_ARMOR_SHORT.get(lang, HUD_ARMOR_SHORT[LANG_EN]).get(
                name,
                TextCatalog.item_kind(lang, cat, name),
            )
        return TextCatalog.item_kind(lang, cat, name)

    @staticmethod
    def item_kind(lang, cat, name):
        if lang != LANG_JA:
            return name
        if cat == CAT_POT: return POT_JA.get(name, name)
        if cat == CAT_SCR: return SCR_JA.get(name, name)
        if cat == CAT_FOOD: return FOOD_JA.get(name, name)
        if cat == CAT_WPN: return WEAPON_JA.get(name, name)
        if cat == CAT_ARM: return ARMOR_JA.get(name, name)
        if cat == CAT_RING: return RING_JA.get(name, name)
        if cat == CAT_STICK: return STICK_JA.get(name, name)
        if cat == CAT_AMULET: return "イェンダーの魔除け"
        return name

# ===========================================================
#  Dice
# ===========================================================
def roll(s: str) -> int:
    n, d = s.split("d"); return RNG.roll(int(n), int(d))

def roll_damage_expr(expr: str) -> int:
    total = 0
    for part in expr.split("/"):
        sep = "x" if "x" in part else "d"
        n, d = part.split(sep)
        total += RNG.roll(int(n), int(d))
    return total

def rnd(n: int) -> int:
    return RNG.rnd(n)

def in_map(x: int, y: int) -> bool:
    return 0 <= x < MAP_W and 0 <= y < MAP_H

def in_play_area(x: int, y: int) -> bool:
    return 0 <= x < MAP_W and PLAY_Y_MIN <= y <= PLAY_Y_MAX

# ===========================================================
#  Item data  (Rogue 5.4.4)
# ===========================================================
POTIONS = [
    {"name":"confusion","prob":7},{"name":"hallucination","prob":8},
    {"name":"poison","prob":8},{"name":"gain strength","prob":13},
    {"name":"see invisible","prob":3},{"name":"healing","prob":13},
    {"name":"monster detection","prob":6},{"name":"magic detection","prob":6},
    {"name":"raise level","prob":2},{"name":"extra healing","prob":5},
    {"name":"haste self","prob":5},{"name":"restore strength","prob":13},
    {"name":"blindness","prob":5},
    {"name":"levitation","prob":6},
]
POT_COLORS = ["blue","red","green","grey","brown","clear",
              "pink","white","purple","yellow","plaid","amber",
              "black","orange"]

SCROLLS = [
    {"name":"monster confusion","prob":7},
    {"name":"magic mapping","prob":4},{"name":"hold monster","prob":2},
    {"name":"sleep","prob":3},{"name":"enchant armor","prob":7},
    {"name":"identify potion","prob":10},{"name":"identify scroll","prob":10},
    {"name":"identify weapon","prob":6},{"name":"identify armor","prob":7},
    {"name":"identify ring, wand or staff","prob":10},
    {"name":"scare monster","prob":3},{"name":"food detection","prob":2},
    {"name":"teleportation","prob":5},{"name":"enchant weapon","prob":8},
    {"name":"create monster","prob":4},{"name":"remove curse","prob":7},
    {"name":"aggravate monsters","prob":3},{"name":"protect armor","prob":2},
]
SCR_SYLS = ["blech","foo","bstr","bar","xyzzy","fnord","snafu","fro",
            "aimfiz","aefg","zorch","elam","isko","temov","gnik","snef",
            "forz","juyed","cohah","tstr","priky","motke","ando","wacl"]

FOODS = [{"name":"food ration","nut":900},{"name":"slime-mold","nut":700}]

WEAPONS = [
    {"name":"mace","damage":"2d4","hurl_damage":"1d3","wield":True},
    {"name":"long sword","damage":"3d4","hurl_damage":"1d2","wield":True},
    {"name":"short bow","damage":"1d1","hurl_damage":"1d1","wield":True},
    {"name":"arrow","damage":"1d1","hurl_damage":"2d3","wield":False,"stack":True,"missile":True,"launcher":2},
    {"name":"dagger","damage":"1d6","hurl_damage":"1d4","wield":True,"missile":True},
    {"name":"two-handed sword","damage":"4d4","hurl_damage":"1d2","wield":True},
    {"name":"dart","damage":"1d1","hurl_damage":"1d3","wield":False,"stack":True,"missile":True},
    {"name":"shuriken","damage":"1d2","hurl_damage":"2d4","wield":False,"stack":True,"missile":True},
    {"name":"spear","damage":"2d3","hurl_damage":"1d6","wield":True,"missile":True},
]

STR_PLUS = [-7,-6,-5,-4,-3,-2,-1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,2,2,2,2,2,2,3]
ADD_DAM = [-7,-6,-5,-4,-3,-2,-1,0,0,0,0,0,0,0,0,0,1,1,2,3,3,4,5,5,5,5,5,5,5,5,5,6]

ARMORS = [
    {"name":"leather armor","ac":8},{"name":"ring mail","ac":7},
    {"name":"studded leather","ac":7},{"name":"scale mail","ac":6},
    {"name":"chain mail","ac":5},{"name":"splint mail","ac":4},
    {"name":"banded mail","ac":4},{"name":"plate mail","ac":3},
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
    MonsterSpec("A","aquator",5,2,"0x0/0x0",20,9,"rust"),
    MonsterSpec("B","bat",1,3,"1x2",1,1,"erratic,fly"),
    MonsterSpec("C","centaur",4,4,"1x2/1x5/1x5",17,7,"", carry=15),
    MonsterSpec("D","dragon",10,-1,"1x8/1x8/3x10",5000,21,"", carry=100),
    MonsterSpec("E","emu",1,7,"1x2",2,1,""),
    MonsterSpec("F","venus flytrap",8,3,"0x0",80,12,"hold"),
    MonsterSpec("G","griffin",13,2,"4x3/3x5",2000,17,"fly,regen", carry=20),
    MonsterSpec("H","hobgoblin",1,5,"1x8",3,1,""),
    MonsterSpec("I","ice monster",1,9,"0x0",5,5,"freeze"),
    MonsterSpec("J","jabberwock",15,6,"2x12/2x4",3000,20,"", carry=70),
    MonsterSpec("K","kestrel",1,7,"1x4",1,1,"fly"),
    MonsterSpec("L","leprechaun",3,8,"1x1",10,6,"steal_gold"),
    MonsterSpec("M","medusa",8,2,"3x4/3x4/2x5",200,18,rogue_monsters.FLAG_CAN_CONFUSE, carry=40),
    MonsterSpec("N","nymph",3,9,"0x0",37,9,"steal_item", carry=100),
    MonsterSpec("O","orc",1,6,"1x8",5,5,"", carry=15),
    MonsterSpec("P","phantom",8,3,"4x4",120,15,rogue_monsters.FLAG_INVISIBLE),
    MonsterSpec("Q","quagga",3,3,"1x5/1x5",15,8,""),
    MonsterSpec("R","rattlesnake",2,3,"1x6",9,4,"poison"),
    MonsterSpec("S","snake",1,5,"1x3",2,2,""),
    MonsterSpec("T","troll",6,4,"1x8/1x8/2x6",120,13,"regen", carry=50),
    MonsterSpec("U","black unicorn",7,-2,"1x9/1x9/2x9",190,18,""),
    MonsterSpec("V","vampire",8,1,"1x10",350,16,"drain,regen", carry=20),
    MonsterSpec("W","wraith",5,4,"1x6",55,14,"drain_level"),
    MonsterSpec("X","xeroc",7,7,"4x4",100,11,"mimic", carry=30),
    MonsterSpec("Y","yeti",4,6,"1x6/1x6",50,10,"", carry=30),
    MonsterSpec("Z","zombie",2,8,"1x8",6,7,""),
]
MCOL = {"A":14,"B":28,"C":17,"D": 2,"E": 8,"F": 5,"G":13,"H":21,"I":27,"J": 1,
        "K":15,"L":14,"M": 1,"N":26,"O":17,"P": 6,"Q":22,"R": 6,"S": 5,"T":17,
        "U": 1,"V": 2,"W":26,"X": 8,"Y": 6,"Z": 1}
PALETTE_MONSTER_COLORS = {
    PALETTE_FLEXOKI_LIGHT: {"K": 30},
}

# 8-direction vectors
DIR8 = {
    "N":(0,-1),"S":(0,1),"W":(-1,0),"E":(1,0),
    "NW":(-1,-1),"NE":(1,-1),"SW":(-1,1),"SE":(1,1),
}
B_TAP_FRAMES = 8
BACK_TAP_FRAMES = 8

# ===========================================================
#  Menu actions
# ===========================================================
MENU_ACTIONS = [
    ("Quaff",   CAT_POT),("Read",   CAT_SCR),("Eat",    CAT_FOOD),
    ("Wield",   CAT_WPN),("Wear",   CAT_ARM),("Put on", CAT_RING),("Take off",None),
    ("Zap",     CAT_STICK),("Throw",   None),   ("Drop",   None),
]
AUX_ACTIONS = ["Inventory", "Help", "Search", "Trap", "Pickup", "Language", "Palette", "Quit"]

# ===========================================================
#  Classes
# ===========================================================
class Room:
    def __init__(s,x,y,w,h,flags=None):
        s.x,s.y,s.w,s.h=x,y,w,h
        s.flags=set(flags or ())
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
    def __init__(s,cat,kind,ench=0,cursed=False,qty=1,hit_plus=None,dam_plus=None,charges=0,known=True):
        s.uid=Item._nid; Item._nid+=1
        s.cat=cat; s.kind=kind; s.cursed=cursed; s.qty=qty
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
        if s.cat==CAT_AMULET: return {"name":"Amulet of Yendor"}
        return {}
    @property
    def stackable(s):
        return s.cat==CAT_FOOD or (s.cat==CAT_WPN and s.data.get("stack",False))
    @property
    def sym(s): return ISYM.get(s.cat,"?")
    def plus_key(s):
        return (s.hit_plus,s.dam_plus) if s.cat==CAT_WPN else (s.ench,0)

class Monster:
    def __init__(s,x,y,sym,name,hp,level,armor,damage_expr,exp,fl):
        s.x,s.y,s.sym,s.name=x,y,sym,name
        s.disguise=sym
        s.hp=s.max_hp=hp
        s.level=level; s.armor=armor; s.damage_expr=damage_expr; s.exp=exp
        s.flags=set(fl.split(",")) if fl else set()
        s.held=s.scared=s.confused=0
        s.running=False; s.dest=DEST_PLAYER; s.turn=True
        s.mean=True; s.target=False; s.found=False; s.vf_hit=0
        s.pack=[]
    @property
    def alive(s): return s.hp>0

def monster_hp(spec: object) -> int:
    return max(1, roll_damage_expr(f"{spec.level}x8"))

class Player:
    # Rogue 5.4.4 extern.c:e_levels[] with a leading level-1 sentinel for Pyxel indexing.
    EXP_T=[0,10,20,40,80,160,320,640,1300,2600,5200,13000,26000,
           50000,100000,200000,400000,800000,2000000,4000000,8000000]
    def __init__(s):
        s.x=s.y=0; s.hp=s.max_hp=16; s.st=s.max_st=16
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
        if s.level>=len(s.EXP_T): return False
        if s.exp>=s.EXP_T[s.level]:
            s.level+=1; g=RNG.randint(3,8); s.max_hp+=g; s.hp+=g; return True
        return False
    def hunger(s):
        prev=s.state
        if s.food<=0:
            if s.food < -STARVETIME:
                s.hp=0; s.state="faint"; return "pyxel.starve_to_death"
            s.food-=1
            if RNG.randrange(5)==0:
                s.no_command=max(s.no_command,RNG.randint(4,11))
                s.state="faint"; return "pyxel.faint_from_lack_of_food"
            s.state="faint"; return None
        s.food-=1 + rogue_rings.ring_eat(s.ring_l, RNG) + rogue_rings.ring_eat(s.ring_r, RNG)
        if s.food<=0:
            s.state="faint"
            return None
        if s.food<MORETIME:
            s.state="weak"
            return "pyxel.are_weak" if prev!="weak" else None
        if s.food<2*MORETIME:
            s.state="hungry"
            return "pyxel.feel_hungry" if prev!="hungry" else None
        s.state="normal"
        return None
    def heal_tick(s):
        if s.hp>=s.max_hp: return
        s.quiet+=1
        old=s.hp
        if s.level<8:
            if s.quiet+(s.level<<1)>20:
                s.hp+=1
        elif s.quiet>=3:
            s.hp+=RNG.randint(1,max(1,s.level-7))
        s.hp+=rogue_rings.regeneration_count(s)
        if s.hp!=old:
            s.hp=min(s.hp,s.max_hp); s.quiet=0
    def recalc_ac(s):
        s.ac = (s.arm.data["ac"]-s.arm.ench) if s.arm else 10
        s.ac -= rogue_rings.protection_bonus(s)
    def str_hit_plus(s):
        return STR_PLUS[max(0,min(s.st,len(STR_PLUS)-1))]
    def str_dam_plus(s):
        return ADD_DAM[max(0,min(s.st,len(ADD_DAM)-1))]
    def inv_full(s): return len(s.inv)>=INV_MAX
    def add_item(s,it):
        if it.stackable:
            for i in s.inv:
                if i.cat==it.cat and i.kind==it.kind and i.plus_key()==it.plus_key():
                    i.qty+=it.qty; return True
        if s.inv_full(): return False
        s.inv.append(it); return True
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
    def __init__(s, lang=LANG_EN):
        s.lang = lang
        s.pcol=RNG.sample(POT_COLORS,len(POTIONS))
        syls=list(SCR_SYLS); RNG.shuffle(syls)
        s.snam=[]
        for i in range(len(SCROLLS)):
            n=RNG.randint(2,3); st=(i*3)%len(syls)
            s.snam.append(" ".join(syls[(st+j)%len(syls)] for j in range(n)))
        s.pk=[False]*len(POTIONS); s.sk=[False]*len(SCROLLS)
        s.pg=[None]*len(POTIONS); s.sg=[None]*len(SCROLLS)
        s.rstones=rogue_rings.init_stones(RNG)
        s.rk=[False]*len(RINGS)
        s.rg=[None]*len(RINGS)
        s.wtypes,s.wmades=rogue_sticks.init_materials(RNG)
        s.wk=[False]*len(STICKS)
        s.wg=[None]*len(STICKS)
    def set_lang(s, lang):
        s.lang = lang if lang in (LANG_EN, LANG_JA) else LANG_EN
    def name(s,it,lang=None):
        lang = s.lang if lang is None else lang
        if it.cat==CAT_POT:
            if s.pk[it.kind]:
                nm=TextCatalog.item_kind(lang, CAT_POT, POTIONS[it.kind]["name"])
                return f"potion of {nm}" if lang==LANG_EN else f"{nm}水薬"
            if s.pg[it.kind] is not None:
                g=s.pg[it.kind]
                col=s.pcol[it.kind]
                return f"{col} potion called {g}" if lang==LANG_EN else f"{POT_COLOR_JA.get(col,col)}水薬（{g}）"
            col=s.pcol[it.kind]
            return f"{col} potion" if lang==LANG_EN else f"{POT_COLOR_JA.get(col,col)}水薬"
        if it.cat==CAT_SCR:
            if s.sk[it.kind]:
                nm=TextCatalog.item_kind(lang, CAT_SCR, SCROLLS[it.kind]["name"])
                return f"scroll of {nm}" if lang==LANG_EN else f"{nm}巻き物"
            if s.sg[it.kind] is not None:
                g=s.sg[it.kind]
                return f"scroll called {g}" if lang==LANG_EN else f"巻き物（{g}）"
            return f"scroll [{s.snam[it.kind]}]" if lang==LANG_EN else f"巻き物 [{s.snam[it.kind]}]"
        if it.cat==CAT_FOOD:
            nm=TextCatalog.item_kind(lang, CAT_FOOD, it.data["name"])
            if it.qty>1 and lang==LANG_EN and not nm.endswith("s"):
                nm = f"{nm}s"
            prefix = f"{it.qty} " if it.qty>1 else ""
            return f"{prefix}{nm}"
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
            return f"{'+' if e>=0 else ''}{e} {nm} [protection {protection}]{label}"
        if it.cat==CAT_RING:
            spec=RINGS[it.kind]
            if s.rk[it.kind]:
                nm=TextCatalog.item_kind(lang, CAT_RING, spec["name"])
                num=rogue_rings.ring_num(it) if it.known else ""
                return f"ring of {nm}{num}" if lang==LANG_EN else f"{nm}の指輪{num}"
            if s.rg[it.kind] is not None:
                g=s.rg[it.kind]; stone=s.rstones[it.kind]
                return f"{stone} ring called {g}" if lang==LANG_EN else f"{stone}の指輪（{g}）"
            stone=s.rstones[it.kind]
            return f"{stone} ring" if lang==LANG_EN else f"{stone}の指輪"
        if it.cat==CAT_STICK:
            spec=STICKS[it.kind]
            typ=s.wtypes[it.kind]
            made=s.wmades[it.kind]
            if s.wk[it.kind]:
                nm=TextCatalog.item_kind(lang, CAT_STICK, spec["name"])
                charges=rogue_sticks.charge_str(it) if it.known else ""
                return f"{typ} of {nm}{charges}({made})" if lang==LANG_EN else f"{nm}の{typ}{charges}({made})"
            if s.wg[it.kind] is not None:
                g=s.wg[it.kind]
                return f"{made} {typ} called {g}" if lang==LANG_EN else f"{made}{typ}（{g}）"
            return f"{made} {typ}"
        if it.cat==CAT_AMULET:
            nm=TextCatalog.item_kind(lang, CAT_AMULET, it.data["name"])
            return f"the {nm}" if lang==LANG_EN else nm
        return "something" if lang==LANG_EN else "何者か"

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
    def gen(depth):
        # C: new_level.c:new_level()
        tm=[[T_VOID]*MAP_W for _ in range(MAP_H)]; rooms=[]; sr={}
        gone=set()
        for _ in range(rnd(4)):
            while True:
                i=rnd(GRID_C*GRID_R)
                if i not in gone:
                    gone.add(i); break
        for i in range(GRID_C*GRID_R):
            gx,gy=i%GRID_C,i//GRID_C
            top_x,top_y=gx*SEC_W+1,gy*SEC_H
            flags=set()
            if i in gone:
                flags.add(ROOM_GONE)
            elif rnd(10) < depth - 1:
                flags.add(ROOM_MAZE if rnd(15)==0 else ROOM_DARK)
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
                DGen._maze_room(tm,r)
            else:
                DGen._room(tm,r)
        for a,b in DGen._passage_edges():
            DGen._conn(tm,rooms[a],rooms[b],abs(a-b)==1)
        DGen._ensure(tm,rooms); return tm,rooms

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
    def _maze_room(t,r):
        for y in range(r.y,r.y+r.h):
            for x in range(r.x,r.x+r.w):
                if in_play_area(x,y):
                    t[y][x]=T_VOID
        cells=[
            (x,y)
            for y in range(r.y+1,r.y+r.h-1,2)
            for x in range(r.x+1,r.x+r.w-1,2)
        ]
        if not cells:
            return
        start=RNG.choice(cells)
        t[start[1]][start[0]]=T_CORR
        seen={start}; stack=[start]
        while stack:
            x,y=stack[-1]
            nxt=[]
            for dx,dy in ((2,0),(-2,0),(0,2),(0,-2)):
                nx,ny=x+dx,y+dy
                if r.x<nx<r.x+r.w-1 and r.y<ny<r.y+r.h-1 and (nx,ny) not in seen:
                    nxt.append((nx,ny,dx,dy))
            if not nxt:
                stack.pop()
                continue
            nx,ny,dx,dy=RNG.choice(nxt)
            t[y+dy//2][x+dx//2]=T_CORR
            t[ny][nx]=T_CORR
            seen.add((nx,ny)); stack.append((nx,ny))
    @staticmethod
    def _conn(t,r1,r2,horiz=None):
        """Connect two rooms by choosing wall doors first, like Rogue's conn()."""
        if horiz is None:
            horiz = abs(r1.cx-r2.cx) >= abs(r1.cy-r2.cy)
        if horiz:
            if r1.cx <= r2.cx:
                d1,s=DGen._exit(t,r1,"R",outward=True)
                d2,e=DGen._exit(t,r2,"L",outward=True)
            else:
                d1,s=DGen._exit(t,r1,"L",outward=True)
                d2,e=DGen._exit(t,r2,"R",outward=True)
        else:
            if r1.cy <= r2.cy:
                d1,s=DGen._exit(t,r1,"D",outward=True)
                d2,e=DGen._exit(t,r2,"U",outward=True)
            else:
                d1,s=DGen._exit(t,r1,"U",outward=True)
                d2,e=DGen._exit(t,r2,"D",outward=True)
        if d1 is not None: DGen._door(t,d1)
        if d2 is not None: DGen._door(t,d2)
        DGen._dig_pass(t,s,e,horiz)
    @staticmethod
    def _exit(t,r,side,outward=True):
        if r.is_gone:
            p=DGen._passage_side_point(r,side)
            DGen._corr(t,p)
            return None,p
        if r.is_maze:
            p=DGen._maze_exit(t,r,side)
            return None,p
        door=DGen._pick_wall_door(t,r,side)
        x,y=door
        dx,dy={"L":(-1,0),"R":(1,0),"U":(0,-1),"D":(0,1)}[side]
        return door,(x+dx,y+dy) if outward else door
    @staticmethod
    def _passage_side_point(r,side):
        if side=="L": return r.x,r.cy
        if side=="R": return r.x+r.w-1,r.cy
        if side=="U": return r.cx,r.y
        return r.cx,r.y+r.h-1
    @staticmethod
    def _maze_exit(t,r,side):
        if side in ("L","R"):
            xs=range(r.x+1,r.x+r.w-1)
            target_x = r.x if side=="L" else r.x+r.w-1
            cands=[(x,y) for y in range(r.y+1,r.y+r.h-1) for x in xs if t[y][x]==T_CORR]
            cands.sort(key=lambda p: abs(p[0]-target_x))
        else:
            ys=range(r.y+1,r.y+r.h-1)
            target_y = r.y if side=="U" else r.y+r.h-1
            cands=[(x,y) for x in range(r.x+1,r.x+r.w-1) for y in ys if t[y][x]==T_CORR]
            cands.sort(key=lambda p: abs(p[1]-target_y))
        p=RNG.choice(cands[:max(1,min(4,len(cands)))]) if cands else DGen._passage_side_point(r,side)
        DGen._corr(t,p)
        return p
    @staticmethod
    def _pick_wall_door(t,r,side):
        if side in ("L","R"):
            x = r.x if side=="L" else r.x+r.w-1
            cands=[(x,y) for y in range(r.y+1,r.y+r.h-1)]
        else:
            y = r.y if side=="U" else r.y+r.h-1
            cands=[(x,y) for x in range(r.x+1,r.x+r.w-1)]
        RNG.shuffle(cands)
        for p in cands:
            if DGen._door_ok(t,p): return p
        return cands[0]
    @staticmethod
    def _door_ok(t,p):
        x,y=p
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx,ny=x+dx,y+dy
            if in_map(nx,ny) and t[ny][nx]==T_DOOR:
                return False
        return True
    @staticmethod
    def _door(t,p):
        x,y=p
        if in_play_area(x,y): t[y][x]=T_DOOR
    @staticmethod
    def _corr(t,p):
        x,y=p
        if in_play_area(x,y): t[y][x]=T_CORR
    @staticmethod
    def _dig_pass(t,s,e,first_horiz):
        x,y=s; ex,ey=e
        if first_horiz:
            turn_x=DGen._turn_coord(x,ex)
            DGen._hl(t,x,turn_x,y)
            DGen._vl(t,y,ey,turn_x)
            DGen._hl(t,turn_x,ex,ey)
        else:
            turn_y=DGen._turn_coord(y,ey)
            DGen._vl(t,y,turn_y,x)
            DGen._hl(t,x,ex,turn_y)
            DGen._vl(t,turn_y,ey,ex)
    @staticmethod
    def _turn_coord(a,b):
        lo,hi=min(a,b),max(a,b)
        if hi-lo <= 2:
            return RNG.randint(lo,hi) if a!=b else a
        return RNG.randint(lo+1,hi-1)
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
    @staticmethod
    def _ensure(t,rooms):
        rooms=[r for r in rooms if r.usable]
        if len(rooms)<=1: return
        def flood(sx,sy):
            vis=set();stk=[(sx,sy)]
            while stk:
                x,y=stk.pop()
                if (x,y) in vis or not(0<=x<MAP_W and 0<=y<MAP_H): continue
                if t[y][x]==T_VOID: continue
                vis.add((x,y))
                for dx,dy in((-1,0),(1,0),(0,-1),(0,1)): stk.append((x+dx,y+dy))
            return vis
        base=flood(rooms[0].cx,rooms[0].cy)
        for r in rooms[1:]:
            if(r.cx,r.cy) not in base:
                DGen._conn(t,rooms[0],r); base=flood(rooms[0].cx,rooms[0].cy)

# ===========================================================
#  Item factory
# ===========================================================
def wchoice(tbl):
    tot=sum(e["prob"] for e in tbl); r=RNG.randint(1,tot); a=0
    for i,e in enumerate(tbl):
        a+=e["prob"]
        if r<=a: return i
    return 0

def make_item(depth):
    c=RNG.random()
    if c<.26: return Item(CAT_POT,wchoice(POTIONS))
    if c<.62: return Item(CAT_SCR,wchoice(SCROLLS))
    if c<.78: return Item(CAT_FOOD,RNG.randint(0,len(FOODS)-1))
    if c<.85:
        k=RNG.randint(0,len(WEAPONS)-1)
        r=RNG.randrange(100)
        hit_plus=0
        cursed=False
        if r<10:
            hit_plus-=RNG.randrange(3)+1; cursed=True
        elif r<15:
            hit_plus+=RNG.randrange(3)+1
        q=RNG.randint(8,15) if WEAPONS[k].get("stack") else 1
        return Item(CAT_WPN,k,hit_plus=hit_plus,dam_plus=0,cursed=cursed,qty=q,known=False)
    if c<.92:
        k=RNG.randint(0,len(ARMORS)-1)
        r=RNG.rnd(100)
        e=0
        cursed=False
        if r<20:
            e-=RNG.rnd(3)+1; cursed=True
        elif r<28:
            e+=RNG.rnd(3)+1
        return Item(CAT_ARM,k,ench=e,cursed=cursed,known=False)
    if c<.96:
        ring=rogue_rings.make_ring(RNG, CAT_RING)
        return Item(CAT_RING,ring.kind,ench=ring.ench,cursed=ring.cursed,known=False)
    stick=rogue_sticks.make_stick(RNG, CAT_STICK)
    return Item(CAT_STICK,stick.kind,charges=stick.charges,known=False)

def start_inv():
    w=Item(CAT_WPN,0,hit_plus=1,dam_plus=1) # mace +1,+1
    a=Item(CAT_ARM,0,ench=1)        # leather +1
    ar=Item(CAT_WPN,3,hit_plus=0,dam_plus=0,qty=25)# arrows
    b=Item(CAT_WPN,2,hit_plus=1,dam_plus=0) # bow +1,+0
    f=Item(CAT_FOOD,0)              # ration
    return [w,a,ar,b,f],w,a


# ===========================================================
#  GAME
# ===========================================================
class Game:
    def __init__(self):
        self.settings = Settings()
        pyxel.init(SCR_W, SCR_H, title="Pyxel Rogue", fps=30, quit_key=pyxel.KEY_NONE)
        self.apply_palette()
        self.font = pyxel.Font(FONT_PATH)
        self.st = ST_LOADING
        self._loading_phase = 0
        pyxel.run(self.update, self.draw)

    def ensure_settings(self):
        if "settings" not in self.__dict__:
            self.settings = Settings()
        return self.settings

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
        if not hasattr(pyxel, 'colors'):
            return
        palette = PALETTES.get(self.ensure_settings().palette, GBC_PALETTE)
        for i, rgb in enumerate(palette):
            if i < len(pyxel.colors):
                pyxel.colors[i] = rgb
            else:
                pyxel.colors.append(rgb)

    def run_step_interval(self):
        return DASH_INTERVAL if self.ensure_settings().show_run_steps else 1

    def monster_color(self, sym):
        overrides = PALETTE_MONSTER_COLORS.get(self.ensure_settings().palette, {})
        return overrides.get(sym, MCOL.get(sym, 9))

    def random_thing_sym(self, depth=None):
        # Rogue 5.4.4 misc.c:rnd_thing() omits Amulet before AMULETLEVEL.
        depth = self.p.depth if depth is None else depth
        limit = len(HALLU_THINGS) if depth >= AMULET_LEVEL else len(HALLU_THINGS) - 1
        return HALLU_THINGS[rnd(limit)]

    def hallucination_thing_sym(self):
        return self.random_thing_sym()

    def visible_tile_sym(self, x, y, tile):
        if self.p.hallucinating > 0 and tile == T_STAIR:
            return self.hallucination_thing_sym()
        return TILE_CH.get(tile, (" ", 0))[0]

    def visible_item_sym(self, item):
        if self.p.hallucinating > 0:
            return self.hallucination_thing_sym()
        return item.sym

    def visible_monster_sym(self, monster):
        if self.p.hallucinating > 0:
            return chr(ord("A") + rnd(26))
        return getattr(monster, "disguise", monster.sym)

    def detected_monster_sym(self, monster):
        if self.p.hallucinating > 0:
            return chr(ord("A") + rnd(26))
        return monster.sym

    def toggle_palette(self):
        settings = self.ensure_settings()
        i = PALETTE_IDS.index(settings.palette) if settings.palette in PALETTE_IDS else 0
        settings.palette = PALETTE_IDS[(i + 1) % len(PALETTE_IDS)]
        self.apply_palette()
        self.msg("pyxel.palette_set", palette=PALETTE_LABELS[settings.palette])

    def txt(self, x, y, s, c):
        pyxel.text(x, y, str(s), c, self.font)

    def item_name(self,it, describe=True):
        name=self.ident.name(it)
        if describe and it is self.p.wpn: return f"{name} (weapon in hand)"
        if describe and it is self.p.arm: return f"{name} (being worn)"
        if describe and it is self.p.ring_l: return f"{name} (on left hand)"
        if describe and it is self.p.ring_r: return f"{name} (on right hand)"
        return name

    def equip_name(self,it):
        return self.item_name(it, describe=False)

    def hud_equip_name(self,it):
        lang = self.lang if self.lang in (LANG_EN, LANG_JA) else LANG_EN
        if it.cat == CAT_WPN:
            nm=TextCatalog.hud_item_kind(lang, CAT_WPN, it.data["name"])
            hp = f"{'+' if it.hit_plus>=0 else ''}{it.hit_plus}"
            dp = f"{'+' if it.dam_plus>=0 else ''}{it.dam_plus}"
            prefix = f"{it.qty} " if it.stackable and it.qty>1 else ""
            return f"{prefix}{hp},{dp} {nm}"
        if it.cat == CAT_ARM:
            e=it.ench
            nm=TextCatalog.hud_item_kind(lang, CAT_ARM, it.data["name"])
            return f"{'+' if e>=0 else ''}{e} {nm}"
        return self.equip_name(it)

    # ---------- Init ----------
    def new_game(self):
        self.ensure_settings()
        self.p = Player()
        inv,w,a = start_inv()
        self.p.inv=inv; self.p.wpn=w; self.p.arm=a; self.p.recalc_ac()
        self.ident = IdentTable(self.lang)
        self.msgs = []; self.msg_turns = []; self.explored = set(); self.visible = set()
        self.gitems = []; self.mons = []; self.turn = 0
        self.traps = {}; self.hidden_tiles = {}
        self.st = ST_PLAY; self.mcur = 0; self.icur = 0; self.acur = 0
        self.cact = None; self.dact = None; self.fitems = []
        self.call_input = ""; self.call_preset_idx = 0; self.call_item = None
        self.disc_scroll = 0
        self.turn_msg_start = 0
        self.throw_dir = None; self.zap_item = None; self.action_origin = ST_PLAY
        self.cam_x = self.cam_y = 0
        self.dashing = False; self.dash_d = (0,0); self.dash_t = 0
        self.dash_steps = 0
        self.dash_restart_guard = False
        self.b_prev = False; self.b_frames = 0
        self.b_used = False; self.b_tap = False
        self.back_prev = False; self.back_frames = 0
        self.back_used = False; self.back_tap = False
        self.b_menu_guard = False
        self.diag_assist = False
        self.auto_pickup = True
        self.dir_pending = None
        self.throw_anim = None
        self.turn_after_throw_anim = False
        self.last_hp_seen = None
        self.hp_damage_from = None
        self.hp_damage_turn = None
        self.death_cause = ""
        self.options = {"tombstone": True, "name": os.environ.get("USER", "rogue")}
        self.max_depth = 0
        self.wander_timer = 0
        self.wander_between = 0
        self.fuses = rogue_daemons.FuseList()
        self.daemons = rogue_daemons.DaemonList()
        self.haste_half_turn = False
        self.result_scores = []
        self.result_entry = None
        self.result_outcome = None
        self.descend()
        self.msg("pyxel.welcome_to_dungeons")

    def result_level(self, outcome):
        return self.max_depth if outcome == "winner" else self.p.depth

    def result_flags(self, outcome):
        if outcome == "killed" and self.p.has_amulet:
            return "killed_with_amulet"
        return outcome

    def result_killer(self, outcome):
        if outcome in ("quit", "winner"):
            return ""
        killer = self.death_cause or "died"
        return killer.replace("killed by a ", "").replace("killed by ", "")

    def enter_result_state(self, outcome):
        self.result_outcome = outcome
        self.result_entry = build_score_entry(
            result_flags=self.result_flags(outcome),
            level=self.result_level(outcome),
            killer=self.result_killer(outcome),
            player_name=self.options.get("name", "rogue"),
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            gold=self.p.gold,
        )
        save_score_entry(self.result_entry)
        self.result_scores = get_top_scores(load_score_entries(), limit=10)
        if outcome == "winner":
            self.st = ST_WIN
        elif outcome == "quit":
            self.st = ST_QUIT
        else:
            self.st = ST_DEAD

    def set_lang(self, lang):
        self.lang = lang if lang in (LANG_EN, LANG_JA) else LANG_EN
        if hasattr(self, "ident"):
            self.ident.set_lang(self.lang)

    def toggle_lang(self):
        self.set_lang(LANG_JA if self.lang == LANG_EN else LANG_EN)
        self.msg("pyxel.language_japanese" if self.lang == LANG_JA else "pyxel.language_english")

    def descend(self):
        self.p.depth += 1
        self.max_depth = max(getattr(self, "max_depth", 0), self.p.depth)
        self.tm, self.rooms = DGen.gen(self.p.depth)
        usable_rooms = self.usable_rooms()
        self.mons=[]; self.gitems=[]; self.traps={}; self.hidden_tiles={}
        self.visible=set(); self.explored=set()
        self.daemons.kill("rollwand")
        self.fuses.extinguish("swander")
        self.fuses.fuse("swander", RNG.spread(WANDERTIME), rogue_daemons.AFTER)
        self.wander_timer=self.fuses.remaining("swander")
        self.wander_between=0
        px,py = self.random_room_tile(RNG.choice(usable_rooms), WALKABLE)
        self.p.x,self.p.y = px,py
        sr=RNG.choice(usable_rooms); sx,sy=self.random_room_tile(sr, WALKABLE); self.tm[sy][sx]=T_STAIR
        self._spawn_mons(); self._spawn_items(); self._spawn_amulet()
        self._hide_secret_features(); self._spawn_traps()
        self._center_cam(); self.update_fov()

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

    def _center_cam(self):
        max_x = max(0, MAP_W - ZV_COLS)
        min_y = PLAY_Y_MIN
        max_y = max(min_y, PLAY_Y_MAX - ZV_ROWS + 1)
        self.cam_x = max(0, min(self.p.x - ZV_COLS//2, max_x))
        self.cam_y = max(min_y, min(self.p.y - ZV_ROWS//2, max_y))

    def _spawn_mons(self):
        # C: new_level.c:put_things()
        d=self.p.depth; n=RNG.randint(3,4+d)
        cands=[b for b in BESTIARY if b.min_depth<=d]
        if not cands: cands=[b for b in BESTIARY if b.min_depth<=3]
        rooms=self.usable_rooms()
        for _ in range(n):
            rm=RNG.choice(rooms); e=RNG.choice(cands)
            for _ in range(30):
                mx,my=self.random_room_tile(rm, WALKABLE)
                if self.tm[my][mx] in WALKABLE and not self.mon_at(mx,my) \
                   and not(mx==self.p.x and my==self.p.y):
                    monster=self.new_monster_from_spec(mx,my,e)
                    self.give_pack(monster)
                    self.mons.append(monster)
                    break

    def spawn_wanderer(self):
        # C: monsters.c:wanderer()
        cands=self.wanderer_floor_candidates()
        if not cands:
            return False
        x,y=RNG.choice(cands)
        spec=self.random_monster_spec(self.p.depth)
        monster=self.new_monster_from_spec(x,y,spec)
        self.mons.append(monster)
        self.runto(monster)
        return True

    def random_monster_spec(self, depth):
        return RNG.choice([b for b in BESTIARY if b.min_depth<=depth] or BESTIARY)

    def new_monster_from_spec(self,x,y,spec,depth=None):
        # C: monsters.c:new_monster()
        monster=Monster(
            x, y, spec.sym, spec.name, monster_hp(spec),
            spec.level, spec.armor, spec.damage, spec.exp, spec.flags
        )
        self.set_monster_disguise(monster,depth=depth)
        return monster

    def set_monster_disguise(self,m,depth=None):
        m.disguise = rogue_monsters.initial_disguise(m.sym, lambda: self.random_thing_sym(depth))

    def give_pack(self,m,depth=None):
        # C: monsters.c:give_pack()
        spec=self.monster_spec_for_sym(m.sym)
        depth = self.p.depth if depth is None else depth
        if not spec or depth < getattr(self, "max_depth", self.p.depth):
            return
        if RNG.rnd(100) < spec.carry:
            m.pack.append(make_item(depth))

    def wanderer_floor_candidates(self):
        player_room=self.room_containing(self.p.x,self.p.y)
        return [
            (x,y)
            for y,row in enumerate(self.tm)
            for x,tile in enumerate(row)
            if tile in (T_FLOOR,T_CORR)
            and (x,y)!=(self.p.x,self.p.y)
            and not self.mon_at(x,y)
            and self.room_containing(x,y) is not player_room
        ]

    def _spawn_items(self):
        # C: new_level.c:put_things()
        d=self.p.depth
        rooms=self.usable_rooms()
        if rogue_dungeon.should_place_treasure_room(RNG):
            self._spawn_treasure_room()
        for _ in range(RNG.randint(1,3)):
            rm=RNG.choice(rooms)
            for _ in range(20):
                ix,iy=self.random_room_tile(rm, {T_FLOOR,T_CORR})
                if self.tm[iy][ix] in (T_FLOOR,T_CORR) and not self.gi_at(ix,iy):
                    g=Item(CAT_GOLD,0); g.qty=RNG.randint(1,10)*d; g.x,g.y=ix,iy
                    self.gitems.append(g); break
        for _ in range(RNG.randint(2,4+d//3)):
            rm=RNG.choice(rooms)
            for _ in range(20):
                ix,iy=self.random_room_tile(rm, {T_FLOOR,T_CORR})
                if self.tm[iy][ix] in (T_FLOOR,T_CORR) and not self.gi_at(ix,iy):
                    it=make_item(d); it.x,it.y=ix,iy; self.gitems.append(it); break

    def _spawn_treasure_room(self, room=None):
        # Rogue 5.4.4 new_level.c:treas_room().
        rooms=self.usable_rooms()
        room = room or RNG.choice(rooms)
        inner_area=max(0,(room.w-2)*(room.h-2))
        treasure_count, monster_count = rogue_dungeon.treasure_room_counts(inner_area,RNG)
        for _ in range(treasure_count):
            for _ in range(2 * rogue_dungeon.MAXTRIES):
                ix,iy=self.random_room_tile(room,{T_FLOOR,T_CORR})
                if self.tm[iy][ix] in (T_FLOOR,T_CORR) and not self.gi_at(ix,iy) and not self.mon_at(ix,iy):
                    it=make_item(self.p.depth); it.x,it.y=ix,iy; self.gitems.append(it); break
        monster_depth=self.p.depth+1
        for _ in range(monster_count):
            for _ in range(rogue_dungeon.MAXTRIES):
                mx,my=self.random_room_tile(room,{T_FLOOR,T_CORR})
                if (self.tm[my][mx] in (T_FLOOR,T_CORR) and not self.gi_at(mx,my)
                        and not self.mon_at(mx,my) and (mx,my)!=(self.p.x,self.p.y)):
                    spec=self.random_monster_spec(monster_depth)
                    monster=self.new_monster_from_spec(mx,my,spec,depth=monster_depth)
                    monster.mean=True
                    self.give_pack(monster,depth=monster_depth)
                    self.mons.append(monster)
                    break

    def _spawn_amulet(self):
        # Rogue 5.4.4 new_level.c: level >= AMULETLEVEL && !amulet.
        if self.p.depth < AMULET_LEVEL or self.p.has_amulet:
            return
        if any(item.cat==CAT_AMULET for item in self.p.inv + self.gitems):
            return
        cands=[
            (x,y)
            for y,row in enumerate(self.tm)
            for x,tile in enumerate(row)
            if tile==T_FLOOR
            and (x,y)!=(self.p.x,self.p.y)
            and not self.gi_at(x,y)
            and not self.mon_at(x,y)
        ]
        if not cands:
            return
        x,y=RNG.choice(cands)
        amulet=Item(CAT_AMULET,0)
        amulet.x,amulet.y=x,y
        self.gitems.append(amulet)

    def _secret_chance(self, denom):
        # Rogue 5.4.4 passages.c: rnd(10)+1 < level, then a per-feature rnd().
        return rnd(10)+1 < self.p.depth and rnd(denom)==0

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
        if rnd(10) >= self.p.depth:
            return
        n=min(MAX_TRAPS,rnd(self.p.depth//4)+1)
        cands=[
            (x,y)
            for y,row in enumerate(self.tm)
            for x,tile in enumerate(row)
            if tile==T_FLOOR
            and (x,y)!=(self.p.x,self.p.y)
            and not self.gi_at(x,y)
            and not self.mon_at(x,y)
        ]
        RNG.shuffle(cands)
        for x,y in cands[:n]:
            self.traps[(x,y)]=rnd(len(TRAPS))

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
    def diag_ok(self,sx,sy,ex,ey):
        # C: chase.c:diag_ok()
        if not in_play_area(ex,ey):
            return False
        if sx==ex or sy==ey:
            return True
        return (
            in_play_area(sx,sy)
            and self.tm[ey][ex] in WALKABLE
            and self.tm[ey][sx] in WALKABLE
            and self.tm[sy][ex] in WALKABLE
        )
    def room_at(self,x,y):
        for r in self.rooms:
            if r.x<x<r.x+r.w-1 and r.y<y<r.y+r.h-1: return r
        return None
    def room_containing(self,x,y):
        # C: chase.c:roomin()
        for r in self.rooms:
            if r.x<=x<r.x+r.w and r.y<=y<r.y+r.h: return r
        return None
    def room_for_ai(self,x,y,actor=False):
        if not (0<=x<MAP_W and 0<=y<MAP_H):
            return None
        tile=self.tm[y][x]
        if tile==T_CORR or (actor and tile==T_DOOR):
            return "corridor"
        if tile==T_DOOR:
            return self.room_near_door(x,y) or "corridor"
        return self.room_containing(x,y)
    def room_near_door(self,x,y):
        for dx,dy in((-1,0),(1,0),(0,-1),(0,1)):
            r=self.room_at(x+dx,y+dy) or self.room_containing(x+dx,y+dy)
            if r: return r
        return None
    def room_exits(self,room):
        exits=[]
        for x in range(room.x,room.x+room.w):
            for y in (room.y,room.y+room.h-1):
                if 0<=x<MAP_W and 0<=y<MAP_H and self.tm[y][x]==T_DOOR:
                    exits.append((x,y))
        for y in range(room.y,room.y+room.h):
            for x in (room.x,room.x+room.w-1):
                if 0<=x<MAP_W and 0<=y<MAP_H and self.tm[y][x]==T_DOOR:
                    exits.append((x,y))
        return list(dict.fromkeys(exits))
    def dist2(self,a,b):
        # C: chase.c:dist()
        return (a[0]-b[0])*(a[0]-b[0])+(a[1]-b[1])*(a[1]-b[1])
    def same_ai_room(self,a,b):
        return a is not None and a==b
    def _append_msg(self, text):
        if len(getattr(self, "msg_turns", [])) != len(self.msgs):
            self.msg_turns = [self.turn] * len(self.msgs)
        self.msgs.append(text)
        self.msg_turns.append(self.turn)
        if len(self.msgs) > 100:
            drop = len(self.msgs) - 100
            self.msgs = self.msgs[drop:]
            self.msg_turns = self.msg_turns[drop:]
            self.turn_msg_start = max(0, self.turn_msg_start - drop)

    def msg(self,t,**kw):
        self._append_msg(TextCatalog.msg(self.lang,t,**kw))

    def msg_text(self,t):
        self._append_msg(t)

    def combat_monster_name(self,m,upper=False):
        name=TextCatalog.monster(self.lang,m.name)
        if self.lang==LANG_EN:
            name=f"the {name}"
            if upper:
                name=name[:1].upper()+name[1:]
        return name

    def combat_message(self,keys,**kw):
        return TextCatalog.msg(self.lang,keys[RNG.rnd(len(keys))],**kw)

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
        return TextCatalog.msg(self.lang,"fight.defeated_target",target=target)

    def thrown_hit_message(self,it,item,target):
        if it.cat==CAT_WPN:
            return TextCatalog.msg(self.lang,"fight.thrown_weapon_hits",item=item,target=target)
        return TextCatalog.msg(self.lang,"fight.you_hit_target",target=target)

    def thrown_miss_message(self,it,item,target):
        if it.cat==CAT_WPN:
            return TextCatalog.msg(self.lang,"fight.thrown_weapon_misses",item=item,target=target)
        return TextCatalog.msg(self.lang,"fight.you_missed_target",target=target)

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
                if 0<=nx<MAP_W and 0<=ny<MAP_H: self.visible.add((nx,ny))
        self.explored |= self.visible

    # ---------- Combat ----------
    def swing_hits(self, at_lvl, op_arm, wplus):
        # C: fight.c:swing()
        need = (20 - at_lvl) - op_arm
        return RNG.randrange(20) + wplus >= need

    def player_weapon_profile(self, weap=None, thrown=False):
        hplus = dplus = 0
        damage = "1d2"
        if weap and weap.cat == CAT_WPN:
            data = weap.data
            hplus += weap.hit_plus
            dplus += weap.dam_plus
            hplus += rogue_rings.weapon_hit_bonus(self.p, weap, thrown)
            dplus += rogue_rings.weapon_damage_bonus(self.p, weap, thrown)
            damage = data["damage"]
            if thrown:
                launcher = data.get("launcher")
                if data.get("missile") and launcher is not None and self.p.wpn and self.p.wpn.kind == launcher:
                    damage = data["hurl_damage"]
                    hplus += self.p.wpn.hit_plus
                    dplus += self.p.wpn.dam_plus
                elif launcher is None:
                    damage = data["hurl_damage"]
        return damage, hplus, dplus

    def roll_player_attack(self, m, weap=None, thrown=False):
        # C: fight.c:roll_em()
        damage_expr, hplus, dplus = self.player_weapon_profile(weap, thrown)
        if not m.running:
            hplus += 4
        hplus += self.p.str_hit_plus()
        did_hit = False
        total = 0
        for part in damage_expr.split("/"):
            if self.swing_hits(self.p.level, m.armor, hplus):
                total += max(0, roll_damage_expr(part) + dplus + self.p.str_dam_plus())
                did_hit = True
        return did_hit, total

    def roll_monster_attack(self, m):
        # C: fight.c:roll_em()
        hplus = 4 if self.p.stuck else 0
        did_hit = False
        total = 0
        for part in m.damage_expr.split("/"):
            if self.swing_hits(m.level, self.p.ac, hplus):
                total += roll_damage_expr(part)
                did_hit = True
        return did_hit, total

    def award_monster_kill(self, m, translated_name=None):
        # C: fight.c:killed()
        mn = translated_name or TextCatalog.monster(self.lang,m.name)
        self.p.exp+=m.exp
        if self.p.held_by is m:
            self.p.held_by=None
        if self.p.lvlup():
            self.msg("pyxel.welcome_to_level", level=self.p.level)
        self.remove_monster(m, was_kill=True)
        return mn

    def p_attack(self, m):
        # C: fight.c:fight()
        self.runto(m)
        if self.reveal_xeroc_for_attack(m, thrown=False):
            return
        mn=self.combat_monster_name(m)
        hit,dmg=self.roll_player_attack(m,self.p.wpn,False)
        if hit:
            m.hp-=dmg
            self.msg_text(self.player_hit_message(mn))
            if self.p.can_confuse_monster:
                self.p.can_confuse_monster=False
                m.confused=1
                self.msg("fight.your_hands_stop_glowing_color", color="red")
            if not m.alive:
                self.msg_text(self.defeated_message(mn))
                self.award_monster_kill(m,mn)
            elif m.confused>0:
                self.msg("fight.subject_appears_confused", subject=mn)
        else: self.msg_text(self.player_miss_message(mn))

    def reveal_xeroc_for_attack(self,m,thrown=False):
        # Rogue 5.4.4 fight.c:attack() reveals a disguised Xeroc; melee returns FALSE.
        if not rogue_monsters.is_disguised_xeroc(m) or self.p.blind>0:
            return False
        rogue_monsters.reveal_disguise(m)
        self.msg("fight.heavy_that_s_a_nasty_critter" if self.p.hallucinating>0 else "fight.wait_that_s_a_xeroc")
        return not thrown

    def monster_has_magic_item_to_steal(self):
        for it in self.p.inv:
            if it is self.p.wpn or it is self.p.arm or it is self.p.ring_l or it is self.p.ring_r:
                continue
            if it.cat in (CAT_POT, CAT_SCR, CAT_WPN, CAT_ARM, CAT_RING, CAT_STICK):
                return it
        return None

    def remove_monster(self,m,was_kill=False):
        # C: fight.c:remove_mon()
        if was_kill:
            for item in list(getattr(m, "pack", [])):
                pos=(m.x,m.y) if self.walkable(m.x,m.y) and not self.gi_at(m.x,m.y) else self.fall_position(m.x,m.y)
                if pos:
                    item.x,item.y=pos
                    self.gitems.append(item)
                m.pack.remove(item)
        else:
            m.pack=[]
        if m in self.mons:
            self.mons.remove(m)

    def runto(self,m,dest=DEST_PLAYER):
        # C: chase.c:runto()
        m.running=True; m.held=0; m.dest=dest

    def aggravate_monsters(self):
        # C: misc.c:aggravate()
        for mo in self.mons:
            mo.held=mo.scared=0
            self.runto(mo)

    def wake_monster(self,m):
        # C: monsters.c:wake_monster()
        if not m.alive:
            return
        if (not m.running and m.mean and m.held<=0 and rnd(3)!=0
                and not rogue_rings.is_wearing(self.p, rogue_rings.R_STEALTH)):
            self.runto(m)
        if (m.sym=="M" and m.running and not self.p.blind and not m.found
                and not rogue_monsters.is_cancelled(m)):
            m.found=True
            if not self.save_vs_magic():
                self.p.confused=max(self.p.confused,RNG.randint(15,25))
                mn=TextCatalog.monster(self.lang,m.name)
                self.msg("pyxel.monster_gaze_confused", monster=mn)
        if "steal_gold" in m.flags and not m.running:
            self.runto(m,DEST_GOLD if self.room_gold_target(m) else DEST_PLAYER)

    def wake_visible_monsters(self):
        for mo in self.mons:
            if (mo.x,mo.y) in self.visible:
                self.wake_monster(mo)

    def can_see_monster(self, m):
        # C: misc.c:cansee()
        return (rogue_monsters.FLAG_INVISIBLE not in m.flags
                or self.p.see_invisible > 0
                or rogue_rings.is_wearing(self.p, rogue_rings.R_SEEINVIS))

    def can_detect_monsters(self):
        return getattr(self.p, "see_monsters", 0) > 0

    def save_vs_magic(self):
        return rnd(20) < 7 + self.p.level//2

    def monster_save_throw(self, which, m):
        # Rogue 5.4.4 monsters.c:save_throw().
        return RNG.roll(1,20) >= 14 + which - m.level//2

    def m_attack(self,m):
        # C: fight.c:attack()
        mn=self.combat_monster_name(m,upper=True)
        hit,dmg=self.roll_monster_attack(m)
        if hit:
            if dmg:
                self.p.hp-=dmg
            self.msg_text(self.monster_hit_message(mn))
            if self.p.hp<=0 and not self.death_cause: self.death_cause=f"killed by a {m.name}"
            if not rogue_monsters.is_cancelled(m):
                if "rust" in m.flags and self.can_rust_armor(self.p.arm):
                    self.rust_armor()
                if "steal_gold" in m.flags and self.p.gold>0:
                    s=min(self.p.gold,RNG.randint(10,50)+RNG.randint(10,50))
                    self.p.gold-=s; self.msg("fight.your_purse_feels_lighter")
                    self.remove_monster(m); return
                if ("poison" in m.flags and not rogue_rings.is_wearing(self.p, rogue_rings.R_SUSTSTR)
                        and not self.save_vs_poison() and self.p.st>3):
                    self.p.st-=1; self.msg("pyxel.feel_weaker")
                if "drain_level" in m.flags and rnd(100)<15:
                    if self.p.level>1:
                        self.p.level-=1; self.p.exp=max(0,self.p.EXP_T[self.p.level-1])
                    self.p.max_hp=max(1,self.p.max_hp-roll("1d10"))
                    self.p.hp=max(1,min(self.p.hp,self.p.max_hp)); self.msg("fight.you_suddenly_feel_weaker")
                if "drain" in m.flags and rnd(100)<30:
                    loss=roll("1d3")
                    self.p.max_hp=max(1,self.p.max_hp-loss)
                    self.p.hp=max(1,min(self.p.hp-loss,self.p.max_hp)); self.msg("fight.you_suddenly_feel_weaker")
                if "confuse" in m.flags and not self.save_vs_magic():
                    self.p.confused=RNG.randint(10,20); self.msg("pyxel.feel_confused_bang")
                if "freeze" in m.flags:
                    self.p.no_command+=rnd(2)+2
                    if self.p.no_command>BORE_LEVEL:
                        self.p.hp=0; self.death_cause="hypothermia"
                    self.msg("fight.you_are_frozen")
                if "hold" in m.flags:
                    m.vf_hit+=1
                    self.p.held_by=m
                    self.p.hp-=1
                    if self.p.hp<=0 and not self.death_cause: self.death_cause=f"killed by a {m.name}"
                if "steal_item" in m.flags:
                    t=self.monster_has_magic_item_to_steal()
                    if t:
                        self.p.rm_item(t); self.msg("pyxel.she_stole_item", item=self.ident.name(t))
                        self.remove_monster(m); return
        else: self.msg_text(self.monster_miss_message(mn))

    def m_turn(self,m):
        # C: chase.c (monster turn loop)
        if not m.alive: return
        if not m.running: return
        self.move_monst(m)
        if m.alive and "fly" in m.flags and self.dist2((m.x,m.y),(self.p.x,self.p.y))>=3:
            self.move_monst(m)

    def move_monst(self,m):
        # C: chase.c:move_monst()
        if m.held>0: m.held-=1; return
        for _ in range(rogue_monsters.chase_steps_for_turn(m)):
            if self.do_chase(m)==-1:
                return
        rogue_monsters.finish_chase_turn(m)

    def do_chase(self,m):
        # C: chase.c:do_chase()
        dest=self.find_dest(m)
        rer=self.room_for_ai(m.x,m.y,actor=True)
        ree=self.room_for_ai(dest[0],dest[1],actor=False)
        chase_dest=dest
        if rer!=ree and hasattr(rer,"x"):
            exits=self.room_exits(rer)
            if exits:
                chase_dest=min(exits,key=lambda p:self.dist2(p,dest))
        moved_or_attack=self.chase(m,chase_dest)
        if moved_or_attack=="attack":
            return 0
        if m.dest!=DEST_PLAYER and (m.x,m.y)==dest:
            self.collect_monster_dest(m,dest)
        return 0

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
        if "steal_gold" in m.flags and m.dest==DEST_GOLD:
            target=self.room_gold_target(m)
            if target:
                return target
            m.dest=DEST_PLAYER
        return (self.p.x,self.p.y)

    def collect_monster_dest(self,m,dest):
        gi=self.gi_at(*dest)
        if gi and gi.cat==CAT_GOLD:
            self.gitems.remove(gi)
            m.dest=DEST_PLAYER

    def random_monster_move(self,m):
        # C: chase.c:rndmove()
        dirs=list(DIR8.values())+[(0,0)]
        RNG.shuffle(dirs)
        for dx,dy in dirs:
            nx,ny=m.x+dx,m.y+dy
            if dx==dy==0:
                return (m.x,m.y)
            if self.can_monster_step(m,nx,ny) and self.diag_ok(m.x,m.y,nx,ny):
                return (nx,ny)
        return (m.x,m.y)

    def can_monster_step(self,m,x,y):
        if (x,y)==(self.p.x,self.p.y):
            return True
        if not self.walkable(x,y) or self.mon_at(x,y):
            return False
        gi=self.gi_at(x,y)
        return not (gi and self.is_scare_monster(gi))

    def chase(self,m,dest):
        # C: chase.c:chase()
        px,py=self.p.x,self.p.y
        if m.scared>0:
            m.scared-=1
            dx=-1 if m.x<px else 1 if m.x>px else 0
            dy=-1 if m.y<py else 1 if m.y>py else 0
            if dx and dy:
                if RNG.random()<.5: dx=0
                else: dy=0
            nx,ny=m.x+dx,m.y+dy
            if self.walkable(nx,ny) and not self.mon_at(nx,ny) and not(nx==px and ny==py):
                m.x,m.y=nx,ny
            return
        if "regen" in m.flags and not rogue_monsters.is_cancelled(m) and m.hp<m.max_hp and RNG.random()<.3: m.hp+=1
        if (m.confused>0 and rnd(5)!=0) or (m.sym=="P" and rnd(5)==0) or (m.sym=="B" and rnd(2)==0):
            nx,ny=self.random_monster_move(m)
            if (nx,ny)==(px,py):
                self.m_attack(m); return "attack"
            m.x,m.y=nx,ny
            if m.confused>0 and rnd(20)==0: m.confused=0
            return "move"
        cur=self.dist2((m.x,m.y),dest)
        best=(m.x,m.y); bestd=cur; ties=1
        for dx,dy in DIR8.values():
            nx,ny=m.x+dx,m.y+dy
            if not self.diag_ok(m.x,m.y,nx,ny):
                continue
            if (nx,ny)==(px,py):
                if dest==(px,py):
                    self.m_attack(m); return "attack"
                continue
            if not self.can_monster_step(m,nx,ny):
                continue
            d=self.dist2((nx,ny),dest)
            if d<bestd:
                best=(nx,ny); bestd=d; ties=1
            elif d==bestd and best!=(m.x,m.y) and rnd(ties+1)==0:
                best=(nx,ny); ties+=1
        if best!=(m.x,m.y):
            m.x,m.y=best
        return "move"

    # ---------- Item effects ----------
    def use_pot(self,it):
        # C: potions.c:quaff()
        p=self.p; nm=POTIONS[it.kind]["name"]
        if nm=="healing":
            self.ident.pk[it.kind]=True
            h=max(1,roll("1d4")*p.level)
            p.hp += h
            if p.hp > p.max_hp:
                p.max_hp += 1
                p.hp = p.max_hp
            self.sight()
            self.msg("potions.you_begin_to_feel_better")
        elif nm=="extra healing":
            self.ident.pk[it.kind]=True
            h=max(1,roll("1d8")*p.level)
            p.hp += h
            if p.hp > p.max_hp:
                if p.hp > p.max_hp + p.level + 1:
                    p.max_hp += 1
                p.max_hp += 1
                p.hp = p.max_hp
            self.sight()
            self.come_down()
            self.msg("potions.you_begin_to_feel_much_better")
        elif nm=="poison":
            self.ident.pk[it.kind]=True
            if rogue_rings.is_wearing(p, rogue_rings.R_SUSTSTR):
                self.msg("potions.you_feel_momentarily_sick")
            else:
                l=RNG.randint(1,3); p.st=max(1,p.st-l); self.msg("potions.you_feel_very_sick_now")
                self.come_down()
        elif nm=="gain strength":
            self.ident.pk[it.kind]=True; p.st=min(p.st+1,31); p.max_st=max(p.max_st,p.st); self.msg("potions.you_feel_stronger_now_what_bulging_muscles")
        elif nm=="restore strength":
            # Rogue 5.4.4 potions.c:P_RESTORE temporarily removes R_ADDSTR before restoring max_stats.s_str.
            addstr = sum(r.ench for r in (p.ring_l, p.ring_r) if rogue_rings.is_ring(r, rogue_rings.R_ADDSTR))
            base_max = p.max_st - addstr
            base_st = p.st - addstr
            if base_st < base_max:
                base_st = base_max
            p.st = max(3, min(31, base_st + addstr))
            self.msg("potions.hey_this_tastes_great_it_make_you_feel_warm_all_over")
        elif nm=="confusion":
            if not self.ident.pk[it.kind]:
                self.ident.pk[it.kind]=p.hallucinating <= 0
            duration = RNG.spread(HUHDURATION)
            if p.confused > 0:
                self.fuses.lengthen("unconfuse", duration)
            else:
                self.fuses.fuse("unconfuse", duration, rogue_daemons.AFTER)
            p.confused += duration
            self.msg("potions.what_a_tripy_feeling" if p.hallucinating > 0 else "potions.wait_what_s_going_on_here_huh_what_who")
        elif nm=="hallucination":
            self.ident.pk[it.kind]=True
            duration = RNG.spread(SEEDURATION)
            if p.hallucinating > 0:
                self.fuses.lengthen("come_down", duration)
            else:
                if p.see_monsters > 0:
                    p.see_monsters = 0
                self.fuses.fuse("come_down", duration, rogue_daemons.AFTER)
            p.hallucinating += duration
            self.msg("potions.oh_wow_everything_seems_so_cosmic")
        elif nm=="blindness":
            self.ident.pk[it.kind]=True
            duration = RNG.spread(SEEDURATION)
            if p.blind > 0:
                self.fuses.lengthen("sight", duration)
            else:
                self.fuses.fuse("sight", duration, rogue_daemons.AFTER)
            p.blind += duration
            self.msg("potions.oh_bummer_everything_is_dark_help" if p.hallucinating > 0 else "potions.a_cloak_of_darkness_falls_around_you")
        elif nm=="haste self":
            self.ident.pk[it.kind]=True
            if self.add_haste(True):
                self.msg("potions.you_feel_yourself_moving_much_faster")
        elif nm=="see invisible":
            duration = RNG.spread(SEEDURATION)
            if p.see_invisible > 0:
                self.fuses.lengthen("unsee", duration)
            else:
                self.fuses.fuse("unsee", duration, rogue_daemons.AFTER)
            p.see_invisible += duration
            self.msg("potions.this_potion_tastes_like_item_juice", item="slime-mold")
            if p.blind > 0:
                p.blind = 0
                self.update_fov()
                self.msg("daemons.the_veil_of_darkness_lifts")
        elif nm=="raise level":
            self.ident.pk[it.kind]=True
            p.exp=p.EXP_T[min(p.level,len(p.EXP_T)-1)] + 1; p.lvlup()
            self.msg("potions.you_suddenly_feel_much_more_skillful")
        elif nm=="monster detection":
            if p.see_monsters > 0:
                self.fuses.lengthen("turn_see", HUHDURATION)
                p.see_monsters += HUHDURATION
            else:
                self.fuses.fuse("turn_see", HUHDURATION, rogue_daemons.AFTER)
                p.see_monsters = HUHDURATION
            if self.mons:
                self.msg("pyxel.sense_monsters")
            else:
                self.msg("potions.you_have_a_item_feeling_for_a_moment_then_it_passes",
                         item="normal" if p.hallucinating > 0 else "strange")
        elif nm=="magic detection":
            found = False
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
            self.ident.pk[it.kind]=True
            duration = RNG.spread(HEALTIME)
            if p.levitating > 0:
                self.fuses.lengthen("land", duration)
            else:
                self.fuses.fuse("land", duration, rogue_daemons.AFTER)
            p.levitating += duration
            self.msg("potions.you_start_to_float_in_the_air")
        p.rm_item(it)

    def add_haste(self, potion=True):
        # Rogue 5.4.4 misc.c:add_haste() and daemons.c:nohaste().
        if self.p.haste > 0:
            self.p.no_command += rnd(8)
            self.p.haste = 0
            self.haste_half_turn = False
            self.fuses.extinguish("nohaste")
            self.msg("misc.you_faint_from_exhaustion")
            return False
        self.p.haste = 1
        self.haste_half_turn = False
        if potion:
            duration = rnd(4) + 4
            self.p.haste = duration
            self.fuses.fuse("nohaste", duration, rogue_daemons.AFTER)
        return True

    def nohaste(self):
        # C: daemons.c:nohaste()
        self.p.haste = 0
        self.haste_half_turn = False
        self.msg("daemons.you_feel_yourself_slowing_down")

    def come_down(self):
        # C: daemons.c:come_down()
        if self.p.hallucinating <= 0:
            return
        self.p.hallucinating = 0
        self.msg("daemons.everything_looks_so_boring_now")

    def land(self):
        # C: daemons.c:land()
        self.p.levitating = 0
        self.msg("daemons.you_float_gently_to_the_ground")

    def unconfuse(self):
        # C: daemons.c:unconfuse()
        self.p.confused = 0
        self.msg("daemons.you_feel_less_value_now", value="trippy" if self.p.hallucinating > 0 else "confused")

    def sight(self):
        # C: daemons.c:sight()
        if self.p.blind <= 0:
            return
        self.p.blind = 0
        self.update_fov()
        self.msg("daemons.far_out_everything_is_all_cosmic_again" if self.p.hallucinating > 0 else "daemons.the_veil_of_darkness_lifts")

    def is_magic_item(self, it):
        # Rogue 5.4.4 potions.c:is_magic().
        if it.cat in (CAT_POT, CAT_SCR, CAT_RING, CAT_STICK, CAT_AMULET):
            return True
        if it.cat == CAT_WPN:
            return it.hit_plus != 0 or it.dam_plus != 0
        if it.cat == CAT_ARM:
            return it.protected or it.ench != 0
        return False

    def set_know(self, it):
        # Rogue 5.4.4 wizard.c:set_know().
        # Sets type-level oi_know, clears oi_guess, sets instance ISKNOW flag.
        if it.cat == CAT_POT:
            self.ident.pk[it.kind] = True
            self.ident.pg[it.kind] = None
            it.known = True
            return True
        if it.cat == CAT_SCR:
            self.ident.sk[it.kind] = True
            self.ident.sg[it.kind] = None
            it.known = True
            return True
        if it.cat == CAT_WPN or it.cat == CAT_ARM:
            it.known = True
            return True
        if it.cat == CAT_RING:
            self.ident.rk[it.kind] = True
            self.ident.rg[it.kind] = None
            it.known = True
            return True
        if it.cat == CAT_STICK:
            self.ident.wk[it.kind] = True
            self.ident.wg[it.kind] = None
            it.known = True
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

    def _disc_lines(self):
        # things.c:print_disc(*) — 全カテゴリの発見済みアイテム名を (color, text) リストで返す
        nothing = TextCatalog.msg(self.lang, "misc.nothing_discovered")
        lang = self.lang
        result = []

        def section(label, cat, table, known_arr, guess_arr):
            result.append((27, f"-- {label} --"))
            found = 0
            for i in range(len(table)):
                if known_arr[i] or (guess_arr[i] is not None):
                    dummy = Item(cat, i, known=known_arr[i])
                    result.append((9, self.ident.name(dummy)))
                    found += 1
            if found == 0:
                result.append((5, nothing))

        section("Potions" if lang == LANG_EN else "水薬",   CAT_POT,   POTIONS, self.ident.pk, self.ident.pg)
        result.append((0, ""))
        section("Scrolls" if lang == LANG_EN else "巻き物", CAT_SCR,   SCROLLS, self.ident.sk, self.ident.sg)
        result.append((0, ""))
        section("Rings"   if lang == LANG_EN else "指輪",   CAT_RING,  RINGS,   self.ident.rk, self.ident.rg)
        result.append((0, ""))
        section("Sticks"  if lang == LANG_EN else "杖",     CAT_STICK, STICKS,  self.ident.wk, self.ident.wg)
        return result

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
        if nm == "identify potion":
            return (CAT_POT,)
        if nm == "identify scroll":
            return (CAT_SCR,)
        if nm == "identify weapon":
            return (CAT_WPN,)
        if nm == "identify armor":
            return (CAT_ARM,)
        if nm == "identify ring, wand or staff":
            return (CAT_RING, CAT_STICK)
        return ()

    def use_scr(self,it):
        # C: scrolls.c:read_scroll()
        p=self.p; nm=SCROLLS[it.kind]["name"]; self.ident.sk[it.kind]=nm not in ("monster confusion","scare monster","food detection","teleportation","enchant weapon","create monster","remove curse","aggravate monsters","protect armor","hold monster","enchant armor")
        if nm=="monster confusion":
            p.can_confuse_monster=True
            self.msg("scrolls.your_hands_begin_to_glow_color", color="red")
        elif nm.startswith("identify "):
            cats = self.identify_scroll_target_cats(nm)
            self.msg("scrolls.this_scroll_is_an_item_scroll", item=nm)
            unid=[i for i in p.inv if i.cat in cats and self.needs_identify(i)]
            if unid:
                # Interactive target selection (Rogue 5.4.4 wizard.c:whatis()).
                self.fitems=unid; self.icur=0; self.cact="Identify"; self.st=ST_ITEM
                return True  # Caller must NOT call close_menu()/end_turn() yet.
            else:
                self.msg("pyxel.feel_vaguely_uneasy")
        elif nm=="enchant weapon":
            if p.wpn:
                p.wpn.cursed=False
                if RNG.randrange(2)==0: p.wpn.hit_plus+=1
                else: p.wpn.dam_plus+=1
                p.wpn.ench=p.wpn.hit_plus
                self.msg("scrolls.your_color_glows_color2_for_a_moment", color=p.wpn.data["name"], color2="blue")
            else: self.msg("scrolls.you_feel_a_strange_sense_of_loss")
        elif nm=="enchant armor":
            if p.arm:
                p.arm.ench+=1; p.arm.cursed=False; p.recalc_ac(); self.msg("scrolls.your_armor_glows_color_for_a_moment", color="silver")
            else: self.msg("scrolls.you_feel_a_strange_sense_of_loss")
        elif nm=="remove curse":
            for i in (p.wpn,p.arm,p.ring_l,p.ring_r):
                if i and i.cursed:
                    i.cursed=False
            self.msg("scrolls.you_feel_in_touch_with_the_universal_onenes" if p.hallucinating > 0 else "scrolls.you_feel_as_if_somebody_is_watching_over_you")
        elif nm=="aggravate monsters":
            self.aggravate_monsters(); self.msg("scrolls.you_hear_a_high_pitched_humming_noise")
        elif nm=="scare monster":
            for mo in self.mons:
                if abs(mo.x-p.x)+abs(mo.y-p.y)<=6: mo.scared=RNG.randint(10,20)
            self.msg("scrolls.you_hear_maniacal_laughter_in_the_distance")
        elif nm=="sleep":
            p.no_command+=rnd(SLEEPTIME)+4; self.dashing=False; self.msg("scrolls.you_fall_asleep")
        elif nm=="teleportation":
            old_room = self.room_at(p.x, p.y)
            r=RNG.choice(self.usable_rooms()); p.x,p.y=self.random_room_tile(r, WALKABLE); self.update_fov(); self._center_cam()
            if old_room is not self.room_at(p.x, p.y):
                self.ident.sk[it.kind]=True
            self.finish_teleport()
        elif nm=="create monster":
            pick=None
            count=0
            for dy in (-1,0,1):
                for dx in (-1,0,1):
                    if dx==0 and dy==0:
                        continue
                    nx,ny=p.x+dx,p.y+dy
                    if self.walkable(nx,ny) and not self.mon_at(nx,ny):
                        gi=self.gi_at(nx,ny)
                        if gi and self.is_scare_scroll(gi):
                            continue
                        count += 1
                        if RNG.rnd(count) == 0:
                            pick = (nx, ny)
            if pick:
                nx,ny=pick
                cs=[b for b in BESTIARY if b.min_depth<=p.depth]
                if cs:
                    e=RNG.choice(cs)
                    self.mons.append(self.new_monster_from_spec(nx,ny,e))
                    if rogue_rings.is_wearing(p, rogue_rings.R_AGGR):
                        self.runto(self.mons[-1])
            else:
                self.msg("scrolls.you_hear_a_faint_cry_of_anguish_in_the_distance")
        elif nm=="magic mapping":
            for (x,y),tile in list(self.hidden_tiles.items()):
                self.tm[y][x]=tile
                self.explored.add((x,y))
                self.hidden_tiles.pop((x,y),None)
            for x,y in self.traps:
                self.tm[y][x]=T_TRAP
                self.explored.add((x,y))
            for y in range(MAP_H):
                for x in range(MAP_W):
                    if self.tm[y][x]!=T_VOID: self.explored.add((x,y))
            self.msg("scrolls.oh_now_this_scroll_has_a_map_on_it")
        elif nm=="hold monster":
            held_count = 0
            for mo in self.mons:
                if abs(mo.x-p.x)<=2 and abs(mo.y-p.y)<=2 and mo.running:
                    mo.running = False
                    mo.held=RNG.randint(10,20)
                    held_count += 1
            if held_count:
                self.ident.sk[it.kind]=True
                self.msg("scrolls.the_monster_freezes" if held_count == 1 else "scrolls.the_monsters_around_you_freeze")
            else:
                self.msg("scrolls.you_feel_a_strange_sense_of_loss")
        elif nm=="food detection":
            found=False
            for gi in self.gitems:
                if gi.cat==CAT_FOOD:
                    self.visible.add((gi.x,gi.y))
                    self.explored.add((gi.x,gi.y))
                    found=True
            if found:
                self.ident.sk[it.kind]=True
                self.msg("scrolls.your_nose_tingles_and_you_smell_food")
            else:
                self.msg("scrolls.your_nose_tingles")
        elif nm=="protect armor":
            if p.arm:
                p.arm.protected=True
                self.msg("scrolls.your_armor_is_covered_by_a_shimmering_color_shield", color="gold")
            else:
                self.msg("scrolls.you_feel_a_strange_sense_of_loss")
        elif nm=="blank paper": self.msg("pyxel.scroll_is_blank")
        p.rm_item(it)

    def first_zap_target(self, dx, dy):
        x,y=self.p.x,self.p.y
        for _ in range(max(MAP_W,MAP_H)):
            nx,ny=x+dx,y+dy
            if not (0<=nx<MAP_W and 0<=ny<MAP_H):
                return None
            m=self.mon_at(nx,ny)
            if m:
                return m
            if not self.walkable(nx,ny):
                return None
            x,y=nx,ny
        return None

    def monster_spec_for_sym(self, sym):
        for spec in BESTIARY:
            if spec.sym == sym:
                return spec
        return None

    def set_monster_from_spec(self, m, spec):
        # Rogue 5.4.4 monsters.c:new_monster() rebuilds monster stats from monsters[].
        lev_add=max(0,self.p.depth-AMULET_LEVEL)
        level=spec.level+lev_add
        m.sym=spec.sym; m.name=spec.name
        m.level=level; m.armor=spec.armor-lev_add
        m.damage_expr=spec.damage; m.exp=spec.exp+lev_add*10
        m.hp=m.max_hp=max(1,RNG.roll(level,8))
        m.flags=set(spec.flags.split(",")) if spec.flags else set()
        m.pack=[]
        m.held=m.scared=m.confused=0
        m.running=False; m.dest=DEST_PLAYER; m.turn=True
        m.mean=True; m.target=False; m.found=False; m.vf_hit=0
        self.set_monster_disguise(m)
        if self.p.depth>29:
            m.flags.add(rogue_monsters.FLAG_HASTE)
        if rogue_rings.is_wearing(self.p, rogue_rings.R_AGGR):
            self.runto(m)

    def clear_player_hold(self):
        # Rogue 5.4.4 wizard.c:teleport() clears ISHELD/vf_hit after teleporting.
        if self.p.held_by is not None:
            self.p.held_by.vf_hit = 0
            self.p.held_by = None

    def finish_teleport(self):
        # Rogue 5.4.4 wizard.c:teleport() clears ISHELD/vf_hit, no_move, count, running.
        self.clear_player_hold()
        self.p.no_move = 0
        self.dashing = False
        self.dash_steps = 0

    def polymorph_monster(self,m):
        # C: sticks.c (WS_POLYMORPH)
        spec=self.monster_spec_for_sym(chr(RNG.rnd(26)+ord("A")))
        if spec:
            self.set_monster_from_spec(m,spec)

    def random_monster_floor(self,avoid=None):
        avoid=set(avoid or ())
        cands=[
            (x,y)
            for y,row in enumerate(self.tm)
            for x,tile in enumerate(row)
            if tile in (T_FLOOR,T_CORR)
            and (x,y) not in avoid
            and (x,y)!=(self.p.x,self.p.y)
            and not self.mon_at(x,y)
        ]
        return RNG.choice(cands) if cands else None

    def relocate_monster(self,m,pos):
        # C: chase.c:relocate()
        if pos and self.walkable(pos[0],pos[1]) and not self.mon_at(pos[0],pos[1]):
            m.x,m.y=pos

    def cancel_monster(self,m):
        # C: sticks.c (WS_CANCEL)
        m.flags.add(rogue_monsters.FLAG_CANCELLED)
        m.flags.discard(rogue_monsters.FLAG_INVISIBLE)
        m.flags.discard(rogue_monsters.FLAG_CAN_CONFUSE)
        rogue_monsters.reveal_disguise(m)
        if self.p.held_by is m:
            self.p.held_by=None
        m.vf_hit=0

    def drain_targets(self):
        proom=self.room_for_ai(self.p.x,self.p.y,actor=True)
        if proom=="corridor":
            return [m for m in self.mons if m.alive and abs(m.x-self.p.x)<=1 and abs(m.y-self.p.y)<=1]
        return [m for m in self.mons if m.alive and self.same_ai_room(self.room_for_ai(m.x,m.y,actor=True),proom)]

    def drain_life(self):
        if self.p.hp < 2:
            self.msg("sticks.you_are_too_weak_to_use_it")
            return False
        targets=self.drain_targets()
        if not targets:
            self.msg("sticks.you_have_a_tingling_feeling")
            return True
        self.p.hp//=2
        dmg=self.p.hp//len(targets)
        for m in list(targets):
            m.hp-=dmg
            if m.alive:
                self.runto(m)
            else:
                self.award_monster_kill(m)
        return True

    def hit_monster_with_magic_missile(self,m):
        self.runto(m)
        dmg=max(0,RNG.roll(1,4)+1+self.p.str_dam_plus())
        m.hp-=dmg
        self.msg_text(self.thrown_hit_message(Item(CAT_STICK, rogue_sticks.WS_MISSILE), "magic missile", self.combat_monster_name(m)))
        if not m.alive:
            self.msg_text(self.defeated_message(self.combat_monster_name(m)))
            self.award_monster_kill(m)

    def bolt_name(self, kind):
        if kind == rogue_sticks.WS_ELECT:
            return "bolt"
        if kind == rogue_sticks.WS_FIRE:
            return "flame"
        return "ice"

    def bolt_bounces_at(self, x, y):
        return (not in_play_area(x, y)) or self.tm[y][x] in (T_VOID, T_HWALL, T_VWALL, T_DOOR)

    def hit_monster_with_bolt(self, m, name):
        dmg=RNG.roll(6,6)
        m.hp-=dmg
        self.runto(m)
        self.msg_text(self.thrown_hit_message(Item(CAT_STICK, rogue_sticks.WS_FIRE), name, self.combat_monster_name(m)))
        if not m.alive:
            self.msg_text(self.defeated_message(self.combat_monster_name(m)))
            self.award_monster_kill(m)

    def fire_bolt(self, dx, dy, name):
        # Rogue 5.4.4 sticks.c:fire_bolt() bounces from walls/doors and uses 6x6 damage.
        x,y=self.p.x,self.p.y
        hit_hero=False
        changed=False
        steps=0
        bounces=0
        while steps < BOLT_LENGTH and bounces < BOLT_LENGTH * 2:
            x+=dx; y+=dy
            if self.bolt_bounces_at(x,y):
                if not changed:
                    hit_hero=not hit_hero
                changed=False
                dx=-dx; dy=-dy
                bounces+=1
                self.msg("sticks.the_value_bounces", value=name)
                continue
            steps+=1
            target=self.mon_at(x,y)
            if target and not hit_hero:
                hit_hero=True
                changed=not changed
                if not self.monster_save_throw(VS_MAGIC,target):
                    if target.sym=="D" and name=="flame":
                        self.msg("sticks.the_flame_bounces")
                    else:
                        self.hit_monster_with_bolt(target,name)
                    return True
                self.runto(target)
                self.msg("sticks.the_value_whizzes_past_value2", value=name, value2=self.combat_monster_name(target))
            elif hit_hero and (x,y)==(self.p.x,self.p.y):
                hit_hero=False
                changed=not changed
                if not self.save_vs_magic():
                    self.p.hp-=RNG.roll(6,6)
                    if self.p.hp<=0 and not self.death_cause:
                        self.death_cause=f"killed by a {name}"
                    self.msg("sticks.you_are_hit_by_the_value", value=name)
                    return True
                self.msg("sticks.the_value_whizzes_by_you", value=name)
        return False

    def zap_stick(self,it,dx,dy):
        # C: sticks.c:do_zap()
        if it.cat != CAT_STICK:
            self.msg("sticks.you_cant_zap_with_that")
            return False
        if it.charges <= 0:
            self.msg("sticks.nothing_happens")
            return True
        kind=it.kind
        if kind == rogue_sticks.WS_LIGHT:
            self.ident.wk[kind]=True
            room=self.room_at(self.p.x,self.p.y) or self.room_containing(self.p.x,self.p.y)
            if room and room.usable and room.is_dark:
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
            target=self.first_zap_target(dx,dy)
            if target and not self.monster_save_throw(VS_MAGIC,target):
                self.hit_monster_with_magic_missile(target)
            else:
                self.msg("sticks.the_missle_vanishes_with_a_puff_of_smoke")
        elif kind in (rogue_sticks.WS_ELECT, rogue_sticks.WS_FIRE, rogue_sticks.WS_COLD):
            self.ident.wk[kind]=True
            self.fire_bolt(dx,dy,self.bolt_name(kind))
        else:
            target=self.first_zap_target(dx,dy)
            if target:
                if target.sym=="F" and self.p.held_by is target:
                    self.p.held_by=None
                if kind == rogue_sticks.WS_INVIS:
                    target.flags.add(rogue_monsters.FLAG_INVISIBLE)
                elif kind == rogue_sticks.WS_POLYMORPH:
                    self.polymorph_monster(target)
                elif kind == rogue_sticks.WS_CANCEL:
                    self.cancel_monster(target)
                elif kind == rogue_sticks.WS_HASTE_M:
                    rogue_monsters.haste_monster(target)
                    self.runto(target)
                elif kind == rogue_sticks.WS_SLOW_M:
                    rogue_monsters.slow_monster(target)
                    self.runto(target)
                elif kind == rogue_sticks.WS_TELAWAY:
                    self.runto(target)
                    self.relocate_monster(target,self.random_monster_floor({(target.x,target.y)}))
                elif kind == rogue_sticks.WS_TELTO:
                    self.runto(target)
                    self.relocate_monster(target,(self.p.x+dx,self.p.y+dy))
                else:
                    self.runto(target)
        it.charges-=1
        return True

    def eat(self,it):
        # C: misc.c:eat()
        self.p.food=min(STOMACHSIZE,max(self.p.food,0)+HUNGERTIME-200+RNG.randrange(400))
        self.p.state="normal"
        self.msg("pyxel.eat_item_yum", item=it.data["name"]); self.p.rm_item(it)

    def wield(self,it):
        # C: weapons.c:wield()
        if self.p.wpn and self.p.wpn.cursed: self.msg("pyxel.cant_let_go"); return
        self.p.wpn=it; self.msg("pyxel.wield_item", item=self.ident.name(it))

    def wear(self,it):
        # C: armor.c:wear()
        if self.p.arm:
            msg = (
                TextCatalog.msg(self.lang, "armor.you_are_already_wearing_some")
                + TextCatalog.msg(self.lang, "armor.you_ll_have_to_take_it_off_first")
            )
            self.msg_text(msg)
            return
        it.known=True
        self.p.arm=it; self.p.recalc_ac(); self.msg("pyxel.put_on_item", item=self.ident.name(it))

    def put_on_ring(self,it):
        # C: rings.c:ring_on()
        if self.p.ring_l is not None and self.p.ring_r is not None:
            self.msg("pyxel.already_ring_each_hand")
            return
        if rogue_rings.put_on_ring(self.p,it):
            self.p.recalc_ac()
            if it.kind == rogue_rings.R_AGGR:
                self.aggravate_monsters()
            if it.kind in (rogue_rings.R_PROTECT, rogue_rings.R_ADDSTR,
                           rogue_rings.R_ADDHIT, rogue_rings.R_ADDDAM):
                self.ident.rk[it.kind]=True
            self.msg("pyxel.now_wearing_item", item=self.ident.name(it))

    def takeoff(self,it):
        # C: armor.c:take_off()
        if it is self.p.arm:
            if it.cursed: self.msg("pyxel.its_cursed"); return
            self.p.arm=None; self.p.recalc_ac()
        elif it is self.p.wpn:
            if it.cursed: self.msg("pyxel.its_cursed"); return
            self.p.wpn=None
        elif it is self.p.ring_l or it is self.p.ring_r:
            if not rogue_rings.remove_ring(self.p,it):
                self.msg("pyxel.cant_appears_cursed")
                return
            self.p.recalc_ac()
        self.msg("pyxel.remove_item", item=self.ident.name(it))

    def drop(self,it):
        # C: things.c:drop()
        if (it is self.p.wpn or it is self.p.arm or it is self.p.ring_l or it is self.p.ring_r) and it.cursed:
            self.msg("pyxel.its_cursed"); return
        self.p.rm_item(it); it.x,it.y=self.p.x,self.p.y
        self.gitems.append(it); self.msg("pyxel.drop_item", item=self.ident.name(it))

    def is_scare_monster(self,it):
        return it.cat==CAT_SCR and SCROLLS[it.kind]["name"]=="scare monster"

    def fall_position(self,x,y):
        choice=None; cnt=0
        for yy in range(y-1,y+2):
            for xx in range(x-1,x+2):
                if (xx,yy)==(self.p.x,self.p.y): continue
                if not (0<=xx<MAP_W and 0<=yy<MAP_H): continue
                if not self.walkable(xx,yy) or self.tm[yy][xx]==T_DOOR: continue
                if self.mon_at(xx,yy) or self.gi_at(xx,yy): continue
                cnt+=1
                if RNG.randrange(cnt)==0:
                    choice=(xx,yy)
        return choice

    def drop_thrown(self,it,x,y,around=True):
        # C: weapons.c:fall()
        pos=self.fall_position(x,y) if around else None
        pos=pos or ((x,y) if self.walkable(x,y) and not self.gi_at(x,y) else None)
        if not pos:
            if it.cat==CAT_WPN: self.msg("pyxel.item_vanishes_as_hits_ground", item=it.data["name"])
            return
        it.x,it.y=pos; self.gitems.append(it)

    def resolve_throw_anim(self, anim):
        outcome = anim.get("outcome")
        if not outcome:
            return
        if outcome["kind"] == "floor":
            self.drop_thrown(outcome["item"], outcome["x"], outcome["y"], around=outcome["around"])
            return
        if outcome["kind"] != "monster":
            return
        m = outcome["monster"]
        thrown = outcome["item"]
        tx, ty = outcome["x"], outcome["y"]
        self.reveal_xeroc_for_attack(m, thrown=True)
        hit, dmg = self.roll_player_attack(m, thrown, True)
        mn = self.combat_monster_name(m)
        item = self.ident.name(thrown)
        if hit:
            m.hp -= dmg
            self.msg_text(self.thrown_hit_message(thrown, item, mn))
            if not m.alive:
                self.msg_text(self.defeated_message(mn))
                self.award_monster_kill(m, mn)
        else:
            self.msg_text(self.thrown_miss_message(thrown, item, mn))
            self.drop_thrown(thrown, tx, ty)

    def throw(self,it,dx,dy):
        # C: weapons.c:missile()
        p=self.p
        if it is p.wpn and it.cursed: self.msg("pyxel.cant_let_go_short"); return False
        if it.stackable and it.qty>1:
            thrown=Item(it.cat,it.kind,cursed=it.cursed,qty=1,hit_plus=it.hit_plus,dam_plus=it.dam_plus); it.qty-=1
        else: p.rm_item(it); thrown=it
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
            if not self.walkable(nx,ny) or self.tm[ny][nx]==T_DOOR: break
            tx,ty=nx,ny; path.append((tx,ty))
        self.throw_anim={"path":path,"sym":thrown.sym,"col":ICOL.get(thrown.cat,7),"tick":0,"delay":2,
                         "outcome":{"kind":"floor","item":thrown,"x":tx,"y":ty,"around":False}}
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
        if p.held_by and (p.x+dx,p.y+dy)!=(p.held_by.x,p.held_by.y):
            self.msg("move.you_are_being_held")
            return False
        if p.no_move>0:
            p.no_move-=1
            self.msg("move.you_are_still_stuck_in_the_bear_trap")
            self.end_turn()
            return True
        if p.confused>0:
            dx,dy = RNG.choice([-1,0,1]), RNG.choice([-1,0,1])
        if dx or dy:
            p.facing=(dx,dy)
        nx, ny = p.x+dx, p.y+dy
        if not self.diag_ok(p.x,p.y,nx,ny):
            return False
        m = self.mon_at(nx, ny)
        if m: self.p_attack(m); self.end_turn(); return True
        if self.walkable(nx, ny):
            p.x, p.y = nx, ny
            trapped = (nx,ny) in self.traps
            if trapped and p.levitating <= 0:
                self.trigger_trap(nx,ny)
                if not self.p.alive or self.st!=ST_PLAY:
                    self.end_turn()
                    return True
            gi = self.gi_at(nx,ny)
            if gi and self.auto_pickup and not trapped:
                self.pickup_at(nx,ny)
            elif gi and not trapped:
                self.msg("pyxel.see_item_here", item=self.ident.name(gi))
            self.update_fov(); self.wake_visible_monsters()
            self.update_cam(); self.end_turn(); return True
        return False

    def do_search(self, front_only=False, spend_turn=True, quiet_fail=False):
        # C: command.c:search()
        p=self.p
        dirs=[p.facing] if front_only else list(DIR8.values())
        found=False
        probinc=(3 if p.hallucinating>0 else 0)+(2 if p.blind>0 else 0)
        for dx,dy in dirs:
            nx,ny=p.x+dx,p.y+dy
            if 0<=nx<MAP_W and 0<=ny<MAP_H:
                hidden=self.hidden_tiles.get((nx,ny))
                if hidden==T_DOOR and rnd(5+probinc)==0:
                    found = self.reveal_hidden_at(nx,ny) or found
                elif hidden==T_CORR and rnd(3+probinc)==0:
                    found = self.reveal_hidden_at(nx,ny) or found
                elif (nx,ny) in self.traps and self.tm[ny][nx]!=T_TRAP and rnd(2+probinc)==0:
                    trap = self.traps[(nx,ny)]
                    found = self.reveal_trap_at(nx,ny) or found
                    if found:
                        if p.hallucinating > 0:
                            trap = rnd(len(TRAPS))
                        self.msg("pyxel.have_found_trap", trap=self.trap_name(trap))
        if found:
            self.msg("pyxel.found_something")
        elif not quiet_fail:
            self.msg("pyxel.find_nothing")
        if found:
            self.update_fov()
        if spend_turn:
            self.end_turn()

    def trap_hits(self, bonus=0):
        th=RNG.randint(1,20)+bonus
        return th>=self.p.ac or th-bonus==20

    def save_vs_poison(self):
        return rnd(20) < 7 + self.p.level//2

    def drop_arrow_at_player(self):
        arrow=Item(CAT_WPN,3,qty=1)
        # C: move.c:T_ARROW falls via weapons.c:fall()/fallpos().
        self.drop_thrown(arrow,self.p.x,self.p.y)

    def teleport_player(self):
        # C: scrolls.c (teleportation)
        cands=[
            (x,y)
            for y,row in enumerate(self.tm)
            for x,tile in enumerate(row)
            if tile in WALKABLE and tile!=T_TRAP and not self.mon_at(x,y)
        ]
        if cands:
            self.p.x,self.p.y=RNG.choice(cands)
            self.update_fov(); self._center_cam()
            self.finish_teleport()

    def trigger_trap(self,x,y):
        # C: move.c:be_trapped()
        self.reveal_trap_at(x,y)
        kind=self.traps.get((x,y),0)
        name=TRAPS[kind]["name"] if 0<=kind<len(TRAPS) else ""
        self.dashing=False
        if name=="trap door":
            self.msg("move.you_fell_into_a_trap")
            self.descend()
        elif name=="bear trap":
            self.p.no_move+=BEARTIME
            self.msg("move.you_are_caught_in_a_bear_trap")
        elif name=="sleeping gas trap":
            self.p.no_command+=SLEEPTIME
            self.msg("move.a_strange_white_mist_envelops_you_and_you_fall_asleep")
        elif name=="arrow trap":
            if self.trap_hits(self.p.level-1):
                self.p.hp-=roll("1d6")
                if self.p.hp<=0 and not self.death_cause:
                    self.death_cause="an arrow killed you"
                    self.msg("move.an_arrow_killed_you")
                else:
                    self.msg("move.oh_no_an_arrow_shot_you")
            else:
                self.drop_arrow_at_player()
                self.msg("move.an_arrow_shoots_past_you")
        elif name=="teleport trap":
            self.teleport_player()
        elif name=="dart trap":
            if self.trap_hits(self.p.level+1):
                self.p.hp-=roll("1d4")
                if self.p.hp<=0 and not self.death_cause:
                    self.death_cause="a poisoned dart killed you"
                    self.msg("move.a_poisoned_dart_killed_you")
                    return
                if (self.p.st>3 and not rogue_rings.is_wearing(self.p, rogue_rings.R_SUSTSTR)
                        and not self.save_vs_poison()):
                    self.p.st-=1
                self.msg("move.a_small_dart_just_hit_you_in_the_shoulder")
            else:
                self.msg("move.a_small_dart_whizzes_by_your_ear_and_vanishes")
        elif name=="rust trap":
            self.msg("move.a_gush_of_water_hits_you_on_the_head")
            self.rust_armor()
        elif name=="mysterious trap":
            self.mysterious_trap_msg()

    def rust_armor(self):
        # C: move.c:rust_armor()
        arm=self.p.arm
        if not self.can_rust_armor(arm):
            return
        if arm.protected or rogue_rings.is_wearing(self.p, rogue_rings.R_SUSTARM):
            self.msg("move.the_rust_vanishes_instantly")
            return
        arm.ench-=1
        self.p.recalc_ac()
        self.msg("move.your_armor_weakens")

    def can_rust_armor(self, arm):
        # C: move.c:rust_armor() skips NULL, non-armor, LEATHER, and o_arm >= 9.
        return bool(arm and arm.cat==CAT_ARM and arm.data["name"]!="leather armor"
                    and arm.data["ac"] - arm.ench < 9)

    def mysterious_trap_msg(self):
        msgs=[
            ("move.you_are_suddenly_in_a_parallel_dimension",None),
            ("move.the_light_in_here_suddenly_seems_color","color"),
            ("move.you_feel_a_sting_in_the_side_of_your_neck",None),
            ("move.multi_colored_lines_swirl_around_you_then_fade",None),
            ("move.a_color_light_flashes_in_your_eyes","color"),
            ("move.a_spike_shoots_past_your_ear",None),
            ("move.value_sparks_dance_across_your_armor","value"),
            ("move.you_suddenly_feel_very_thirsty",None),
            ("move.you_feel_time_speed_up_suddenly",None),
            ("move.time_now_seems_to_be_going_slower",None),
            ("move.you_pack_turns_value","value"),
        ]
        key,arg=msgs[rnd(11)]
        kw={arg:RAINBOW[rnd(len(RAINBOW))]} if arg in ("color","value") else {}
        self.msg(key,**kw)

    def inspect_trap(self,dx,dy):
        x,y=self.p.x+dx,self.p.y+dy
        trap=self.visible_trap_at(x,y)
        if trap is None:
            self.msg("command.no_trap_there")
        else:
            if self.p.hallucinating > 0:
                trap = rnd(len(TRAPS))
            self.msg("pyxel.have_found_trap", trap=self.trap_name(trap))

    def do_action(self):
        p=self.p; px,py=p.x,p.y
        if self.tm[py][px]==T_STAIR or self.gi_at(px,py):
            self.do_pickup(); return
        self.msg("pyxel.swing_empty_air")
        self.do_search(front_only=True)

    def do_pickup(self):
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
                self.msg("pyxel.escaped_with_amulet")
                self.enter_result_state("winner")
                return
            p.depth-=2
            self.descend()
            self.msg("pyxel.wrenching_sensation_gut")
            self.end_turn()
            return
        self.msg("pyxel.descend_to_depth", depth=p.depth + 1)
        self.descend()
        self.msg("pyxel.dungeon_depth", depth=p.depth)
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
            return True
        if self.is_scare_monster(gi) and gi.picked_up:
            self.gitems.remove(gi)
            self.ident.sk[gi.kind]=True
            self.msg("pack.the_scroll_turns_to_dust_as_you_pick_it_up")
            return True
        if p.add_item(gi):
            gi.picked_up=True
            if gi.cat==CAT_AMULET:
                p.has_amulet=True
            self.gitems.remove(gi); self.msg("pyxel.pick_up_item", item=self.ident.name(gi))
            return True
        self.msg("pyxel.pack_too_full")
        return True

    def do_wait(self): self.end_turn()

    def ring_after_turn(self):
        for hand in (rogue_rings.LEFT, rogue_rings.RIGHT):
            ring = rogue_rings.equipped_ring(self.p, hand)
            if rogue_rings.is_ring(ring, rogue_rings.R_SEARCH):
                self.do_search(spend_turn=False, quiet_fail=True)
            elif rogue_rings.is_ring(ring, rogue_rings.R_TELEPORT) and rnd(50)==0:
                self.teleport_player()

    def end_turn(self):
        msg_start = min(getattr(self, "turn_msg_start", 0), len(self.msg_turns))
        if self.p.haste > 0 and not self.haste_half_turn:
            # Rogue 5.4.4 command.c:command() gives ISHASTE two player actions
            # before do_fuses(AFTER) and monster/daemon work advance.
            self.haste_half_turn = True
            return
        self.haste_half_turn = False
        self.turn+=1
        for i in range(msg_start, len(self.msg_turns)):
            self.msg_turns[i] = self.turn
        m=self.p.hunger()
        if m:
            self.msg(m); self.dashing=False
        if self.p.hp<=0 and not self.death_cause:
            self.death_cause="starved to death"
        if not self.p.alive:
            self.msg("pyxel.died_restart"); self.enter_result_state("killed")
            self.turn_msg_start = len(self.msgs)
            return
        if self.p.no_command>0: self.p.no_command-=1
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
                self.msg("daemons.you_float_gently_to_the_ground")
        self.do_before_daemons()
        self.do_after_daemons()
        due_fuses = self.fuses.tick(rogue_daemons.AFTER)
        if "unconfuse" in due_fuses:
            self.unconfuse()
        if "sight" in due_fuses:
            self.sight()
        if "turn_see" in due_fuses:
            self.p.see_monsters = 0
        if "unsee" in due_fuses:
            self.p.see_invisible = 0
        if "come_down" in due_fuses:
            self.come_down()
        if "land" in due_fuses:
            self.land()
        if "nohaste" in due_fuses:
            self.nohaste()
        if "swander" in due_fuses:
            self.swander()
        if "nohaste" not in due_fuses and self.p.haste>0:
            remaining = self.fuses.remaining("nohaste")
            if remaining:
                self.p.haste = remaining
            else:
                self.p.haste -= 1
                if self.p.haste == 0:
                    self.msg("daemons.you_feel_yourself_slowing_down")
        self.p.heal_tick()
        self.ring_after_turn()
        for mo in self.mons: self.m_turn(mo)
        self.mons=[mo for mo in self.mons if mo.alive]
        if not self.p.alive:
            if not self.death_cause: self.death_cause="died"
            self.msg("pyxel.died_restart"); self.enter_result_state("killed")
        self.turn_msg_start = len(self.msgs)

    def do_before_daemons(self):
        # Rogue 5.4.4 command.c calls do_daemons(BEFORE), then do_fuses(BEFORE).
        for name in self.daemons.tick(rogue_daemons.BEFORE):
            if name == "rollwand":
                self.roll_wanderer()
        due_fuses = self.fuses.tick(rogue_daemons.BEFORE)
        if "swander" in due_fuses:
            self.swander()
        self.wander_timer = self.fuses.remaining("swander")

    def swander(self):
        # C: daemons.c:swander()
        self.daemons.start("rollwand", rogue_daemons.AFTER)

    def roll_wanderer(self):
        # C: daemons.c:rollwand()
        self.wander_between+=1
        if self.wander_between<4:
            return
        self.wander_between=0
        if RNG.roll(1,6)==4 and self.spawn_wanderer():
            self.daemons.kill("rollwand")
            self.fuses.fuse("swander", RNG.spread(WANDERTIME), rogue_daemons.AFTER)
            self.wander_timer=self.fuses.remaining("swander")

    def do_after_daemons(self):
        # Rogue 5.4.4 command.c calls do_daemons(AFTER) before do_fuses(AFTER).
        for name in self.daemons.tick(rogue_daemons.AFTER):
            if name == "rollwand":
                self.roll_wanderer()

    # ---------- Dash ----------
    def dash_turn_ok(self,x,y):
        return 0<=x<MAP_W and 0<=y<MAP_H and self.tm[y][x] in (T_CORR,T_DOOR)

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
        if tile!=T_CORR: return False
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
                self.dashing=False; self.dash_restart_guard=True; return
            self.dash_d=nd
            dx,dy=nd
        ox,oy=self.p.x,self.p.y
        moved=self.try_move(dx,dy)
        if not moved or (self.p.x,self.p.y)==(ox,oy) or self.st!=ST_PLAY or not self.p.alive:
            self.dashing=False; self.dash_restart_guard=True; return
        self.dash_steps+=1
        self.dashing=not self.dash_should_stop_here(dx,dy)
        if not self.dashing:
            self.dash_restart_guard=True

    # ---------- Menu logic ----------
    def open_menu(self):
        self.st=ST_MENU; self.mcur=0; self.dir_pending=None
        self.b_menu_guard=self.kh(pyxel.GAMEPAD1_BUTTON_B)
    def close_menu(self):
        self.st=ST_PLAY; self.mcur=self.icur=0; self.cact=None; self.dact=None; self.fitems=[]
        self.throw_dir=None; self.zap_item=None; self.action_origin=ST_PLAY
        self.call_item=None; self.call_input=""; self.call_preset_idx=0
        self.b_menu_guard=False; self.dir_pending=None

    def menu_select(self):
        aname,cat = MENU_ACTIONS[self.mcur]
        self.start_item_action(aname, cat)

    def start_item_action(self, aname, cat=None):
        if cat is None:
            cat = next((c for n,c in MENU_ACTIONS if n == aname), None)
        self.action_origin = self.st
        self.cact = aname; p = self.p
        if aname=="Take off":
            self.fitems=[i for i in p.inv if i is p.wpn or i is p.arm or i is p.ring_l or i is p.ring_r]
        elif aname in("Throw","Drop"):
            self.fitems=list(p.inv)
        elif aname=="Call":
            self.fitems=[i for i in p.inv if i.cat in (CAT_POT, CAT_SCR, CAT_RING, CAT_STICK)]
        elif cat:
            self.fitems=[i for i in p.inv if i.cat==cat]
        else:
            self.fitems=list(p.inv)
        if not self.fitems:
            self.msg("pyxel.nothing_to_action", action=aname.lower()); self.close_menu(); return
        self.icur=0
        if aname=="Throw":
            self.throw_dir=None; self.dact="Throw"; self.st=ST_DIR
        elif aname=="Call":
            self.call_item=None; self.call_input=CALL_PRESETS[0]; self.call_preset_idx=0
            self.st=ST_CALL
        else:
            self.st=ST_ITEM

    def item_confirm(self):
        if not self.fitems: self.close_menu(); return
        it=self.fitems[self.icur]; a=self.cact
        if a=="Throw":
            if self.throw_dir:
                dx,dy=self.throw_dir
                self.p.facing=(dx,dy)
                animating = self.throw(it,dx,dy)
                self.close_menu()
                if animating:
                    self.turn_after_throw_anim = True
                else:
                    self.end_turn()
            else:
                self.dact="Throw"; self.st=ST_DIR
            return
        if a=="Zap":
            self.zap_item=it; self.dact="Zap"; self.st=ST_DIR
            return
        if a=="Identify":
            # Rogue 5.4.4 wizard.c:whatis() — player selected item to identify.
            self.set_know(it)
            self.msg("pyxel.it_is_item", item=self.ident.name(it))
            self.close_menu(); self.end_turn()
            return
        if a=="Quaff":   self.use_pot(it)
        elif a=="Read":
            if self.use_scr(it):
                return  # use_scr set up next picker state; don't close yet.
        elif a=="Eat":   self.eat(it)
        elif a=="Wield": self.wield(it)
        elif a=="Wear":  self.wear(it)
        elif a=="Put on": self.put_on_ring(it)
        elif a=="Take off": self.takeoff(it)
        elif a=="Drop":  self.drop(it)
        self.close_menu(); self.end_turn()

    def dir_confirm(self,dx,dy):
        if self.dact=="Trap":
            self.inspect_trap(dx,dy)
            self.st=ST_PLAY; self.dact=None; self.cact=None; self.dir_pending=None
            return
        if self.dact=="Throw":
            self.throw_dir=(dx,dy)
            self.dact=None
            self.st=ST_ITEM
            return
        if self.dact=="Zap":
            if self.zap_item:
                self.p.facing=(dx,dy)
                self.zap_stick(self.zap_item,dx,dy)
                self.close_menu()
                self.end_turn()
            return

    def start_trap_inspect(self):
        self.cact="Trap"; self.dact="Trap"; self.st=ST_DIR; self.dir_pending=None

    # ---------- Input helpers ----------
    def kp(self,*ks): return any(k is not None and pyxel.btnp(k) for k in ks)
    def kh(self,*ks): return any(k is not None and pyxel.btn(k) for k in ks)

    def begin_input(self):
        self.b_tap=False
        self.back_tap=False
        b_now=self.kh(pyxel.GAMEPAD1_BUTTON_B)
        back_now=self.back_held()
        if not self.dash_held():
            self.dash_restart_guard=False
        if b_now:
            self.b_frames = self.b_frames+1 if self.b_prev else 1
        else:
            if self.b_prev and not self.b_used and self.b_frames<=B_TAP_FRAMES:
                self.b_tap=True
            self.b_frames=0; self.b_used=False
        self.b_prev=b_now
        if b_now and (self.kh(pyxel.KEY_UP,pyxel.KEY_DOWN,pyxel.KEY_LEFT,pyxel.KEY_RIGHT,
                              pyxel.GAMEPAD1_BUTTON_DPAD_UP,pyxel.GAMEPAD1_BUTTON_DPAD_DOWN,
                              pyxel.GAMEPAD1_BUTTON_DPAD_LEFT,pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
                      or self.kh(pyxel.GAMEPAD1_BUTTON_A)):
            self.b_used=True
        if back_now:
            self.back_frames = self.back_frames+1 if self.back_prev else 1
        else:
            if self.back_prev and not self.back_used and self.back_frames<=BACK_TAP_FRAMES:
                self.back_tap=True
            self.back_frames=0; self.back_used=False
        self.back_prev=back_now
        if back_now and self.kh(pyxel.KEY_RETURN, pyxel.KEY_ESCAPE,
                                pyxel.GAMEPAD1_BUTTON_A, pyxel.GAMEPAD1_BUTTON_B):
            self.back_used=True
        if back_now and self.dir_held_any():
            self.back_used=True

    GP = pyxel.GAMEPAD1_BUTTON_DPAD_UP
    def _held_up(self): return self.kh(pyxel.KEY_UP, pyxel.KEY_K, pyxel.GAMEPAD1_BUTTON_DPAD_UP)
    def _held_dn(self): return self.kh(pyxel.KEY_DOWN, pyxel.KEY_J, pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)
    def _held_lt(self): return self.kh(pyxel.KEY_LEFT, pyxel.KEY_H, pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)
    def _held_rt(self): return self.kh(pyxel.KEY_RIGHT, pyxel.KEY_L, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)

    def dir_press(self):
        """Return (dx,dy) for direction pressed this frame (btnp), or None."""
        # Diagonal keys (vi: Y U B N)
        if self.kp(pyxel.KEY_Y): self.dir_pending=None; return (-1,-1)
        if self.kp(pyxel.KEY_U): self.dir_pending=None; return (1,-1)
        if self.kp(pyxel.KEY_B): self.dir_pending=None; return (-1,1)
        if self.kp(pyxel.KEY_N): self.dir_pending=None; return (1,1)
        u=self._held_up(); d=self._held_dn(); l=self._held_lt(); r=self._held_rt()
        diag_pressed = (
            self.kp(pyxel.KEY_UP,pyxel.KEY_DOWN,pyxel.KEY_LEFT,pyxel.KEY_RIGHT,
                    pyxel.GAMEPAD1_BUTTON_DPAD_UP,pyxel.GAMEPAD1_BUTTON_DPAD_DOWN,
                    pyxel.GAMEPAD1_BUTTON_DPAD_LEFT,pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
        )
        if u and r and diag_pressed: self.dir_pending=None; return (1,-1)
        if u and l and diag_pressed: self.dir_pending=None; return (-1,-1)
        if d and r and diag_pressed: self.dir_pending=None; return (1,1)
        if d and l and diag_pressed: self.dir_pending=None; return (-1,1)
        if self.dir_pending is not None:
            pdx,pdy = self.dir_pending
            self.dir_pending = None
            if pdy < 0 and u:
                if r and not l: return (1,-1)
                if l and not r: return (-1,-1)
            elif pdy > 0 and d:
                if r and not l: return (1,1)
                if l and not r: return (-1,1)
            elif pdx < 0 and l:
                if u and not d: return (-1,-1)
                if d and not u: return (-1,1)
            elif pdx > 0 and r:
                if u and not d: return (1,-1)
                if d and not u: return (1,1)
            return (pdx,pdy)
        if self.diag_assist:
            self.dir_pending=None
            return None
        # Cardinal
        if self.kp(pyxel.KEY_UP,    pyxel.KEY_K, pyxel.GAMEPAD1_BUTTON_DPAD_UP):
            self.dir_pending=(0,-1); return None
        if self.kp(pyxel.KEY_DOWN,  pyxel.KEY_J, pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
            self.dir_pending=(0,1); return None
        if self.kp(pyxel.KEY_LEFT,  pyxel.KEY_H, pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            self.dir_pending=(-1,0); return None
        if self.kp(pyxel.KEY_RIGHT, pyxel.KEY_L, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            self.dir_pending=(1,0); return None
        return None

    def dir_prompt_press(self):
        if self.kp(pyxel.KEY_Y): return (-1,-1)
        if self.kp(pyxel.KEY_U): return (1,-1)
        if self.kp(pyxel.KEY_B): return (-1,1)
        if self.kp(pyxel.KEY_N): return (1,1)
        u=self._held_up(); d=self._held_dn(); l=self._held_lt(); r=self._held_rt()
        pressed=self.kp(pyxel.KEY_UP,pyxel.KEY_DOWN,pyxel.KEY_LEFT,pyxel.KEY_RIGHT,
                        pyxel.KEY_H,pyxel.KEY_J,pyxel.KEY_K,pyxel.KEY_L,
                        pyxel.GAMEPAD1_BUTTON_DPAD_UP,pyxel.GAMEPAD1_BUTTON_DPAD_DOWN,
                        pyxel.GAMEPAD1_BUTTON_DPAD_LEFT,pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
        if not pressed:
            return None
        dx = -1 if l and not r else 1 if r and not l else 0
        dy = -1 if u and not d else 1 if d and not u else 0
        return (dx,dy) if (dx or dy) else None

    def held_dir(self):
        u=self._held_up(); d=self._held_dn(); l=self._held_lt(); r=self._held_rt()
        dx = -1 if l and not r else 1 if r and not l else 0
        dy = -1 if u and not d else 1 if d and not u else 0
        if dx and dy:
            return (dx,dy)
        if self.diag_assist:
            return None
        return (dx,dy) if (dx or dy) else None

    def dir_held_any(self):
        return self._held_up() or self._held_dn() or self._held_lt() or self._held_rt()

    def menu_vertical_press(self):
        if self.kp(pyxel.KEY_UP, pyxel.KEY_K, pyxel.GAMEPAD1_BUTTON_DPAD_UP): return -1
        if self.kp(pyxel.KEY_DOWN, pyxel.KEY_J, pyxel.GAMEPAD1_BUTTON_DPAD_DOWN): return 1
        return 0

    def shift_held(self):
        return self.kh(pyxel.KEY_SHIFT, pyxel.KEY_LSHIFT, pyxel.KEY_RSHIFT)
    def btn_a(self): return self.kp(pyxel.KEY_RETURN, pyxel.GAMEPAD1_BUTTON_A)
    def held_a(self): return self.kh(pyxel.KEY_RETURN, pyxel.GAMEPAD1_BUTTON_A)
    def btn_b(self): return self.kp(pyxel.KEY_ESCAPE) or self.b_tap
    def btn_cancel(self): return self.kp(pyxel.KEY_ESCAPE, pyxel.GAMEPAD1_BUTTON_B)
    def btn_overlay_cancel(self):
        if self.kp(pyxel.KEY_ESCAPE): return True
        if self.back_tap: return True
        b_now=self.kh(pyxel.GAMEPAD1_BUTTON_B)
        if self.b_menu_guard:
            if not b_now:
                self.b_menu_guard=False
            return False
        if self.kp(pyxel.GAMEPAD1_BUTTON_B):
            self.b_used=True
            return True
        return self.b_tap
    def btn_menu(self): return self.kp(pyxel.KEY_ESCAPE) or self.b_tap
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
    def btn_search(self): return self.key_lower(pyxel.KEY_S)
    def btn_trap_inspect(self):
        return self.shift_held() and self.kp(getattr(pyxel,"KEY_6",None))
    def btn_inventory(self): return self.key_lower(pyxel.KEY_I)
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
        if not self.back_held():
            return None
        u=self.kh(pyxel.KEY_UP, pyxel.GAMEPAD1_BUTTON_DPAD_UP)
        d=self.kh(pyxel.KEY_DOWN, pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)
        l=self.kh(pyxel.KEY_LEFT, pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)
        r=self.kh(pyxel.KEY_RIGHT, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
        pressed=self.kp(pyxel.KEY_UP, pyxel.KEY_DOWN, pyxel.KEY_LEFT, pyxel.KEY_RIGHT,
                        pyxel.GAMEPAD1_BUTTON_DPAD_UP, pyxel.GAMEPAD1_BUTTON_DPAD_DOWN,
                        pyxel.GAMEPAD1_BUTTON_DPAD_LEFT, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
        if not pressed:
            return None
        dx = -1 if l and not r else 1 if r and not l else 0
        dy = -1 if u and not d else 1 if d and not u else 0
        if dx or dy:
            self.back_used=True
            return (dx,dy)
        return None
    def btn_r(self): return self.kp(pyxel.KEY_QUESTION, pyxel.KEY_SLASH)
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
        if self.key_lower(getattr(pyxel, "KEY_W", None)): return "Wear"
        if self.key_lower(pyxel.KEY_Z): return "Zap"
        if self.key_upper(getattr(pyxel, "KEY_W", None)): return "Wield"
        if self.key_upper(getattr(pyxel, "KEY_T", None)): return "Take off"
        if self.key_upper(getattr(pyxel, "KEY_P", None)): return "Put on"
        if self.key_lower(pyxel.KEY_C): return "Call"
        return None

    # ---------- Update ----------
    def update(self):
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
            if self.btn_a() or self.btn_start_tap() or pyxel.btnp(pyxel.KEY_R): self.st=ST_SCORE
            return
        if self.st==ST_WIN:
            if self.btn_a() or self.btn_start_tap() or pyxel.btnp(pyxel.KEY_R): self.st=ST_SCORE
            return
        if self.st==ST_QUIT:
            if self.btn_a() or self.btn_start_tap() or pyxel.btnp(pyxel.KEY_R): self.st=ST_SCORE
            return
        if self.st==ST_SCORE:
            if self.btn_a() or self.btn_start_tap() or pyxel.btnp(pyxel.KEY_R): self.new_game()
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
        elif self.st==ST_HELP:
            if self.btn_any_key():
                self.st=ST_PLAY
        elif self.st==ST_INVENTORY:
            if self.btn_a() or self.btn_overlay_cancel() or self.btn_inventory() or self.btn_back() or self.btn_r():
                self.st=ST_PLAY

    def upd_play(self):
        if self.p.no_command>0:
            self.msg("pyxel.unable_to_move")
            self.end_turn()
            return

        # Dash continuation
        if self.dashing:
            if not self.dash_held():
                self.dashing=False; return
            self.b_used=True
            self.dash_t+=1
            if self.dash_t>=self.run_step_interval():
                self.dash_t=0
                self.dash_step()
            return

        # Overlays
        sd=self.select_dir_press()
        if sd:
            self.inspect_trap(*sd)
            self.dir_pending=None
            return
        if self.btn_select_a():
            self.do_search()
            self.dir_pending=None
            return
        if self.btn_select_b():
            self.start_item_action("Throw")
            self.dir_pending=None
            return
        if self.btn_inventory(): self.st=ST_INVENTORY; return
        if self.btn_back():  self.open_aux(); return
        if self.btn_r():     self.st=ST_HELP; return
        if self.btn_wait():  self.do_wait(); return
        if self.btn_search(): self.do_search(); return
        if self.btn_trap_inspect(): self.start_trap_inspect(); return
        if self.key_upper(getattr(pyxel, "KEY_D", None)):
            self.disc_scroll = 0; self.st = ST_DISC; return
        aname = self.rogue_command_action()
        if aname:
            self.start_item_action(aname)
            return

        # Dash start: B/Shift held + direction
        dash_guarded = getattr(self, "dash_restart_guard", False)
        if self.dash_held() and (not dash_guarded or self.dash_restart_dir_press()):
            d = self.held_dir()
            if d:
                self.dashing=True; self.dash_d=d; self.dash_t=0
                self.dash_steps=0
                self.dash_restart_guard=False
                self.b_used=True
                self.dash_step()
                return

        # Normal direction
        d = self.dir_press()
        if d:
            self.try_move(*d)
            return

        if self.btn_start_tap():
            self.dir_pending=None
            self.diag_assist = not self.diag_assist
            self.msg("pyxel.diagonal_assist_on" if self.diag_assist else "pyxel.diagonal_assist_off")
            return
        if self.btn_a(): self.do_action(); return
        if self.btn_menu(): self.open_menu(); return

    def upd_menu(self):
        dy=self.menu_vertical_press()
        if dy: self.mcur=(self.mcur+dy)%len(MENU_ACTIONS); return
        if self.btn_a(): self.menu_select(); return
        if self.btn_overlay_cancel(): self.close_menu(); return

    def upd_item(self):
        dy=self.menu_vertical_press()
        if dy and self.fitems: self.icur=(self.icur+dy)%len(self.fitems); return
        if self.btn_a(): self.item_confirm(); return
        if self.btn_overlay_cancel():
            if self.cact=="Throw" and self.throw_dir is not None:
                if self.action_origin==ST_MENU:
                    self.st=ST_MENU
                else:
                    self.close_menu()
            else:
                self.st=ST_MENU
            self.throw_dir=None
            return

    def upd_call(self):
        # Phase 1: アイテム選択
        if self.call_item is None:
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
                self.close_menu(); return
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
            self._call_it_apply(self.call_item, self.call_input)
            self.close_menu()
            # ターン消費なし (misc.c:call_it() 準拠)
            return
        if self.btn_overlay_cancel():
            self.close_menu(); return

    def upd_disc(self):
        lines = self._disc_lines()
        visible = 18
        max_scroll = max(0, len(lines) - visible)
        dy = self.menu_vertical_press()
        if dy:
            self.disc_scroll = max(0, min(self.disc_scroll + dy, max_scroll))
            return
        if self.btn_a() or self.btn_overlay_cancel():
            self.st = ST_PLAY; return

    def upd_dir(self):
        d=self.dir_prompt_press()
        if d: self.dir_confirm(*d); return
        if self.btn_overlay_cancel():
            if self.dact=="Trap":
                self.st=ST_PLAY
                self.dact=None
            elif self.dact=="Throw":
                if self.action_origin==ST_MENU:
                    self.st=ST_MENU
                    self.dact=None
                else:
                    self.close_menu()
            else:
                self.st=ST_ITEM
            return

    def open_aux(self):
        self.st=ST_AUX; self.acur=0; self.dir_pending=None
        self.b_menu_guard=self.kh(pyxel.GAMEPAD1_BUTTON_B)

    def upd_aux(self):
        dy=self.menu_vertical_press()
        if dy: self.acur=(self.acur+dy)%len(AUX_ACTIONS); return
        if self.btn_overlay_cancel(): self.st=ST_PLAY; return
        if not self.btn_a(): return
        act=AUX_ACTIONS[self.acur]
        if act=="Inventory": self.st=ST_INVENTORY
        elif act=="Help": self.st=ST_HELP
        elif act=="Search":
            self.st=ST_PLAY
            self.do_search()
        elif act=="Trap":
            self.start_trap_inspect()
        elif act=="Pickup":
            self.auto_pickup = not self.auto_pickup
            self.msg("pyxel.pickup_on" if self.auto_pickup else "pyxel.pickup_off")
            self.st=ST_PLAY
        elif act=="Language":
            self.toggle_lang()
            self.st=ST_PLAY
        elif act=="Palette":
            self.toggle_palette()
            self.st=ST_PLAY
        elif act=="Quit":
            self.st=ST_QUIT_CONFIRM
        self.dir_pending=None

    # =====================================================
    #  DRAW
    # =====================================================
    def draw(self):
        pyxel.cls(0)
        if self.st == ST_LOADING:
            msg = "Loading..." if self.lang == LANG_EN else "ロード中..."
            self.txt(SCR_W // 2 - 30, SCR_H // 2, msg, 10)
            return
        self.draw_title()
        self.draw_zoom()
        self.draw_stat()
        self.draw_msgs()
        # Overlays
        if self.st==ST_MENU: self.draw_menu()
        elif self.st==ST_ITEM: self.draw_isel()
        elif self.st==ST_CALL: self.draw_call_input()
        elif self.st==ST_DISC: self.draw_disc()
        elif self.st==ST_DIR: self.draw_dirp()
        elif self.st==ST_AUX: self.draw_aux()
        elif self.st==ST_INVENTORY: self.draw_inventory()
        elif self.st==ST_HELP: self.draw_help()
        elif self.st==ST_DEAD: self.draw_dead()
        elif self.st==ST_WIN: self.draw_win()
        elif self.st==ST_QUIT: self.draw_quit()
        elif self.st==ST_QUIT_CONFIRM: self.draw_quit_confirm()
        elif self.st==ST_SCORE: self.draw_score_screen()

    def draw_title(self):
        self.txt(HUD_X, 3, "Rogue V5", 10)
        self.txt(HUD_X, 13, UI_BUILD, 5)

    def should_draw_memory_tile(self, mx, my, tile):
        room = self.room_at(mx, my)
        if tile == T_FLOOR and room and room.is_dark:
            return False
        return True

    def memory_tile_color(self, tile):
        if tile == T_STAIR:
            return TILE_CH[T_STAIR][1]
        return MEMORY_TILE_COLOR

    def draw_zoom(self):
        cx,cy = self.cam_x, self.cam_y
        blind = self.p.blind > 0
        pyxel.rectb(ZV_X-1, ZV_Y-1, ZV_PX_W+2, ZV_PX_H+2, 3)
        px,py = self.p.x, self.p.y

        for vy in range(ZV_ROWS):
            for vx in range(ZV_COLS):
                mx,my = cx+vx, cy+vy
                if not(0<=mx<MAP_W and 0<=my<MAP_H): continue
                sx = ZV_X + vx*TILE_W
                sy = ZV_Y + vy*TILE_H
                if blind and (mx, my) == (px, py):
                    self.txt(sx+1, sy+1, "@", 30)
                    continue
                vis = (mx,my) in self.visible and not blind
                exp = (mx,my) in self.explored and not blind

                if vis:
                    tile=self.tm[my][mx]; _,col=TILE_CH.get(tile,(" ",0)); ch=self.visible_tile_sym(mx,my,tile)
                    if ch!=" ": self.txt(sx+1,sy+1,ch,col)
                    # Ground item
                    gi=self.gi_at(mx,my)
                    if gi: self.txt(sx+1,sy+1,self.visible_item_sym(gi),ICOL.get(gi.cat,9))
                    # Monster
                    mo=self.mon_at(mx,my)
                    if mo and (self.can_see_monster(mo) or self.can_detect_monsters()):
                        sym = self.visible_monster_sym(mo) if self.can_see_monster(mo) else self.detected_monster_sym(mo)
                        self.txt(sx+1,sy+1,sym,self.monster_color(mo.sym))
                    # Player
                    if mx==px and my==py:
                        self.txt(sx+1,sy+1,"@",30)
                elif exp:
                    tile=self.tm[my][mx]; ch,_=TILE_CH.get(tile,(" ",0))
                    if ch!=" " and self.should_draw_memory_tile(mx,my,tile):
                        self.txt(sx+1,sy+1,ch,self.memory_tile_color(tile))
                    gi=self.gi_at(mx,my)
                    if gi: self.txt(sx+1,sy+1,gi.sym,ICOL.get(gi.cat,9))
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
        sx,sy=HUD_X,HUD_Y+28; p=self.p; hc=9 if p.hp>p.max_hp//3 else 22
        self.txt(sx,sy,f"Depth {p.depth}",9)
        sy+=11
        self.txt(sx,sy,f"Turn {self.turn}",6); sy+=13
        self.txt(sx,sy,f"HP {p.hp}/{p.max_hp}",hc); sy+=11
        bw=HUD_W-10; pyxel.rect(sx,sy,bw,4,1)
        if p.max_hp>0:
            if self.last_hp_seen is not None and p.hp < self.last_hp_seen:
                self.hp_damage_from = min(self.last_hp_seen, p.max_hp)
                self.hp_damage_turn = self.turn
            cur_w=max(0,int(bw*p.hp/p.max_hp))
            if self.hp_damage_turn == self.turn and self.hp_damage_from is not None:
                old_w=max(cur_w,int(bw*self.hp_damage_from/p.max_hp))
                pyxel.rect(sx+cur_w,sy,old_w-cur_w,4,21)
            pyxel.rect(sx,sy,cur_w,4,22 if p.hp<=p.max_hp//3 else 9)
            self.last_hp_seen = p.hp
        sy+=12
        self.txt(sx,sy,f"Lv {p.level} Exp {p.exp}",9); sy+=11
        self.txt(sx,sy,f"Str {p.st}/{p.max_st}",9)
        sy+=11
        self.txt(sx,sy,f"Arm {p.ac}",9); sy+=11
        self.txt(sx,sy,f"Gold {p.gold}",29); sy+=11
        state = p.state if p.state else "normal"
        if state != "normal":
            self.txt(sx,sy,f"Food {state}",22); sy+=11
        if self.diag_assist:
            self.txt(sx,sy,"Diag ON",27); sy+=11
        if not self.auto_pickup:
            self.txt(sx,sy,"Pickup OFF",23); sy+=11
        sy+=6
        self.txt(sx,sy,"-- Equip --",27); sy+=11
        wn=self.hud_equip_name(p.wpn) if p.wpn else "bare hands"
        an=self.hud_equip_name(p.arm) if p.arm else "no armor"
        self.txt(sx,sy,f"W {wn[:11]}",9); sy+=11
        self.txt(sx,sy,f"A {an[:11]}",9); sy+=16
        self.txt(sx,sy,"-- Effect --",27); sy+=11
        eff=[]
        if p.state=="hungry": eff.append("Hungry")
        elif p.state=="weak": eff.append("Weak")
        elif p.state=="faint": eff.append("Faint")
        if p.confused>0: eff.append("Confused")
        if p.blind>0: eff.append("Blind")
        if p.haste>0: eff.append("Haste")
        if p.hallucinating>0: eff.append("Halu")
        if p.levitating>0: eff.append("Levit")
        if not eff:
            eff.append("None")
        for e in eff[:5]:
            self.txt(sx,sy,e,22 if e!="None" else 6)
            sy+=11

    def draw_msgs(self):
        rows=[]
        msg_turns = self.msg_turns if len(getattr(self, "msg_turns", [])) == len(self.msgs) else []
        last_index = len(self.msgs) - 1
        for mi,m in enumerate(reversed(self.msgs)):
            src_i = last_index - mi
            same_turn = msg_turns and msg_turns[src_i] == self.turn
            c=30 if same_turn or (not msg_turns and mi==0) else 6
            parts=[m[i:i+MSG_COLS] for i in range(0,len(m),MSG_COLS)] or [""]
            for part in reversed(parts):
                rows.append((part,c))
                if len(rows)>=MSG_LINES: break
            if len(rows)>=MSG_LINES: break
        rows=list(reversed(rows))
        for i,(m,c) in enumerate(rows):
            self.txt(MSG_X,MSG_Y+i*MSG_LINE_H,m,c)

    # ---------- Overlays ----------
    def _box(self,x,y,w,h,title=""):
        pyxel.rect(x,y,w,h,0); pyxel.rectb(x,y,w,h,5)
        if title: self.txt(x+4,y+3,title,27)

    def draw_menu(self):
        bx,by=ZV_X+20,ZV_Y+8; bw=130; bh=len(MENU_ACTIONS)*14+18
        self._box(bx,by,bw,bh,"-- Action --")
        for i,(nm,_) in enumerate(MENU_ACTIONS):
            ty=by+16+i*14; c=27 if i==self.mcur else 9
            pre=">" if i==self.mcur else " "
            self.txt(bx+4,ty,f"{pre} {TextCatalog.menu(self.lang,nm)}",c)

    def draw_isel(self):
        bx,by=ZV_X+20,ZV_Y+8; n=min(len(self.fitems),10); bw=220; bh=n*14+20
        self._box(bx,by,bw,bh,f"-- {self.cact} --")
        st=max(0,self.icur-9)
        for i,it in enumerate(self.fitems[st:st+10]):
            ri=st+i; ty=by+16+i*14
            idx=self.p.inv.index(it) if it in self.p.inv else 0
            lt=chr(ord('a')+idx)
            ln=self.item_name(it)
            c=27 if ri==self.icur else 9
            pre=">" if ri==self.icur else " "
            self.txt(bx+4,ty,f"{pre}{lt}) {ln[:32]}",c)

    def draw_call_input(self):
        if self.call_item is None:
            self.draw_isel()
            return
        prompt = TextCatalog.msg(self.lang, "misc.what_to_call_it")
        bx, by = ZV_X + 20, ZV_Y + 60; bw = 240; bh = 36
        self._box(bx, by, bw, bh, f"-- {self.cact} --")
        self.txt(bx + 4, by + 14, f"{prompt}", 9)
        cursor = "_" if (pyxel.frame_count // 15) % 2 == 0 else " "
        self.txt(bx + 4, by + 24, f"> {self.call_input}{cursor}", 27)

    def draw_disc(self):
        bx, by = 20, 12; bw = SCR_W - 40; bh = SCR_H - 80
        title = TextCatalog.msg(self.lang, "misc.discoveries_title")
        hint  = TextCatalog.msg(self.lang, "misc.discoveries_hint")
        self._box(bx, by, bw, bh, f"=== {title} ===")
        lines = self._disc_lines()
        visible = (bh - 24) // 9
        start = self.disc_scroll
        for i, (col, text) in enumerate(lines[start:start + visible]):
            if not text:
                continue
            self.txt(bx + 6, by + 16 + i * 9, text[:60], col if col else 9)
        self.txt(bx + 4, by + bh - 10, hint, 5)

    def draw_dirp(self):
        bx,by=ZV_X+50,ZV_Y+90
        title="Trap direction? [D-pad/YUBN]" if self.dact=="Trap" else "Direction? [D-pad/YUBN]"
        self._box(bx,by,190 if self.dact=="Trap" else 170,20,title)

    def draw_aux(self):
        bx,by=ZV_X+20,ZV_Y+8; bw=120; bh=len(AUX_ACTIONS)*14+18
        self._box(bx,by,bw,bh,"-- Assist --")
        for i,nm in enumerate(AUX_ACTIONS):
            ty=by+16+i*14; c=27 if i==self.acur else 9
            pre=">" if i==self.acur else " "
            self.txt(bx+4,ty,f"{pre} {TextCatalog.menu(self.lang,nm)}",c)

    def draw_inventory(self):
        bx,by=30,20; bw=SCR_W-60; bh=SCR_H-40
        self._box(bx,by,bw,bh,"=== Inventory ===")
        p=self.p
        inv_x0, inv_y0 = bx+8, by+18
        for i,it in enumerate(p.inv):
            lt=chr(ord('a')+i); ln=self.item_name(it)
            self.txt(inv_x0,inv_y0+i*9,f"{lt}) {ln[:70]}",9)

    def draw_help(self):
        bx,by=30,20; bw=SCR_W-60; bh=SCR_H-40
        self._box(bx,by,bw,bh,"=== Help ===")
        gamepad=[
            "--- Gamepad ---",
            "D-pad       Move/Dir",
            "Start       Diag assist",
            "A           Action",
            "A+B         Wait",
            "B+dir       Dash",
            "B           Menu/Cancel",
            "Select      Assist menu",
            "Select+A    Search around",
            "Select+B    Quick throw",
            "Select+dir  Inspect trap",
        ]
        keyboard=[
            "--- Keyboard: Pad ---",
            "Arrows/HJKL Move/Dir",
            "YUBN        Diagonal",
            "Space       Diag assist",
            "Enter       Action",
            "Enter+Esc   Wait",
            "Shift+dir   Dash",
            "Esc         Menu/Cancel",
            "Tab         Assist menu",
            "Tab+Enter   Search around",
            "Tab+Esc     Quick throw",
            "Tab+dir     Inspect trap",
        ]
        y=by+18
        for i in range(max(len(gamepad), len(keyboard))):
            if i < len(gamepad):
                ln=gamepad[i]; self.txt(bx+8,y,ln,HELP_HEADER_COL if ln.startswith("---") else HELP_TEXT_COL)
            if i < len(keyboard):
                ln=keyboard[i]; self.txt(bx+250,y,ln,HELP_HEADER_COL if ln.startswith("---") else HELP_TEXT_COL)
            y+=11
        y+=8
        self.txt(bx+8,y,"--- Keyboard commands ---",HELP_HEADER_COL); y+=11
        commands=[
            ". Wait   s Search   t Throw   ^ Trap",
            "i Inv    ? Help",
            "q Quaff  r Read     e Eat     z Zap",
            "w Wear   W Wield    T Take off",
        ]
        for ln in commands:
            self.txt(bx+8,y,ln,HELP_TEXT_COL); y+=11

    def draw_top_scores(self, bx=412, by=30):
        bw=156; bh=144
        self._box(bx, by, bw, bh, TextCatalog.msg(self.lang, "ui.top_10"))
        scores = self.result_scores or get_top_scores(load_score_entries(), limit=10)
        y = by + 16
        for i, entry in enumerate(scores[:10], start=1):
            name = str(entry.get("player_name", "rogue"))[:8]
            score = int(entry.get("score", 0))
            self.txt(bx + 6, y, f"{i:>2} {score:>5} {name}", 9 if i != 1 else 10)
            y += 12
        if not scores:
            self.txt(bx + 6, y, TextCatalog.msg(self.lang, "ui.no_scores_yet"), 5)

    def draw_score_screen(self):
        bx,by=118,34; bw=340; bh=220
        self._box(bx, by, bw, bh)
        scores = self.result_scores or get_top_scores(load_score_entries(), limit=10)
        y = by + 14
        for i, line in enumerate(format_top_score_lines(scores)):
            self.txt(bx + 12, y, line, 10 if i == 0 else 9)
            y += 14
        if not scores:
            self.txt(bx + 12, y, TextCatalog.msg(self.lang, "ui.no_scores_yet"), 5)
        self.txt(bx + 12, by + bh - 18, TextCatalog.msg(self.lang, "ui.press_confirm_new_game"), 10)

    def draw_dead(self):
        if not self.options.get("tombstone", True):
            bx,by=105,42; bw=270; bh=190
            self._box(bx,by,bw,bh,"=== R.I.P. ===")
            p=self.p; x=bx+18; y=by+24
            self.txt(x,y,"Here lies a brave rogue.",7); y+=22
            self.txt(x,y,f"Cause: {self.death_cause or 'died'}",8); y+=18
            self.txt(x,y,f"Depth: {p.depth}",7); y+=14
            self.txt(x,y,f"Level: {p.level}",7); y+=14
            self.txt(x,y,f"Gold:  {p.gold}",10); y+=14
            next_exp=p.EXP_T[min(p.level,len(p.EXP_T)-1)]
            self.txt(x,y,f"Exp:   {p.exp}/{next_exp}",7); y+=14
            self.txt(x,y,f"Turn:  {self.turn}",5); y+=24
            self.txt(x,y,TextCatalog.msg(self.lang, "ui.press_confirm_scores"),10); y+=14
            self.txt(x,y,"B          Stay here",5)
            return
        bx,by=88,30; bw=320; bh=232
        self._box(bx,by,bw,bh,"=== R.I.P. ===")
        p=self.p; x=bx+18; y=by+24
        killer=(self.death_cause or "died").replace("killed by ","")
        name=self.options.get("name","rogue")
        year=time.localtime().tm_year
        rip=[
            "        __________",
            "       /          \\",
            "      /    REST    \\",
            "     /      IN      \\",
            "    /     PEACE      \\",
            "    |                |",
            f"    | {name[:14].center(14)} |",
            f"    | {str(p.gold) + ' Au':^14} |",
            "    |  killed by a  |",
            f"    | {killer[:14].center(14)} |",
            f"    | {str(year):^14} |",
            "   *|   *  *  *    |*",
            "____)/\\_//(\\/(/\\)/\\//\\|_)____",
        ]
        for ln in rip:
            self.txt(x,y,ln,7); y+=11
        y+=4
        self.txt(x,y,f"Depth: {p.depth}",7); y+=14
        self.txt(x,y,f"Level: {p.level}",7); y+=14
        next_exp=p.EXP_T[min(p.level,len(p.EXP_T)-1)]
        self.txt(x,y,f"Exp:   {p.exp}/{next_exp}",7); y+=14
        self.txt(x,y,f"Turn:  {self.turn}",5); y+=18
        self.txt(x,y,TextCatalog.msg(self.lang, "ui.press_confirm_scores"),10); y+=14
        self.txt(x,y,"B          Stay here",5)

    def draw_win(self):
        bx,by=82,50; bw=334; bh=176
        self._box(bx,by,bw,bh,"=== Victory ===")
        p=self.p; x=bx+18; y=by+26
        self.txt(x,y,"You escaped from the Dungeons of Doom",10); y+=16
        self.txt(x,y,"with the Amulet of Yendor.",10); y+=24
        self.txt(x,y,f"Gold:  {p.gold}",10); y+=14
        self.txt(x,y,f"Level: {p.level}",7); y+=14
        self.txt(x,y,f"Exp:   {p.exp}",7); y+=14
        self.txt(x,y,f"Turn:  {self.turn}",5); y+=28
        self.txt(x,y,TextCatalog.msg(self.lang, "ui.press_confirm_scores"),10)

    def draw_quit_confirm(self):
        bx,by=176,132; bw=224; bh=56
        self._box(bx,by,bw,bh,"-- Quit --")
        self.txt(bx+12, by+20, TextCatalog.msg(self.lang, "main.really_quit"), 10)
        self.txt(bx+12, by+34, TextCatalog.msg(self.lang, "ui.quit_confirm_hint"), 5)

    def draw_quit(self):
        bx,by=96,60; bw=300; bh=148
        self._box(bx,by,bw,bh,"=== Quit ===")
        p=self.p; x=bx+18; y=by+24
        self.txt(x,y,TextCatalog.msg(self.lang, "ui.you_quit_with_gold", gold=p.gold),10); y+=24
        self.txt(x,y,f"Depth: {p.depth}",7); y+=14
        self.txt(x,y,f"Level: {p.level}",7); y+=14
        self.txt(x,y,f"Turn:  {self.turn}",5); y+=26
        self.txt(x,y,TextCatalog.msg(self.lang, "ui.press_confirm_scores"),10)

# ===========================================================
if __name__=="__main__":
    Game()
