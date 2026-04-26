"""Monster flag helpers aligned with Rogue 5.4.4 creature flags."""

FLAG_CAN_CONFUSE = "confuse"  # Rogue 5.4.4 CANHUH
FLAG_CANCELLED = "cancel"    # Rogue 5.4.4 ISCANC
FLAG_FLYING = "fly"          # Rogue 5.4.4 ISFLY
FLAG_HASTE = "haste"         # Rogue 5.4.4 ISHASTE
FLAG_INVISIBLE = "invis"     # Rogue 5.4.4 ISINVIS
FLAG_SLOW = "slow"           # Rogue 5.4.4 ISSLOW
FLAG_GREED = "greed"         # Rogue 5.4.4 ISGREED
FLAG_MEAN = "mean"           # Rogue 5.4.4 ISMEAN

LEVEL_MONSTERS = "KEBSHIROZLCQANYFTWPXUMVGJD"
WANDER_MONSTERS = ("K", "E", "B", "S", "H", None, "R", "O", "Z", None, "C", "Q", "A",
                   None, "Y", None, "T", "W", "P", None, "U", "M", "V", "G", "J", None)


def parse_flags(flags: str):
    return set(flags.split(",")) if flags else set()


def is_mean(flags) -> bool:
    return FLAG_MEAN in flags


def force_mean(monster) -> None:
    monster.flags.add(FLAG_MEAN)
    monster.mean = True


def is_greedy(monster) -> bool:
    return FLAG_GREED in monster.flags


def is_flying(monster) -> bool:
    return FLAG_FLYING in monster.flags


def is_invisible(monster) -> bool:
    return FLAG_INVISIBLE in monster.flags


def apply_deep_haste(monster, depth: int) -> None:
    """Rogue 5.4.4 monsters.c:new_monster() sets ISHASTE when level > 29."""
    if depth > 29:
        monster.flags.add(FLAG_HASTE)


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


def exp_add(level: int, max_hp: int) -> int:
    """Rogue 5.4.4 monsters.c:exp_add()."""
    mod = max_hp // (8 if level == 1 else 6)
    if level > 9:
        mod *= 20
    elif level > 6:
        mod *= 4
    return mod


def new_monster_stats(base_level: int, base_armor: int, base_exp: int, depth: int, amulet_level: int, roll):
    """Rogue 5.4.4 monsters.c:new_monster() stat rebuild."""
    lev_add = max(0, depth - amulet_level)
    level = base_level + lev_add
    hp = max(1, roll(level, 8))
    armor = base_armor - lev_add
    exp = base_exp + lev_add * 10 + exp_add(level, hp)
    return level, hp, armor, exp


def save_throw(which: int, level: int, roll) -> bool:
    """Rogue 5.4.4 monsters.c:save_throw()."""
    return roll(1, 20) >= 14 + which - level // 2


def initial_disguise(sym, random_thing):
    """Rogue 5.4.4 monsters.c:new_monster() sets Xeroc t_disguise = rnd_thing()."""
    return random_thing() if sym == "X" else sym


def is_disguised_xeroc(monster):
    """Rogue 5.4.4 fight.c:attack() checks t_type == 'X' and t_disguise != 'X'."""
    return monster.sym == "X" and getattr(monster, "disguise", monster.sym) != "X"


def reveal_disguise(monster):
    """Rogue 5.4.4 sticks.c:WS_CANCEL sets t_disguise = t_type."""
    monster.disguise = monster.sym


def cancel_monster(monster) -> None:
    """Rogue 5.4.4 sticks.c:WS_CANCEL creature flag changes."""
    monster.flags.add(FLAG_CANCELLED)
    monster.flags.discard(FLAG_INVISIBLE)
    monster.flags.discard(FLAG_CAN_CONFUSE)
    reveal_disguise(monster)


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
