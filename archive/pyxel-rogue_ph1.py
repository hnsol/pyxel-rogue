"""
PYXEL ROGUE - Phase 1
A faithful clone of the original Rogue (5.4) for Pyxel.
Controls:
  Arrow keys / HJKL / D-pad : Move & bump attack
  Z / A button              : Action (pick up / descend stairs)
  X / B button              : Wait one turn
  R                         : Restart (on game over)
"""

import pyxel
import random

# ===========================================================
# Constants
# ===========================================================

# Map geometry (divisible by 3 for sector grid)
MAP_W = 48
MAP_H = 24
GRID_COLS = 3
GRID_ROWS = 3
SECTOR_W = MAP_W // GRID_COLS  # 16
SECTOR_H = MAP_H // GRID_ROWS  # 8

# Room size limits
MIN_ROOM_W = 5
MAX_ROOM_W = 12
MIN_ROOM_H = 4
MAX_ROOM_H = 7

# Screen layout
SCREEN_W = 480
SCREEN_H = 310

# Zoom view (left panel)
ZOOM_TILE = 14
ZOOM_COLS = 19
ZOOM_ROWS = 15
ZOOM_X = 4
ZOOM_Y = 14
ZOOM_PX_W = ZOOM_COLS * ZOOM_TILE  # 266
ZOOM_PX_H = ZOOM_ROWS * ZOOM_TILE  # 210

# Minimap (right panel)
MINI_TILE = 3
MINI_X = ZOOM_X + ZOOM_PX_W + 16  # 286
MINI_Y = ZOOM_Y
MINI_PX_W = MAP_W * MINI_TILE  # 144
MINI_PX_H = MAP_H * MINI_TILE  # 72

# Stats area (below minimap)
STAT_X = MINI_X
STAT_Y = MINI_Y + MINI_PX_H + 10

# Message area (below zoom view)
MSG_X = ZOOM_X
MSG_Y = ZOOM_Y + ZOOM_PX_H + 6
MSG_LINES = 3

# Tile types
T_VOID = 0
T_FLOOR = 1
T_HWALL = 2
T_VWALL = 3
T_DOOR = 4
T_CORRIDOR = 5
T_STAIRS = 6
T_GOLD = 7

# Tile display: (character, color_when_visible)
TILE_DISP = {
    T_VOID: (" ", 0),
    T_FLOOR: (".", 5),
    T_HWALL: ("-", 6),
    T_VWALL: ("|", 6),
    T_DOOR: ("+", 9),
    T_CORRIDOR: ("#", 5),
    T_STAIRS: ("%", 10),
    T_GOLD: ("*", 10),
}

WALKABLE = {T_FLOOR, T_DOOR, T_CORRIDOR, T_STAIRS, T_GOLD}

# ===========================================================
# Monster definitions faithful to Rogue 5.4
# level = earliest dungeon depth they appear
# ===========================================================
BESTIARY = [
    # sym  name            HP  ATK DEF EXP  lvl  flags
    ("A", "aquator",        30,  7,  2,  20,  9,  "rust"),
    ("B", "bat",             3,  1,  0,   1,  1,  "erratic,fly"),
    ("C", "centaur",        17,  6,  2,  15,  7,  ""),
    ("D", "dragon",         80, 14,  5, 100, 21,  ""),
    ("E", "emu",             5,  2,  0,   2,  1,  ""),
    ("F", "venus flytrap",  30,  8,  3,  25, 12,  "hold"),
    ("G", "griffin",        52, 10,  3,  40, 17,  "fly"),
    ("H", "hobgoblin",       8,  3,  1,   5,  1,  ""),
    ("I", "ice monster",    10,  4,  2,   8,  5,  "freeze"),
    ("J", "jabberwock",     60, 12,  4,  60, 20,  ""),
    ("K", "kestrel",         4,  2,  0,   2,  1,  "fly"),
    ("L", "leprechaun",     10,  2,  0,  10,  6,  "steal_gold"),
    ("M", "medusa",         40,  9,  3,  35, 18,  "confuse"),
    ("N", "nymph",          20,  3,  0,  15,  9,  "steal_item"),
    ("O", "orc",            12,  5,  3,  10,  5,  ""),
    ("P", "phantom",        30,  8,  3,  25, 15,  "invis"),
    ("Q", "quagga",         16,  5,  2,  12,  8,  ""),
    ("R", "rattlesnake",    10,  4,  1,   8,  4,  "poison"),
    ("S", "snake",           6,  2,  1,   3,  2,  ""),
    ("T", "troll",          30,  8,  3,  25, 13,  "regen"),
    ("U", "ur-vile",        40, 10,  4,  40, 18,  ""),
    ("V", "vampire",        35,  9,  3,  30, 16,  "drain"),
    ("W", "wraith",         25,  7,  2,  20, 14,  "drain_level"),
    ("X", "xeroc",          20,  6,  2,  15, 11,  "mimic"),
    ("Y", "yeti",           22,  6,  2,  18, 10,  ""),
    ("Z", "zombie",         15,  5,  2,  10,  7,  ""),
]

