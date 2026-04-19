"""Monster flag helpers aligned with Rogue 5.4.4 creature flags."""

FLAG_CAN_CONFUSE = "confuse"  # Rogue 5.4.4 CANHUH
FLAG_CANCELLED = "cancel"    # Rogue 5.4.4 ISCANC
FLAG_HASTE = "haste"         # Rogue 5.4.4 ISHASTE
FLAG_INVISIBLE = "invis"     # Rogue 5.4.4 ISINVIS
FLAG_SLOW = "slow"           # Rogue 5.4.4 ISSLOW


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
