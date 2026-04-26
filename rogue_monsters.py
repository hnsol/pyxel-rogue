"""Monster flag helpers aligned with Rogue 5.4.4 creature flags."""

FLAG_CAN_CONFUSE = "confuse"  # Rogue 5.4.4 CANHUH
FLAG_CANCELLED = "cancel"    # Rogue 5.4.4 ISCANC
FLAG_HASTE = "haste"         # Rogue 5.4.4 ISHASTE
FLAG_INVISIBLE = "invis"     # Rogue 5.4.4 ISINVIS
FLAG_SLOW = "slow"           # Rogue 5.4.4 ISSLOW

LEVEL_MONSTERS = "KEBSHIROZLCQANYFTWPXUMVGJD"
WANDER_MONSTERS = ("K", "E", "B", "S", "H", None, "R", "O", "Z", None, "C", "Q", "A",
                   None, "Y", None, "T", "W", "P", None, "U", "M", "V", "G", "J", None)


def randmonster(level: int, rnd, wander: bool = False) -> str:
    """Rogue 5.4.4 monsters.c:randmonster()."""
    table = WANDER_MONSTERS if wander else LEVEL_MONSTERS
    while True:
        depth = level + (rnd(10) - 6)
        if depth < 0:
            depth = rnd(5)
        if depth > 25:
            depth = rnd(5) + 21
        monster = table[depth]
        if monster:
            return monster


def initial_disguise(sym, random_thing):
    """Rogue 5.4.4 monsters.c:new_monster() sets Xeroc t_disguise = rnd_thing()."""
    return random_thing() if sym == "X" else sym


def is_disguised_xeroc(monster):
    """Rogue 5.4.4 fight.c:attack() checks t_type == 'X' and t_disguise != 'X'."""
    return monster.sym == "X" and getattr(monster, "disguise", monster.sym) != "X"


def reveal_disguise(monster):
    """Rogue 5.4.4 sticks.c:WS_CANCEL sets t_disguise = t_type."""
    monster.disguise = monster.sym


def is_cancelled(monster):
    return FLAG_CANCELLED in monster.flags


def has_special(monster, flag):
    return flag in monster.flags and not is_cancelled(monster)


def chase_steps_for_turn(monster):
    """Rogue 5.4.4 chase.c:move_monst() ISSLOW/ISHASTE step budget."""
    steps = 0
    if FLAG_SLOW not in monster.flags or monster.turn:
        steps += 1
    if FLAG_HASTE in monster.flags:
        steps += 1
    return steps


def finish_chase_turn(monster):
    monster.turn = not monster.turn


def haste_monster(monster):
    """Rogue 5.4.4 sticks.c:do_zap() WS_HASTE_M flag toggle."""
    if FLAG_SLOW in monster.flags:
        monster.flags.discard(FLAG_SLOW)
    else:
        monster.flags.add(FLAG_HASTE)


def slow_monster(monster):
    """Rogue 5.4.4 sticks.c:do_zap() WS_SLOW_M flag toggle."""
    if FLAG_HASTE in monster.flags:
        monster.flags.discard(FLAG_HASTE)
    else:
        monster.flags.add(FLAG_SLOW)
    monster.turn = True


def should_give_pack(level: int, max_level: int, carry_prob: int, rnd) -> bool:
    """Rogue 5.4.4 monsters.c:give_pack()."""
    return level >= max_level and rnd(100) < carry_prob
