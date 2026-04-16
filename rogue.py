"""
PYXEL ROGUE  Phase 3
Faithful Rogue 5.4 clone  ·  Shiren-style controls  ·  BDF font

Gamepad:                        Keyboard:
  D-pad        Move (8-dir)      Arrow / HJKL   Move
  Start tap    Diag assist       YUBN           Diagonal
  B + D-pad    Dash (run)        Shift+dir      Dash
  A            Action/Search     Z / Enter      Action
  B tap        Menu/Cancel       Esc            Cancel
  A + B        Wait a turn       . (period)     Wait
  Back         Assist menu       Tab            Assist menu
  Back + A     Quick throw       Tab + Z        Quick throw
  Back + B     Search            S              Search
                                I              Status
                                ?              Help
"""

import pyxel
import random
import os

LANG_EN = "en"
LANG_JA = "ja"
DEFAULT_LANG = os.environ.get("PYXEL_ROGUE_LANG", LANG_EN).lower()
if DEFAULT_LANG not in (LANG_EN, LANG_JA):
    DEFAULT_LANG = LANG_EN

# ===========================================================
#  Font
# ===========================================================
_pyxel_dir = os.path.dirname(pyxel.__file__)
FONT_PATH = os.path.join(_pyxel_dir, "examples", "assets", "umplus_j10r.bdf")

# ===========================================================
#  Map
# ===========================================================
MAP_W, MAP_H = 48, 24
GRID_C, GRID_R = 3, 3
SEC_W, SEC_H = MAP_W // GRID_C, MAP_H // GRID_R
RM_MIN_W, RM_MAX_W = 5, 12
RM_MIN_H, RM_MAX_H = 4, 7

# Tiles
T_VOID, T_FLOOR, T_HWALL, T_VWALL, T_DOOR, T_CORR, T_STAIR, T_TRAP = range(8)
TILE_CH = {
    T_VOID: (" ", 0), T_FLOOR: (".", 5), T_HWALL: ("-", 6),
    T_VWALL: ("|", 6), T_DOOR: ("+", 9), T_CORR: ("#", 5),
    T_STAIR: ("%", 10), T_TRAP: ("^", 8),
}
WALKABLE = {T_FLOOR, T_DOOR, T_CORR, T_STAIR, T_TRAP}

# ===========================================================
#  Screen layout  (BDF j10r: ASCII 6×~10 px)
# ===========================================================
SCR_W, SCR_H = 512, 320
TILE_W, TILE_H = 7, 12          # per-char cell in zoom view
ZV_COLS, ZV_ROWS = MAP_W, MAP_H # full 48×24 dungeon view
ZV_PX_W = ZV_COLS * TILE_W      # 336
ZV_PX_H = ZV_ROWS * TILE_H      # 288
DEAD_ZONE_X = 8                  # camera edge zone; leaves ~50% center still
DEAD_ZONE_Y = 5

# Main view + right HUD
ZV_X, ZV_Y = 4, 4                # top-left pixel of full dungeon view
HUD_X = ZV_X + ZV_PX_W + 10
HUD_Y = ZV_Y
HUD_W = SCR_W - HUD_X - 4

# Messages
MSG_LINES = 2
MSG_X, MSG_Y = 4, SCR_H - MSG_LINES * TILE_H - 2
MSG_COLS = (SCR_W - MSG_X * 2) // 6

INV_MAX = 26
DASH_INTERVAL = 3                # frames between dash steps
HUNGERTIME = 1300
MORETIME = 150
STOMACHSIZE = 2000
STARVETIME = 850
MAX_TRAPS = 10
BEARTIME = 3
SLEEPTIME = 5

# ===========================================================
#  UI states
# ===========================================================
ST_PLAY = 0; ST_MENU = 1; ST_ITEM = 2; ST_DIR = 3
ST_DEAD = 4; ST_STATUS = 5; ST_HELP = 6
ST_AUX = 7

# ===========================================================
#  Item categories
# ===========================================================
CAT_POT = "pot"; CAT_SCR = "scr"; CAT_FOOD = "food"
CAT_WPN = "wpn"; CAT_ARM = "arm"; CAT_GOLD = "gold"
ISYM = {CAT_POT:"!",CAT_SCR:"?",CAT_FOOD:":",CAT_WPN:")",CAT_ARM:"]",CAT_GOLD:"*"}
ICOL = {CAT_POT:12,CAT_SCR:7,CAT_FOOD:4,CAT_WPN:7,CAT_ARM:7,CAT_GOLD:10}