# Colors for monster letters (Pyxel palette indices)
MON_COLORS = {
    "A": 12, "B": 1, "C": 11, "D": 8, "E": 3,
    "F": 3, "G": 10, "H": 5, "I": 12, "J": 8,
    "K": 6, "L": 11, "M": 2, "N": 14, "O": 4,
    "P": 13, "Q": 4, "R": 8, "S": 11, "T": 3,
    "U": 2, "V": 8, "W": 13, "X": 9, "Y": 7,
    "Z": 5,
}


# ===========================================================
# Data classes
# ===========================================================

class Room:
    """A rectangular room on the map."""

    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    @property
    def cx(self):
        return self.x + self.w // 2

    @property
    def cy(self):
        return self.y + self.h // 2

    def inner_point(self):
        """Random floor point inside the room (excluding walls)."""
        return (
            random.randint(self.x + 1, self.x + self.w - 2),
            random.randint(self.y + 1, self.y + self.h - 2),
        )


class Monster:
    """A dungeon inhabitant."""

    def __init__(self, x, y, sym, name, hp, atk, def_, exp, flags_str):
        self.x = x
        self.y = y
        self.sym = sym
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.atk = atk
        self.def_ = def_
        self.exp = exp
        self.flags = set(flags_str.split(",")) if flags_str else set()

    @property
    def alive(self):
        return self.hp > 0


class Player:
    """The brave adventurer."""

    def __init__(self):
        self.x = 0
        self.y = 0
        self.hp = 16
        self.max_hp = 16
        self.str = 16
        self.max_str = 16
        self.atk = 4
        self.def_ = 1
        self.level = 1
        self.exp = 0
        self.gold = 0
        self.depth = 0   # incremented when descending
        self.food = 1300  # turns until starving
        self.state = "normal"  # normal / hungry / weak / faint

    @property
    def alive(self):
        return self.hp > 0

    # Rogue 5.4 experience table (cumulative)
    EXP_TABLE = [0, 10, 20, 40, 80, 160, 320, 640, 1300, 2600,
                 5200, 10000, 20000, 40000, 80000, 160000, 320000,
                 640000, 1300000, 2600000, 5200000]

    def check_levelup(self):
        """Returns True if levelled up."""
        if self.level >= len(self.EXP_TABLE):
            return False
        if self.exp >= self.EXP_TABLE[self.level]:
            self.level += 1
            gain = random.randint(3, 8)
            self.max_hp += gain
            self.hp += gain
            self.atk += 1
            return True
        return False

    def hunger_tick(self):
        """Process one turn of hunger. Returns message or None."""
        self.food -= 1
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


# ===========================================================
# Dungeon generator (faithful Rogue 3×3 grid algorithm)
# ===========================================================

