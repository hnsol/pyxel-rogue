from dataclasses import dataclass

import rogue_things

LEFT = 0
RIGHT = 1

R_PROTECT = 0
R_ADDSTR = 1
R_SUSTSTR = 2
R_SEARCH = 3
R_SEEINVIS = 4
R_NOP = 5
R_AGGR = 6
R_ADDHIT = 7
R_ADDDAM = 8
R_REGEN = 9
R_DIGEST = 10
R_TELEPORT = 11
R_STEALTH = 12
R_SUSTARM = 13


@dataclass(frozen=True)
class RingSpec:
    name: str
    prob: int
    worth: int


@dataclass
class RingItem:
    cat: str
    kind: int
    ench: int = 0
    cursed: bool = False
    qty: int = 1


# Rogue 5.4.4 extern.c:ring_info[] order matches rogue.h R_* constants.
RINGS = [
    RingSpec("protection", 9, 400),
    RingSpec("add strength", 9, 400),
    RingSpec("sustain strength", 5, 280),
    RingSpec("searching", 10, 420),
    RingSpec("see invisible", 10, 310),
    RingSpec("adornment", 1, 10),
    RingSpec("aggravate monster", 10, 10),
    RingSpec("dexterity", 8, 440),
    RingSpec("increase damage", 8, 400),
    RingSpec("regeneration", 4, 460),
    RingSpec("slow digestion", 9, 240),
    RingSpec("teleportation", 5, 30),
    RingSpec("stealth", 7, 470),
    RingSpec("maintain armor", 5, 380),
]

# Rogue 5.4.4 init.c:stones[].
STONES = [
    "agate", "alexandrite", "amethyst", "carnelian", "diamond", "emerald",
    "germanium", "granite", "garnet", "jade", "kryptonite", "lapis lazuli",
    "moonstone", "obsidian", "onyx", "opal", "pearl", "peridot", "ruby",
    "sapphire", "stibotantalite", "tiger eye", "topaz", "turquoise",
    "taaffeite", "zircon",
]

_RING_EAT_USES = [1, 1, 1, -3, -5, 0, 0, -3, -3, 2, -2, 0, 1, 1]
_BONUS_RINGS = {R_PROTECT, R_ADDSTR, R_ADDHIT, R_ADDDAM}
_ALWAYS_CURSED = {R_AGGR, R_TELEPORT}


def pick_ring_kind(rng):
    """Rogue 5.4.4 things.c:pick_one(ring_info, MAXRINGS)."""
    return rogue_things.pick_one([(spec.name, spec.prob) for spec in RINGS], rng.rnd(100))


def make_ring(rng, cat="ring"):
    """Create ring fields using Rogue 5.4.4 things.c:new_thing() ring branch."""
    kind = pick_ring_kind(rng)
    ench = 0
    cursed = False
    if kind in _BONUS_RINGS:
        ench = rng.rnd(3)
        if ench == 0:
            ench = -1
            cursed = True
    elif kind in _ALWAYS_CURSED:
        cursed = True
    return RingItem(cat=cat, kind=kind, ench=ench, cursed=cursed)


def init_stones(rng):
    """Rogue 5.4.4 init.c:init_stones() without worth mutation."""
    stones = list(STONES)
    rng.shuffle(stones)
    return stones[:len(RINGS)]


def is_ring(item, kind):
    """Return True if item is a ring of the given kind constant."""
    return item is not None and getattr(item, "kind", None) == kind


def is_wearing(player, kind):
    """Return True if player is wearing a ring of the given kind in either hand."""
    return is_ring(player.ring_l, kind) or is_ring(player.ring_r, kind)


def wearing_hands(player, kind):
    """Yield LEFT and/or RIGHT for each hand wearing a ring of the given kind."""
    if is_ring(player.ring_l, kind):
        yield LEFT
    if is_ring(player.ring_r, kind):
        yield RIGHT


def ring_num(item):
    """Return the enchantment suffix string for bonus rings (e.g. ' [+2]')."""
    kind = getattr(item, "kind", None)
    if kind not in _BONUS_RINGS:
        return ""
    ench = getattr(item, "ench", 0)
    return f" [{'+' if ench >= 0 else ''}{ench}]"


