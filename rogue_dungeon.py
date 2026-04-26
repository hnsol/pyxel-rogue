TREAS_ROOM = 20
MINTREAS = 2
MAXTREAS = 10
MAXTRIES = 10
MAXOBJ = 9
PUT_THINGS_PROB = 36


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
