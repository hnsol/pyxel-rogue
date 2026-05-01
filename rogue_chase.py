"""Rogue 5.4.4 chase.c helpers."""
from __future__ import annotations

import rogue_monsters


def runners(monsters, monster_turn) -> None:
    """Rogue 5.4.4 chase.c:runners() ISHELD/ISRUN gate."""
    for monster in list(monsters):
        if getattr(monster, "held", 0) > 0 or not getattr(monster, "running", False):
            continue
        orig_pos = (monster.x, monster.y)
        was_target = getattr(monster, "target", False)
        monster_turn(monster)
        if was_target and (monster.x, monster.y) != orig_pos:
            monster.target = False


def monster_turn(monster, move_monst, distance_to_hero) -> None:
    """Rogue 5.4.4 chase.c:runners() per-monster move plus ISFLY extra move."""
    if not getattr(monster, "alive", False) or not getattr(monster, "running", False):
        return
    if move_monst(monster) == -1:
        return
    if getattr(monster, "alive", False) and rogue_monsters.is_flying(monster) and distance_to_hero(monster) >= 3:
        move_monst(monster)


def move_monst(monster, do_chase, chase_steps_for_turn, finish_chase_turn) -> None:
    """Rogue 5.4.4 chase.c:move_monst() step loop."""
    for _ in range(chase_steps_for_turn(monster)):
        if do_chase(monster) == -1:
            return -1
    finish_chase_turn(monster)
    return 0


def runto(monster, dest) -> None:
    """Rogue 5.4.4 chase.c:runto()."""
    monster.running = True
    monster.held = 0
    monster.dest = dest


def diag_ok(sx, sy, ex, ey, in_bounds, step_ok) -> bool:
    """Rogue 5.4.4 chase.c:diag_ok()."""
    if not in_bounds(ex, ey):
        return False
    if sx == ex or sy == ey:
        return True
    return step_ok(sx, ey) and step_ok(ex, sy)


def dist(y1, x1, y2, x2) -> int:
    """Rogue 5.4.4 chase.c:dist()."""
    return ((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))


def dist_points(c1, c2) -> int:
    """Rogue 5.4.4 chase.c:dist_cp()."""
    return dist(c1[1], c1[0], c2[1], c2[0])


def roomin(x, y, rooms):
    """Rogue 5.4.4 chase.c:roomin() room-rectangle lookup."""
    for room in rooms:
        if room.x <= x < room.x + room.w and room.y <= y < room.y + room.h:
            return room
    return None


def see_monst(
    player_blind: bool,
    monster_invisible: bool,
    can_see_invisible: bool,
    lamp_visible: bool = True,
    same_lit_room_visible: bool = True,
) -> bool:
    """Rogue 5.4.4 chase.c:see_monst() sight gate."""
    if player_blind:
        return False
    if monster_invisible and not can_see_invisible:
        return False
    if lamp_visible:
        return True
    return same_lit_room_visible


def within_lamp_distance(distance2: int, lampdist: int) -> bool:
    """Rogue 5.4.4 chase.c:see_monst()/cansee() dist(...) < LAMPDIST."""
    return distance2 < lampdist


def lamp_diagonal_clear(hero_pos, target_pos, step_ok) -> bool:
    """Rogue 5.4.4 chase.c:see_monst()/cansee() diagonal lamp sight gate."""
    hx, hy = hero_pos
    tx, ty = target_pos
    if tx == hx or ty == hy:
        return True
    return step_ok((tx, hy)) or step_ok((hx, ty))


def same_lit_room_visible(target_room, player_room, target_room_dark: bool) -> bool:
    """Rogue 5.4.4 chase.c:cansee() same-room lit visibility gate."""
    return target_room == player_room and not target_room_dark


def cansee(not_blind: bool, lamp_visible: bool, room_visible: bool) -> bool:
    """Rogue 5.4.4 chase.c:cansee() final visibility order."""
    if not not_blind:
        return False
    if lamp_visible:
        return True
    return room_visible