# ===========================================================
#  Text catalog
# ===========================================================
POT_JA = {
    "healing":"体力が回復する", "extra healing":"体力がとても回復する",
    "poison":"毒の", "gain strength":"強さが増す",
    "restore strength":"強さが元にもどる", "confusion":"頭が混乱する",
    "blindness":"目が見えなくなる", "haste self":"素早くなる",
    "see invisible":"見えないものが見える", "raise level":"経験が増す",
    "detect monster":"遠くの怪物がわかる", "magic detection":"遠くのものがわかる",
}
SCR_JA = {
    "identify":"持ちものの種類がわかる", "enchant weapon":"武器に魔法をかける",
    "enchant armor":"よろいに魔法をかける", "remove curse":"のろいを解く",
    "aggravate monsters":"怪物を怒らせる", "scare monster":"怪物を近寄せない",
    "sleep":"眠りにおちる", "teleportation":"テレポートする",
    "create monster":"怪物を作りだす", "magic mapping":"魔法の地図の",
    "hold monster":"怪物を封じこめる", "blank paper":"白紙の",
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
MONSTER_JA = {
    "aquator":"水ごけの怪物", "bat":"大こうもり", "centaur":"ケンタウロス",
    "dragon":"ドラゴン", "emu":"大うずら", "venus flytrap":"はえとりぐさ",
    "griffin":"翼ライオン", "hobgoblin":"小鬼", "ice monster":"氷の怪物",
    "jabberwock":"巨大トカゲ", "kestrel":"大はやぶさ",
    "leprechaun":"金持ち妖精", "medusa":"メデューサ", "nymph":"ニンフ",
    "orc":"欲ばり鬼", "phantom":"幽霊", "quagga":"大つのじか",
    "rattlesnake":"がらがらへび", "snake":"へび", "troll":"巨人",
    "ur-vile":"一角獣", "vampire":"バンパイア", "wraith":"死霊",
    "xeroc":"物まねの怪物", "yeti":"雪男", "zombie":"ゾンビ",
}
POT_COLOR_JA = {
    "blue":"青い", "red":"赤い", "green":"緑の", "grey":"灰色の",
    "brown":"茶色の", "clear":"透明な", "pink":"ピンクの",
    "white":"白い", "purple":"紫の", "yellow":"黄色い",
    "plaid":"水色の", "amber":"琥珀色の",
}

class TextCatalog:
    MSG = {
        LANG_EN: {},
        LANG_JA: {
            "Welcome to the Dungeons of Doom!":"やあ、ローグ。 運命の洞窟へようこそ...",
            "You feel hungry.":"空腹になってきた。",
            "You are weak.":"空腹のせいで力がなくなってきた。",
            "You faint from lack of food.":"空腹で、目がくらくらする。",
            "You starve to death.":"空腹で、もう死にそうだ。",
            "You find nothing.":"何も見つからなかった。",
            "You found something!":"何かを見つけた！",
            "no trap there":"そこには罠はない。",
            "You have found {trap}.":"{trap}を見つけている。",
            "you fell into a trap!":"落とし穴に落ちた！",
            "you are caught in a bear trap":"くくり罠にかかった。",
            "a strange white mist envelops you and you fall asleep":"白い霧に包まれ、眠ってしまった。",
            "oh no! An arrow shot you":"矢に撃たれた！",
            "an arrow shoots past you":"矢がかすめて飛んでいった。",
            "a small dart just hit you in the shoulder":"小さな毒矢が肩に刺さった。",
            "a small dart whizzes by your ear and vanishes":"小さな毒矢が耳元をかすめて消えた。",
            "a gush of water hits you on the head":"水しぶきが頭に降りかかった。",
            "the rust vanishes instantly":"さびはすぐに消えた。",
            "your armor weakens":"よろいが弱くなった。",
            "you are suddenly in a parallel dimension":"突然、別の次元に迷い込んだ。",
            "the light in here suddenly seems {color}":"あたりの光が突然{color}に見えた。",
            "you feel a sting in the side of your neck":"首筋にちくりと痛みを感じた。",
            "multi-colored lines swirl around you, then fade":"色とりどりの線が渦巻き、やがて消えた。",
            "a {color} light flashes in your eyes":"{color}の光が目の前で閃いた。",
            "a spike shoots past your ear!":"トゲが耳元を飛び抜けた！",
            "{color} sparks dance across your armor":"{color}の火花がよろいの上で踊った。",
            "you suddenly feel very thirsty":"突然、とても喉が渇いた。",
            "you feel time speed up suddenly":"時間が急に速くなったように感じた。",
            "time now seems to be going slower":"時間がゆっくり流れているように感じる。",
            "your pack turns {color}!":"荷物が{color}に変わった！",
            "Nothing here.":"ここには、何もない。",
            "pack too full":"もうこれ以上、物は持てない。",
            "the scroll turns to dust as you pick it up":"巻き物は拾うと灰になった。",
            "Pickup ON.":"自動拾い ON。",
            "Pickup OFF.":"自動拾い OFF。",
            "Language: English.":"Language: English.",
            "Language: Japanese.":"言語: 日本語。",
            "Diagonal assist ON.":"斜め補助モード ON。",
            "Diagonal assist OFF.":"斜め補助モード OFF。",
            "You died... [A/Start] to restart.":"あなたは死んだ... [A/Start] で再開。",
            "You defeated the {monster}. ({exp} exp)":"{monster}を倒した。 ({exp} exp)",
            "Welcome to level {level}!":"レベル{level}へようこそ。",
            "You hit the {monster} ({dmg}).":"{monster}への攻撃は命中した。 ({dmg})",
            "You miss the {monster}.":"{monster}への攻撃はそれた。",
            "The {monster} hits! ({dmg})":"{monster}の攻撃は命中した。 ({dmg})",
            "The {monster} misses.":"{monster}の攻撃はそれた。",
            "{gold} gold pieces":"{gold}個の金塊",
            "You see a {item} here.":"{item}の上にいる。",
            "You pick up the {item}.":"{item}を手に入れた。",
        },
    }
    MENU = {
        LANG_EN: {
            "Quaff":"Quaff", "Read":"Read", "Eat":"Eat", "Wield":"Wield",
            "Wear":"Wear", "Take off":"Take off", "Throw":"Throw", "Drop":"Drop",
            "Status":"Status", "Help":"Help", "Search":"Search", "Pickup":"Pickup",
            "Trap":"Trap", "Language":"Language",
        },
        LANG_JA: {
            "Quaff":"飲む", "Read":"読む", "Eat":"食べる", "Wield":"武器にする",
            "Wear":"身につける", "Take off":"はずす", "Throw":"投げる", "Drop":"落とす",
            "Status":"状態", "Help":"ヘルプ", "Search":"探す", "Pickup":"自動拾い",
            "Trap":"罠", "Language":"言語",
        },
    }
    TRAP = {
        LANG_EN: {},
        LANG_JA: {
            "trap door":"落とし穴", "arrow trap":"矢の罠",
            "sleeping gas trap":"眠りガスの罠", "bear trap":"くくり罠",
            "teleport trap":"テレポートの罠", "dart trap":"毒矢の罠",
            "rust trap":"さびの罠", "mysterious trap":"不思議な罠",
        },
    }

    @staticmethod
    def msg(lang, key, **kw):
        s = TextCatalog.MSG.get(lang, {}).get(key, key)
        return s.format(**kw) if kw else s

    @staticmethod
    def menu(lang, key):
        return TextCatalog.MENU.get(lang, {}).get(key, key)

    @staticmethod
    def trap(lang, key):
        return TextCatalog.TRAP.get(lang, {}).get(key, key)

    @staticmethod
    def monster(lang, name):
        return MONSTER_JA.get(name, name) if lang == LANG_JA else name

    @staticmethod
    def item_kind(lang, cat, name):
        if lang != LANG_JA:
            return name
        if cat == CAT_POT: return POT_JA.get(name, name)
        if cat == CAT_SCR: return SCR_JA.get(name, name)
        if cat == CAT_FOOD: return FOOD_JA.get(name, name)
        if cat == CAT_WPN: return WEAPON_JA.get(name, name)
        if cat == CAT_ARM: return ARMOR_JA.get(name, name)
        return name

# ===========================================================
#  Dice
# ===========================================================
def roll(s):
    n, d = s.split("d"); return sum(random.randint(1, int(d)) for _ in range(int(n)))

def rnd(n):
    return random.randrange(n) if n > 0 else 0

# ===========================================================
#  Item data  (Rogue 5.4)
# ===========================================================
POTIONS = [
    {"name":"healing","prob":13},{"name":"extra healing","prob":5},
    {"name":"poison","prob":8},{"name":"gain strength","prob":13},
    {"name":"restore strength","prob":13},{"name":"confusion","prob":7},
    {"name":"blindness","prob":5},{"name":"haste self","prob":5},
    {"name":"see invisible","prob":3},{"name":"raise level","prob":2},
    {"name":"detect monster","prob":6},{"name":"magic detection","prob":6},
]
POT_COLORS = ["blue","red","green","grey","brown","clear",
              "pink","white","purple","yellow","plaid","amber"]

SCROLLS = [
    {"name":"identify","prob":21},{"name":"enchant weapon","prob":8},
    {"name":"enchant armor","prob":7},{"name":"remove curse","prob":7},
    {"name":"aggravate monsters","prob":3},{"name":"scare monster","prob":4},
    {"name":"sleep","prob":3},{"name":"teleportation","prob":5},
    {"name":"create monster","prob":4},{"name":"magic mapping","prob":4},
    {"name":"hold monster","prob":2},{"name":"blank paper","prob":1},
]
SCR_SYLS = ["blech","foo","bstr","bar","xyzzy","fnord","snafu","fro",
            "aimfiz","aefg","zorch","elam","isko","temov","gnik","snef",
            "forz","juyed","cohah","tstr","priky","motke","ando","wacl"]

FOODS = [{"name":"food ration","nut":900},{"name":"slime-mold","nut":700}]

WEAPONS = [
    {"name":"mace","dam":"2d4","hurl":"1d3","wield":True},
    {"name":"long sword","dam":"3d4","hurl":"1d2","wield":True},
    {"name":"short bow","dam":"1d1","hurl":"1d1","wield":True},
    {"name":"arrow","dam":"1d1","hurl":"2d3","wield":False,"stack":True},
    {"name":"dagger","dam":"1d6","hurl":"1d4","wield":True},
    {"name":"two-handed sword","dam":"4d4","hurl":"1d2","wield":True},
    {"name":"dart","dam":"1d1","hurl":"1d3","wield":False,"stack":True},
    {"name":"shuriken","dam":"1d2","hurl":"2d4","wield":False,"stack":True},
    {"name":"spear","dam":"2d3","hurl":"1d6","wield":True},
]

ARMORS = [
    {"name":"leather armor","ac":8},{"name":"ring mail","ac":7},
    {"name":"studded leather","ac":7},{"name":"scale mail","ac":6},
    {"name":"chain mail","ac":5},{"name":"splint mail","ac":4},
    {"name":"banded mail","ac":4},{"name":"plate mail","ac":3},
]

TRAPS = [
    {"name":"trap door"}, {"name":"arrow trap"},
    {"name":"sleeping gas trap"}, {"name":"bear trap"},
    {"name":"teleport trap"}, {"name":"dart trap"},
    {"name":"rust trap"}, {"name":"mysterious trap"},
]
RAINBOW = ["red","orange","yellow","green","blue","violet"]

# ===========================================================
#  Bestiary  (Rogue 5.4)
# ===========================================================
BESTIARY = [
    ("A","aquator",30,7,2,20,9,"rust"),("B","bat",3,1,0,1,1,"erratic,fly"),
    ("C","centaur",17,6,2,15,7,""),("D","dragon",80,14,5,100,21,""),
    ("E","emu",5,2,0,2,1,""),("F","venus flytrap",30,8,3,25,12,"hold"),
    ("G","griffin",52,10,3,40,17,"fly"),("H","hobgoblin",8,3,1,5,1,""),
    ("I","ice monster",10,4,2,8,5,"freeze"),("J","jabberwock",60,12,4,60,20,""),
    ("K","kestrel",4,2,0,2,1,"fly"),("L","leprechaun",10,2,0,10,6,"steal_gold"),
    ("M","medusa",40,9,3,35,18,"confuse"),("N","nymph",20,3,0,15,9,"steal_item"),
    ("O","orc",12,5,3,10,5,""),("P","phantom",30,8,3,25,15,"invis"),
    ("Q","quagga",16,5,2,12,8,""),("R","rattlesnake",10,4,1,8,4,"poison"),
    ("S","snake",6,2,1,3,2,""),("T","troll",30,8,3,25,13,"regen"),
    ("U","ur-vile",40,10,4,40,18,""),("V","vampire",35,9,3,30,16,"drain"),
    ("W","wraith",25,7,2,20,14,"drain_level"),("X","xeroc",20,6,2,15,11,"mimic"),
    ("Y","yeti",22,6,2,18,10,""),("Z","zombie",15,5,2,10,7,""),
]
MCOL = {"A":12,"B":1,"C":11,"D":8,"E":3,"F":3,"G":10,"H":5,"I":12,"J":8,
        "K":6,"L":11,"M":2,"N":14,"O":4,"P":13,"Q":4,"R":8,"S":11,"T":3,
        "U":2,"V":8,"W":13,"X":9,"Y":7,"Z":5}

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
    ("Wield",   CAT_WPN),("Wear",   CAT_ARM),("Take off",None),
    ("Throw",   None),   ("Drop",   None),
]
AUX_ACTIONS = ["Status", "Help", "Search", "Trap", "Pickup", "Language"]

# ===========================================================
#  Classes
# ===========================================================
class Room:
    def __init__(s,x,y,w,h): s.x,s.y,s.w,s.h=x,y,w,h
    @property
    def cx(s): return s.x+s.w//2
    @property
    def cy(s): return s.y+s.h//2
    def inner(s):
        return random.randint(s.x+1,s.x+s.w-2),random.randint(s.y+1,s.y+s.h-2)

class Item:
    _nid=0
    def __init__(s,cat,kind,ench=0,cursed=False,qty=1):
        s.uid=Item._nid; Item._nid+=1
        s.cat=cat; s.kind=kind; s.ench=ench; s.cursed=cursed; s.qty=qty
        s.x=s.y=0
        s.picked_up=False
    @property
    def data(s):
        if s.cat==CAT_POT: return POTIONS[s.kind]
        if s.cat==CAT_SCR: return SCROLLS[s.kind]
        if s.cat==CAT_FOOD: return FOODS[s.kind]
        if s.cat==CAT_WPN: return WEAPONS[s.kind]
        if s.cat==CAT_ARM: return ARMORS[s.kind]
        return {}
    @property
    def stackable(s): return s.cat==CAT_WPN and s.data.get("stack",False)
    @property
    def sym(s): return ISYM.get(s.cat,"?")

class Monster:
    def __init__(s,x,y,sym,name,hp,atk,df,exp,fl):
        s.x,s.y,s.sym,s.name=x,y,sym,name
        s.hp=s.max_hp=hp; s.atk=atk; s.df=df; s.exp=exp
        s.flags=set(fl.split(",")) if fl else set()
        s.held=s.scared=0
    @property
    def alive(s): return s.hp>0

