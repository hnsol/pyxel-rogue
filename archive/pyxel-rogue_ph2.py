"""
PYXEL ROGUE - Phase 2
A faithful clone of the original Rogue (5.4) for Pyxel.

Controls:
  Arrow keys / HJKL / D-pad : Move & bump attack
  Z / A button              : Action (pick up / descend stairs / confirm)
  X / B button              : Open menu / cancel
  R                         : Restart (on game over)
"""

import pyxel
import random

# ===========================================================
# Constants
# ===========================================================
MAP_W, MAP_H = 48, 24
GRID_COLS, GRID_ROWS = 3, 3
SECTOR_W, SECTOR_H = MAP_W // GRID_COLS, MAP_H // GRID_ROWS
MIN_ROOM_W, MAX_ROOM_W = 5, 12
MIN_ROOM_H, MAX_ROOM_H = 4, 7

SCREEN_W, SCREEN_H = 480, 310
ZOOM_TILE = 14
ZOOM_COLS, ZOOM_ROWS = 19, 15
ZOOM_X, ZOOM_Y = 4, 14
ZOOM_PX_W = ZOOM_COLS * ZOOM_TILE
ZOOM_PX_H = ZOOM_ROWS * ZOOM_TILE
MINI_TILE = 3
MINI_X = ZOOM_X + ZOOM_PX_W + 16
MINI_Y = ZOOM_Y
MINI_PX_W = MAP_W * MINI_TILE
MINI_PX_H = MAP_H * MINI_TILE
STAT_X, STAT_Y = MINI_X, MINI_Y + MINI_PX_H + 10
MSG_X = ZOOM_X
MSG_Y = ZOOM_Y + ZOOM_PX_H + 6
MSG_LINES = 3
INV_MAX = 26

# Tile types
T_VOID, T_FLOOR, T_HWALL, T_VWALL, T_DOOR, T_CORRIDOR, T_STAIRS = range(7)
TILE_DISP = {
    T_VOID: (" ", 0), T_FLOOR: (".", 5), T_HWALL: ("-", 6),
    T_VWALL: ("|", 6), T_DOOR: ("+", 9), T_CORRIDOR: ("#", 5),
    T_STAIRS: ("%", 10),
}
WALKABLE = {T_FLOOR, T_DOOR, T_CORRIDOR, T_STAIRS}

# UI states
ST_PLAY = 0
ST_MENU = 1          # Action menu open
ST_ITEM_SELECT = 2   # Choosing item
ST_DIR_SELECT = 3    # Choosing direction (throw)
ST_DEAD = 4

# Item categories
CAT_POTION = "potion"
CAT_SCROLL = "scroll"
CAT_FOOD = "food"
CAT_WEAPON = "weapon"
CAT_ARMOR = "armor"
CAT_GOLD = "gold"

ITEM_SYMS = {
    CAT_POTION: "!", CAT_SCROLL: "?", CAT_FOOD: ":",
    CAT_WEAPON: ")", CAT_ARMOR: "]", CAT_GOLD: "*",
}
ITEM_COLORS = {
    CAT_POTION: 12, CAT_SCROLL: 7, CAT_FOOD: 4,
    CAT_WEAPON: 7, CAT_ARMOR: 7, CAT_GOLD: 10,
}

# ===========================================================
# Dice
# ===========================================================
def roll(s):
    n, d = s.split("d")
    return sum(random.randint(1, int(d)) for _ in range(int(n)))


# ===========================================================
# Item data — faithful to Rogue 5.4
# ===========================================================

# --- Potions ---
POTIONS = [
    {"name": "healing",         "prob": 13},
    {"name": "extra healing",   "prob": 5},
    {"name": "poison",          "prob": 8},
    {"name": "gain strength",   "prob": 13},
    {"name": "restore strength","prob": 13},
    {"name": "confusion",       "prob": 7},
    {"name": "blindness",       "prob": 5},
    {"name": "haste self",      "prob": 5},
    {"name": "see invisible",   "prob": 3},
    {"name": "raise level",     "prob": 2},
    {"name": "detect monster",  "prob": 6},
    {"name": "magic detection", "prob": 6},
]
POTION_COLORS = [
    "blue", "red", "green", "grey", "brown", "clear",
    "pink", "white", "purple", "yellow", "plaid", "amber",
]

# --- Scrolls ---
SCROLLS = [
    {"name": "identify",          "prob": 21},
    {"name": "enchant weapon",    "prob": 8},
    {"name": "enchant armor",     "prob": 7},
    {"name": "remove curse",      "prob": 7},
    {"name": "aggravate monsters","prob": 3},
    {"name": "scare monster",     "prob": 4},
    {"name": "sleep",             "prob": 3},
    {"name": "teleportation",     "prob": 5},
    {"name": "create monster",    "prob": 4},
    {"name": "magic mapping",     "prob": 4},
    {"name": "hold monster",      "prob": 2},
    {"name": "blank paper",       "prob": 1},
]
SCROLL_SYLLABLES = [
    "blech", "foo", "bstrgo", "bar", "bstrgo", "xyzzy",
    "fnord", "snafu", "frobozz", "aimfiz", "aefg", "zorch",
    "elam", "isko", "temov", "gnik", "snefru", "forz",
    "juyed", "cohah", "tstrg", "prikyma", "motke", "andova",
]

# --- Food ---
FOODS = [
    {"name": "food ration", "nutrition": 900},
    {"name": "slime-mold",  "nutrition": 700},
]

# --- Weapons ---
WEAPONS = [
    {"name": "mace",            "dam": "2d4", "hurl": "1d3", "hit": 0, "wield": True},
    {"name": "long sword",      "dam": "3d4", "hurl": "1d2", "hit": 0, "wield": True},
    {"name": "short bow",       "dam": "1d1", "hurl": "1d1", "hit": 0, "wield": True},
    {"name": "arrow",           "dam": "1d1", "hurl": "2d3", "hit": 0, "wield": False, "stackable": True},
    {"name": "dagger",          "dam": "1d6", "hurl": "1d4", "hit": 0, "wield": True},
    {"name": "two-handed sword","dam": "4d4", "hurl": "1d2", "hit": 0, "wield": True},
    {"name": "dart",            "dam": "1d1", "hurl": "1d3", "hit": 0, "wield": False, "stackable": True},
    {"name": "shuriken",        "dam": "1d2", "hurl": "2d4", "hit": 0, "wield": False, "stackable": True},
    {"name": "spear",           "dam": "2d3", "hurl": "1d6", "hit": 0, "wield": True},
]

# --- Armor ---
ARMORS = [
    {"name": "leather armor",    "ac": 8},
    {"name": "ring mail",        "ac": 7},
    {"name": "studded leather",  "ac": 7},
    {"name": "scale mail",       "ac": 6},
    {"name": "chain mail",       "ac": 5},
    {"name": "splint mail",      "ac": 4},
    {"name": "banded mail",      "ac": 4},
    {"name": "plate mail",       "ac": 3},
]

# Starting equipment
START_WEAPON = 0   # mace
START_ARMOR = 0    # leather armor
START_ARROWS = 3   # index, with quantity

