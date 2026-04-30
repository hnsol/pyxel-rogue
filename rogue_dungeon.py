TREAS_ROOM = 20
MINTREAS = 2
MAXTREAS = 10
MAXTRIES = 10
MAXOBJ = 9
PUT_THINGS_PROB = 36
MAXTRAPS = 10
NTRAPS = 8


def treasure_room_spots(inner_area):
    """Rogue 5.4.4 new_level.c:treas_room() spots cap."""
    return max(1, min(max(0, inner_area - MINTREAS), MAXTREAS - MINTREAS))


def treasure_room_counts(inner_area, rng):
    """Return (treasures, monsters) for Rogue 5.4.4 treas_room()."""
    spots = treasure_room_spots(inner_area)
    treasures = rng.rnd(spots) + MINTREAS
    monsters = rng.rnd(spots) + MINTREAS
    if monsters < treasures + 2:
        monsters = treasures + 2
    return treasures, min(monsters, inner_area)


def should_place_treasure_room(rng):
    """Rogue 5.4.4 new_level.c:put_things() rnd(TREAS_ROOM)==0."""
    return rng.rnd(TREAS_ROOM) == 0


def put_things_item_count(rng):
    """Rogue 5.4.4 new_level.c:put_things() MAXOBJ attempts at 36% each."""
    return sum(1 for _ in range(MAXOBJ) if rng.rnd(100) < PUT_THINGS_PROB)


def should_put_things(has_amulet: bool, level: int, max_level: int) -> bool:
    """Rogue 5.4.4 new_level.c:put_things() amulet ascent gate."""
    return not (has_amulet and level < max_level)


def should_place_room_gold(rng, has_amulet: bool, level: int, max_level: int) -> bool:
    """Rogue 5.4.4 rooms.c:do_rooms() room gold gate."""
    return rng.rnd(2) == 0 and (not has_amulet or level >= max_level)


def should_place_room_monster(rng, has_gold: bool) -> bool:
    """Rogue 5.4.4 rooms.c:do_rooms() room monster gate."""
    return rng.rnd(100) < (80 if has_gold else 25)


def find_floor_monster_candidates(
    tm,
    room_at,
    occupied,
    player_pos,
    walkable,
    avoid=(),
    excluded_room=None,
):
    """Rogue 5.4.4 rooms.c:find_floor(..., monst=TRUE) candidate gate."""
    avoid = set(avoid or ())
    occupied = set(occupied or ())
    candidates = []
    for y, row in enumerate(tm):
        for x, tile in enumerate(row):
            room = room_at(x, y)
            if room is None or room is excluded_room:
                continue
            pos = (x, y)
            if tile in walkable and pos not in avoid and pos != player_pos and pos not in occupied:
                candidates.append(pos)
    return candidates


def trap_count_for_level(level: int, rng) -> int:
    """Rogue 5.4.4 new_level.c:new_level() trap count."""
    if rng.rnd(10) >= level:
        return 0
    return min(MAXTRAPS, rng.rnd(level // 4) + 1)


def trap_kind(rng) -> int:
    """Rogue 5.4.4 new_level.c:new_level() trap kind roll."""
    return rng.rnd(NTRAPS)
