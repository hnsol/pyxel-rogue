"""Rogue 5.4.4 scrolls.c helpers."""
from __future__ import annotations


def enchant_weapon(weapon, rnd) -> bool:
    """Apply Rogue 5.4.4 scrolls.c:S_ENCH to the current weapon."""
    if weapon is None:
        return False
    weapon.cursed = False
    if rnd(2) == 0:
        weapon.hit_plus += 1
    else:
        weapon.dam_plus += 1
    weapon.ench = weapon.hit_plus
    return True


def enchant_armor(armor) -> bool:
    """Apply Rogue 5.4.4 scrolls.c:S_ARMOR to the current armor."""
    if armor is None:
        return False
    armor.ench += 1
    armor.cursed = False
    return True


def protect_armor(armor) -> bool:
    """Apply Rogue 5.4.4 scrolls.c:S_PROTECT to the current armor."""
    if armor is None:
        return False
    armor.protected = True
    return True


def remove_curse_equipment(items) -> None:
    """Apply Rogue 5.4.4 scrolls.c:S_REMOVE uncurse() calls."""
    for item in items:
        if item is not None:
            item.cursed = False


def monster_confusion(player) -> None:
    """Apply Rogue 5.4.4 scrolls.c:S_CONFUSE to the player."""
    player.can_confuse_monster = True


def sleep_scroll(player, rnd, sleep_time: int) -> int:
    """Apply Rogue 5.4.4 scrolls.c:S_SLEEP no_command change."""
    player.no_command += rnd(sleep_time) + 4
    return player.no_command


def hold_monsters(player, monsters, held_roll) -> int:
    """Apply Rogue 5.4.4 scrolls.c:S_HOLD to running monsters near the player."""
    count = 0
    for monster in monsters:
        if abs(monster.x - player.x) <= 2 and abs(monster.y - player.y) <= 2 and monster.running:
            monster.running = False
            monster.held = held_roll(monster)
            count += 1
    return count


def choose_create_monster_pos(player, candidates, rnd):
    """Choose a Rogue 5.4.4 scrolls.c:S_CREATE target using rnd(++i)."""
    pick = None
    count = 0
    for pos in candidates:
        if pos == (player.x, player.y):
            continue
        count += 1
        if rnd(count) == 0:
            pick = pos
    return pick


def food_detection_positions(items, food_cat):
    """Return Rogue 5.4.4 scrolls.c:S_FDET food object positions."""
    return [(item.x, item.y) for item in items if item.cat == food_cat]


def magic_mapping_targets(hidden_tiles, traps, trap_tile):
    """Return Rogue 5.4.4 scrolls.c:S_MAP cells to reveal."""
    targets = list(hidden_tiles.items())
    targets.extend((pos, trap_tile) for pos in traps)
    return targets


def aggravate_monsters(monsters, runto) -> None:
    """Apply Rogue 5.4.4 scrolls.c:S_AGGR / misc.c:aggravate()."""
    for monster in monsters:
        runto(monster)


def teleport_identifies(old_room, new_room) -> bool:
    """Return Rogue 5.4.4 scrolls.c:S_TELEP identification result."""
    return old_room is not new_room


def identify_target_cats(name: str, cats) -> tuple:
    """Return Rogue 5.4.4 scrolls.c:S_ID_* id_type[] category targets."""
    if name == "identify potion":
        return (cats.CAT_POT,)
    if name == "identify scroll":
        return (cats.CAT_SCR,)
    if name == "identify weapon":
        return (cats.CAT_WPN,)
    if name == "identify armor":
        return (cats.CAT_ARM,)
    if name == "identify ring, wand or staff":
        return (cats.CAT_RING, cats.CAT_STICK)
    return ()