class DungeonGenerator:
    """Generates a Rogue-style dungeon level."""

    @staticmethod
    def generate(depth):
        tilemap = [[T_VOID] * MAP_W for _ in range(MAP_H)]
        rooms = []
        sector_rooms = {}

        # Decide which sectors get rooms (minimum 6 of 9)
        sector_list = [(gx, gy) for gy in range(GRID_ROWS) for gx in range(GRID_COLS)]
        random.shuffle(sector_list)
        num_rooms = random.randint(6, 9)
        active_sectors = set(sector_list[:num_rooms])

        # Create rooms in active sectors
        for gx, gy in sector_list:
            if (gx, gy) not in active_sectors:
                continue
            sx = gx * SECTOR_W
            sy = gy * SECTOR_H
            rw = random.randint(MIN_ROOM_W, min(MAX_ROOM_W, SECTOR_W - 2))
            rh = random.randint(MIN_ROOM_H, min(MAX_ROOM_H, SECTOR_H - 2))
            rx = sx + random.randint(1, max(1, SECTOR_W - rw - 1))
            ry = sy + random.randint(1, max(1, SECTOR_H - rh - 1))
            # Clamp to map bounds
            if rx + rw > MAP_W - 1:
                rw = MAP_W - 1 - rx
            if ry + rh > MAP_H - 1:
                rh = MAP_H - 1 - ry
            room = Room(rx, ry, rw, rh)
            rooms.append(room)
            sector_rooms[(gx, gy)] = room
            DungeonGenerator._carve_room(tilemap, room)

        # Connect adjacent sectors that both have rooms
        connected_pairs = set()
        for gy in range(GRID_ROWS):
            for gx in range(GRID_COLS):
                if (gx, gy) not in sector_rooms:
                    continue
                # Right neighbour
                if gx + 1 < GRID_COLS and (gx + 1, gy) in sector_rooms:
                    pair = ((gx, gy), (gx + 1, gy))
                    if pair not in connected_pairs:
                        DungeonGenerator._carve_corridor(
                            tilemap,
                            sector_rooms[(gx, gy)],
                            sector_rooms[(gx + 1, gy)],
                        )
                        connected_pairs.add(pair)
                # Down neighbour
                if gy + 1 < GRID_ROWS and (gx, gy + 1) in sector_rooms:
                    pair = ((gx, gy), (gx, gy + 1))
                    if pair not in connected_pairs:
                        DungeonGenerator._carve_corridor(
                            tilemap,
                            sector_rooms[(gx, gy)],
                            sector_rooms[(gx, gy + 1)],
                        )
                        connected_pairs.add(pair)

        # Ensure full connectivity via flood-fill check
        DungeonGenerator._ensure_connectivity(tilemap, rooms)

        # Place gold piles
        DungeonGenerator._place_gold(tilemap, rooms, depth)

        return tilemap, rooms

    @staticmethod
    def _carve_room(tilemap, r):
        for y in range(r.y, r.y + r.h):
            for x in range(r.x, r.x + r.w):
                if 0 <= y < MAP_H and 0 <= x < MAP_W:
                    if y == r.y or y == r.y + r.h - 1:
                        tilemap[y][x] = T_HWALL
                    elif x == r.x or x == r.x + r.w - 1:
                        tilemap[y][x] = T_VWALL
                    else:
                        tilemap[y][x] = T_FLOOR

    @staticmethod
    def _carve_corridor(tilemap, r1, r2):
        x1, y1 = r1.cx, r1.cy
        x2, y2 = r2.cx, r2.cy
        if random.random() < 0.5:
            DungeonGenerator._hline(tilemap, x1, x2, y1)
            DungeonGenerator._vline(tilemap, y1, y2, x2)
        else:
            DungeonGenerator._vline(tilemap, y1, y2, x1)
            DungeonGenerator._hline(tilemap, x1, x2, y2)

    @staticmethod
    def _hline(tilemap, x1, x2, y):
        if not (0 <= y < MAP_H):
            return
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if not (0 <= x < MAP_W):
                continue
            t = tilemap[y][x]
            if t in (T_HWALL, T_VWALL):
                tilemap[y][x] = T_DOOR
            elif t in (T_VOID,):
                tilemap[y][x] = T_CORRIDOR
            # FLOOR, DOOR, CORRIDOR, STAIRS — leave as-is

    @staticmethod
    def _vline(tilemap, y1, y2, x):
        if not (0 <= x < MAP_W):
            return
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if not (0 <= y < MAP_H):
                continue
            t = tilemap[y][x]
            if t in (T_HWALL, T_VWALL):
                tilemap[y][x] = T_DOOR
            elif t in (T_VOID,):
                tilemap[y][x] = T_CORRIDOR

    @staticmethod
    def _flood(tilemap, start):
        visited = set()
        stack = [start]
        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue
            if not (0 <= x < MAP_W and 0 <= y < MAP_H):
                continue
            if tilemap[y][x] == T_VOID:
                continue
            visited.add((x, y))
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                stack.append((x + dx, y + dy))
        return visited

    @staticmethod
    def _ensure_connectivity(tilemap, rooms):
        if len(rooms) <= 1:
            return
        base = DungeonGenerator._flood(tilemap, (rooms[0].cx, rooms[0].cy))
        for room in rooms[1:]:
            if (room.cx, room.cy) not in base:
                DungeonGenerator._carve_corridor(tilemap, rooms[0], room)
                base = DungeonGenerator._flood(tilemap, (rooms[0].cx, rooms[0].cy))

    @staticmethod
    def _place_gold(tilemap, rooms, depth):
        num = random.randint(1, 3)
        for _ in range(num):
            room = random.choice(rooms)
            for _try in range(20):
                gx, gy = room.inner_point()
                if tilemap[gy][gx] == T_FLOOR:
                    tilemap[gy][gx] = T_GOLD
                    break