def find_dest(
    carry_prob: int,
    monster_room,
    player_room,
    can_see_monster: bool,
    items,
    claimed_dests,
    room_of_item,
    dest_of_item,
    is_scare_scroll,
    rnd,
):
    """Rogue 5.4.4 chase.c:find_dest(); None means hero."""
    if carry_prob <= 0 or monster_room == player_room or can_see_monster:
        return None
    for item in items:
        if is_scare_scroll(item):
            continue
        if room_of_item(item) == monster_room and rnd(100) < carry_prob and dest_of_item(item) not in claimed_dests:
            return item
    return None


def should_random_move(confused: int, monster_sym: str, rnd) -> bool:
    """Rogue 5.4.4 chase.c:chase() random movement gate."""
    if confused > 0 and rnd(5) != 0:
        return True
    if monster_sym == "P" and rnd(5) == 0:
        return True
    if monster_sym == "B" and rnd(2) == 0:
        return True
    return False


def confusion_clears_after_random_move(confused: int, rnd) -> bool:
    """Rogue 5.4.4 chase.c:chase() ISHUH clear chance after rndmove()."""
    return rnd(20) == 0 and confused > 0


def choose_chase_step(best, best_distance: int, tie_count: int, candidate, candidate_distance: int, rnd):
    """Rogue 5.4.4 chase.c:chase() closest-step tie selection."""
    if candidate_distance < best_distance:
        return candidate, candidate_distance, 1
    if candidate_distance == best_distance:
        tie_count += 1
        if rnd(tie_count) == 0:
            return candidate, candidate_distance, tie_count
    return best, best_distance, tie_count


def is_chase_candidate(diagonal_ok: bool, step_ok: bool, scare_scroll: bool, xeroc: bool) -> bool:
    """Rogue 5.4.4 chase.c:chase() candidate tile gate."""
    return diagonal_ok and step_ok and not scare_scroll and not xeroc


def chase_candidate_offsets():
    """Rogue 5.4.4 chase.c:chase() scans x outer, y inner around the monster."""
    return [
        (dx, dy)
        for dx in (-1, 0, 1)
        for dy in (-1, 0, 1)
        if dx != 0 or dy != 0
    ]


def chase_continues(current_distance: int, chosen_pos, hero_pos) -> bool:
    """Rogue 5.4.4 chase.c:chase() return value."""
    return current_distance != 0 and chosen_pos != hero_pos


def dragon_breath_direction(monster_sym, monster_pos, hero_pos, distance2, bolt_length, cancelled, rnd, dragonshot=5):
    """Rogue 5.4.4 chase.c:do_chase() Dragon flame gate."""
    mx, my = monster_pos
    hx, hy = hero_pos
    dx = hx - mx
    dy = hy - my
    if monster_sym != "D":
        return None
    if not (dx == 0 or dy == 0 or abs(dx) == abs(dy)):
        return None
    if distance2 > bolt_length * bolt_length:
        return None
    if cancelled:
        return None
    if rnd(dragonshot) != 0:
        return None
    return (dx > 0) - (dx < 0), (dy > 0) - (dy < 0)


def nearest_exit_to_dest(exits, dest, distance):
    """Rogue 5.4.4 chase.c:do_chase() nearest room exit selection."""
    if not exits:
        return None
    return min(exits, key=lambda exit_pos: distance(exit_pos, dest))


def should_stop_after_dest(monster_sym: str) -> bool:
    """Rogue 5.4.4 chase.c:do_chase() stoprun gate after reaching t_dest."""
    return monster_sym != "F"


def greedy_destination(is_greedy: bool, current_dest, gold_target, player_dest):
    """Rogue 5.4.4 chase.c:do_chase() ISGREED destination fallback."""
    if not is_greedy:
        return current_dest
    return gold_target if gold_target is not None else player_dest


def destination_room(dest_is_hero: bool, player_room, dest_room):
    """Rogue 5.4.4 chase.c:do_chase() chasee room selection."""
    return player_room if dest_is_hero else dest_room
