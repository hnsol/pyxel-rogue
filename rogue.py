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
import rogue_pack
import rogue_potions
import rogue_scrolls
import rogue_rings
import rogue_rooms
import rogue_search
import rogue_sticks
import rogue_things
import rogue_dungeon
import rogue_daemons
import rogue_armor
import rogue_chase
import rogue_fight
import rogue_food
import rogue_init
import rogue_levels
import rogue_misc
import rogue_move
import rogue_weapons
from rogue_combat_text import (
    MONSTER_HIT_MESSAGE_KEYS,
    MONSTER_MISS_MESSAGE_KEYS,
    PLAYER_HIT_MESSAGE_KEYS,
    PLAYER_MISS_MESSAGE_KEYS,
)
from rogue_items import (
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
from rogue_lang import DEFAULT_LANG, LANG_EN, LANG_JA, Settings
from rogue_layout import (
    DEAD_ZONE_X,
    DEAD_ZONE_Y,
    HUD_W,
    HUD_X,
    HUD_Y,
    MSG_COLS,
    MSG_LINES,
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
from rogue_map import (
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
from rogue_palettes import (
    DEFAULT_PALETTE,
    GBC_HIGH_CONTRAST_PALETTE,
    GBC_PALETTE,
    FLEXOKI_LIGHT_PALETTE,
    PALETTE_FLEXOKI_LIGHT,
    PALETTE_GBC,
    PALETTE_GBC_HIGH_CONTRAST,
    PALETTE_IDS,
    PALETTE_LABELS,
    PALETTES,
)
from rogue_scores import build_score_entry, format_top_score_lines, get_top_scores, load_score_entries, save_score_entry
from rogue_timing import (
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
from rogue_ui import (
    AUX_ACTIONS,
    BACK_TAP_FRAMES,
    B_TAP_FRAMES,
    CALL_PRESETS,
    MENU_ACTIONS,
    ST_AUX,
    ST_CALL,
    ST_DEAD,
    ST_DIR,
    ST_DISC,
    ST_HELP,
    ST_INVENTORY,
    ST_ITEM,
    ST_LOADING,
    ST_MENU,
    ST_PLAY,
    ST_QUIT,
    ST_QUIT_CONFIRM,
    ST_SCORE,
    ST_WIN,
)

RNG = RogueRng(random)
UI_BUILD = "260427_2002"

# ===========================================================
#  Font
# ===========================================================
_pyxel_dir = os.path.dirname(pyxel.__file__)
FONT_PATH = os.path.join(_pyxel_dir, "examples", "assets", "umplus_j10r.bdf")

INV_MAX = 26
DASH_INTERVAL = 1                # frames between dash steps
DEST_PLAYER = "player"
DEST_GOLD = "gold"
HELP_HEADER_COL = 31
HELP_TEXT_COL = 30

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
    rogue_weapons.apply_init_dam({"name":"mace","prob":11,"wield":True}, 0),
    rogue_weapons.apply_init_dam({"name":"long sword","prob":11,"wield":True}, 1),
    rogue_weapons.apply_init_dam({"name":"short bow","prob":12,"wield":True}, 2),
    rogue_weapons.apply_init_dam({"name":"arrow","prob":12,"wield":False}, 3),
    rogue_weapons.apply_init_dam({"name":"dagger","prob":8,"wield":True}, 4),
    rogue_weapons.apply_init_dam({"name":"two-handed sword","prob":10,"wield":True}, 5),
    rogue_weapons.apply_init_dam({"name":"dart","prob":12,"wield":False}, 6),
    rogue_weapons.apply_init_dam({"name":"shuriken","prob":12,"wield":False}, 7),
    rogue_weapons.apply_init_dam({"name":"spear","prob":12,"wield":True}, 8),
]

STR_PLUS = rogue_fight.STR_PLUS
ADD_DAM = rogue_fight.ADD_DAM

ARMORS = [
    {"name":"leather armor","prob":20,"ac":8},{"name":"ring mail","prob":15,"ac":7},
    {"name":"studded leather","prob":15,"ac":7},{"name":"scale mail","prob":13,"ac":6},
    {"name":"chain mail","prob":12,"ac":5},{"name":"splint mail","prob":10,"ac":4},
    {"name":"banded mail","prob":10,"ac":4},{"name":"plate mail","prob":5,"ac":3},
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
    MonsterSpec("M","medusa",8,2,"3x4/3x4/2x5",200,18,f"{rogue_monsters.FLAG_CAN_CONFUSE},mean", carry=40),
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
        s.flags=rogue_monsters.parse_flags(fl)
        s.held=s.scared=s.confused=0
        s.running=False; s.dest=DEST_PLAYER; s.turn=True
        s.mean=rogue_monsters.is_mean(s.flags); s.target=False; s.found=False; s.vf_hit=0
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
        s.ac = (s.arm.data["ac"]-s.arm.ench) if s.arm else 10
        s.ac -= rogue_rings.protection_bonus(s)
    def str_hit_plus(s):
        return rogue_fight.str_hit_plus(s.st)
    def str_dam_plus(s):
        return rogue_fight.str_dam_plus(s.st)
    def inv_full(s): return len(s.inv)>=INV_MAX
    def add_item(s,it):
        if not rogue_pack.pack_room_allows(len(s.inv), INV_MAX):
            return False
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
    return rogue_things.pick_one([(e["name"], e["prob"]) for e in tbl], RNG.rnd(sum(e["prob"] for e in tbl)))

def make_item(depth, no_food=0):
    cat=rogue_things.new_thing_category_roll(RNG.rnd, no_food)
    if cat=="potion": return Item(CAT_POT,wchoice(POTIONS))
    if cat=="scroll": return Item(CAT_SCR,wchoice(SCROLLS))
    if cat=="food": return Item(CAT_FOOD,rogue_things.new_thing_food_kind(RNG.rnd))
    if cat=="weapon":
        k=wchoice(WEAPONS)
        r=RNG.rnd(100)
        hit_plus,cursed=rogue_weapons.new_thing_weapon_enchant(r,RNG.rnd)
        q=rogue_weapons.initial_weapon_count(WEAPONS[k]["name"], WEAPONS[k].get("stack", False), RNG.rnd)
        return Item(CAT_WPN,k,hit_plus=hit_plus,dam_plus=0,cursed=cursed,qty=q,known=False)
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
    ar=Item(CAT_WPN,3,hit_plus=0,dam_plus=0,qty=rogue_init.initial_arrow_count(RNG.rnd))# arrows
    b=Item(CAT_WPN,2,hit_plus=1,dam_plus=0) # bow +1,+0
    f=Item(CAT_FOOD,0)              # ration
    return rogue_init.initial_pack_order(f,a,w,b,ar),w,a


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
        self.no_food = 0
        self.wander_timer = 0
        self.wander_between = 0
        self.delayed_actions = rogue_daemons.DelayedActionTable()
        self.fuses = self.delayed_actions.fuses
        self.daemons = self.delayed_actions.daemons
        self.daemons.start("runners", rogue_daemons.AFTER)
        self.daemons.start("doctor", rogue_daemons.AFTER)
        self.daemons.start("stomach", rogue_daemons.AFTER)
        self.haste_half_turn = False
        self.result_scores = []
        self.result_entry = None
        self.result_outcome = None
        self.descend()
        self.fuses.fuse("swander", RNG.spread(WANDERTIME), rogue_daemons.AFTER)
        self.wander_timer = self.fuses.remaining("swander")
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
        self.no_food = rogue_things.no_food_after_new_level(getattr(self, "no_food", 0))
        usable_rooms = self.usable_rooms()
        self.mons=[]; self.gitems=[]; self.traps={}; self.hidden_tiles={}
        self.visible=set(); self.explored=set()
        self.wander_timer=self.fuses.remaining("swander")
        px,py = self.random_room_tile(RNG.choice(usable_rooms), WALKABLE)
        self.p.x,self.p.y = px,py
        sr=RNG.choice(usable_rooms); sx,sy=self.random_room_tile(sr, WALKABLE); self.tm[sy][sx]=T_STAIR
        self._spawn_room_gold(); self._spawn_mons(); self._spawn_items(); self._spawn_amulet()
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
        # C: rooms.c:do_rooms()
        d=self.p.depth
        for rm in self.usable_rooms():
            if not rogue_dungeon.should_place_room_monster(RNG, self.room_has_gold(rm)):
                continue
            e=self.random_monster_spec(d)
            for _ in range(30):
                mx,my=self.random_room_tile(rm, WALKABLE)
                if self.tm[my][mx] in WALKABLE and not self.mon_at(mx,my) \
                   and not(mx==self.p.x and my==self.p.y):
                    monster=self.new_monster_from_spec(mx,my,e)
                    self.give_pack(monster)
                    self.mons.append(monster)
                    break

    def room_has_gold(self, room):
        return any(
            item.cat == CAT_GOLD
            and room.x <= item.x < room.x + room.w
            and room.y <= item.y < room.y + room.h
            for item in self.gitems
        )

    def spawn_wanderer(self):
        # C: monsters.c:wanderer()
        cands=self.wanderer_floor_candidates()
        if not cands:
            return False
        x,y=RNG.choice(cands)
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
            item = make_item(depth, before)
        except TypeError:
            item = make_item(depth)
        self.no_food = rogue_things.no_food_after_new_thing(item.cat, before)
        return item

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
        if not rogue_dungeon.should_put_things(self.p.has_amulet, d, getattr(self, "max_depth", d)):
            return
        rooms=self.usable_rooms()
        if rogue_dungeon.should_place_treasure_room(RNG):
            self._spawn_treasure_room()
        for _ in range(rogue_dungeon.put_things_item_count(RNG)):
            rm=RNG.choice(rooms)
            for _ in range(20):
                ix,iy=self.random_room_tile(rm, {T_FLOOR,T_CORR})
                if self.tm[iy][ix] in (T_FLOOR,T_CORR) and not self.gi_at(ix,iy):
                    it=self.make_game_item(d); it.x,it.y=ix,iy; self.gitems.append(it); break

    def _spawn_room_gold(self):
        # C: rooms.c:do_rooms()
        d=self.p.depth
        for rm in self.usable_rooms():
            if not rogue_dungeon.should_place_room_gold(RNG, self.p.has_amulet, d, getattr(self, "max_depth", d)):
                continue
            for _ in range(20):
                ix,iy=self.random_room_tile(rm, {T_FLOOR,T_CORR})
                if self.tm[iy][ix] in (T_FLOOR,T_CORR) and not self.gi_at(ix,iy):
                    g=Item(CAT_GOLD,0); g.qty=goldcalc(d); g.x,g.y=ix,iy
                    self.gitems.append(g); break

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
                    it=self.make_game_item(self.p.depth); it.x,it.y=ix,iy; self.gitems.append(it); break
        monster_depth=self.p.depth+1
        for _ in range(monster_count):
            for _ in range(rogue_dungeon.MAXTRIES):
                mx,my=self.random_room_tile(room,{T_FLOOR,T_CORR})
                if (self.tm[my][mx] in (T_FLOOR,T_CORR) and not self.gi_at(mx,my)
                        and not self.mon_at(mx,my) and (mx,my)!=(self.p.x,self.p.y)):
                    spec=self.monster_spec_for_sym(rogue_monsters.randmonster(monster_depth, RNG.rnd, wander=False))
                    monster=self.new_monster_from_spec(mx,my,spec,depth=monster_depth)
                    rogue_monsters.force_mean(monster)
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
            self.traps[(x,y)]=rogue_dungeon.trap_kind(RNG)

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
        return rogue_chase.dist_points(a, b)
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
        if rogue_fight.thrown_message_uses_weapon_name(it.cat):
            return TextCatalog.msg(self.lang,"fight.thrown_weapon_hits",item=item,target=target)
        return TextCatalog.msg(self.lang,"fight.you_hit_target",target=target)

    def thrown_miss_message(self,it,item,target):
        if rogue_fight.thrown_message_uses_weapon_name(it.cat):
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
        return rogue_fight.swing(at_lvl, op_arm, wplus, RNG.rnd)

    def player_weapon_profile(self, weap=None, thrown=False):
        hplus = dplus = 0
        damage = "1x4"
        if weap and weap.cat == CAT_WPN:
            data = weap.data
            damage, hplus, dplus = rogue_fight.weapon_profile(
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
        return damage, hplus, dplus

    def roll_player_attack(self, m, weap=None, thrown=False):
        # C: fight.c:roll_em()
        damage_expr, hplus, dplus = self.player_weapon_profile(weap, thrown)
        hplus = rogue_fight.hit_plus_vs_defender(hplus, m.running)
        hplus += self.p.str_hit_plus()
        return rogue_fight.roll_em_damage(
            damage_expr,
            lambda: self.swing_hits(self.p.level, m.armor, hplus),
            roll_damage_expr,
            dplus,
            self.p.str_dam_plus(),
        )

    def roll_monster_attack(self, m):
        # C: fight.c:roll_em()
        hplus = rogue_fight.hit_plus_vs_defender(0, rogue_fight.player_defender_running(self.p.no_command))
        return rogue_fight.roll_em_damage(
            m.damage_expr,
            lambda: self.swing_hits(m.level, self.p.ac, hplus),
            roll_damage_expr,
            0,
            0,
        )

    def award_monster_kill(self, m, translated_name=None):
        # C: fight.c:killed()
        mn = translated_name or TextCatalog.monster(self.lang,m.name)
        self.p.exp+=m.exp
        if self.p.held_by is m:
            m.vf_hit, m.damage_expr = rogue_fight.venus_flytrap_release()
            self.p.held_by=None
        if m.sym == "L" and self.p.depth >= getattr(self, "max_depth", self.p.depth):
            gold = Item(CAT_GOLD, 0)
            first_gold = goldcalc(self.p.depth)
            gold.qty = rogue_fight.leprechaun_kill_gold_after_first(first_gold, self.p.depth, self.save_vs_magic(), goldcalc)
            m.pack.append(gold)
        if self.p.lvlup():
            self.msg("misc.welcome_to_level_level", level=self.p.level)
        self.remove_monster(m, was_kill=True)
        return mn

    def p_attack(self, m):
        # C: fight.c:fight()
        self.dashing = False
        self.p.quiet = 0
        self.runto(m)
        if self.reveal_xeroc_for_attack(m, thrown=False):
            return
        mn=self.combat_monster_name(m)
        hit,dmg=self.roll_player_attack(m,self.p.wpn,False)
        if hit:
            m.hp-=dmg
            self.msg_text(self.player_hit_message(mn))
            self.p.can_confuse_monster, confused_by_hit = rogue_fight.confusion_hit_effect(self.p.can_confuse_monster)
            if confused_by_hit:
                m.confused=1
                self.msg("fight.your_hands_stop_glowing_color", color="red")
            if not m.alive:
                self.msg_text(self.defeated_message(mn))
                self.award_monster_kill(m,mn)
            elif rogue_fight.confusion_message_allowed(confused_by_hit, self.p.blind > 0):
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
        return rogue_fight.magic_item_to_steal(
            self.p.inv,
            {self.p.wpn, self.p.arm, self.p.ring_l, self.p.ring_r},
            self.is_magic_item,
            rnd,
        )

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
        rogue_chase.runto(m, dest)

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
                self.msg("pyxel.monster_gaze_confused", monster=mn)
        if rogue_monsters.is_greedy(m) and not m.running:
            self.runto(m,DEST_GOLD if self.room_gold_target(m) else DEST_PLAYER)

    def wake_visible_monsters(self):
        for mo in self.mons:
            if (mo.x,mo.y) in self.visible:
                self.wake_monster(mo)

    def can_see_monster(self, m):
        # C: chase.c:see_monst()
        return rogue_chase.see_monst(
            self.p.blind > 0,
            rogue_monsters.is_invisible(m),
            self.p.see_invisible > 0 or rogue_rings.is_wearing(self.p, rogue_rings.R_SEEINVIS),
        )

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
        self.dashing = False
        self.p.quiet = 0
        if rogue_monsters.is_disguised_xeroc(m) and self.p.blind <= 0:
            rogue_monsters.reveal_disguise(m)
        mn=self.combat_monster_name(m,upper=True)
        hit,dmg=self.roll_monster_attack(m)
        if hit:
            if dmg:
                self.p.hp-=dmg
            if rogue_fight.monster_attack_message_allowed(m.sym):
                self.msg_text(self.monster_hit_message(mn))
            if self.p.hp<=0 and not self.death_cause: self.death_cause=f"killed by a {m.name}"
            if not rogue_monsters.is_cancelled(m):
                if rogue_monsters.has_special(m, "rust") and self.can_rust_armor(self.p.arm):
                    self.rust_armor()
                if rogue_monsters.has_special(m, "steal_gold"):
                    old_gold = self.p.gold
                    first_loss = goldcalc(self.p.depth)
                    loss=rogue_fight.leprechaun_gold_loss_after_first(first_loss, self.p.depth, self.save_vs_magic(), goldcalc)
                    self.p.gold=max(0,self.p.gold-loss)
                    if self.p.gold != old_gold:
                        self.msg("fight.your_purse_feels_lighter")
                    self.remove_monster(m); return
                if rogue_monsters.has_special(m, "poison"):
                    self.p.st, poison_result = rogue_fight.poison_bite_strength(
                        self.p.st,
                        self.save_vs_poison(),
                        rogue_rings.is_wearing(self.p, rogue_rings.R_SUSTSTR),
                    )
                    if poison_result == "weakened":
                        self.msg("fight.you_feel_a_bite_in_your_leg_and_now_feel_weaker")
                    elif poison_result == "sustained":
                        self.msg("fight.a_bite_momentarily_weakens_you")
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
                    self.msg("fight.you_suddenly_feel_weaker")
                if rogue_monsters.has_special(m, "drain") and rogue_fight.drain_hits("V", rnd):
                    self.p.hp, self.p.max_hp, died = rogue_fight.max_hp_drain(
                        self.p.hp, self.p.max_hp, lambda: roll("1d3")
                    )
                    if died:
                        self.p.hp = 0
                        self.death_cause = f"killed by a {m.name}"
                        return
                    self.msg("fight.you_suddenly_feel_weaker")
                if rogue_monsters.has_special(m, "confuse") and not self.save_vs_magic():
                    self.p.confused=RNG.randint(10,20); self.msg("pyxel.feel_confused_bang")
                if rogue_monsters.has_special(m, "freeze"):
                    self.p.no_command, should_message, hypothermia = rogue_fight.ice_freeze(
                        self.p.no_command, BORE_LEVEL, rnd
                    )
                    if hypothermia:
                        self.p.hp=0; self.death_cause="hypothermia"
                    if should_message:
                        self.msg("fight.you_are_frozen")
                if rogue_monsters.has_special(m, "hold"):
                    m.vf_hit, m.damage_expr = rogue_fight.venus_flytrap_hit(m.vf_hit)
                    self.p.held_by=m
                    self.p.hp-=1
                    if self.p.hp<=0 and not self.death_cause: self.death_cause=f"killed by a {m.name}"
                if rogue_monsters.has_special(m, "steal_item"):
                    t=self.monster_has_magic_item_to_steal()
                    if t:
                        self.p.rm_item(t); self.msg("fight.she_stole_target", target=self.ident.name(t))
                        self.remove_monster(m); return
        else:
            if m.sym == "F" and m.vf_hit > 0:
                self.p.hp = rogue_fight.venus_flytrap_miss_hp(self.p.hp, m.vf_hit)
                if self.p.hp<=0 and not self.death_cause: self.death_cause=f"killed by a {m.name}"
            if rogue_fight.monster_attack_message_allowed(m.sym):
                self.msg_text(self.monster_miss_message(mn))

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
        dest=self.find_dest(m)
        rer=self.room_for_ai(m.x,m.y,actor=True)
        ree=rogue_chase.destination_room(
            dest == (self.p.x, self.p.y),
            self.room_for_ai(self.p.x,self.p.y,actor=True),
            self.room_for_ai(dest[0],dest[1],actor=False),
        )
        chase_dest=dest
        if rer!=ree and hasattr(rer,"x"):
            chase_dest = rogue_chase.nearest_exit_to_dest(
                self.room_exits(rer),
                dest,
                self.dist2,
            ) or chase_dest
        elif self.try_dragon_breath(m):
            return 0
        moved_or_attack=self.chase(m,chase_dest)
        if moved_or_attack=="attack":
            return 0
        if m.dest!=DEST_PLAYER and (m.x,m.y)==dest:
            self.collect_monster_dest(m,dest)
        return 0

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
        self.dashing=False
        self.p.quiet=0
        self.fire_bolt_from(m.x,m.y,sx,sy,"flame")
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
            {mo.dest for mo in self.mons if mo is not m},
            lambda item: self.room_for_ai(item.x, item.y),
            lambda item: (item.x, item.y),
            self.is_scare_monster,
            RNG.rnd,
        )
        if target:
            return (target.x, target.y)
        return (self.p.x,self.p.y)

    def collect_monster_dest(self,m,dest):
        gi=self.gi_at(*dest)
        if gi and gi.cat==CAT_GOLD:
            self.gitems.remove(gi)
            m.dest=DEST_PLAYER

    def random_monster_move(self,m):
        # C: move.c:rndmove()
        return rogue_move.rndmove(
            (m.x, m.y),
            rnd,
            lambda src, dst: self.can_monster_step(m, dst[0], dst[1])
            and self.diag_ok(src[0], src[1], dst[0], dst[1]),
        )

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
        if rogue_monsters.has_special(m, "regen") and m.hp<m.max_hp and RNG.random()<.3: m.hp+=1
        if rogue_chase.should_random_move(m.confused, m.sym, rnd):
            nx,ny=self.random_monster_move(m)
            if (nx,ny)==(px,py):
                self.m_attack(m); return "attack"
            m.x,m.y=nx,ny
            if rogue_chase.confusion_clears_after_random_move(m.confused, rnd): m.confused=0
            return "move"
        cur=self.dist2((m.x,m.y),dest)
        best=(m.x,m.y); bestd=cur; ties=1
        for dx,dy in DIR8.values():
            nx,ny=m.x+dx,m.y+dy
            diagonal_ok=self.diag_ok(m.x,m.y,nx,ny)
            if not diagonal_ok:
                continue
            if (nx,ny)==(px,py):
                if dest==(px,py):
                    self.m_attack(m); return "attack"
                continue
            gi=self.gi_at(nx,ny)
            if not rogue_chase.is_chase_candidate(
                diagonal_ok,
                self.walkable(nx,ny) and not self.mon_at(nx,ny),
                bool(gi and self.is_scare_monster(gi)),
                False,
            ):
                continue
            d=self.dist2((nx,ny),dest)
            best,bestd,ties=rogue_chase.choose_chase_step(best,bestd,ties,(nx,ny),d,rnd)
        if best!=(m.x,m.y):
            m.x,m.y=best
        return "move" if rogue_chase.chase_continues(bestd, best, (px, py)) else "arrived"

    # ---------- Item effects ----------
    def use_pot(self,it):
        # C: potions.c:quaff()
        p=self.p; nm=POTIONS[it.kind]["name"]
        if nm=="healing":
            self.ident.pk[it.kind]=True
            h=RNG.roll(p.level,4)
            p.hp,p.max_hp=rogue_potions.healing_hp(p.hp,p.max_hp,h)
            self.sight()
            self.msg("potions.you_begin_to_feel_better")
        elif nm=="extra healing":
            self.ident.pk[it.kind]=True
            h=RNG.roll(p.level,8)
            p.hp,p.max_hp=rogue_potions.extra_healing_hp(p.hp,p.max_hp,p.level,h)
            self.sight()
            self.come_down()
            self.msg("potions.you_begin_to_feel_much_better")
        elif nm=="poison":
            self.ident.pk[it.kind]=True
            if rogue_rings.is_wearing(p, rogue_rings.R_SUSTSTR):
                self.msg("potions.you_feel_momentarily_sick")
            else:
                l=RNG.randint(1,3); p.st=rogue_potions.poison_strength(p.st,l); self.msg("potions.you_feel_very_sick_now")
                self.come_down()
        elif nm=="gain strength":
            self.ident.pk[it.kind]=True; p.st,p.max_st=rogue_potions.gain_strength(p.st,p.max_st); self.msg("potions.you_feel_stronger_now_what_bulging_muscles")
        elif nm=="restore strength":
            # Rogue 5.4.4 potions.c:P_RESTORE temporarily removes R_ADDSTR before restoring max_stats.s_str.
            addstr = sum(r.ench for r in (p.ring_l, p.ring_r) if rogue_rings.is_ring(r, rogue_rings.R_ADDSTR))
            p.st = rogue_potions.restore_strength(p.st, p.max_st, addstr)
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
            self.sight()
        elif nm=="raise level":
            self.ident.pk[it.kind]=True
            p.exp=rogue_levels.raise_level_exp(p.level,p.EXP_T)
            self.msg("potions.you_suddenly_feel_much_more_skillful")
            if p.lvlup():
                self.msg("misc.welcome_to_level_level", level=p.level)
        elif nm=="monster detection":
            if p.see_monsters > 0:
                self.fuses.fuse("turn_see", HUHDURATION, rogue_daemons.AFTER)
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
        result = rogue_misc.add_haste_result(self.p.haste > 0, potion, rnd)
        if not result.ok:
            self.p.no_command += result.no_command_add
            self.p.haste = 0
            self.haste_half_turn = False
            self.fuses.extinguish("nohaste")
            self.msg("misc.you_faint_from_exhaustion")
            return False
        self.p.haste = 1
        self.haste_half_turn = False
        if potion:
            self.p.haste = result.duration
            self.fuses.fuse("nohaste", result.duration, rogue_daemons.AFTER)
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
        self.fuses.extinguish("sight")
        self.p.blind = 0
        self.update_fov()
        self.msg("daemons.far_out_everything_is_all_cosmic_again" if self.p.hallucinating > 0 else "daemons.the_veil_of_darkness_lifts")

    def is_magic_item(self, it):
        # Rogue 5.4.4 potions.c:is_magic().
        return rogue_potions.is_magic_item(
            it.cat,
            it.cat == CAT_WPN and (it.hit_plus != 0 or it.dam_plus != 0),
            it.cat == CAT_ARM and (it.protected or it.ench != 0),
        )

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
        return rogue_scrolls.identify_target_cats(nm, sys.modules[__name__])

    def use_scr(self,it):
        # C: scrolls.c:read_scroll()
        p=self.p; nm=SCROLLS[it.kind]["name"]; self.ident.sk[it.kind]=nm not in ("monster confusion","scare monster","food detection","teleportation","enchant weapon","create monster","remove curse","aggravate monsters","protect armor","hold monster","enchant armor")
        if nm=="monster confusion":
            rogue_scrolls.monster_confusion(p)
            self.msg("scrolls.your_hands_begin_to_glow_color", color="red")
        elif nm.startswith("identify "):
            cats = self.identify_scroll_target_cats(nm)
            self.msg("scrolls.this_scroll_is_an_item_scroll", item=nm)
            p.rm_item(it)
            unid=[i for i in p.inv if i.cat in cats and self.needs_identify(i)]
            if unid:
                # Interactive target selection (Rogue 5.4.4 wizard.c:whatis()).
                self.fitems=unid; self.icur=0; self.cact="Identify"; self.st=ST_ITEM
                return True  # Caller must NOT call close_menu()/end_turn() yet.
            else:
                self.msg("pyxel.feel_vaguely_uneasy")
        elif nm=="enchant weapon":
            if rogue_scrolls.enchant_weapon(p.wpn, RNG.rnd):
                self.msg("scrolls.your_color_glows_color2_for_a_moment", color=p.wpn.data["name"], color2="blue")
            else: self.msg("scrolls.you_feel_a_strange_sense_of_loss")
        elif nm=="enchant armor":
            if rogue_scrolls.enchant_armor(p.arm):
                p.recalc_ac(); self.msg("scrolls.your_armor_glows_color_for_a_moment", color="silver")
            else: self.msg("scrolls.you_feel_a_strange_sense_of_loss")
        elif nm=="remove curse":
            rogue_scrolls.remove_curse_equipment((p.arm, p.wpn, p.ring_l, p.ring_r))
            self.msg("scrolls.you_feel_in_touch_with_the_universal_onenes" if p.hallucinating > 0 else "scrolls.you_feel_as_if_somebody_is_watching_over_you")
        elif nm=="aggravate monsters":
            self.aggravate_monsters(); self.msg("scrolls.you_hear_a_high_pitched_humming_noise")
        elif nm=="scare monster":
            self.msg("scrolls.you_hear_maniacal_laughter_in_the_distance")
        elif nm=="sleep":
            rogue_scrolls.sleep_scroll(p, rnd, SLEEPTIME); self.dashing=False; self.msg("scrolls.you_fall_asleep")
        elif nm=="teleportation":
            old_room = self.room_at(p.x, p.y)
            r=RNG.choice(self.usable_rooms()); p.x,p.y=self.random_room_tile(r, WALKABLE); self.update_fov(); self._center_cam()
            if rogue_scrolls.teleport_identifies(old_room, self.room_at(p.x, p.y)):
                self.ident.sk[it.kind]=True
            self.finish_teleport()
        elif nm=="create monster":
            candidates = []
            for dy in (-1,0,1):
                for dx in (-1,0,1):
                    if dx==0 and dy==0:
                        continue
                    nx,ny=p.x+dx,p.y+dy
                    if self.walkable(nx,ny) and not self.mon_at(nx,ny):
                        gi=self.gi_at(nx,ny)
                        if gi and self.is_scare_scroll(gi):
                            continue
                        candidates.append((nx, ny))
            pick = rogue_scrolls.choose_create_monster_pos(p, candidates, RNG.rnd)
            if pick:
                nx,ny=pick
                spec = self.monster_spec_for_sym(rogue_monsters.randmonster(p.depth, RNG.rnd, wander=False))
                if spec:
                    self.mons.append(self.new_monster_from_spec(nx,ny,spec))
                    if rogue_rings.is_wearing(p, rogue_rings.R_AGGR):
                        self.runto(self.mons[-1])
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
            held_count = rogue_scrolls.hold_monsters(p, self.mons, lambda mo: RNG.randint(10,20))
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
        self.dashing = False
        self.dash_steps = 0

    def polymorph_monster(self,m):
        # C: sticks.c (WS_POLYMORPH)
        pack=m.pack
        spec=self.monster_spec_for_sym(chr(RNG.rnd(26)+ord("A")))
        if spec:
            self.set_monster_from_spec(m,spec)
            m.pack=pack

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
        rogue_monsters.cancel_monster(m)
        if self.p.held_by is m:
            self.p.held_by=None
        m.vf_hit=0

    def drain_targets(self):
        proom=self.room_for_ai(self.p.x,self.p.y,actor=True)
        return [m for m in self.mons if m.alive and self.same_ai_room(self.room_for_ai(m.x,m.y,actor=True),proom)]

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
        self.msg_text(self.thrown_hit_message(Item(CAT_STICK, rogue_sticks.WS_MISSILE), "magic missile", mn))
        self.p.can_confuse_monster, confused_by_hit = rogue_fight.confusion_hit_effect(self.p.can_confuse_monster)
        if confused_by_hit:
            m.confused = 1
            self.msg("fight.your_hands_stop_glowing_color", color="red")
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
        self.msg_text(self.thrown_hit_message(Item(CAT_WPN, 0), name, mn))
        self.p.can_confuse_monster, confused_by_hit = rogue_fight.confusion_hit_effect(self.p.can_confuse_monster)
        if confused_by_hit:
            m.confused = 1
            self.msg("fight.your_hands_stop_glowing_color", color="red")
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
                    self.msg("sticks.you_are_hit_by_the_value", value=name)
                    return True
                self.msg("sticks.the_value_whizzes_by_you", value=name)
            if rogue_sticks.bolt_should_bounce(self.bolt_bounces_at(x,y), (x,y)==(self.p.x,self.p.y)):
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
                wake_miss, show_miss = rogue_sticks.saved_monster_miss_feedback(
                    hero_started,
                    rogue_monsters.is_disguised_xeroc(target),
                )
                if wake_miss:
                    self.runto(target)
                if show_miss:
                    self.msg("sticks.the_value_whizzes_past_value2", value=name, value2=self.combat_monster_name(target))
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
        self.p.food, outcome, exp_gain = rogue_food.eat_food(
            self.p.food, it.kind, RNG.rnd, RNG.rnd, HUNGERTIME, STOMACHSIZE
        )
        self.p.state="normal"
        if outcome == "slime-mold":
            self.msg("misc.my_that_was_a_yummy_value", value="slime-mold")
        elif outcome == "awful":
            self.p.exp += exp_gain
            self.msg("misc.value_this_food_tastes_awful", value="yuk")
            if self.p.lvlup():
                self.msg("misc.welcome_to_level_level", level=self.p.level)
        else:
            self.msg("misc.value_that_tasted_good", value="yum")
        self.p.rm_item(it)

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
                if not (0<=xx<MAP_W and 0<=yy<MAP_H): continue
                if self.mon_at(xx,yy) or self.gi_at(xx,yy): continue
                tile_name = "PASSAGE" if self.tm[yy][xx] == T_CORR else "FLOOR" if self.tm[yy][xx] == T_FLOOR else ""
                if not rogue_weapons.is_fallpos_candidate((xx,yy), (self.p.x,self.p.y), tile_name):
                    continue
                choice,cnt=rogue_weapons.choose_fallpos(choice,cnt,(xx,yy),RNG.rnd)
        return choice

    def drop_thrown(self,it,x,y,around=True):
        # C: weapons.c:fall()
        pos=self.fall_position(x,y) if around else None
        pos=pos or ((x,y) if self.walkable(x,y) and not self.gi_at(x,y) else None)
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
            self.p.can_confuse_monster, confused_by_hit = rogue_fight.confusion_hit_effect(self.p.can_confuse_monster)
            if confused_by_hit:
                m.confused = 1
                self.msg("fight.your_hands_stop_glowing_color", color="red")
            if not m.alive:
                self.msg_text(self.defeated_message(mn))
                self.award_monster_kill(m, mn)
            elif rogue_fight.confusion_message_allowed(confused_by_hit, self.p.blind > 0):
                self.msg("fight.subject_appears_confused", subject=mn)
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
        probinc=rogue_search.search_probinc(p.hallucinating>0, p.blind>0)
        for dx,dy in dirs:
            nx,ny=p.x+dx,p.y+dy
            if 0<=nx<MAP_W and 0<=ny<MAP_H:
                hidden=self.hidden_tiles.get((nx,ny))
                if hidden==T_DOOR and rogue_search.reveals_secret_door(rnd(5+probinc), probinc):
                    found = self.reveal_hidden_at(nx,ny) or found
                elif hidden==T_CORR and rogue_search.reveals_secret_passage(rnd(3+probinc), probinc):
                    found = self.reveal_hidden_at(nx,ny) or found
                elif (nx,ny) in self.traps and self.tm[ny][nx]!=T_TRAP and rogue_search.reveals_trap(rnd(2+probinc), probinc):
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

    def trap_hits(self, at_lvl):
        # C: move.c:be_trapped() uses pstats.s_arm, not cur_armor->o_arm.
        return self.swing_hits(at_lvl, 10, 1)

    def save_vs_poison(self):
        return rogue_monsters.save_throw(0,self.p.level,RNG.roll)

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
            self.p.no_move=rogue_move.bear_trap_no_move(self.p.no_move, BEARTIME)
            self.msg("move.you_are_caught_in_a_bear_trap")
        elif name=="sleeping gas trap":
            self.p.no_command=rogue_move.sleep_trap_no_command(self.p.no_command, SLEEPTIME)
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
                poison_saved = self.save_vs_poison()
                self.p.st = rogue_move.dart_poison_strength(
                    self.p.st,
                    poison_saved,
                    rogue_rings.is_wearing(self.p, rogue_rings.R_SUSTSTR),
                )
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
        result = rogue_move.rust_armor_result(
            arm.protected,
            rogue_rings.is_wearing(self.p, rogue_rings.R_SUSTARM),
        )
        if result == "vanish":
            self.msg("move.the_rust_vanishes_instantly")
            return
        arm.ench-=1
        self.p.recalc_ac()
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
        if self.is_scare_monster(gi):
            scare_result=rogue_pack.scare_scroll_pickup_result(gi.picked_up)
            if scare_result=="dust":
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
        self.do_before_daemons()
        if self.p.no_command>0:
            self.p.no_command-=1
            if self.p.no_command==0:
                self.msg("command.you_can_move_again")
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
            self.msg("pyxel.died_restart"); self.enter_result_state("killed")
        self.turn_msg_start = len(self.msgs)

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
            self.p.see_monsters = 0
        elif name == "unsee":
            self.p.see_invisible = 0
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
            RNG.spread(WANDERTIME),
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

    def run_runners(self):
        # C: chase.c:runners()
        rogue_chase.runners(self.mons, self.m_turn)

    def run_stomach(self):
        # C: daemons.c:stomach()
        old_state = self.p.state
        m=self.p.hunger()
        if m:
            self.msg(m)
        if rogue_daemons.stomach_stops_running(old_state, self.p.state):
            self.dashing=False
        if self.p.hp<=0 and not self.death_cause:
            self.death_cause="starved to death"

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
