"""Rogue 5.4.4 move.c helpers."""
from __future__ import annotations


def can_rust_armor(is_armor: bool, is_leather: bool, armor_class: int) -> bool:
    """Rogue 5.4.4 move.c:rust_armor() legality gate."""
    return is_armor and not is_leather and armor_class < 9


def rust_armor_result(protected: bool, sustain_armor: bool) -> str:
    """Rogue 5.4.4 move.c:rust_armor() protected/ring branch."""
    if protected or sustain_armor:
        return "vanish"
    return "weaken"


MYSTERIOUS_TRAP_MESSAGES = [
    ("move.you_are_suddenly_in_a_parallel_dimension", None),
    ("move.the_light_in_here_suddenly_seems_color", "color"),
    ("move.you_feel_a_sting_in_the_side_of_your_neck", None),
    ("move.multi_colored_lines_swirl_around_you_then_fade", None),
    ("move.a_color_light_flashes_in_your_eyes", "color"),
    ("move.a_spike_shoots_past_your_ear", None),
    ("move.value_sparks_dance_across_your_armor", "value"),
    ("move.you_suddenly_feel_very_thirsty", None),
    ("move.you_feel_time_speed_up_suddenly", None),
    ("move.time_now_seems_to_be_going_slower", None),
    ("move.you_pack_turns_value", "value"),
]


def mysterious_trap_message(index: int):
    """Rogue 5.4.4 move.c:be_trapped() T_MYST message switch."""
    return MYSTERIOUS_TRAP_MESSAGES[index]


def bear_trap_no_move(no_move: int, beartime: int) -> int:
    """Rogue 5.4.4 move.c:be_trapped() T_BEAR branch."""
    return no_move + beartime


def sleep_trap_no_command(no_command: int, sleeptime: int) -> int:
    """Rogue 5.4.4 move.c:be_trapped() T_SLEEP branch."""
    return no_command + sleeptime


def dart_poison_strength(strength: int, poison_saved: bool, sustain_strength: bool) -> int:
    """Rogue 5.4.4 move.c:be_trapped() T_DART poison branch."""
    if poison_saved or sustain_strength or strength <= 3:
        return strength
    return strength - 1


def confused_player_uses_random_move(confused: bool, rnd) -> bool:
    """Rogue 5.4.4 move.c:do_move() ISHUH random movement gate."""
    return confused and rnd(5) != 0


def held_move_blocked(held: bool, target_is_flytrap: bool) -> bool:
    """Rogue 5.4.4 move.c:do_move() ISHELD gate blocks ch != 'F'."""
    return held and not target_is_flytrap


def rndmove(origin, rnd, is_legal):
    """Rogue 5.4.4 move.c:rndmove() one-attempt confused move."""
    x, y = origin
    dy = rnd(3) - 1
    dx = rnd(3) - 1
    dst = (x + dx, y + dy)
    if dst == origin:
        return dst
    if not is_legal(origin, dst):
        return origin
    return dst