class Player:
    EXP_T=[0,10,20,40,80,160,320,640,1300,2600,5200,10000,20000,
           40000,80000,160000,320000,640000,1300000,2600000,5200000]
    def __init__(s):
        s.x=s.y=0; s.hp=s.max_hp=16; s.st=s.max_st=16
        s.level=1; s.exp=0; s.gold=0; s.depth=0; s.food=HUNGERTIME
        s.state="normal"; s.ac=10; s.inv=[]; s.wpn=None; s.arm=None
        s.confused=s.blind=s.haste=s.stuck=0
        s.quiet=0
        s.facing=(0,1)
    @property
    def alive(s): return s.hp>0
    def lvlup(s):
        if s.level>=len(s.EXP_T): return False
        if s.exp>=s.EXP_T[s.level]:
            s.level+=1; g=random.randint(3,8); s.max_hp+=g; s.hp+=g; return True
        return False
    def hunger(s):
        prev=s.state
        s.food-=1
        if s.food<=0:
            if s.food < -STARVETIME:
                s.hp=0; s.state="faint"; return "You starve to death."
            if random.randrange(5)==0:
                s.stuck=max(s.stuck,random.randint(4,11))
                s.state="faint"; return "You faint from lack of food."
            s.state="faint"; return None
        if s.food<MORETIME:
            s.state="weak"
            return "You are weak." if prev!="weak" else None
        if s.food<2*MORETIME:
            s.state="hungry"
            return "You feel hungry." if prev!="hungry" else None
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
            s.hp+=random.randint(1,max(1,s.level-7))
        if s.hp!=old:
            s.hp=min(s.hp,s.max_hp); s.quiet=0
    def recalc_ac(s):
        s.ac = (s.arm.data["ac"]-s.arm.ench) if s.arm else 10
    def melee_dmg(s):
        return roll(s.wpn.data["dam"])+s.wpn.ench if s.wpn else roll("1d2")
    def inv_full(s): return len(s.inv)>=INV_MAX
    def add_item(s,it):
        if it.stackable:
            for i in s.inv:
                if i.cat==it.cat and i.kind==it.kind and i.ench==it.ench:
                    i.qty+=it.qty; return True
        if s.inv_full(): return False
        s.inv.append(it); return True
    def rm_item(s,it):
        if it in s.inv: s.inv.remove(it)
        if s.wpn is it: s.wpn=None
        if s.arm is it: s.arm=None; s.recalc_ac()

class IdentTable:
    def __init__(s, lang=LANG_EN):
        s.lang = lang
        s.pcol=random.sample(POT_COLORS,len(POTIONS))
        syls=list(SCR_SYLS); random.shuffle(syls)
        s.snam=[]
        for i in range(len(SCROLLS)):
            n=random.randint(2,3); st=(i*3)%len(syls)
            s.snam.append(" ".join(syls[(st+j)%len(syls)] for j in range(n)))
        s.pk=[False]*len(POTIONS); s.sk=[False]*len(SCROLLS)
    def set_lang(s, lang):
        s.lang = lang if lang in (LANG_EN, LANG_JA) else LANG_EN
    def name(s,it,lang=None):
        lang = s.lang if lang is None else lang
        if it.cat==CAT_POT:
            if s.pk[it.kind]:
                nm=TextCatalog.item_kind(lang, CAT_POT, POTIONS[it.kind]["name"])
                return f"potion of {nm}" if lang==LANG_EN else f"{nm}水薬"
            col=s.pcol[it.kind]
            return f"{col} potion" if lang==LANG_EN else f"{POT_COLOR_JA.get(col,col)}水薬"
        if it.cat==CAT_SCR:
            if s.sk[it.kind]:
                nm=TextCatalog.item_kind(lang, CAT_SCR, SCROLLS[it.kind]["name"])
                return f"scroll of {nm}" if lang==LANG_EN else f"{nm}巻き物"
            return f"scroll [{s.snam[it.kind]}]" if lang==LANG_EN else f"巻き物 [{s.snam[it.kind]}]"
        if it.cat==CAT_FOOD: return TextCatalog.item_kind(lang, CAT_FOOD, it.data["name"])
        if it.cat==CAT_WPN:
            e=it.ench; q=f" ({it.qty})" if it.stackable and it.qty>1 else ""
            nm=TextCatalog.item_kind(lang, CAT_WPN, it.data["name"])
            return f"{'+' if e>=0 else ''}{e} {nm}{q}"
        if it.cat==CAT_ARM:
            e=it.ench; nm=TextCatalog.item_kind(lang, CAT_ARM, it.data["name"])
            return f"{'+' if e>=0 else ''}{e} {nm}"
        return "something" if lang==LANG_EN else "何者か"

# ===========================================================
#  Dungeon generator
# ===========================================================
class DGen:
    @staticmethod
    def gen(depth):
        tm=[[T_VOID]*MAP_W for _ in range(MAP_H)]; rooms=[]; sr={}
        sl=[(gx,gy) for gy in range(GRID_R) for gx in range(GRID_C)]
        random.shuffle(sl); nr=random.randint(6,9)
        act={random.choice(sl)}
        while len(act)<nr:
            frontier=[]
            for gx,gy in act:
                for nx,ny in ((gx+1,gy),(gx-1,gy),(gx,gy+1),(gx,gy-1)):
                    if 0<=nx<GRID_C and 0<=ny<GRID_R and (nx,ny) not in act:
                        frontier.append((nx,ny))
            act.add(random.choice(frontier))
        for gx,gy in sl:
            if (gx,gy) not in act: continue
            sx,sy=gx*SEC_W,gy*SEC_H
            rw=random.randint(RM_MIN_W,min(RM_MAX_W,SEC_W-2))
            rh=random.randint(RM_MIN_H,min(RM_MAX_H,SEC_H-2))
            rx=sx+random.randint(1,max(1,SEC_W-rw-1))
            ry=sy+random.randint(1,max(1,SEC_H-rh-1))
            if rx+rw>MAP_W-1: rw=MAP_W-1-rx
            if ry+rh>MAP_H-1: rh=MAP_H-1-ry
            r=Room(rx,ry,rw,rh); rooms.append(r); sr[(gx,gy)]=r
            DGen._room(tm,r)
        conn=set()
        for gy in range(GRID_R):
            for gx in range(GRID_C):
                if (gx,gy) not in sr: continue
                if gx+1<GRID_C and (gx+1,gy) in sr:
                    p=((gx,gy),(gx+1,gy))
                    if p not in conn: DGen._conn(tm,sr[(gx,gy)],sr[(gx+1,gy)],True); conn.add(p)
                if gy+1<GRID_R and (gx,gy+1) in sr:
                    p=((gx,gy),(gx,gy+1))
                    if p not in conn: DGen._conn(tm,sr[(gx,gy)],sr[(gx,gy+1)],False); conn.add(p)
        DGen._ensure(tm,rooms); return tm,rooms
    @staticmethod
    def _room(t,r):
        for y in range(r.y,r.y+r.h):
            for x in range(r.x,r.x+r.w):
                if 0<=y<MAP_H and 0<=x<MAP_W:
                    if y==r.y or y==r.y+r.h-1: t[y][x]=T_HWALL
                    elif x==r.x or x==r.x+r.w-1: t[y][x]=T_VWALL
                    else: t[y][x]=T_FLOOR
    @staticmethod
    def _conn(t,r1,r2,horiz=None):
        """Connect two rooms by choosing wall doors first, like Rogue's conn()."""
        if horiz is None:
            horiz = abs(r1.cx-r2.cx) >= abs(r1.cy-r2.cy)
        if horiz:
            if r1.cx <= r2.cx:
                d1=DGen._pick_wall_door(t,r1,"R")
                d2=DGen._pick_wall_door(t,r2,"L")
                s=(d1[0]+1,d1[1]); e=(d2[0]-1,d2[1])
            else:
                d1=DGen._pick_wall_door(t,r1,"L")
                d2=DGen._pick_wall_door(t,r2,"R")
                s=(d1[0]-1,d1[1]); e=(d2[0]+1,d2[1])
        else:
            if r1.cy <= r2.cy:
                d1=DGen._pick_wall_door(t,r1,"D")
                d2=DGen._pick_wall_door(t,r2,"U")
                s=(d1[0],d1[1]+1); e=(d2[0],d2[1]-1)
            else:
                d1=DGen._pick_wall_door(t,r1,"U")
                d2=DGen._pick_wall_door(t,r2,"D")
                s=(d1[0],d1[1]-1); e=(d2[0],d2[1]+1)
        DGen._door(t,d1); DGen._door(t,d2)
        DGen._dig_pass(t,s,e,horiz)
    @staticmethod
    def _pick_wall_door(t,r,side):
        if side in ("L","R"):
            x = r.x if side=="L" else r.x+r.w-1
            cands=[(x,y) for y in range(r.y+1,r.y+r.h-1)]
        else:
            y = r.y if side=="U" else r.y+r.h-1
            cands=[(x,y) for x in range(r.x+1,r.x+r.w-1)]
        random.shuffle(cands)
        for p in cands:
            if DGen._door_ok(t,p): return p
        return cands[0]
    @staticmethod
    def _door_ok(t,p):
        x,y=p
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx,ny=x+dx,y+dy
            if 0<=nx<MAP_W and 0<=ny<MAP_H and t[ny][nx]==T_DOOR:
                return False
        return True
    @staticmethod
    def _door(t,p):
        x,y=p
        if 0<=x<MAP_W and 0<=y<MAP_H: t[y][x]=T_DOOR
    @staticmethod
    def _dig_pass(t,s,e,first_horiz):
        x,y=s; ex,ey=e
        if first_horiz:
            turn_x=random.randint(min(x,ex),max(x,ex)) if x!=ex else x
            DGen._hl(t,x,turn_x,y)
            DGen._vl(t,y,ey,turn_x)
            DGen._hl(t,turn_x,ex,ey)
        else:
            turn_y=random.randint(min(y,ey),max(y,ey)) if y!=ey else y
            DGen._vl(t,y,turn_y,x)
            DGen._hl(t,x,ex,turn_y)
            DGen._vl(t,turn_y,ey,ex)
    @staticmethod
    def _hl(t,x1,x2,y):
        if not(0<=y<MAP_H): return
        for x in range(min(x1,x2),max(x1,x2)+1):
            if not(0<=x<MAP_W): continue
            v=t[y][x]
            if v==T_VOID or v==T_CORR: t[y][x]=T_CORR
    @staticmethod
    def _vl(t,y1,y2,x):
        if not(0<=x<MAP_W): return
        for y in range(min(y1,y2),max(y1,y2)+1):
            if not(0<=y<MAP_H): continue
            v=t[y][x]
            if v==T_VOID or v==T_CORR: t[y][x]=T_CORR
    @staticmethod
    def _ensure(t,rooms):
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
    tot=sum(e["prob"] for e in tbl); r=random.randint(1,tot); a=0
    for i,e in enumerate(tbl):
        a+=e["prob"]
        if r<=a: return i
    return 0