# ===========================================================
# Monster definitions (Rogue 5.4)
# ===========================================================
BESTIARY = [
    ("A","aquator",     30, 7, 2,20, 9,"rust"),
    ("B","bat",          3, 1, 0, 1, 1,"erratic,fly"),
    ("C","centaur",     17, 6, 2,15, 7,""),
    ("D","dragon",      80,14, 5,100,21,""),
    ("E","emu",          5, 2, 0, 2, 1,""),
    ("F","venus flytrap",30, 8, 3,25,12,"hold"),
    ("G","griffin",     52,10, 3,40,17,"fly"),
    ("H","hobgoblin",    8, 3, 1, 5, 1,""),
    ("I","ice monster", 10, 4, 2, 8, 5,"freeze"),
    ("J","jabberwock",  60,12, 4,60,20,""),
    ("K","kestrel",      4, 2, 0, 2, 1,"fly"),
    ("L","leprechaun",  10, 2, 0,10, 6,"steal_gold"),
    ("M","medusa",      40, 9, 3,35,18,"confuse"),
    ("N","nymph",       20, 3, 0,15, 9,"steal_item"),
    ("O","orc",         12, 5, 3,10, 5,""),
    ("P","phantom",     30, 8, 3,25,15,"invis"),
    ("Q","quagga",      16, 5, 2,12, 8,""),
    ("R","rattlesnake", 10, 4, 1, 8, 4,"poison"),
    ("S","snake",        6, 2, 1, 3, 2,""),
    ("T","troll",       30, 8, 3,25,13,"regen"),
    ("U","ur-vile",     40,10, 4,40,18,""),
    ("V","vampire",     35, 9, 3,30,16,"drain"),
    ("W","wraith",      25, 7, 2,20,14,"drain_level"),
    ("X","xeroc",       20, 6, 2,15,11,"mimic"),
    ("Y","yeti",        22, 6, 2,18,10,""),
    ("Z","zombie",      15, 5, 2,10, 7,""),
]
MON_COLORS = {
    "A":12,"B":1,"C":11,"D":8,"E":3,"F":3,"G":10,"H":5,"I":12,"J":8,
    "K":6,"L":11,"M":2,"N":14,"O":4,"P":13,"Q":4,"R":8,"S":11,"T":3,
    "U":2,"V":8,"W":13,"X":9,"Y":7,"Z":5,
}


# ===========================================================
# Classes
# ===========================================================

class Room:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    @property
    def cx(self):
        return self.x + self.w // 2

    @property
    def cy(self):
        return self.y + self.h // 2

    def inner_point(self):
        return (
            random.randint(self.x + 1, self.x + self.w - 2),
            random.randint(self.y + 1, self.y + self.h - 2),
        )


class Item:
    _next_id = 0

    def __init__(self, category, kind, enchant=0, cursed=False, quantity=1):
        self.uid = Item._next_id
        Item._next_id += 1
        self.category = category
        self.kind = kind        # index into category table
        self.enchant = enchant
        self.cursed = cursed
        self.quantity = quantity
        self.x = 0
        self.y = 0

    @property
    def data(self):
        if self.category == CAT_POTION:  return POTIONS[self.kind]
        if self.category == CAT_SCROLL:  return SCROLLS[self.kind]
        if self.category == CAT_FOOD:    return FOODS[self.kind]
        if self.category == CAT_WEAPON:  return WEAPONS[self.kind]
        if self.category == CAT_ARMOR:   return ARMORS[self.kind]
        return {}

    @property
    def stackable(self):
        if self.category == CAT_WEAPON:
            return self.data.get("stackable", False)
        return False

    @property
    def sym(self):
        return ITEM_SYMS.get(self.category, "?")


class Monster:
    def __init__(self, x, y, sym, name, hp, atk, def_, exp, flags_str):
        self.x, self.y = x, y
        self.sym, self.name = sym, name
        self.hp, self.max_hp = hp, hp
        self.atk, self.def_, self.exp = atk, def_, exp
        self.flags = set(flags_str.split(",")) if flags_str else set()
        self.held = 0      # turns held/frozen
        self.scared = 0    # turns scared

    @property
    def alive(self):
        return self.hp > 0


class Player:
    EXP_TABLE = [0,10,20,40,80,160,320,640,1300,2600,
                 5200,10000,20000,40000,80000,160000,320000,
                 640000,1300000,2600000,5200000]

    def __init__(self):
        self.x = self.y = 0
        self.hp = self.max_hp = 16
        self.str = self.max_str = 16
        self.level = 1
        self.exp = 0
        self.gold = 0
        self.depth = 0
        self.food = 1300
        self.state = "normal"
        self.ac = 10         # armor class (lower=better, 10=naked)
        self.inventory = []  # list of Item
        self.weapon = None   # equipped Item ref
        self.armor = None    # equipped Item ref
        # Status effects
        self.confused = 0
        self.blind = 0
        self.haste = 0

    @property
    def alive(self):
        return self.hp > 0

    def check_levelup(self):
        if self.level >= len(self.EXP_TABLE):
            return False
        if self.exp >= self.EXP_TABLE[self.level]:
            self.level += 1
            gain = random.randint(3, 8)
            self.max_hp += gain
            self.hp += gain
            return True
        return False

    def hunger_tick(self):
        rate = 1
        self.food -= rate
        if self.food <= 0:
            prev = self.state
            self.state = "faint"
            self.hp -= 1
            if self.food % 20 == 0 or prev != "faint":
                return "You faint from lack of food."
        elif self.food < 150:
            if self.state != "weak":
                self.state = "weak"
                return "You are weak. You need food badly."
        elif self.food < 300:
            if self.state != "hungry":
                self.state = "hungry"
                return "You feel hungry."
        else:
            self.state = "normal"
        return None

    def recalc_ac(self):
        base = 10
        if self.armor:
            base = self.armor.data["ac"] - self.armor.enchant
        self.ac = base

    def attack_damage(self):
        """Melee damage from wielded weapon."""
        if self.weapon:
            return roll(self.weapon.data["dam"]) + self.weapon.enchant
        return roll("1d2")  # bare fist

    def inv_letter(self, item):
        try:
            idx = self.inventory.index(item)
            return chr(ord('a') + idx)
        except ValueError:
            return '?'

    def inv_full(self):
        return len(self.inventory) >= INV_MAX

    def add_item(self, item):
        """Add item to inventory. Returns True on success."""
        # Stack check
        if item.stackable:
            for inv_item in self.inventory:
                if (inv_item.category == item.category
                        and inv_item.kind == item.kind
                        and inv_item.enchant == item.enchant):
                    inv_item.quantity += item.quantity
                    return True
        if self.inv_full():
            return False
        self.inventory.append(item)
        return True

    def remove_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
            if self.weapon is item:
                self.weapon = None
            if self.armor is item:
                self.armor = None
                self.recalc_ac()


