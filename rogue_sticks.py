from dataclasses import dataclass

import rogue_things

WS_LIGHT = 0
WS_INVIS = 1
WS_ELECT = 2
WS_FIRE = 3
WS_COLD = 4
WS_POLYMORPH = 5
WS_MISSILE = 6
WS_HASTE_M = 7
WS_SLOW_M = 8
WS_DRAIN = 9
WS_NOP = 10
WS_TELAWAY = 11
WS_TELTO = 12
WS_CANCEL = 13


@dataclass(frozen=True)
class StickSpec:
    name: str
    prob: int
    worth: int


@dataclass
class StickItem:
    cat: str
    kind: int
    charges: int = 0


# Rogue 5.4.4 extern.c:ws_info[] order matches rogue.h WS_* constants.
STICKS = [
    StickSpec("light", 12, 250),
    StickSpec("invisibility", 6, 5),
    StickSpec("lightning", 3, 330),
    StickSpec("fire", 3, 330),
    StickSpec("cold", 3, 330),
    StickSpec("polymorph", 15, 310),
    StickSpec("magic missile", 10, 170),
    StickSpec("haste monster", 10, 5),
    StickSpec("slow monster", 11, 350),
    StickSpec("drain life", 9, 300),
    StickSpec("nothing", 1, 5),
    StickSpec("teleport away", 6, 340),
    StickSpec("teleport to", 6, 50),
    StickSpec("cancellation", 5, 280),
]

# Rogue 5.4.4 init.c:metal[] / wood[].
METALS = [
    "aluminum", "beryllium", "bone", "brass", "bronze", "copper",
    "electrum", "gold", "iron", "lead", "magnesium", "mercury",
    "nickel", "pewter", "platinum", "steel", "silver", "silicon",
    "tin", "titanium", "tungsten", "zinc",
]

WOODS = [
    "avocado wood", "balsa", "bamboo", "banyan", "birch", "cedar",
    "cherry", "cinnibar", "cypress", "dogwood", "driftwood", "ebony",
    "elm", "eucalyptus", "fall", "hemlock", "holly", "ironwood",
    "kukui wood", "mahogany", "manzanita", "maple", "oaken",
    "persimmon wood", "pecan", "pine", "poplar", "redwood", "rosewood",
    "spruce", "teak", "walnut", "zebrawood",
]


def pick_stick_kind(rng):
    """Rogue 5.4.4 things.c:pick_one(ws_info, MAXSTICKS)."""
    return rogue_things.pick_one([(spec.name, spec.prob) for spec in STICKS], rng.rnd(100))


def initial_charges(kind, rng):
    """Rogue 5.4.4 sticks.c:fix_stick() charge branch."""
    if kind == WS_LIGHT:
        return rng.rnd(10) + 10
    return rng.rnd(5) + 3


def make_stick(rng, cat="stick"):
    """Create stick fields using Rogue 5.4.4 things.c:new_thing()."""
    kind = pick_stick_kind(rng)
    return StickItem(cat=cat, kind=kind, charges=initial_charges(kind, rng))


def stick_damage(stick_type):
    """Rogue 5.4.4 sticks.c:fix_stick() melee and thrown damage."""
    if stick_type == "staff":
        return "2x3", "1x1"
    return "1x1", "1x1"


def saved_monster_miss_feedback(hero_started: bool):
    """Rogue 5.4.4 sticks.c:fire_bolt() saved monster miss runto/message branch."""
    return hero_started, True


def bolt_death_cause(hero_started: bool, source_monster_name: str | None) -> str:
    """Rogue 5.4.4 sticks.c:fire_bolt() death('b') vs source monster."""
    return "bolt" if hero_started else source_monster_name


def bolt_should_bounce(is_bounce_tile: bool, hero_at_pos: bool) -> bool:
    """Rogue 5.4.4 sticks.c:fire_bolt() DOOR under hero exception."""
    return is_bounce_tile and not hero_at_pos


def polymorph_identifies(in_sight: bool, can_see_monster: bool) -> bool:
    """Rogue 5.4.4 sticks.c:WS_POLYMORPH oi_know |= see_monst(tp)."""
    return in_sight and can_see_monster


def magic_missile_damage(roll_1d4: int, weapon_dam_plus: int, strength_dam_plus: int) -> int:
    """Rogue 5.4.4 sticks.c:WS_MISSILE / fight.c:roll_em()."""
    return max(0, roll_1d4 + 1 + weapon_dam_plus + strength_dam_plus)


def drain_life_split(current_hp: int, target_count: int) -> tuple[int, int]:
    """Rogue 5.4.4 sticks.c:drain() HP half and per-target damage."""
    if target_count <= 0:
        return current_hp, 0
    drained_hp = current_hp // 2
    return drained_hp, drained_hp // target_count


def teleport_to_position(hero_pos: tuple[int, int], delta: tuple[int, int]) -> tuple[int, int]:
    """Rogue 5.4.4 sticks.c:WS_TELTO new_pos = hero + delta."""
    return hero_pos[0] + delta[0], hero_pos[1] + delta[1]


def zap_releases_flytrap(kind: int) -> bool:
    """Rogue 5.4.4 sticks.c:do_zap() case group that clears player ISHELD for F."""
    return kind in {WS_INVIS, WS_POLYMORPH, WS_TELAWAY, WS_TELTO, WS_CANCEL}


def light_uses_room_branch(has_usable_room: bool) -> bool:
    """Rogue 5.4.4 sticks.c:WS_LIGHT checks ISGONE before room-lit branch."""
    return has_usable_room


def init_materials(rng):
    """Rogue 5.4.4 init.c:init_materials()."""
    wood_used = [False] * len(WOODS)
    metal_used = [False] * len(METALS)
    types = []
    made = []
    for _ in range(len(STICKS)):
        while True:
            if rng.rnd(2) == 0:
                j = rng.rnd(len(METALS))
                if not metal_used[j]:
                    metal_used[j] = True
                    types.append("wand")
                    made.append(METALS[j])
                    break
            else:
                j = rng.rnd(len(WOODS))
                if not wood_used[j]:
                    wood_used[j] = True
                    types.append("staff")
                    made.append(WOODS[j])
                    break
    return types, made


def charge_str(stick, terse=False):
    """Rogue 5.4.4 sticks.c:charge_str()."""
    if not getattr(stick, "known", True):
        return ""
    charges = getattr(stick, "charges", None)
    if charges is None:
        return ""
    return f" [{charges}]" if terse else f" [{charges} charges]"