def make_item(depth):
    c=random.random()
    if c<.27: return Item(CAT_POT,wchoice(POTIONS))
    if c<.54: return Item(CAT_SCR,wchoice(SCROLLS))
    if c<.64: return Item(CAT_FOOD,random.randint(0,len(FOODS)-1))
    if c<.82:
        k=random.randint(0,len(WEAPONS)-1)
        e=random.randint(-1,2) if depth>3 else random.randint(0,1)
        q=random.randint(2,8) if WEAPONS[k].get("stack") else 1
        return Item(CAT_WPN,k,ench=e,cursed=e<0,qty=q)
    k=random.randint(0,len(ARMORS)-1)
    e=random.randint(-1,2) if depth>3 else random.randint(0,1)
    return Item(CAT_ARM,k,ench=e,cursed=e<0)

def start_inv():
    w=Item(CAT_WPN,0,ench=1)        # mace +1
    a=Item(CAT_ARM,0,ench=1)        # leather +1
    ar=Item(CAT_WPN,3,ench=0,qty=25)# arrows
    b=Item(CAT_WPN,2,ench=1)        # bow +1
    f=Item(CAT_FOOD,0)              # ration
    return [w,a,ar,b,f],w,a


# ===========================================================
#  GAME
# ===========================================================
class Game:
    def __init__(self):
        pyxel.init(SCR_W, SCR_H, title="Pyxel Rogue", fps=30)
        self.font = pyxel.Font(FONT_PATH)
        self.lang = DEFAULT_LANG
        self.new_game()
        pyxel.run(self.update, self.draw)

    def txt(self, x, y, s, c):
        pyxel.text(x, y, str(s), c, self.font)

    # ---------- Init ----------
    def new_game(self):
        if not hasattr(self, "lang"):
            self.lang = DEFAULT_LANG
        self.p = Player()
        inv,w,a = start_inv()
        self.p.inv=inv; self.p.wpn=w; self.p.arm=a; self.p.recalc_ac()
        self.ident = IdentTable(self.lang)
        self.msgs = []; self.explored = set(); self.visible = set()
        self.gitems = []; self.mons = []; self.turn = 0
        self.traps = {}; self.hidden_tiles = {}
        self.st = ST_PLAY; self.mcur = 0; self.icur = 0; self.acur = 0
        self.cact = None; self.dact = None; self.fitems = []
        self.cam_x = self.cam_y = 0
        self.dashing = False; self.dash_d = (0,0); self.dash_t = 0
        self.dash_steps = 0
        self.b_prev = False; self.b_frames = 0
        self.b_used = False; self.b_tap = False
        self.back_prev = False; self.back_frames = 0
        self.back_used = False; self.back_tap = False
        self.b_menu_guard = False
        self.diag_assist = False
        self.auto_pickup = True
        self.dir_pending = None
        self.throw_anim = None
        self.death_cause = ""
        self.descend()
        self.msg("Welcome to the Dungeons of Doom!")

    def set_lang(self, lang):
        self.lang = lang if lang in (LANG_EN, LANG_JA) else LANG_EN
        if hasattr(self, "ident"):
            self.ident.set_lang(self.lang)

    def toggle_lang(self):
        self.set_lang(LANG_JA if self.lang == LANG_EN else LANG_EN)
        self.msg("Language: Japanese." if self.lang == LANG_JA else "Language: English.")

    def descend(self):
        self.p.depth += 1
        self.tm, self.rooms = DGen.gen(self.p.depth)
        self.mons=[]; self.gitems=[]; self.traps={}; self.hidden_tiles={}
        self.visible=set(); self.explored=set()
        px,py = self.rooms[0].inner()
        self.p.x,self.p.y = px,py
        sr=self.rooms[-1]; sx,sy=sr.inner(); self.tm[sy][sx]=T_STAIR
        self._spawn_mons(); self._spawn_items()
        self._hide_secret_features(); self._spawn_traps()
        self._center_cam(); self.update_fov()

    def _center_cam(self):
        max_x = max(0, MAP_W - ZV_COLS)
        max_y = max(0, MAP_H - ZV_ROWS)
        self.cam_x = max(0, min(self.p.x - ZV_COLS//2, max_x))
        self.cam_y = max(0, min(self.p.y - ZV_ROWS//2, max_y))

    def _spawn_mons(self):
        d=self.p.depth; n=random.randint(3,4+d)
        cands=[b for b in BESTIARY if b[6]<=d]
        if not cands: cands=[b for b in BESTIARY if b[6]<=3]
        for _ in range(n):
            rm=random.choice(self.rooms); e=random.choice(cands)
            for _ in range(30):
                mx,my=rm.inner()
                if self.tm[my][mx] in WALKABLE and not self.mon_at(mx,my) \
                   and not(mx==self.p.x and my==self.p.y):
                    sym,nm,hp,at,df,exp,_,fl=e
                    self.mons.append(Monster(mx,my,sym,nm,hp+random.randint(0,d//3),at,df,exp,fl))
                    break

    def _spawn_items(self):
        d=self.p.depth
        for _ in range(random.randint(1,3)):
            rm=random.choice(self.rooms)
            for _ in range(20):
                ix,iy=rm.inner()
                if self.tm[iy][ix]==T_FLOOR and not self.gi_at(ix,iy):
                    g=Item(CAT_GOLD,0); g.qty=random.randint(1,10)*d; g.x,g.y=ix,iy
                    self.gitems.append(g); break
        for _ in range(random.randint(2,4+d//3)):
            rm=random.choice(self.rooms)
            for _ in range(20):
                ix,iy=rm.inner()
                if self.tm[iy][ix]==T_FLOOR and not self.gi_at(ix,iy):
                    it=make_item(d); it.x,it.y=ix,iy; self.gitems.append(it); break

    def _secret_chance(self, denom):
        # Rogue 5.4 passages.c: rnd(10)+1 < level, then a per-feature rnd().
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
        # Rogue 5.4 new_level.c: if rnd(10) < level, place rnd(level/4)+1 traps.
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
        random.shuffle(cands)
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
    def walkable(self,x,y):
        return 0<=x<MAP_W and 0<=y<MAP_H and self.tm[y][x] in WALKABLE
    def diag_ok(self,sx,sy,ex,ey):
        if not (0<=ex<MAP_W and 0<=ey<MAP_H):
            return False
        if sx==ex or sy==ey:
            return True
        return (
            0<=sx<MAP_W and 0<=sy<MAP_H
            and self.tm[ey][ex] in WALKABLE
            and self.tm[ey][sx] in WALKABLE
            and self.tm[sy][ex] in WALKABLE
        )
    def room_at(self,x,y):
        for r in self.rooms:
            if r.x<x<r.x+r.w-1 and r.y<y<r.y+r.h-1: return r
        return None
    def msg(self,t,**kw):
        self.msgs.append(TextCatalog.msg(self.lang,t,**kw)); self.msgs=self.msgs[-100:]

    # ---------- Camera ----------
    def update_cam(self):
        max_x = max(0, MAP_W - ZV_COLS)
        max_y = max(0, MAP_H - ZV_ROWS)
        if max_x == 0:
            self.cam_x = 0
        if max_y == 0:
            self.cam_y = 0
        rx = self.p.x - self.cam_x
        ry = self.p.y - self.cam_y
        if max_x and rx < DEAD_ZONE_X:
            self.cam_x = max(0, self.p.x - DEAD_ZONE_X)
        elif max_x and rx >= ZV_COLS - DEAD_ZONE_X:
            self.cam_x = min(max_x, self.p.x - ZV_COLS + DEAD_ZONE_X + 1)
        if max_y and ry < DEAD_ZONE_Y:
            self.cam_y = max(0, self.p.y - DEAD_ZONE_Y)
        elif max_y and ry >= ZV_ROWS - DEAD_ZONE_Y:
            self.cam_y = min(max_y, self.p.y - ZV_ROWS + DEAD_ZONE_Y + 1)

    # ---------- FOV ----------
    def update_fov(self):
        self.visible = set()
        px,py = self.p.x,self.p.y
        room = self.room_at(px,py)
        if room:
            for ry in range(room.y, room.y+room.h):
                for rx in range(room.x, room.x+room.w):
                    if 0<=rx<MAP_W and 0<=ry<MAP_H:
                        self.visible.add((rx,ry))
                        if self.tm[ry][rx]==T_DOOR:
                            for dx,dy in((-1,0),(1,0),(0,-1),(0,1)):
                                nx,ny=rx+dx,ry+dy
                                if 0<=nx<MAP_W and 0<=ny<MAP_H: self.visible.add((nx,ny))
        for dy in range(-1,2):
            for dx in range(-1,2):
                nx,ny=px+dx,py+dy
                if 0<=nx<MAP_W and 0<=ny<MAP_H: self.visible.add((nx,ny))
        self.explored |= self.visible

    # ---------- Combat ----------
    def p_attack(self, m):
        mn=TextCatalog.monster(self.lang,m.name)
        th=random.randint(1,20)+self.p.level
        wb=self.p.wpn.ench if self.p.wpn else 0
        if th+wb>=10-m.df or th==20:
            dmg=max(1,self.p.melee_dmg())
            m.hp-=dmg
            if not m.alive:
                self.msg("You defeated the {monster}. ({exp} exp)",monster=mn,exp=m.exp)
                self.p.exp+=m.exp
                if self.p.lvlup(): self.msg("Welcome to level {level}!",level=self.p.level)
            else: self.msg("You hit the {monster} ({dmg}).",monster=mn,dmg=dmg)
        else: self.msg("You miss the {monster}.",monster=mn)

    def m_attack(self,m):
        mn=TextCatalog.monster(self.lang,m.name)
        th=random.randint(1,20)
        if th>=self.p.ac or th==20:
            dmg=max(1,m.atk+random.randint(0,2))
            self.p.hp-=dmg; self.msg("The {monster} hits! ({dmg})",monster=mn,dmg=dmg)
            if self.p.hp<=0 and not self.death_cause: self.death_cause=f"killed by a {m.name}"
            if "rust" in m.flags and self.p.arm and self.p.arm.ench>-3:
                self.p.arm.ench-=1; self.p.recalc_ac(); self.msg("Your armor weakens!")
            if "steal_gold" in m.flags and self.p.gold>0:
                s=min(self.p.gold,random.randint(10,50)); self.p.gold-=s; self.msg(f"Steals {s} gold!")
            if "poison" in m.flags and random.random()<.3 and self.p.st>6:
                self.p.st-=1; self.msg("You feel weaker!")
            if "drain" in m.flags and random.random()<.3:
                self.p.max_hp=max(1,self.p.max_hp-1); self.msg("You feel drained!")
            if "confuse" in m.flags and random.random()<.3:
                self.p.confused=random.randint(10,20); self.msg("You feel confused!")
            if "freeze" in m.flags and random.random()<.3:
                self.p.stuck=max(self.p.stuck,random.randint(2,4)); self.msg("You can't move!")
            if "steal_item" in m.flags and self.p.inv:
                t=random.choice(self.p.inv)
                if t is not self.p.wpn and t is not self.p.arm:
                    self.p.rm_item(t); self.msg(f"She stole your {self.ident.name(t)}!")
        else: self.msg("The {monster} misses.",monster=mn)

    def m_turn(self,m):
        if not m.alive: return
        if m.held>0: m.held-=1; return
        px,py=self.p.x,self.p.y
        if m.scared>0:
            m.scared-=1
            dx=-1 if m.x<px else 1 if m.x>px else 0
            dy=-1 if m.y<py else 1 if m.y>py else 0
            if dx and dy:
                if random.random()<.5: dx=0
                else: dy=0
            nx,ny=m.x+dx,m.y+dy
            if self.walkable(nx,ny) and not self.mon_at(nx,ny) and not(nx==px and ny==py):
                m.x,m.y=nx,ny
            return
        dist=abs(m.x-px)+abs(m.y-py)
        if "erratic" in m.flags and random.random()<.5:
            dx,dy=random.choice([-1,0,1]),random.choice([-1,0,1])
        elif dist<=8 and (m.x,m.y) in self.visible:
            dx=(1 if m.x<px else -1 if m.x>px else 0)
            dy=(1 if m.y<py else -1 if m.y>py else 0)
            if dx and dy:
                if random.random()<.5: dx=0
                else: dy=0
        else: return
        if "regen" in m.flags and m.hp<m.max_hp and random.random()<.3: m.hp+=1
        nx,ny=m.x+dx,m.y+dy
        if not self.diag_ok(m.x,m.y,nx,ny): return
        if nx==px and ny==py: self.m_attack(m); return
        if self.walkable(nx,ny) and not self.mon_at(nx,ny): m.x,m.y=nx,ny

    # ---------- Item effects ----------
    def use_pot(self,it):
        p=self.p; nm=POTIONS[it.kind]["name"]; self.ident.pk[it.kind]=True
        if nm=="healing":
            h=max(1,roll("1d4")*p.level); p.hp=min(p.hp+h,p.max_hp); self.msg(f"You feel better. (+{h})")
        elif nm=="extra healing":
            h=max(1,roll("1d8")*p.level); p.hp=min(p.hp+h,p.max_hp+2)
            if p.hp>p.max_hp: p.max_hp=p.hp; self.msg(f"You feel much better. (+{h})")
        elif nm=="poison":
            l=random.randint(1,3); p.st=max(1,p.st-l); self.msg(f"You feel sick. (Str -{l})")
        elif nm=="gain strength": p.st=min(p.st+1,31); p.max_st=max(p.max_st,p.st); self.msg("Str +1!")
        elif nm=="restore strength": p.st=p.max_st; self.msg("You feel warm all over.")
        elif nm=="confusion": p.confused=random.randint(15,25); self.msg("You feel confused.")
        elif nm=="blindness": p.blind=random.randint(50,100); self.msg("Darkness falls.")
        elif nm=="haste self": p.haste=random.randint(10,20); self.msg("You speed up!")
        elif nm=="see invisible": self.msg("You can see invisible monsters.")
        elif nm=="raise level":
            p.exp=p.EXP_T[min(p.level,len(p.EXP_T)-1)]; p.lvlup()
            self.msg(f"You rise to level {p.level}!")
        elif nm=="detect monster":
            for mo in self.mons: self.visible.add((mo.x,mo.y)); self.explored.add((mo.x,mo.y))
            self.msg("You sense monsters.")
        elif nm=="magic detection":
            for i in self.gitems:
                if i.cat in(CAT_POT,CAT_SCR): self.visible.add((i.x,i.y)); self.explored.add((i.x,i.y))
            self.msg("You sense magic.")
        p.rm_item(it)

    def use_scr(self,it):
        p=self.p; nm=SCROLLS[it.kind]["name"]; self.ident.sk[it.kind]=True
        if nm=="identify":
            unid=[i for i in p.inv if (i.cat==CAT_POT and not self.ident.pk[i.kind])
                  or (i.cat==CAT_SCR and not self.ident.sk[i.kind])]
            if unid:
                t=random.choice(unid)
                if t.cat==CAT_POT: self.ident.pk[t.kind]=True
                else: self.ident.sk[t.kind]=True
                self.msg(f"It is a {self.ident.name(t)}.")
            else: self.msg("You feel vaguely uneasy.")
        elif nm=="enchant weapon":
            if p.wpn: p.wpn.ench+=1; p.wpn.cursed=False; self.msg(f"Your {p.wpn.data['name']} glows blue!")
            else: self.msg("You feel a sense of loss.")
        elif nm=="enchant armor":
            if p.arm: p.arm.ench+=1; p.arm.cursed=False; p.recalc_ac(); self.msg(f"Your armor glows!")
            else: self.msg("You feel a sense of loss.")
        elif nm=="remove curse":
            changed=False
            for i in (p.wpn,p.arm):
                if i and i.cursed:
                    i.cursed=False; changed=True
            self.msg("Your equipment feels lighter." if changed else "Somebody watches over you.")
        elif nm=="aggravate monsters":
            for mo in self.mons: mo.held=mo.scared=0; self.msg("You hear a humming noise.")
        elif nm=="scare monster":
            for mo in self.mons:
                if abs(mo.x-p.x)+abs(mo.y-p.y)<=6: mo.scared=random.randint(10,20)
            self.msg("Maniacal laughter echoes.")
        elif nm=="sleep":
            p.stuck=max(p.stuck,random.randint(4,8)); self.msg("You fall asleep.")
        elif nm=="teleportation":
            r=random.choice(self.rooms); p.x,p.y=r.inner(); self.update_fov(); self._center_cam()
            self.msg("You are teleported!")
        elif nm=="create monster":
            for dx,dy in((-1,0),(1,0),(0,-1),(0,1)):
                nx,ny=p.x+dx,p.y+dy
                if self.walkable(nx,ny) and not self.mon_at(nx,ny):
                    cs=[b for b in BESTIARY if b[6]<=p.depth]
                    if cs:
                        e=random.choice(cs); sym,nm2,hp,at,df,exp,_,fl=e
                        self.mons.append(Monster(nx,ny,sym,nm2,hp,at,df,exp,fl))
                    break
            self.msg("A monster appears!")
        elif nm=="magic mapping":
            for y in range(MAP_H):
                for x in range(MAP_W):
                    if self.tm[y][x]!=T_VOID: self.explored.add((x,y))
            self.msg("A map appears in your mind!")
        elif nm=="hold monster":
            for mo in self.mons:
                if abs(mo.x-p.x)+abs(mo.y-p.y)<=4: mo.held=random.randint(10,20)
            self.msg("Nearby monsters freeze!")
        elif nm=="blank paper": self.msg("This scroll is blank.")
        p.rm_item(it)

    def eat(self,it):
        self.p.food=min(STOMACHSIZE,max(self.p.food,0)+HUNGERTIME-200+random.randrange(400))
        self.p.state="normal"
        self.msg(f"You eat the {it.data['name']}. Yum!"); self.p.rm_item(it)

    def wield(self,it):
        if self.p.wpn and self.p.wpn.cursed: self.msg("You can't let go!"); return
        self.p.wpn=it; self.msg(f"You wield the {self.ident.name(it)}.")

    def wear(self,it):
        if self.p.arm:
            if self.p.arm.cursed: self.msg("Cursed armor won't come off!"); return
        self.p.arm=it; self.p.recalc_ac(); self.msg(f"You put on the {self.ident.name(it)}.")

    def takeoff(self,it):
        if it is self.p.arm:
            if it.cursed: self.msg("It's cursed!"); return
            self.p.arm=None; self.p.recalc_ac()
        elif it is self.p.wpn:
            if it.cursed: self.msg("It's cursed!"); return
            self.p.wpn=None
        self.msg(f"You remove the {self.ident.name(it)}.")

    def drop(self,it):
        if (it is self.p.wpn or it is self.p.arm) and it.cursed:
            self.msg("It's cursed!"); return
        self.p.rm_item(it); it.x,it.y=self.p.x,self.p.y
        self.gitems.append(it); self.msg(f"You drop the {self.ident.name(it)}.")

    def is_scare_monster(self,it):
        return it.cat==CAT_SCR and SCROLLS[it.kind]["name"]=="scare monster"

    def throw(self,it,dx,dy):
        p=self.p
        if it is p.wpn and it.cursed: self.msg("Can't let go!"); return
        if it.stackable and it.qty>1:
            thrown=Item(it.cat,it.kind,it.ench,it.cursed,1); it.qty-=1
        else: p.rm_item(it); thrown=it
        tx,ty=p.x,p.y; path=[]
        for _ in range(8):
            nx,ny=tx+dx,ty+dy
            if not self.walkable(nx,ny): break
            tx,ty=nx,ny; path.append((tx,ty))
            m=self.mon_at(tx,ty)
            if m:
                self.throw_anim={"path":path,"sym":thrown.sym,"col":ICOL.get(thrown.cat,7),"tick":0,"delay":2}
                dmg=max(1,roll(it.data.get("hurl","1d2"))+it.ench if it.cat==CAT_WPN else roll("1d2"))
                m.hp-=dmg; self.msg(f"The {self.ident.name(thrown)} hits the {m.name}. ({dmg})")
                if not m.alive:
                    self.msg(f"The {m.name} is defeated!"); p.exp+=m.exp
                    if p.lvlup(): self.msg(f"Welcome to level {p.level}!")
                return
        self.throw_anim={"path":path,"sym":thrown.sym,"col":ICOL.get(thrown.cat,7),"tick":0,"delay":2}
        thrown.x,thrown.y=tx,ty; self.gitems.append(thrown)

    # ---------- Movement & turns ----------
    def try_move(self, dx, dy):
        p = self.p
        if p.confused>0:
            dx,dy = random.choice([-1,0,1]), random.choice([-1,0,1])
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
            if trapped:
                self.trigger_trap(nx,ny)
                if not self.p.alive or self.st!=ST_PLAY:
                    self.end_turn()
                    return True
            gi = self.gi_at(nx,ny)
            if gi and self.auto_pickup and not trapped:
                self.pickup_at(nx,ny)
            elif gi and not trapped:
                self.msg("You see a {item} here.",item=self.ident.name(gi))
            self.update_fov(); self.update_cam(); self.end_turn(); return True
        return False

    def do_search(self, front_only=False):
        p=self.p
        dirs=[p.facing] if front_only else list(DIR8.values())
        found=False
        probinc=(3 if p.confused>0 else 0)+(2 if p.blind>0 else 0)
        for dx,dy in dirs:
            nx,ny=p.x+dx,p.y+dy
            if 0<=nx<MAP_W and 0<=ny<MAP_H:
                hidden=self.hidden_tiles.get((nx,ny))
                if hidden==T_DOOR and rnd(5+probinc)==0:
                    found = self.reveal_hidden_at(nx,ny) or found
                elif hidden==T_CORR and rnd(3+probinc)==0:
                    found = self.reveal_hidden_at(nx,ny) or found
                elif (nx,ny) in self.traps and self.tm[ny][nx]!=T_TRAP and rnd(2+probinc)==0:
                    found = self.reveal_trap_at(nx,ny) or found
        self.msg("You find nothing." if not found else "You found something!")
        if found:
            self.update_fov()
        self.end_turn()

    def trap_hits(self, bonus=0):
        th=random.randint(1,20)+bonus
        return th>=self.p.ac or th-bonus==20

    def save_vs_poison(self):
        return rnd(20) < 7 + self.p.level//2

    def drop_arrow_at_player(self):
        if self.gi_at(self.p.x,self.p.y):
            return
        arrow=Item(CAT_WPN,3,qty=1)
        arrow.x,arrow.y=self.p.x,self.p.y
        self.gitems.append(arrow)

    def teleport_player(self):
        cands=[
            (x,y)
            for y,row in enumerate(self.tm)
            for x,tile in enumerate(row)
            if tile in WALKABLE and tile!=T_TRAP and not self.mon_at(x,y)
        ]
        if cands:
            self.p.x,self.p.y=random.choice(cands)
            self.update_fov(); self._center_cam()

    def trigger_trap(self,x,y):
        self.reveal_trap_at(x,y)
        kind=self.traps.get((x,y),0)
        name=TRAPS[kind]["name"] if 0<=kind<len(TRAPS) else ""
        self.dashing=False
        if name=="trap door":
            self.msg("you fell into a trap!")
            self.descend()
        elif name=="bear trap":
            self.p.stuck=max(self.p.stuck,BEARTIME)
            self.msg("you are caught in a bear trap")
        elif name=="sleeping gas trap":
            self.p.stuck=max(self.p.stuck,SLEEPTIME)
            self.msg("a strange white mist envelops you and you fall asleep")
        elif name=="arrow trap":
            if self.trap_hits(self.p.level-1):
                self.p.hp-=roll("1d6")
                if self.p.hp<=0 and not self.death_cause:
                    self.death_cause="an arrow killed you"
                self.msg("oh no! An arrow shot you")
            else:
                self.drop_arrow_at_player()
                self.msg("an arrow shoots past you")
        elif name=="teleport trap":
            self.teleport_player()
        elif name=="dart trap":
            if self.trap_hits(self.p.level+1):
                self.p.hp-=roll("1d4")
                if self.p.st>3 and not self.save_vs_poison():
                    self.p.st-=1
                if self.p.hp<=0 and not self.death_cause:
                    self.death_cause="a poisoned dart killed you"
                self.msg("a small dart just hit you in the shoulder")
            else:
                self.msg("a small dart whizzes by your ear and vanishes")
        elif name=="rust trap":
            self.msg("a gush of water hits you on the head")
            self.rust_armor()
        elif name=="mysterious trap":
            self.mysterious_trap_msg()

    def rust_armor(self):
        arm=self.p.arm
        if not arm or arm.data["name"]=="leather armor":
            return
        if arm.ench>-3:
            arm.ench-=1
            self.p.recalc_ac()
            self.msg("your armor weakens")

    def mysterious_trap_msg(self):
        color=random.choice(RAINBOW)
        msgs=[
            ("you are suddenly in a parallel dimension",{}),
            ("the light in here suddenly seems {color}",{"color":color}),
            ("you feel a sting in the side of your neck",{}),
            ("multi-colored lines swirl around you, then fade",{}),
            ("a {color} light flashes in your eyes",{"color":color}),
            ("a spike shoots past your ear!",{}),
            ("{color} sparks dance across your armor",{"color":color}),
            ("you suddenly feel very thirsty",{}),
            ("you feel time speed up suddenly",{}),
            ("time now seems to be going slower",{}),
            ("your pack turns {color}!",{"color":color}),
        ]
        key,kw=random.choice(msgs)
        self.msg(key,**kw)

    def inspect_trap(self,dx,dy):
        x,y=self.p.x+dx,self.p.y+dy
        trap=self.visible_trap_at(x,y)
        if trap is None:
            self.msg("no trap there")
        else:
            self.msg("You have found {trap}.",trap=self.trap_name(trap))

    def do_action(self):
        p=self.p; px,py=p.x,p.y
        if self.tm[py][px]==T_STAIR or self.gi_at(px,py):
            self.do_pickup(); return
        self.msg("You swing at empty air.")
        self.do_search(front_only=True)

    def do_pickup(self):
        p=self.p; px,py=p.x,p.y
        if self.tm[py][px]==T_STAIR:
            self.msg(f"You descend to depth {p.depth+1}..."); self.descend()
            self.msg(f"Dungeon depth {p.depth}."); return
        if not self.pickup_at(px,py):
            self.msg("Nothing here.")

    def pickup_at(self,x,y):
        p=self.p
        gi=self.gi_at(x,y)
        if not gi:
            return False
        if gi.cat==CAT_GOLD:
            p.gold+=gi.qty; self.gitems.remove(gi); self.msg("{gold} gold pieces",gold=gi.qty)
            return True
        if self.is_scare_monster(gi) and gi.picked_up:
            self.gitems.remove(gi)
            self.ident.sk[gi.kind]=True
            self.msg("the scroll turns to dust as you pick it up")
            return True
        if p.add_item(gi):
            gi.picked_up=True
            self.gitems.remove(gi); self.msg("You pick up the {item}.",item=self.ident.name(gi))
            return True
        self.msg("pack too full")
        return True

    def do_wait(self): self.end_turn()

    def end_turn(self):
        self.turn+=1; m=self.p.hunger()
        if m:
            self.msg(m); self.dashing=False
        if self.p.hp<=0 and not self.death_cause:
            self.death_cause="starved to death"
        if not self.p.alive:
            self.msg("You died... [A/Start] to restart."); self.st=ST_DEAD
            return
        if self.p.stuck>0: self.p.stuck-=1
        if self.p.confused>0: self.p.confused-=1
        if self.p.blind>0: self.p.blind-=1
        if self.p.haste>0: self.p.haste-=1
        self.p.heal_tick()
        for mo in self.mons: self.m_turn(mo)
        self.mons=[mo for mo in self.mons if mo.alive]
        if not self.p.alive:
            if not self.death_cause: self.death_cause="died"
            self.msg("You died... [A/Start] to restart."); self.st=ST_DEAD

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
        for m in self.mons:
            if m.alive and (m.x,m.y) in self.visible and m is not next_mon:
                self.dashing=False; return
        if not self.walkable(nx,ny) and not next_mon:
            nd=self.next_dash_dir(dx,dy)
            if not nd:
                self.dashing=False; return
            self.dash_d=nd
            dx,dy=nd
        ox,oy=self.p.x,self.p.y
        moved=self.try_move(dx,dy)
        if not moved or (self.p.x,self.p.y)==(ox,oy) or self.st!=ST_PLAY or not self.p.alive:
            self.dashing=False; return
        self.dash_steps+=1
        self.dashing=not self.dash_should_stop_here(dx,dy)

    # ---------- Menu logic ----------
    def open_menu(self):
        self.st=ST_MENU; self.mcur=0; self.dir_pending=None
        self.b_menu_guard=self.kh(pyxel.GAMEPAD1_BUTTON_B)
    def close_menu(self):
        self.st=ST_PLAY; self.mcur=self.icur=0; self.cact=None; self.dact=None; self.fitems=[]
        self.b_menu_guard=False; self.dir_pending=None

    def menu_select(self):
        aname,cat = MENU_ACTIONS[self.mcur]
        self.start_item_action(aname, cat)

    def start_item_action(self, aname, cat=None):
        if cat is None:
            cat = next((c for n,c in MENU_ACTIONS if n == aname), None)
        self.cact = aname; p = self.p
        if aname=="Take off":
            self.fitems=[i for i in p.inv if i is p.wpn or i is p.arm]
        elif aname in("Throw","Drop"):
            self.fitems=list(p.inv)
        elif cat:
            self.fitems=[i for i in p.inv if i.cat==cat]
        else:
            self.fitems=list(p.inv)
        if not self.fitems:
            self.msg(f"Nothing to {aname.lower()}."); self.close_menu(); return
        self.icur=0; self.st=ST_ITEM

    def item_confirm(self):
        if not self.fitems: self.close_menu(); return
        it=self.fitems[self.icur]; a=self.cact
        if a=="Throw":
            self.dact="Throw"; self.st=ST_DIR; return
        if a=="Quaff":   self.use_pot(it)
        elif a=="Read":  self.use_scr(it)
        elif a=="Eat":   self.eat(it)
        elif a=="Wield": self.wield(it)
        elif a=="Wear":  self.wear(it)
        elif a=="Take off": self.takeoff(it)
        elif a=="Drop":  self.drop(it)
        self.close_menu(); self.end_turn()

    def dir_confirm(self,dx,dy):
        if self.dact=="Trap":
            self.inspect_trap(dx,dy)
            self.st=ST_PLAY; self.dact=None; self.cact=None; self.dir_pending=None
            return
        self.p.facing=(dx,dy)
        self.throw(self.fitems[self.icur],dx,dy); self.close_menu(); self.end_turn()

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
        if back_now and self.kh(pyxel.GAMEPAD1_BUTTON_A, pyxel.GAMEPAD1_BUTTON_B):
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
        if self.diag_assist:
            self.dir_pending=None
            return None
        if self.dir_pending:
            d=self.dir_pending
            self.dir_pending=None
            return d
        # Cardinal
        if self.kp(pyxel.KEY_UP,    pyxel.KEY_K, pyxel.GAMEPAD1_BUTTON_DPAD_UP):    self.dir_pending=(0,-1); return None
        if self.kp(pyxel.KEY_DOWN,  pyxel.KEY_J, pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):  self.dir_pending=(0,1); return None
        if self.kp(pyxel.KEY_LEFT,  pyxel.KEY_H, pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):  self.dir_pending=(-1,0); return None
        if self.kp(pyxel.KEY_RIGHT, pyxel.KEY_L, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT): self.dir_pending=(1,0); return None
        return None

    def dir_prompt_press(self):
        if self.kp(pyxel.KEY_Y): return (-1,-1)
        if self.kp(pyxel.KEY_U): return (1,-1)
        if self.kp(pyxel.KEY_B): return (-1,1)
        if self.kp(pyxel.KEY_N): return (1,1)
        u=self._held_up(); d=self._held_dn(); l=self._held_lt(); r=self._held_rt()
        pressed=self.kp(pyxel.KEY_UP,pyxel.KEY_DOWN,pyxel.KEY_LEFT,pyxel.KEY_RIGHT,
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

    def btn_a(self): return self.kp(pyxel.KEY_Z, pyxel.KEY_RETURN, pyxel.GAMEPAD1_BUTTON_A)
    def held_a(self): return self.kh(pyxel.KEY_Z, pyxel.KEY_RETURN, pyxel.GAMEPAD1_BUTTON_A)
    def btn_b(self): return self.kp(pyxel.KEY_ESCAPE) or self.b_tap
    def btn_cancel(self): return self.kp(pyxel.KEY_ESCAPE, pyxel.GAMEPAD1_BUTTON_B)
    def btn_overlay_cancel(self):
        if self.kp(pyxel.KEY_ESCAPE): return True
        b_now=self.kh(pyxel.GAMEPAD1_BUTTON_B)
        if self.b_menu_guard:
            if not b_now:
                self.b_menu_guard=False
            return False
        if self.kp(pyxel.GAMEPAD1_BUTTON_B):
            self.b_used=True
            return True
        return self.b_tap
    def btn_menu(self): return self.kp(pyxel.KEY_C) or self.b_tap
    def btn_wait(self):
        return self.kp(pyxel.KEY_PERIOD) or (
            self.kh(pyxel.GAMEPAD1_BUTTON_A) and self.kh(pyxel.GAMEPAD1_BUTTON_B)
            and (self.kp(pyxel.GAMEPAD1_BUTTON_A) or self.kp(pyxel.GAMEPAD1_BUTTON_B))
            and not self.dir_held_any()
        )
    def btn_search(self): return self.kp(pyxel.KEY_S)
    def btn_trap_inspect(self):
        return self.kh(pyxel.KEY_SHIFT, pyxel.KEY_LSHIFT, pyxel.KEY_RSHIFT) \
            and self.kp(getattr(pyxel,"KEY_6",None))
    def btn_status(self): return self.kp(pyxel.KEY_I)
    def btn_start_tap(self): return self.kp(pyxel.GAMEPAD1_BUTTON_START)
    def kp_back(self): return self.kp(pyxel.KEY_TAB, pyxel.GAMEPAD1_BUTTON_BACK)
    def back_held(self): return self.kh(pyxel.KEY_TAB, pyxel.GAMEPAD1_BUTTON_BACK)
    def btn_back(self): return self.back_tap
    def btn_select_a(self):
        hit = (self.back_held() and self.btn_a()) or (self.kp_back() and self.held_a())
        if hit:
            self.back_used=True; self.b_used=True
        return hit
    def btn_select_b(self):
        hit = (self.back_held() and self.kp(pyxel.GAMEPAD1_BUTTON_B)) or (
            self.kp_back() and self.kh(pyxel.GAMEPAD1_BUTTON_B)
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
    def dash_held(self):
        return self.kh(pyxel.KEY_SHIFT, pyxel.KEY_LSHIFT, pyxel.KEY_RSHIFT, pyxel.GAMEPAD1_BUTTON_B)

    # ---------- Update ----------
    def update(self):
        self.begin_input()
        if self.throw_anim:
            self.throw_anim["tick"] += 1
            if self.throw_anim["tick"] >= len(self.throw_anim["path"]) * self.throw_anim["delay"]:
                self.throw_anim = None
        if self.st==ST_DEAD:
            if self.btn_a() or self.btn_start_tap() or pyxel.btnp(pyxel.KEY_R): self.new_game()
            return
        if self.st==ST_PLAY:   self.upd_play()
        elif self.st==ST_MENU: self.upd_menu()
        elif self.st==ST_ITEM: self.upd_item()
        elif self.st==ST_DIR:  self.upd_dir()
        elif self.st==ST_AUX:  self.upd_aux()
        elif self.st in(ST_STATUS,ST_HELP):
            if self.btn_a() or self.btn_overlay_cancel() or self.btn_status() or self.btn_back() or self.btn_r():
                self.st=ST_PLAY

    def upd_play(self):
        if self.p.stuck>0:
            self.msg("You are unable to move.")
            self.end_turn()
            return

        # Dash continuation
        if self.dashing:
            if not self.dash_held():
                self.dashing=False; return
            self.b_used=True
            self.dash_t+=1
            if self.dash_t>=DASH_INTERVAL:
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
            self.start_item_action("Throw")
            self.dir_pending=None
            return
        if self.btn_select_b():
            self.do_search()
            self.dir_pending=None
            return
        if self.btn_status(): self.st=ST_STATUS; return
        if self.btn_back():  self.open_aux(); return
        if self.btn_r():     self.st=ST_HELP; return
        if self.btn_wait():  self.do_wait(); return
        if self.btn_search(): self.do_search(); return
        if self.btn_trap_inspect(): self.start_trap_inspect(); return

        # Dash start: B/Shift held + direction
        if self.dash_held():
            d = self.held_dir()
            if d:
                self.dashing=True; self.dash_d=d; self.dash_t=0
                self.dash_steps=0
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
            self.msg(f"Diagonal assist {'ON' if self.diag_assist else 'OFF'}.")
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
        if self.btn_overlay_cancel(): self.st=ST_MENU; return

    def upd_dir(self):
        d=self.dir_prompt_press()
        if d: self.dir_confirm(*d); return
        if self.btn_overlay_cancel():
            self.st=ST_PLAY if self.dact=="Trap" else ST_ITEM
            self.dact=None if self.st==ST_PLAY else self.dact
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
        if act=="Status": self.st=ST_STATUS
        elif act=="Help": self.st=ST_HELP
        elif act=="Search":
            self.st=ST_PLAY
            self.do_search()
        elif act=="Trap":
            self.start_trap_inspect()
        elif act=="Pickup":
            self.auto_pickup = not self.auto_pickup
            self.msg("Pickup ON." if self.auto_pickup else "Pickup OFF.")
            self.st=ST_PLAY
        elif act=="Language":
            self.toggle_lang()
            self.st=ST_PLAY
        self.dir_pending=None

    # =====================================================
    #  DRAW
    # =====================================================
    def draw(self):
        pyxel.cls(0)
        self.draw_title()
        self.draw_zoom()
        self.draw_stat()
        self.draw_msgs()
        # Overlays
        if self.st==ST_MENU: self.draw_menu()
        elif self.st==ST_ITEM: self.draw_isel()
        elif self.st==ST_DIR: self.draw_dirp()
        elif self.st==ST_AUX: self.draw_aux()
        elif self.st==ST_STATUS: self.draw_status()
        elif self.st==ST_HELP: self.draw_help()
        elif self.st==ST_DEAD: self.draw_dead()

    def draw_title(self):
        self.txt(HUD_X, 3, "PYXEL ROGUE", 10)

    def draw_zoom(self):
        cx,cy = self.cam_x, self.cam_y
        blind = self.p.blind > 0
        pyxel.rectb(ZV_X-1, ZV_Y-1, ZV_PX_W+2, ZV_PX_H+2, 1)
        px,py = self.p.x, self.p.y

        for vy in range(ZV_ROWS):
            for vx in range(ZV_COLS):
                mx,my = cx+vx, cy+vy
                if not(0<=mx<MAP_W and 0<=my<MAP_H): continue
                sx = ZV_X + vx*TILE_W
                sy = ZV_Y + vy*TILE_H
                vis = (mx,my) in self.visible and not blind
                exp = (mx,my) in self.explored

                if vis:
                    tile=self.tm[my][mx]; ch,col=TILE_CH.get(tile,(" ",0))
                    if ch!=" ": self.txt(sx+1,sy+1,ch,col)
                    # Ground item
                    gi=self.gi_at(mx,my)
                    if gi: self.txt(sx+1,sy+1,gi.sym,ICOL.get(gi.cat,7))
                    # Monster
                    mo=self.mon_at(mx,my)
                    if mo and "invis" not in mo.flags:
                        self.txt(sx+1,sy+1,mo.sym,MCOL.get(mo.sym,7))
                    # Player
                    if mx==px and my==py:
                        self.txt(sx+1,sy+1,"@",10)
                elif exp:
                    tile=self.tm[my][mx]; ch,_=TILE_CH.get(tile,(" ",0))
                    if ch!=" ": self.txt(sx+1,sy+1,ch,1)
                    gi=self.gi_at(mx,my)
                    if gi: self.txt(sx+1,sy+1,gi.sym,ICOL.get(gi.cat,7))

        if self.throw_anim and self.throw_anim["path"]:
            idx=min(self.throw_anim["tick"]//self.throw_anim["delay"],len(self.throw_anim["path"])-1)
            mx,my=self.throw_anim["path"][idx]
            if (mx,my) in self.visible and not blind:
                sx = ZV_X + (mx-cx)*TILE_W
                sy = ZV_Y + (my-cy)*TILE_H
                if ZV_X <= sx < ZV_X+ZV_PX_W and ZV_Y <= sy < ZV_Y+ZV_PX_H:
                    self.txt(sx+1,sy+1,self.throw_anim["sym"],self.throw_anim["col"])

    def draw_stat(self):
        sx,sy=HUD_X,HUD_Y+16; p=self.p; hc=7 if p.hp>p.max_hp//3 else 8
        self.txt(sx,sy,f"Depth {p.depth}",7)
        self.txt(sx+72,sy,f"Turn {self.turn}",5); sy+=14
        self.txt(sx,sy,f"HP {p.hp}/{p.max_hp}",hc); sy+=11
        bw=HUD_W-10; pyxel.rect(sx,sy,bw,4,1)
        if p.max_hp>0:
            f=max(0,int(bw*p.hp/p.max_hp))
            pyxel.rect(sx,sy,f,4,8 if p.hp<=p.max_hp//3 else 11)
        sy+=12
        next_exp=p.EXP_T[min(p.level,len(p.EXP_T)-1)]
        self.txt(sx,sy,f"Lv {p.level} Exp {p.exp}/{next_exp}",7); sy+=12
        self.txt(sx,sy,f"Str {p.st}/{p.max_st}",7)
        self.txt(sx+72,sy,f"Arm {p.ac}",7); sy+=12
        self.txt(sx,sy,f"Gold {p.gold}",10); sy+=12
        state = p.state if p.state else "normal"
        self.txt(sx,sy,f"Food {state}",13 if p.state!="normal" else 7); sy+=12
        self.txt(sx,sy,f"Diag {'ON' if self.diag_assist else 'OFF'}",11 if self.diag_assist else 5); sy+=12
        self.txt(sx,sy,f"Pickup {'ON' if self.auto_pickup else 'OFF'}",11 if self.auto_pickup else 5); sy+=12
        self.txt(sx,sy,f"Lang {self.lang.upper()}",7); sy+=18
        self.txt(sx,sy,"-- Equip --",10); sy+=12
        wn=self.ident.name(p.wpn) if p.wpn else "bare hands"
        an=self.ident.name(p.arm) if p.arm else "no armor"
        self.txt(sx,sy,f"W {wn[:22]}",7); sy+=12
        self.txt(sx,sy,f"A {an[:22]}",7); sy+=18
        self.txt(sx,sy,"-- Effect --",10); sy+=12
        eff=[]
        if p.state=="hungry": eff.append("Hungry")
        elif p.state=="weak": eff.append("Weak")
        elif p.state=="faint": eff.append("Faint")
        if p.confused>0: eff.append("Confused")
        if p.blind>0: eff.append("Blind")
        if p.haste>0: eff.append("Haste")
        if not eff:
            eff.append("None")
        for e in eff[:5]:
            self.txt(sx,sy,e,13 if e!="None" else 5)
            sy+=12

    def draw_msgs(self):
        rows=[]
        for mi,m in enumerate(reversed(self.msgs)):
            c=7 if mi==0 else 5
            parts=[m[i:i+MSG_COLS] for i in range(0,len(m),MSG_COLS)] or [""]
            for part in reversed(parts):
                rows.append((part,c))
                if len(rows)>=MSG_LINES: break
            if len(rows)>=MSG_LINES: break
        rows=list(reversed(rows))
        for i,(m,c) in enumerate(rows):
            self.txt(MSG_X,MSG_Y+i*TILE_H,m,c)

    # ---------- Overlays ----------
    def _box(self,x,y,w,h,title=""):
        pyxel.rect(x,y,w,h,0); pyxel.rectb(x,y,w,h,6)
        if title: self.txt(x+4,y+3,title,10)

    def draw_menu(self):
        bx,by=ZV_X+20,ZV_Y+8; bw=130; bh=len(MENU_ACTIONS)*14+18
        self._box(bx,by,bw,bh,"-- Action --")
        for i,(nm,_) in enumerate(MENU_ACTIONS):
            ty=by+16+i*14; c=10 if i==self.mcur else 7
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
            ln=self.ident.name(it)
            if it is self.p.wpn: ln+=" *W"
            elif it is self.p.arm: ln+=" *A"
            c=10 if ri==self.icur else 7
            pre=">" if ri==self.icur else " "
            self.txt(bx+4,ty,f"{pre}{lt}) {ln[:32]}",c)

    def draw_dirp(self):
        bx,by=ZV_X+50,ZV_Y+90
        title="Trap direction? [D-pad/YUBN]" if self.dact=="Trap" else "Direction? [D-pad/YUBN]"
        self._box(bx,by,190 if self.dact=="Trap" else 170,20,title)

    def draw_aux(self):
        bx,by=ZV_X+20,ZV_Y+8; bw=120; bh=len(AUX_ACTIONS)*14+18
        self._box(bx,by,bw,bh,"-- Assist --")
        for i,nm in enumerate(AUX_ACTIONS):
            ty=by+16+i*14; c=10 if i==self.acur else 7
            pre=">" if i==self.acur else " "
            self.txt(bx+4,ty,f"{pre} {TextCatalog.menu(self.lang,nm)}",c)

    def draw_status(self):
        bx,by=30,20; bw=SCR_W-60; bh=SCR_H-40
        self._box(bx,by,bw,bh,"=== Status ===")
        p=self.p; y=by+18; x=bx+8
        self.txt(x,y,f"Depth: {p.depth}",7); y+=13
        self.txt(x,y,f"Level: {p.level}",7); y+=13
        self.txt(x,y,f"HP:    {p.hp}/{p.max_hp}",7); y+=13
        self.txt(x,y,f"Str:   {p.st}/{p.max_st}",7); y+=13
        next_exp=p.EXP_T[min(p.level,len(p.EXP_T)-1)]
        self.txt(x,y,f"Armor: {p.ac}",7); y+=13
        self.txt(x,y,f"Exp:   {p.exp}/{next_exp}",7); y+=13
        self.txt(x,y,f"Pickup:{' ON' if self.auto_pickup else ' OFF'}",5); y+=13
        self.txt(x,y,f"Gold:  {p.gold}",10); y+=13
        self.txt(x,y,f"Turn:  {self.turn}",5); y+=13
        self.txt(x,y,f"Food:  {p.food}",7)
        y=by+18; x=bx+178
        self.txt(x,y,"-- Equipment --",10); y+=13
        wn=self.ident.name(p.wpn) if p.wpn else "bare hands"
        an=self.ident.name(p.arm) if p.arm else "no armor"
        self.txt(x,y,f"Weapon: {wn[:22]}",7); y+=13
        self.txt(x,y,f"Armor:  {an[:22]}",7); y+=18
        self.txt(x,y,"-- Inventory --",10); y+=13
        for i,it in enumerate(p.inv[:12]):
            lt=chr(ord('a')+i); ln=self.ident.name(it)
            eq=""
            if it is p.wpn: eq=" (wielded)"
            elif it is p.arm: eq=" (worn)"
            self.txt(x,y,f"{lt}) {(ln+eq)[:24]}",7); y+=12

    def draw_help(self):
        bx,by=30,20; bw=SCR_W-60; bh=SCR_H-40
        self._box(bx,by,bw,bh,"=== Help ===")
        lines=[
            "--- Movement ---",
            "D-pad/Arrows   8-direction move",
            "YUBN           Diagonal move",
            "Start tap      Diag assist on/off",
            "Diag assist    Only diagonal D-pad",
            "Shift/B + dir  Dash (auto-run)",
            "",
            "--- Actions ---",
            "A / Z / Enter  Pickup / Stairs",
            "A on empty     Search front",
            "A+B / .        Wait one turn",
            "Back+A         Quick throw",
            "Back+B / S     Search around",
            "Pickup option   Select menu toggle",
            "B tap / C      Open menu",
            "",
            "--- Info ---",
            "Back menu      Status / Help",
            "I              Status screen",
            "Back  / Tab    Assist menu",
            "?              This help",
            "",
            "Press any button to close",
        ]
        y=by+18
        for ln in lines:
            c=10 if ln.startswith("---") else 7
            self.txt(bx+8,y,ln,c); y+=11

    def draw_dead(self):
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
        self.txt(x,y,"A / Start  New game",10); y+=14
        self.txt(x,y,"B          Stay here",5)

# ===========================================================
if __name__=="__main__":
    Game()