class IdentTable:
    """Tracks identification state for potions and scrolls."""

    def __init__(self):
        self.potion_names = random.sample(POTION_COLORS, len(POTIONS))
        # Generate scroll labels from random syllables
        syls = list(SCROLL_SYLLABLES)
        random.shuffle(syls)
        self.scroll_names = []
        for i in range(len(SCROLLS)):
            n = random.randint(2, 3)
            start = (i * 3) % len(syls)
            name = " ".join(syls[(start + j) % len(syls)] for j in range(n))
            self.scroll_names.append(name)
        self.potion_known = [False] * len(POTIONS)
        self.scroll_known = [False] * len(SCROLLS)

    def item_display(self, item):
        """Get display name for an item."""
        if item.category == CAT_POTION:
            if self.potion_known[item.kind]:
                base = f"potion of {POTIONS[item.kind]['name']}"
            else:
                base = f"{self.potion_names[item.kind]} potion"
            return base
        elif item.category == CAT_SCROLL:
            if self.scroll_known[item.kind]:
                base = f"scroll of {SCROLLS[item.kind]['name']}"
            else:
                base = f"scroll [{self.scroll_names[item.kind]}]"
            return base
        elif item.category == CAT_FOOD:
            return item.data["name"]
        elif item.category == CAT_WEAPON:
            e = item.enchant
            sign = "+" if e >= 0 else ""
            name = item.data["name"]
            q = f" ({item.quantity})" if item.stackable and item.quantity > 1 else ""
            return f"{sign}{e} {name}{q}"
        elif item.category == CAT_ARMOR:
            e = item.enchant
            sign = "+" if e >= 0 else ""
            return f"{sign}{e} {item.data['name']}"
        return "something"

    def inv_line(self, item, letter):
        name = self.item_display(item)
        return f"{letter}) {name}"


# ===========================================================
# Dungeon generator
# ===========================================================

class DungeonGenerator:
    @staticmethod
    def generate(depth):
        tilemap = [[T_VOID] * MAP_W for _ in range(MAP_H)]
        rooms = []
        sector_rooms = {}
        sector_list = [(gx, gy) for gy in range(GRID_ROWS) for gx in range(GRID_COLS)]
        random.shuffle(sector_list)
        num_rooms = random.randint(6, 9)
        active = set(sector_list[:num_rooms])

        for gx, gy in sector_list:
            if (gx, gy) not in active:
                continue
            sx, sy = gx * SECTOR_W, gy * SECTOR_H
            rw = random.randint(MIN_ROOM_W, min(MAX_ROOM_W, SECTOR_W - 2))
            rh = random.randint(MIN_ROOM_H, min(MAX_ROOM_H, SECTOR_H - 2))
            rx = sx + random.randint(1, max(1, SECTOR_W - rw - 1))
            ry = sy + random.randint(1, max(1, SECTOR_H - rh - 1))
            if rx + rw > MAP_W - 1: rw = MAP_W - 1 - rx
            if ry + rh > MAP_H - 1: rh = MAP_H - 1 - ry
            room = Room(rx, ry, rw, rh)
            rooms.append(room)
            sector_rooms[(gx, gy)] = room
            DungeonGenerator._carve_room(tilemap, room)

        connected = set()
        for gy in range(GRID_ROWS):
            for gx in range(GRID_COLS):
                if (gx, gy) not in sector_rooms: continue
                if gx+1 < GRID_COLS and (gx+1,gy) in sector_rooms:
                    p = ((gx,gy),(gx+1,gy))
                    if p not in connected:
                        DungeonGenerator._corridor(tilemap, sector_rooms[(gx,gy)], sector_rooms[(gx+1,gy)])
                        connected.add(p)
                if gy+1 < GRID_ROWS and (gx,gy+1) in sector_rooms:
                    p = ((gx,gy),(gx,gy+1))
                    if p not in connected:
                        DungeonGenerator._corridor(tilemap, sector_rooms[(gx,gy)], sector_rooms[(gx,gy+1)])
                        connected.add(p)

        DungeonGenerator._ensure_conn(tilemap, rooms)
        return tilemap, rooms

    @staticmethod
    def _carve_room(tm, r):
        for y in range(r.y, r.y + r.h):
            for x in range(r.x, r.x + r.w):
                if 0 <= y < MAP_H and 0 <= x < MAP_W:
                    if y == r.y or y == r.y + r.h - 1:
                        tm[y][x] = T_HWALL
                    elif x == r.x or x == r.x + r.w - 1:
                        tm[y][x] = T_VWALL
                    else:
                        tm[y][x] = T_FLOOR

    @staticmethod
    def _corridor(tm, r1, r2):
        x1, y1, x2, y2 = r1.cx, r1.cy, r2.cx, r2.cy
        if random.random() < 0.5:
            DungeonGenerator._hl(tm, x1, x2, y1)
            DungeonGenerator._vl(tm, y1, y2, x2)
        else:
            DungeonGenerator._vl(tm, y1, y2, x1)
            DungeonGenerator._hl(tm, x1, x2, y2)

    @staticmethod
    def _hl(tm, x1, x2, y):
        if not (0 <= y < MAP_H): return
        for x in range(min(x1,x2), max(x1,x2)+1):
            if not (0 <= x < MAP_W): continue
            t = tm[y][x]
            if t in (T_HWALL, T_VWALL): tm[y][x] = T_DOOR
            elif t == T_VOID: tm[y][x] = T_CORRIDOR

    @staticmethod
    def _vl(tm, y1, y2, x):
        if not (0 <= x < MAP_W): return
        for y in range(min(y1,y2), max(y1,y2)+1):
            if not (0 <= y < MAP_H): continue
            t = tm[y][x]
            if t in (T_HWALL, T_VWALL): tm[y][x] = T_DOOR
            elif t == T_VOID: tm[y][x] = T_CORRIDOR

    @staticmethod
    def _ensure_conn(tm, rooms):
        if len(rooms) <= 1: return
        def flood(sx, sy):
            vis = set(); stk = [(sx,sy)]
            while stk:
                x, y = stk.pop()
                if (x,y) in vis: continue
                if not (0<=x<MAP_W and 0<=y<MAP_H): continue
                if tm[y][x] == T_VOID: continue
                vis.add((x,y))
                for dx, dy in ((-1,0),(1,0),(0,-1),(0,1)): stk.append((x+dx,y+dy))
            return vis
        base = flood(rooms[0].cx, rooms[0].cy)
        for r in rooms[1:]:
            if (r.cx, r.cy) not in base:
                DungeonGenerator._corridor(tm, rooms[0], r)
                base = flood(rooms[0].cx, rooms[0].cy)


# ===========================================================
# Item factory
# ===========================================================

def weighted_choice(table):
    total = sum(e["prob"] for e in table)
    r = random.randint(1, total)
    acc = 0
    for i, e in enumerate(table):
        acc += e["prob"]
        if r <= acc:
            return i
    return 0