def ring_eat(ring, rng):
    """Rogue 5.4.4 rings.c:ring_eat()."""
    if ring is None:
        return 0
    eat = _RING_EAT_USES[getattr(ring, "kind", R_NOP)]
    if eat < 0:
        eat = 1 if rng.rnd(-eat) == 0 else 0
    if getattr(ring, "kind", None) == R_DIGEST:
        eat = -eat
    return eat


def equipped_ring(player, hand):
    """Return the ring equipped in the given hand slot (LEFT or RIGHT)."""
    return player.ring_l if hand == LEFT else player.ring_r


def ring_slot_for(player, ring):
    """Return LEFT, RIGHT, or None depending on which hand holds the ring."""
    if player.ring_l is ring:
        return LEFT
    if player.ring_r is ring:
        return RIGHT
    return None


def put_on_ring(player, ring, hand=None):
    """Rogue 5.4.4 rings.c:ring_on() — equip ring into hand slot."""
    if ring_slot_for(player, ring) is not None:
        return False
    if hand is None:
        if player.ring_l is None and player.ring_r is not None:
            hand = LEFT
        elif player.ring_r is None and player.ring_l is not None:
            hand = RIGHT
        else:
            hand = LEFT
    if hand == LEFT:
        if player.ring_l is not None:
            return False
        player.ring_l = ring
    else:
        if player.ring_r is not None:
            return False
        player.ring_r = ring
    _apply_on_effect(player, ring)
    return True


def ring_on_result(item_is_ring: bool, is_current: bool, both_hands_full: bool) -> str:
    """Rogue 5.4.4 rings.c:ring_on() gate result."""
    if not item_is_ring:
        return "not-ring"
    if is_current:
        return "current"
    if both_hands_full:
        return "full"
    return "put-on"


def ring_off_result(is_wearing: bool, is_cursed: bool) -> str:
    """Rogue 5.4.4 rings.c:ring_off() and things.c:dropcheck() gate result."""
    if not is_wearing:
        return "not-wearing"
    if is_cursed:
        return "cursed"
    return "take-off"


def remove_ring(player, ring):
    """Rogue 5.4.4 rings.c:ring_off() — remove ring; refuses if cursed."""
    hand = ring_slot_for(player, ring)
    if hand is None or getattr(ring, "cursed", False):
        return False
    if hand == LEFT:
        player.ring_l = None
    else:
        player.ring_r = None
    _remove_on_effect(player, ring)
    return True


def _apply_on_effect(player, ring):
    """Apply stat side-effects when a ring is equipped (rings.c:ring_on)."""
    if ring.kind == R_ADDSTR:
        player.st += ring.ench


def _remove_on_effect(player, ring):
    """Reverse stat side-effects when a ring is removed (rings.c:ring_off)."""
    if ring.kind == R_ADDSTR:
        player.st -= ring.ench


def protection_bonus(player):
    """Sum R_PROTECT enchantments from both equipped rings."""
    total = 0
    for ring in (player.ring_l, player.ring_r):
        if is_ring(ring, R_PROTECT):
            total += ring.ench
    return total


def weapon_hit_bonus(player, weapon, thrown=False):
    """Return R_ADDHIT bonus when fight.c:roll_em() sees weap == cur_weapon."""
    if weapon is not player.wpn:
        return 0
    total = 0
    for ring in (player.ring_l, player.ring_r):
        if is_ring(ring, R_ADDHIT):
            total += ring.ench
    return total


def weapon_damage_bonus(player, weapon, thrown=False):
    """Return R_ADDDAM bonus when fight.c:roll_em() sees weap == cur_weapon."""
    if weapon is not player.wpn:
        return 0
    total = 0
    for ring in (player.ring_l, player.ring_r):
        if is_ring(ring, R_ADDDAM):
            total += ring.ench
    return total


def regeneration_count(player):
    """Return number of R_REGEN rings equipped (0, 1 or 2)."""
    return int(is_ring(player.ring_l, R_REGEN)) + int(is_ring(player.ring_r, R_REGEN))