# ===========================================================
# Game class
# ===========================================================

class Game:
    def __init__(self):
        pyxel.init(SCREEN_W, SCREEN_H, title="Pyxel Rogue", fps=30)
        self.new_game()
        pyxel.run(self.update, self.draw)

    # -------------------------------------------------------
    # Initialisation
    # -------------------------------------------------------
    def new_game(self):
        self.player = Player()
        self.messages = []
        self.explored = set()
        self.visible = set()
        self.turn = 0
        self.game_over = False
        self.gold_map = {}  # (x,y) -> amount
        self.descend_to_next_level()
        self.add_msg("Welcome to the Dungeons of Doom!")

    def descend_to_next_level(self):
        self.player.depth += 1
        self.tilemap, self.rooms = DungeonGenerator.generate(self.player.depth)
        self.monsters = []
        self.visible = set()
        # explored carries over only within a level (original resets per floor)
        self.explored = set()
        self.gold_map = {}

        # Populate gold amounts
        for y in range(MAP_H):
            for x in range(MAP_W):
                if self.tilemap[y][x] == T_GOLD:
                    self.gold_map[(x, y)] = random.randint(1, 10) * self.player.depth

        # Place player in first room
        px, py = self.rooms[0].inner_point()
        self.player.x, self.player.y = px, py

        # Place stairs in last room
        sr = self.rooms[-1]
        sx, sy = sr.inner_point()
        self.tilemap[sy][sx] = T_STAIRS

        # Spawn monsters
        self.spawn_monsters()

        # Initial FOV
        self.update_fov()

    def spawn_monsters(self):
        depth = self.player.depth
        num = random.randint(3, 4 + depth)
        candidates = [b for b in BESTIARY if b[6] <= depth]
        if not candidates:
            candidates = [b for b in BESTIARY if b[6] <= 3]

        for _ in range(num):
            room = random.choice(self.rooms)
            entry = random.choice(candidates)
            for _try in range(30):
                mx, my = room.inner_point()
                if (self.tilemap[my][mx] in WALKABLE
                        and not self.monster_at(mx, my)
                        and not (mx == self.player.x and my == self.player.y)):
                    sym, name, hp, atk, def_, exp, _lvl, flags = entry
                    # Scale HP slightly with depth
                    hp_scaled = hp + random.randint(0, depth // 3)
                    m = Monster(mx, my, sym, name, hp_scaled, atk, def_, exp, flags)
                    self.monsters.append(m)
                    break

    # -------------------------------------------------------
    # Helpers
    # -------------------------------------------------------
    def monster_at(self, x, y):
        for m in self.monsters:
            if m.alive and m.x == x and m.y == y:
                return m
        return None

    def is_walkable(self, x, y):
        if not (0 <= x < MAP_W and 0 <= y < MAP_H):
            return False
        return self.tilemap[y][x] in WALKABLE

    def room_at(self, x, y):
        for r in self.rooms:
            if r.x < x < r.x + r.w - 1 and r.y < y < r.y + r.h - 1:
                return r
        return None

    def add_msg(self, text):
        self.messages.append(text)
        if len(self.messages) > 100:
            self.messages = self.messages[-100:]

    # -------------------------------------------------------
    # FOV — faithful to original: room = full visibility,
    #        corridor = 1 tile radius
    # -------------------------------------------------------
    def update_fov(self):
        self.visible = set()
        px, py = self.player.x, self.player.y

        # If in a room, reveal entire room + doorways
        room = self.room_at(px, py)
        if room:
            for ry in range(room.y, room.y + room.h):
                for rx in range(room.x, room.x + room.w):
                    if 0 <= rx < MAP_W and 0 <= ry < MAP_H:
                        self.visible.add((rx, ry))
                        # Peek one tile outside doors
                        if self.tilemap[ry][rx] == T_DOOR:
                            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                                nx, ny = rx + dx, ry + dy
                                if 0 <= nx < MAP_W and 0 <= ny < MAP_H:
                                    self.visible.add((nx, ny))

        # Always see 1-tile radius around player
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx, ny = px + dx, py + dy
                if 0 <= nx < MAP_W and 0 <= ny < MAP_H:
                    self.visible.add((nx, ny))

        self.explored |= self.visible

    # -------------------------------------------------------
    # Combat
    # -------------------------------------------------------
    def player_attack(self, m):
        """Player attacks monster (bump attack)."""
        # Rogue-style: d20 roll + level + str_bonus vs AC
        roll = random.randint(1, 20)
        hit = roll + self.player.level
        ac = 10 - m.def_
        if hit >= ac or roll == 20:
            damage = max(1, self.player.atk + random.randint(0, 3) - m.def_)
            m.hp -= damage
            if not m.alive:
                self.add_msg(f"You defeated the {m.name}. ({m.exp} exp)")
                self.player.exp += m.exp
                if self.player.check_levelup():
                    self.add_msg(f"Welcome to level {self.player.level}!")
            else:
                self.add_msg(f"You hit the {m.name} ({damage} dmg).")
        else:
            self.add_msg(f"You miss the {m.name}.")

    def monster_attack(self, m):
        """Monster attacks player."""
        roll = random.randint(1, 20)
        ac = 10 - self.player.def_
        if roll >= ac or roll == 20:
            damage = max(1, m.atk + random.randint(0, 2) - self.player.def_)
            self.player.hp -= damage
            self.add_msg(f"The {m.name} hits! ({damage} dmg)")
            # Special flags
            if "steal_gold" in m.flags and self.player.gold > 0:
                stolen = min(self.player.gold, random.randint(10, 50))
                self.player.gold -= stolen
                self.add_msg(f"The {m.name} steals {stolen} gold!")
            if "poison" in m.flags and random.random() < 0.3:
                if self.player.str > 6:
                    self.player.str -= 1
                    self.add_msg("You feel weaker!")
            if "drain" in m.flags and random.random() < 0.3:
                self.player.max_hp = max(1, self.player.max_hp - 1)
                self.add_msg("You feel drained!")
        else:
            self.add_msg(f"The {m.name} misses.")

    # -------------------------------------------------------
    # Monster AI
    # -------------------------------------------------------
    def monster_turn(self, m):
        if not m.alive:
            return
        px, py = self.player.x, self.player.y
        dist = abs(m.x - px) + abs(m.y - py)

        # Erratic monsters move randomly half the time
        if "erratic" in m.flags and random.random() < 0.5:
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
        elif dist <= 8 and (m.x, m.y) in self.visible:
            # Chase player
            dx = (1 if m.x < px else -1 if m.x > px else 0)
            dy = (1 if m.y < py else -1 if m.y > py else 0)
            # 4-directional: pick one axis
            if dx != 0 and dy != 0:
                if random.random() < 0.5:
                    dx = 0
                else:
                    dy = 0
        else:
            return  # idle

        # Regenerating monsters
        if "regen" in m.flags and m.hp < m.max_hp and random.random() < 0.3:
            m.hp += 1

        nx, ny = m.x + dx, m.y + dy

        # Adjacent to player? Attack.
        if nx == px and ny == py:
            self.monster_attack(m)
            return

        # Move
        if self.is_walkable(nx, ny) and not self.monster_at(nx, ny):
            m.x = nx
            m.y = ny

    # -------------------------------------------------------
    # Turn processing
    # -------------------------------------------------------
    def try_move(self, dx, dy):
        if self.game_over:
            return
        nx = self.player.x + dx
        ny = self.player.y + dy

        # Bump attack?
        m = self.monster_at(nx, ny)
        if m:
            self.player_attack(m)
            self.end_turn()
            return

        if self.is_walkable(nx, ny):
            self.player.x = nx
            self.player.y = ny
            # Pick up gold automatically
            if self.tilemap[ny][nx] == T_GOLD:
                amount = self.gold_map.pop((nx, ny), 0)
                self.player.gold += amount
                self.tilemap[ny][nx] = T_FLOOR
                self.add_msg(f"You found {amount} gold.")
            self.update_fov()
            self.end_turn()

    def do_action(self):
        """Context-sensitive A-button action."""
        if self.game_over:
            return
        px, py = self.player.x, self.player.y
        tile = self.tilemap[py][px]
        if tile == T_STAIRS:
            self.add_msg(f"You descend to depth {self.player.depth + 1}...")
            self.descend_to_next_level()
            self.add_msg(f"Dungeon depth {self.player.depth}.")
        elif tile == T_GOLD:
            amount = self.gold_map.pop((px, py), 0)
            self.player.gold += amount
            self.tilemap[py][px] = T_FLOOR
            self.add_msg(f"You pick up {amount} gold.")
        else:
            self.add_msg("Nothing to do here.")

    def do_wait(self):
        """B-button: wait one turn."""
        if not self.game_over:
            self.end_turn()

    def end_turn(self):
        self.turn += 1

        # Hunger
        msg = self.player.hunger_tick()
        if msg:
            self.add_msg(msg)

        # Monster turns
        for m in self.monsters:
            self.monster_turn(m)

        # Remove dead monsters
        self.monsters = [m for m in self.monsters if m.alive]

        # Check player death
        if not self.player.alive:
            self.add_msg("You died... Press [R] to restart.")
            self.game_over = True

    # -------------------------------------------------------
    # Input
    # -------------------------------------------------------
    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_R):
                self.new_game()
            return

        moved = False
        dx, dy = 0, 0

        # Arrow keys / HJKL / Gamepad D-pad
        if (pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_K)
                or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP)):
            dy = -1; moved = True
        elif (pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.KEY_J)
              or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)):
            dy = 1; moved = True
        elif (pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_H)
              or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)):
            dx = -1; moved = True
        elif (pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_L)
              or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)):
            dx = 1; moved = True

        if moved:
            self.try_move(dx, dy)
            return

        # A button / Z: action
        if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            self.do_action()

        # B button / X: wait
        if pyxel.btnp(pyxel.KEY_X) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
            self.do_wait()

    # -------------------------------------------------------
    # Drawing
    # -------------------------------------------------------
    def draw(self):
        pyxel.cls(0)
        self.draw_title_bar()
        self.draw_zoom_view()
        self.draw_minimap()
        self.draw_stats()
        self.draw_messages()
        self.draw_controls_help()

    def draw_title_bar(self):
        depth_str = f"Depth:{self.player.depth}"
        title = f" PYXEL ROGUE "
        pyxel.text(ZOOM_X, 4, title, 10)
        pyxel.text(ZOOM_X + len(title) * 4 + 8, 4, depth_str, 7)

    def draw_zoom_view(self):
        px, py = self.player.x, self.player.y
        cam_x = px - ZOOM_COLS // 2
        cam_y = py - ZOOM_ROWS // 2

        # Border
        pyxel.rectb(
            ZOOM_X - 1, ZOOM_Y - 1,
            ZOOM_PX_W + 2, ZOOM_PX_H + 2, 1
        )

        for vy in range(ZOOM_ROWS):
            for vx in range(ZOOM_COLS):
                mx = cam_x + vx
                my = cam_y + vy
                sx = ZOOM_X + vx * ZOOM_TILE
                sy = ZOOM_Y + vy * ZOOM_TILE

                if not (0 <= mx < MAP_W and 0 <= my < MAP_H):
                    continue

                is_vis = (mx, my) in self.visible
                is_exp = (mx, my) in self.explored

                if is_vis:
                    tile = self.tilemap[my][mx]
                    ch, col = TILE_DISP.get(tile, (" ", 0))
                    if ch != " ":
                        # Center character in tile cell
                        cx = sx + (ZOOM_TILE - 4) // 2
                        cy = sy + (ZOOM_TILE - 6) // 2
                        pyxel.text(cx, cy, ch, col)

                    # Draw monster
                    mon = self.monster_at(mx, my)
                    if mon and "invis" not in mon.flags:
                        mc = MON_COLORS.get(mon.sym, 7)
                        cx = sx + (ZOOM_TILE - 4) // 2
                        cy = sy + (ZOOM_TILE - 6) // 2
                        pyxel.text(cx, cy, mon.sym, mc)

                    # Draw player (always on top)
                    if mx == px and my == py:
                        cx = sx + (ZOOM_TILE - 4) // 2
                        cy = sy + (ZOOM_TILE - 6) // 2
                        pyxel.text(cx, cy, "@", 10)

                elif is_exp:
                    tile = self.tilemap[my][mx]
                    ch, _ = TILE_DISP.get(tile, (" ", 0))
                    if ch != " ":
                        cx = sx + (ZOOM_TILE - 4) // 2
                        cy = sy + (ZOOM_TILE - 6) // 2
                        pyxel.text(cx, cy, ch, 1)

    def draw_minimap(self):
        ox, oy = MINI_X, MINI_Y
        px, py = self.player.x, self.player.y

        # Label
        pyxel.text(ox, oy - 9, "MAP", 6)

        # Border
        pyxel.rectb(ox - 1, oy - 1, MINI_PX_W + 2, MINI_PX_H + 2, 1)

        for y in range(MAP_H):
            for x in range(MAP_W):
                is_vis = (x, y) in self.visible
                is_exp = (x, y) in self.explored
                if not (is_vis or is_exp):
                    continue

                tile = self.tilemap[y][x]
                if tile == T_VOID:
                    continue

                sx = ox + x * MINI_TILE
                sy = oy + y * MINI_TILE

                if is_vis:
                    # Tile colors
                    if tile == T_FLOOR:
                        col = 5
                    elif tile in (T_HWALL, T_VWALL):
                        col = 6
                    elif tile == T_DOOR:
                        col = 9
                    elif tile == T_CORRIDOR:
                        col = 5
                    elif tile == T_STAIRS:
                        col = 10
                    elif tile == T_GOLD:
                        col = 10
                    else:
                        col = 5
                    pyxel.rect(sx, sy, MINI_TILE - 1, MINI_TILE - 1, col)

                    # Monster dot
                    mon = self.monster_at(x, y)
                    if mon and "invis" not in mon.flags:
                        pyxel.rect(sx, sy, MINI_TILE - 1, MINI_TILE - 1, 8)

                    # Player dot
                    if x == px and y == py:
                        pyxel.rect(sx, sy, MINI_TILE - 1, MINI_TILE - 1, 10)
                else:
                    # Explored but not visible
                    pyxel.rect(sx, sy, MINI_TILE - 1, MINI_TILE - 1, 1)

    def draw_stats(self):
        sx, sy = STAT_X, STAT_Y
        p = self.player
        c7 = 7  # normal
        hp_col = 7 if p.hp > p.max_hp // 3 else 8

        pyxel.text(sx, sy, f"Lv:{p.level}  Str:{p.str}/{p.max_str}", c7)
        pyxel.text(sx, sy + 10, f"HP:{p.hp}/{p.max_hp}", hp_col)

        # HP bar
        bar_w = 60
        bar_x = sx
        bar_y = sy + 20
        pyxel.rect(bar_x, bar_y, bar_w, 4, 1)
        if p.max_hp > 0:
            fill = max(0, int(bar_w * p.hp / p.max_hp))
            pyxel.rect(bar_x, bar_y, fill, 4, 8 if p.hp <= p.max_hp // 3 else 11)

        pyxel.text(sx, sy + 28, f"Atk:{p.atk}  Def:{p.def_}", c7)
        pyxel.text(sx, sy + 38, f"Exp:{p.exp}", c7)
        pyxel.text(sx, sy + 48, f"Gold:{p.gold}", 10)
        pyxel.text(sx, sy + 58, f"Turn:{self.turn}", 5)

        # Hunger indicator
        if p.state == "hungry":
            pyxel.text(sx, sy + 70, "Hungry", 9)
        elif p.state == "weak":
            pyxel.text(sx, sy + 70, "Weak!", 8)
        elif p.state == "faint":
            pyxel.text(sx, sy + 70, "Faint!!", 8)

    def draw_messages(self):
        msgs = self.messages[-(MSG_LINES):]
        for i, msg in enumerate(msgs):
            col = 7 if i == len(msgs) - 1 else 5
            # Truncate long messages
            display = msg[:72]
            pyxel.text(MSG_X, MSG_Y + i * 8, display, col)

    def draw_controls_help(self):
        y = SCREEN_H - 14
        help_text = "[Arrows/HJKL]Move [Z]Action [X]Wait"
        pyxel.text(ZOOM_X, y, help_text, 1)


# ===========================================================
# Entry point
# ===========================================================
if __name__ == "__main__":
    Game()