def make_random_item(depth):
    """Create a random item appropriate for dungeon depth."""
    cat_roll = random.random()
    if cat_roll < 0.27:
        kind = weighted_choice(POTIONS)
        return Item(CAT_POTION, kind)
    elif cat_roll < 0.54:
        kind = weighted_choice(SCROLLS)
        return Item(CAT_SCROLL, kind)
    elif cat_roll < 0.64:
        kind = random.randint(0, len(FOODS) - 1)
        return Item(CAT_FOOD, kind)
    elif cat_roll < 0.82:
        kind = random.randint(0, len(WEAPONS) - 1)
        ench = random.randint(-1, 2) if depth > 3 else random.randint(0, 1)
        cursed = ench < 0
        qty = random.randint(2, 8) if WEAPONS[kind].get("stackable") else 1
        return Item(CAT_WEAPON, kind, enchant=ench, cursed=cursed, quantity=qty)
    else:
        kind = random.randint(0, len(ARMORS) - 1)
        ench = random.randint(-1, 2) if depth > 3 else random.randint(0, 1)
        cursed = ench < 0
        return Item(CAT_ARMOR, kind, enchant=ench, cursed=cursed)


def make_starting_inventory():
    """Give the player Rogue 5.4 starting equipment."""
    items = []
    # Mace +1,+1
    w = Item(CAT_WEAPON, START_WEAPON, enchant=1)
    items.append(w)
    # Leather armor +1
    a = Item(CAT_ARMOR, START_ARMOR, enchant=1)
    items.append(a)
    # 25 arrows +0
    arr = Item(CAT_WEAPON, START_ARROWS, enchant=0, quantity=25)
    items.append(arr)
    # Short bow +1
    bow = Item(CAT_WEAPON, 2, enchant=1)
    items.append(bow)
    # Some food
    food = Item(CAT_FOOD, 0)
    items.append(food)
    return items, w, a  # items, weapon_ref, armor_ref


# ===========================================================
# Menu actions
# ===========================================================

MENU_ACTIONS = [
    ("Quaff",    "q", CAT_POTION),
    ("Read",     "r", CAT_SCROLL),
    ("Eat",      "e", CAT_FOOD),
    ("Wield",    "w", CAT_WEAPON),
    ("Wear",     "W", CAT_ARMOR),
    ("Take off", "t", None),      # special filter
    ("Throw",    "T", None),      # any item
    ("Drop",     "d", None),      # any item
]


# ===========================================================
# Game
# ===========================================================

