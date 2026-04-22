TREAS_ROOM = 20
MINTREAS = 2
MAXTREAS = 10
MAXTRIES = 10


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