class Game:
    def __init__(self):
        pyxel.init(SCREEN_W, SCREEN_H, title="Pyxel Rogue", fps=30)
        self.new_game()
        pyxel.run(self.update, self.draw)

    # ------- Init -------
    def new_game(self):
        self.player = Player()
        inv, weap, arm = make_starting_inventory()
        self.player.inventory = inv
        self.player.weapon = weap
        self.player.armor = arm
        self.player.recalc_ac()
        self.ident = IdentTable()
        self.messages = []
        self.explored = set()
        self.visible = set()
        self.ground_items = []
        self.monsters = []
        self.turn = 0
        self.ui_state = ST_PLAY
        self.menu_cursor = 0
        self.item_cursor = 0
        self.current_action = None
        self.filtered_items = []
        self.descend()
        self.add_msg("Welcome to the Dungeons of Doom!")

    def descend(self):
        self.player.depth += 1
        self.tilemap, self.rooms = DungeonGenerator.generate(self.player.depth)
        self.monsters = []
        self.ground_items = []
        self.visible = set()
        self.explored = set()
        px, py = self.rooms[0].inner_point()
        self.player.x, self.player.y = px, py
        sr = self.rooms[-1]
        sx, sy = sr.inner_point()
        self.tilemap[sy][sx] = T_STAIRS
        self.spawn_monsters()
        self.spawn_items()
        self.update_fov()

    def spawn_monsters(self):
        depth = self.player.depth
        num = random.randint(3, 4 + depth)
        cands = [b for b in BESTIARY if b[6] <= depth]
        if not cands: cands = [b for b in BESTIARY if b[6] <= 3]
        for _ in range(num):
            room = random.choice(self.rooms)
            entry = random.choice(cands)
            for _t in range(30):
                mx, my = room.inner_point()
                if (self.tilemap[my][mx] in WALKABLE
                        and not self.monster_at(mx, my)
                        and not (mx == self.player.x and my == self.player.y)):
                    sym,name,hp,atk,df,exp,_,flags = entry
                    hp2 = hp + random.randint(0, depth // 3)
                    self.monsters.append(Monster(mx,my,sym,name,hp2,atk,df,exp,flags))
                    break

    def spawn_items(self):
        depth = self.player.depth
        # Gold piles
        for _ in range(random.randint(1, 3)):
            room = random.choice(self.rooms)
            for _t in range(20):
                ix, iy = room.inner_point()
                if self.tilemap[iy][ix] == T_FLOOR and not self.ground_item_at(ix, iy):
                    gold = Item(CAT_GOLD, 0)
                    gold.quantity = random.randint(1, 10) * depth
                    gold.x, gold.y = ix, iy
                    self.ground_items.append(gold)
                    break
        # Random items
        for _ in range(random.randint(2, 4 + depth // 3)):
            room = random.choice(self.rooms)
            for _t in range(20):
                ix, iy = room.inner_point()
                if self.tilemap[iy][ix] == T_FLOOR and not self.ground_item_at(ix, iy):
                    item = make_random_item(depth)
                    item.x, item.y = ix, iy
                    self.ground_items.append(item)
                    break

    # ------- Helpers -------
    def monster_at(self, x, y):
        for m in self.monsters:
            if m.alive and m.x == x and m.y == y: return m
        return None

    def ground_item_at(self, x, y):
        for it in self.ground_items:
            if it.x == x and it.y == y: return it
        return None

    def is_walkable(self, x, y):
        if not (0 <= x < MAP_W and 0 <= y < MAP_H): return False
        return self.tilemap[y][x] in WALKABLE

    def room_at(self, x, y):
        for r in self.rooms:
            if r.x < x < r.x+r.w-1 and r.y < y < r.y+r.h-1: return r
        return None

    def add_msg(self, text):
        self.messages.append(text)
        if len(self.messages) > 100: self.messages = self.messages[-100:]

    # ------- FOV -------
    def update_fov(self):
        self.visible = set()
        px, py = self.player.x, self.player.y
        room = self.room_at(px, py)
        if room:
            for ry in range(room.y, room.y + room.h):
                for rx in range(room.x, room.x + room.w):
                    if 0 <= rx < MAP_W and 0 <= ry < MAP_H:
                        self.visible.add((rx, ry))
                        if self.tilemap[ry][rx] == T_DOOR:
                            for dx, dy in ((-1,0),(1,0),(0,-1),(0,1)):
                                nx, ny = rx+dx, ry+dy
                                if 0 <= nx < MAP_W and 0 <= ny < MAP_H:
                                    self.visible.add((nx, ny))
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx, ny = px+dx, py+dy
                if 0 <= nx < MAP_W and 0 <= ny < MAP_H:
                    self.visible.add((nx, ny))
        self.explored |= self.visible

    # ------- Combat -------
    def player_attack(self, m):
        to_hit = random.randint(1, 20) + self.player.level
        ac = 10 - m.def_
        w_bonus = self.player.weapon.enchant if self.player.weapon else 0
        if to_hit + w_bonus >= ac or to_hit == 20:
            damage = max(1, self.player.attack_damage())
            m.hp -= damage
            if not m.alive:
                self.add_msg(f"You defeated the {m.name}. ({m.exp} exp)")
                self.player.exp += m.exp
                if self.player.check_levelup():
                    self.add_msg(f"Welcome to level {self.player.level}!")
            else:
                self.add_msg(f"You hit the {m.name} ({damage}).")
        else:
            self.add_msg(f"You miss the {m.name}.")

    def monster_attack(self, m):
        to_hit = random.randint(1, 20)
        if to_hit >= self.player.ac or to_hit == 20:
            damage = max(1, m.atk + random.randint(0, 2))
            self.player.hp -= damage
            self.add_msg(f"The {m.name} hits! ({damage})")
            # Special attacks
            if "rust" in m.flags and self.player.armor:
                if self.player.armor.enchant > -3:
                    self.player.armor.enchant -= 1
                    self.player.recalc_ac()
                    self.add_msg("Your armor weakens!")
            if "steal_gold" in m.flags and self.player.gold > 0:
                stolen = min(self.player.gold, random.randint(10, 50))
                self.player.gold -= stolen
                self.add_msg(f"It steals {stolen} gold!")
            if "poison" in m.flags and random.random() < 0.3:
                if self.player.str > 6:
                    self.player.str -= 1
                    self.add_msg("You feel weaker!")
            if "drain" in m.flags and random.random() < 0.3:
                self.player.max_hp = max(1, self.player.max_hp - 1)
                self.add_msg("You feel drained!")
            if "confuse" in m.flags and random.random() < 0.3:
                self.player.confused = random.randint(10, 20)
                self.add_msg("You feel confused!")
            if "freeze" in m.flags and random.random() < 0.3:
                self.add_msg("You can't move!")
            if "steal_item" in m.flags and self.player.inventory:
                stolen = random.choice(self.player.inventory)
                if stolen is not self.player.weapon and stolen is not self.player.armor:
                    self.player.remove_item(stolen)
                    self.add_msg(f"She stole your {self.ident.item_display(stolen)}!")
        else:
            self.add_msg(f"The {m.name} misses.")

    def monster_turn(self, m):
        if not m.alive: return
        if m.held > 0:
            m.held -= 1
            return
        if m.scared > 0:
            m.scared -= 1
            # Run away from player
            dx = -1 if m.x < self.player.x else 1 if m.x > self.player.x else 0
            dy = -1 if m.y < self.player.y else 1 if m.y > self.player.y else 0
            if dx != 0 and dy != 0:
                if random.random() < 0.5: dx = 0
                else: dy = 0
            nx, ny = m.x + dx, m.y + dy
            if self.is_walkable(nx, ny) and not self.monster_at(nx, ny):
                if not (nx == self.player.x and ny == self.player.y):
                    m.x, m.y = nx, ny
            return

        px, py = self.player.x, self.player.y
        dist = abs(m.x - px) + abs(m.y - py)

        if "erratic" in m.flags and random.random() < 0.5:
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
        elif dist <= 8 and (m.x, m.y) in self.visible:
            dx = (1 if m.x < px else -1 if m.x > px else 0)
            dy = (1 if m.y < py else -1 if m.y > py else 0)
            if dx != 0 and dy != 0:
                if random.random() < 0.5: dx = 0
                else: dy = 0
        else:
            return

        if "regen" in m.flags and m.hp < m.max_hp and random.random() < 0.3:
            m.hp += 1

        nx, ny = m.x + dx, m.y + dy
        if nx == px and ny == py:
            self.monster_attack(m)
            return
        if self.is_walkable(nx, ny) and not self.monster_at(nx, ny):
            m.x, m.y = nx, ny

    # ------- Item effects -------
    def use_potion(self, item):
        p = self.player
        kind = item.kind
        name = POTIONS[kind]["name"]
        self.ident.potion_known[kind] = True

        if name == "healing":
            heal = max(1, roll("1d4") * p.level)
            p.hp = min(p.hp + heal, p.max_hp)
            self.add_msg(f"You feel better. (+{heal} HP)")
        elif name == "extra healing":
            heal = max(1, roll("1d8") * p.level)
            p.hp = min(p.hp + heal, p.max_hp + 2)
            if p.hp > p.max_hp: p.max_hp = p.hp
            self.add_msg(f"You feel much better. (+{heal} HP)")
        elif name == "poison":
            loss = random.randint(1, 3)
            p.str = max(1, p.str - loss)
            self.add_msg(f"You feel very sick. (Str -{loss})")
        elif name == "gain strength":
            p.str = min(p.str + 1, 31)
            p.max_str = max(p.max_str, p.str)
            self.add_msg("You feel stronger. (Str +1)")
        elif name == "restore strength":
            p.str = p.max_str
            self.add_msg("You feel warm all over.")
        elif name == "confusion":
            p.confused = random.randint(15, 25)
            self.add_msg("You feel confused.")
        elif name == "blindness":
            p.blind = random.randint(50, 100)
            self.add_msg("A cloak of darkness falls around you.")
        elif name == "haste self":
            p.haste = random.randint(10, 20)
            self.add_msg("You feel yourself moving much faster.")
        elif name == "see invisible":
            self.add_msg("You can see invisible monsters.")
        elif name == "raise level":
            p.exp = p.EXP_TABLE[min(p.level, len(p.EXP_TABLE)-1)]
            p.check_levelup()
            self.add_msg(f"You rise to level {p.level}!")
        elif name == "detect monster":
            for mon in self.monsters:
                self.visible.add((mon.x, mon.y))
                self.explored.add((mon.x, mon.y))
            self.add_msg("You sense the presence of monsters.")
        elif name == "magic detection":
            for it in self.ground_items:
                if it.category in (CAT_POTION, CAT_SCROLL):
                    self.visible.add((it.x, it.y))
                    self.explored.add((it.x, it.y))
            self.add_msg("You sense the presence of magic.")

        p.remove_item(item)

    def use_scroll(self, item):
        p = self.player
        kind = item.kind
        name = SCROLLS[kind]["name"]
        self.ident.scroll_known[kind] = True

        if name == "identify":
            # Identify a random unidentified item in inventory
            unid = []
            for it in p.inventory:
                if it.category == CAT_POTION and not self.ident.potion_known[it.kind]:
                    unid.append(it)
                elif it.category == CAT_SCROLL and not self.ident.scroll_known[it.kind]:
                    unid.append(it)
            if unid:
                target = random.choice(unid)
                if target.category == CAT_POTION:
                    self.ident.potion_known[target.kind] = True
                elif target.category == CAT_SCROLL:
                    self.ident.scroll_known[target.kind] = True
                self.add_msg(f"It is a {self.ident.item_display(target)}.")
            else:
                self.add_msg("You feel vaguely uneasy.")
        elif name == "enchant weapon":
            if p.weapon:
                p.weapon.enchant += 1
                p.weapon.cursed = False
                self.add_msg(f"Your {p.weapon.data['name']} glows blue!")
            else:
                self.add_msg("You feel a strange sense of loss.")
        elif name == "enchant armor":
            if p.armor:
                p.armor.enchant += 1
                p.armor.cursed = False
                p.recalc_ac()
                self.add_msg(f"Your {p.armor.data['name']} glows silver!")
            else:
                self.add_msg("You feel a strange sense of loss.")
        elif name == "remove curse":
            for it in p.inventory:
                it.cursed = False
            self.add_msg("You feel as if somebody is watching over you.")
        elif name == "aggravate monsters":
            for mon in self.monsters:
                mon.held = 0
                mon.scared = 0
            self.add_msg("You hear a high pitched humming noise.")
        elif name == "scare monster":
            for mon in self.monsters:
                dist = abs(mon.x - p.x) + abs(mon.y - p.y)
                if dist <= 6:
                    mon.scared = random.randint(10, 20)
            self.add_msg("You hear maniacal laughter in the distance.")
        elif name == "sleep":
            # Player loses some turns (simplified: just skip)
            self.add_msg("You fall asleep.")
        elif name == "teleportation":
            room = random.choice(self.rooms)
            nx, ny = room.inner_point()
            p.x, p.y = nx, ny
            self.update_fov()
            self.add_msg("You are teleported!")
        elif name == "create monster":
            for dx, dy in ((-1,0),(1,0),(0,-1),(0,1)):
                nx, ny = p.x+dx, p.y+dy
                if self.is_walkable(nx, ny) and not self.monster_at(nx, ny):
                    cands = [b for b in BESTIARY if b[6] <= p.depth]
                    if cands:
                        e = random.choice(cands)
                        sym,nm,hp,atk,df,exp,_,fl = e
                        self.monsters.append(Monster(nx,ny,sym,nm,hp,atk,df,exp,fl))
                    break
            self.add_msg("A monster appears!")
        elif name == "magic mapping":
            for y in range(MAP_H):
                for x in range(MAP_W):
                    if self.tilemap[y][x] != T_VOID:
                        self.explored.add((x, y))
            self.add_msg("A map appears in your mind!")
        elif name == "hold monster":
            for mon in self.monsters:
                dist = abs(mon.x - p.x) + abs(mon.y - p.y)
                if dist <= 4:
                    mon.held = random.randint(10, 20)
            self.add_msg("Nearby monsters freeze!")
        elif name == "blank paper":
            self.add_msg("This scroll seems to be blank.")

        p.remove_item(item)

    def eat_food(self, item):
        nutrition = item.data["nutrition"]
        self.player.food += nutrition
        self.player.state = "normal"
        self.add_msg(f"You eat the {item.data['name']}. Yum!")
        self.player.remove_item(item)

    def wield_weapon(self, item):
        if self.player.weapon and self.player.weapon.cursed:
            self.add_msg("You can't let go of your weapon!")
            return
        self.player.weapon = item
        self.add_msg(f"You wield the {self.ident.item_display(item)}.")

    def wear_armor(self, item):
        if self.player.armor:
            if self.player.armor.cursed:
                self.add_msg("You can't remove your cursed armor!")
                return
            self.add_msg("You take off your old armor.")
        self.player.armor = item
        self.player.recalc_ac()
        self.add_msg(f"You put on the {self.ident.item_display(item)}.")

    def take_off(self, item):
        if item is self.player.armor:
            if item.cursed:
                self.add_msg("You can't. It's cursed!")
                return
            self.player.armor = None
            self.player.recalc_ac()
            self.add_msg(f"You take off the {self.ident.item_display(item)}.")
        elif item is self.player.weapon:
            if item.cursed:
                self.add_msg("You can't let go. It's cursed!")
                return
            self.player.weapon = None
            self.add_msg(f"You put away the {self.ident.item_display(item)}.")

    def drop_item(self, item):
        if item is self.player.weapon and item.cursed:
            self.add_msg("You can't let go of it!")
            return
        if item is self.player.armor and item.cursed:
            self.add_msg("You can't take it off!")
            return
        self.player.remove_item(item)
        item.x, item.y = self.player.x, self.player.y
        self.ground_items.append(item)
        self.add_msg(f"You drop the {self.ident.item_display(item)}.")

    def throw_item(self, item, dx, dy):
        """Throw item in direction dx, dy."""
        p = self.player
        if item is p.weapon and item.cursed:
            self.add_msg("You can't let go!")
            return
        # Remove from inventory (stackable: throw 1)
        if item.stackable and item.quantity > 1:
            thrown = Item(item.category, item.kind, item.enchant, item.cursed, 1)
            item.quantity -= 1
        else:
            p.remove_item(item)
            thrown = item

        # Fly until hitting wall or monster
        tx, ty = p.x, p.y
        for _ in range(8):
            nx, ny = tx + dx, ty + dy
            if not self.is_walkable(nx, ny):
                break
            tx, ty = nx, ny
            m = self.monster_at(tx, ty)
            if m:
                # Hit monster
                if item.category == CAT_WEAPON:
                    dmg = roll(item.data["hurl"]) + item.enchant
                else:
                    dmg = roll("1d2")
                dmg = max(1, dmg)
                m.hp -= dmg
                self.add_msg(f"The {self.ident.item_display(thrown)} hits the {m.name}. ({dmg})")
                if not m.alive:
                    self.add_msg(f"The {m.name} is defeated!")
                    p.exp += m.exp
                    if p.check_levelup():
                        self.add_msg(f"Welcome to level {p.level}!")
                return

        # Lands on ground
        thrown.x, thrown.y = tx, ty
        self.ground_items.append(thrown)
        self.add_msg(f"The {self.ident.item_display(thrown)} lands on the floor.")

    # ------- Turns -------
    def try_move(self, dx, dy):
        p = self.player
        # Confusion: random direction
        if p.confused > 0:
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])

        nx, ny = p.x + dx, p.y + dy
        m = self.monster_at(nx, ny)
        if m:
            self.player_attack(m)
            self.end_turn()
            return

        if self.is_walkable(nx, ny):
            p.x, p.y = nx, ny
            # Auto-pickup gold
            gi = self.ground_item_at(nx, ny)
            if gi and gi.category == CAT_GOLD:
                p.gold += gi.quantity
                self.ground_items.remove(gi)
                self.add_msg(f"You found {gi.quantity} gold.")
            elif gi:
                self.add_msg(f"You see a {self.ident.item_display(gi)} here.")
            self.update_fov()
            self.end_turn()

    def do_pickup(self):
        p = self.player
        px, py = p.x, p.y
        tile = self.tilemap[py][px]

        # Check stairs first
        if tile == T_STAIRS:
            self.add_msg(f"You descend to depth {p.depth + 1}...")
            self.descend()
            self.add_msg(f"Dungeon depth {p.depth}.")
            return

        gi = self.ground_item_at(px, py)
        if gi:
            if gi.category == CAT_GOLD:
                p.gold += gi.quantity
                self.ground_items.remove(gi)
                self.add_msg(f"You pick up {gi.quantity} gold.")
            elif p.add_item(gi):
                self.ground_items.remove(gi)
                self.add_msg(f"You pick up the {self.ident.item_display(gi)}.")
            else:
                self.add_msg("Your pack is full.")
        else:
            self.add_msg("Nothing here to pick up.")

    def end_turn(self):
        p = self.player
        self.turn += 1
        msg = p.hunger_tick()
        if msg: self.add_msg(msg)

        if p.confused > 0: p.confused -= 1
        if p.blind > 0: p.blind -= 1
        if p.haste > 0: p.haste -= 1

        # Monster turns (player gets 2 moves when hasted)
        for m in self.monsters:
            self.monster_turn(m)
        self.monsters = [m for m in self.monsters if m.alive]

        if not p.alive:
            self.add_msg("You died... Press [R] to restart.")
            self.ui_state = ST_DEAD

    # ------- Menu logic -------
    def open_menu(self):
        self.ui_state = ST_MENU
        self.menu_cursor = 0

    def close_menu(self):
        self.ui_state = ST_PLAY
        self.menu_cursor = 0
        self.item_cursor = 0
        self.current_action = None
        self.filtered_items = []

    def menu_select_action(self):
        action_name, _key, cat_filter = MENU_ACTIONS[self.menu_cursor]
        self.current_action = action_name

        # Build filtered item list
        p = self.player
        if action_name == "Take off":
            self.filtered_items = [it for it in p.inventory
                                   if it is p.weapon or it is p.armor]
        elif action_name == "Throw" or action_name == "Drop":
            self.filtered_items = list(p.inventory)
        elif cat_filter:
            self.filtered_items = [it for it in p.inventory
                                   if it.category == cat_filter]
        else:
            self.filtered_items = list(p.inventory)

        if not self.filtered_items:
            self.add_msg(f"Nothing to {action_name.lower()}.")
            self.close_menu()
            return

        self.item_cursor = 0
        self.ui_state = ST_ITEM_SELECT

    def item_select_confirm(self):
        if not self.filtered_items:
            self.close_menu()
            return

        item = self.filtered_items[self.item_cursor]
        action = self.current_action

        if action == "Throw":
            self.ui_state = ST_DIR_SELECT
            return

        if action == "Quaff":
            self.use_potion(item)
        elif action == "Read":
            self.use_scroll(item)
        elif action == "Eat":
            self.eat_food(item)
        elif action == "Wield":
            self.wield_weapon(item)
        elif action == "Wear":
            self.wear_armor(item)
        elif action == "Take off":
            self.take_off(item)
        elif action == "Drop":
            self.drop_item(item)

        self.close_menu()
        self.end_turn()

    def dir_select_confirm(self, dx, dy):
        item = self.filtered_items[self.item_cursor]
        self.throw_item(item, dx, dy)
        self.close_menu()
        self.end_turn()

    # ------- Input -------
    def btnp(self, *keys):
        return any(pyxel.btnp(k) for k in keys)

    def dir_input(self):
        """Returns (dx,dy) or None."""
        if self.btnp(pyxel.KEY_UP, pyxel.KEY_K, pyxel.GAMEPAD1_BUTTON_DPAD_UP):
            return (0, -1)
        if self.btnp(pyxel.KEY_DOWN, pyxel.KEY_J, pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
            return (0, 1)
        if self.btnp(pyxel.KEY_LEFT, pyxel.KEY_H, pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            return (-1, 0)
        if self.btnp(pyxel.KEY_RIGHT, pyxel.KEY_L, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            return (1, 0)
        return None

    def btn_a(self):
        return self.btnp(pyxel.KEY_Z, pyxel.GAMEPAD1_BUTTON_A)

    def btn_b(self):
        return self.btnp(pyxel.KEY_X, pyxel.GAMEPAD1_BUTTON_B)

    def update(self):
        if self.ui_state == ST_DEAD:
            if pyxel.btnp(pyxel.KEY_R):
                self.new_game()
            return

        if self.ui_state == ST_PLAY:
            self.update_play()
        elif self.ui_state == ST_MENU:
            self.update_menu()
        elif self.ui_state == ST_ITEM_SELECT:
            self.update_item_select()
        elif self.ui_state == ST_DIR_SELECT:
            self.update_dir_select()

    def update_play(self):
        d = self.dir_input()
        if d:
            self.try_move(*d)
            # Extra move when hasted
            if self.player.haste > 0 and self.player.alive:
                d2 = self.dir_input()  # won't fire again same frame, but haste means monsters don't get extra turn
            return
        if self.btn_a():
            self.do_pickup()
            return
        if self.btn_b():
            self.open_menu()
            return

    def update_menu(self):
        d = self.dir_input()
        if d:
            dy = d[1]
            self.menu_cursor = (self.menu_cursor + dy) % len(MENU_ACTIONS)
            return
        if self.btn_a():
            self.menu_select_action()
            return
        if self.btn_b():
            self.close_menu()
            return

    def update_item_select(self):
        d = self.dir_input()
        if d:
            dy = d[1]
            if self.filtered_items:
                self.item_cursor = (self.item_cursor + dy) % len(self.filtered_items)
            return
        if self.btn_a():
            self.item_select_confirm()
            return
        if self.btn_b():
            self.ui_state = ST_MENU
            return

    def update_dir_select(self):
        d = self.dir_input()
        if d:
            self.dir_select_confirm(*d)
            return
        if self.btn_b():
            self.ui_state = ST_ITEM_SELECT
            return

    # ------- Drawing -------
    def draw(self):
        pyxel.cls(0)
        self.draw_title()
        self.draw_zoom()
        self.draw_minimap()
        self.draw_stats()
        self.draw_messages()
        self.draw_controls()

        # Overlay menus
        if self.ui_state == ST_MENU:
            self.draw_menu()
        elif self.ui_state == ST_ITEM_SELECT:
            self.draw_item_select()
        elif self.ui_state == ST_DIR_SELECT:
            self.draw_dir_prompt()

    def draw_title(self):
        pyxel.text(ZOOM_X, 4, " PYXEL ROGUE ", 10)
        pyxel.text(ZOOM_X + 60, 4, f"Depth:{self.player.depth}", 7)

    def draw_zoom(self):
        px, py = self.player.x, self.player.y
        cx, cy = px - ZOOM_COLS // 2, py - ZOOM_ROWS // 2
        pyxel.rectb(ZOOM_X-1, ZOOM_Y-1, ZOOM_PX_W+2, ZOOM_PX_H+2, 1)

        blind = self.player.blind > 0

        for vy in range(ZOOM_ROWS):
            for vx in range(ZOOM_COLS):
                mx, my = cx + vx, cy + vy
                sx = ZOOM_X + vx * ZOOM_TILE
                sy = ZOOM_Y + vy * ZOOM_TILE
                if not (0 <= mx < MAP_W and 0 <= my < MAP_H): continue

                is_vis = (mx, my) in self.visible and not blind
                is_exp = (mx, my) in self.explored

                if is_vis:
                    tile = self.tilemap[my][mx]
                    ch, col = TILE_DISP.get(tile, (" ", 0))
                    tx = sx + (ZOOM_TILE - 4) // 2
                    ty = sy + (ZOOM_TILE - 6) // 2
                    if ch != " ":
                        pyxel.text(tx, ty, ch, col)
                    # Ground item
                    gi = self.ground_item_at(mx, my)
                    if gi:
                        ic = ITEM_COLORS.get(gi.category, 7)
                        pyxel.text(tx, ty, gi.sym, ic)
                    # Monster
                    mon = self.monster_at(mx, my)
                    if mon and "invis" not in mon.flags:
                        pyxel.text(tx, ty, mon.sym, MON_COLORS.get(mon.sym, 7))
                    # Player
                    if mx == px and my == py:
                        pyxel.text(tx, ty, "@", 10)

                elif is_exp:
                    tile = self.tilemap[my][mx]
                    ch, _ = TILE_DISP.get(tile, (" ", 0))
                    if ch != " ":
                        tx = sx + (ZOOM_TILE - 4) // 2
                        ty = sy + (ZOOM_TILE - 6) // 2
                        pyxel.text(tx, ty, ch, 1)

    def draw_minimap(self):
        ox, oy = MINI_X, MINI_Y
        px, py = self.player.x, self.player.y
        pyxel.text(ox, oy - 9, "MAP", 6)
        pyxel.rectb(ox-1, oy-1, MINI_PX_W+2, MINI_PX_H+2, 1)

        for y in range(MAP_H):
            for x in range(MAP_W):
                is_vis = (x,y) in self.visible
                is_exp = (x,y) in self.explored
                if not (is_vis or is_exp): continue
                tile = self.tilemap[y][x]
                if tile == T_VOID: continue
                sx = ox + x * MINI_TILE
                sy = oy + y * MINI_TILE

                if is_vis:
                    col_map = {T_FLOOR:5, T_HWALL:6, T_VWALL:6, T_DOOR:9, T_CORRIDOR:5, T_STAIRS:10}
                    col = col_map.get(tile, 5)
                    pyxel.rect(sx, sy, MINI_TILE-1, MINI_TILE-1, col)
                    gi = self.ground_item_at(x, y)
                    if gi:
                        pyxel.rect(sx, sy, MINI_TILE-1, MINI_TILE-1, ITEM_COLORS.get(gi.category, 7))
                    mon = self.monster_at(x, y)
                    if mon and "invis" not in mon.flags:
                        pyxel.rect(sx, sy, MINI_TILE-1, MINI_TILE-1, 8)
                    if x == px and y == py:
                        pyxel.rect(sx, sy, MINI_TILE-1, MINI_TILE-1, 10)
                else:
                    pyxel.rect(sx, sy, MINI_TILE-1, MINI_TILE-1, 1)

    def draw_stats(self):
        sx, sy = STAT_X, STAT_Y
        p = self.player
        hp_col = 7 if p.hp > p.max_hp // 3 else 8
        pyxel.text(sx, sy, f"Lv:{p.level} Str:{p.str}/{p.max_str}", 7)
        pyxel.text(sx, sy+10, f"HP:{p.hp}/{p.max_hp}", hp_col)
        bar_w = 60
        pyxel.rect(sx, sy+20, bar_w, 4, 1)
        if p.max_hp > 0:
            fill = max(0, int(bar_w * p.hp / p.max_hp))
            pyxel.rect(sx, sy+20, fill, 4, 8 if p.hp <= p.max_hp//3 else 11)
        pyxel.text(sx, sy+28, f"AC:{p.ac}", 7)
        w_name = self.ident.item_display(p.weapon) if p.weapon else "bare hands"
        # Truncate weapon name for display
        pyxel.text(sx, sy+38, f"W:{w_name[:16]}", 7)
        pyxel.text(sx, sy+48, f"Exp:{p.exp}", 7)
        pyxel.text(sx, sy+58, f"Gold:{p.gold}", 10)
        pyxel.text(sx, sy+68, f"Turn:{self.turn}", 5)
        if p.state == "hungry": pyxel.text(sx, sy+80, "Hungry", 9)
        elif p.state == "weak": pyxel.text(sx, sy+80, "Weak!", 8)
        elif p.state == "faint": pyxel.text(sx, sy+80, "Faint!!", 8)
        if p.confused > 0: pyxel.text(sx+40, sy+80, "Cnfs", 2)

    def draw_messages(self):
        msgs = self.messages[-MSG_LINES:]
        for i, msg in enumerate(msgs):
            col = 7 if i == len(msgs) - 1 else 5
            pyxel.text(MSG_X, MSG_Y + i * 8, msg[:72], col)

    def draw_controls(self):
        y = SCREEN_H - 14
        if self.ui_state == ST_PLAY:
            pyxel.text(ZOOM_X, y, "[Arrows]Move [A/Z]Pickup [B/X]Menu", 1)
        elif self.ui_state in (ST_MENU, ST_ITEM_SELECT):
            pyxel.text(ZOOM_X, y, "[Arrows]Select [A/Z]OK [B/X]Cancel", 1)

    # ------- Menu overlay -------
    def draw_menu(self):
        bx, by = ZOOM_X + 20, ZOOM_Y + 10
        bw, bh = 120, len(MENU_ACTIONS) * 12 + 12
        pyxel.rect(bx, by, bw, bh, 0)
        pyxel.rectb(bx, by, bw, bh, 6)
        pyxel.text(bx + 4, by + 3, "-- Action --", 10)

        for i, (name, _key, _cat) in enumerate(MENU_ACTIONS):
            ty = by + 14 + i * 12
            col = 10 if i == self.menu_cursor else 7
            prefix = ">" if i == self.menu_cursor else " "
            pyxel.text(bx + 4, ty, f"{prefix} {name}", col)

    def draw_item_select(self):
        p = self.player
        bx, by = ZOOM_X + 20, ZOOM_Y + 10
        n = min(len(self.filtered_items), 12)
        bw, bh = 220, n * 10 + 24
        pyxel.rect(bx, by, bw, bh, 0)
        pyxel.rectb(bx, by, bw, bh, 6)
        pyxel.text(bx+4, by+3, f"-- {self.current_action} --", 10)

        # Scroll window if many items
        start = max(0, self.item_cursor - 11)
        for i, item in enumerate(self.filtered_items[start:start+12]):
            real_idx = start + i
            ty = by + 14 + i * 10
            letter = p.inv_letter(item)
            line = self.ident.inv_line(item, letter)
            # Mark equipped
            if item is p.weapon: line += " (wielded)"
            elif item is p.armor: line += " (worn)"
            col = 10 if real_idx == self.item_cursor else 7
            prefix = ">" if real_idx == self.item_cursor else " "
            pyxel.text(bx+4, ty, f"{prefix}{line[:40]}", col)

    def draw_dir_prompt(self):
        bx, by = ZOOM_X + 60, ZOOM_Y + 80
        pyxel.rect(bx, by, 140, 16, 0)
        pyxel.rectb(bx, by, 140, 16, 6)
        pyxel.text(bx + 4, by + 4, "Direction? [Arrows]", 10)


# ===========================================================
if __name__ == "__main__":
    Game()
