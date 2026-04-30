"""Rogue 5.4.4 pack.c helpers."""
from __future__ import annotations


def scare_scroll_pickup_result(is_found: bool) -> str:
    """Rogue 5.4.4 pack.c:add_pack() S_SCARE / ISFOUND branch."""
    return "dust" if is_found else "mark_found"


def pack_room_allows(inpack: int, maxpack: int) -> bool:
    """Rogue 5.4.4 pack.c:pack_room() increments before checking MAXPACK."""
    return inpack + 1 <= maxpack


def leave_pack_counts(count: int, is_mult: bool, all_items: bool):
    """Rogue 5.4.4 pack.c:leave_pack() count split result."""
    if count > 1 and not all_items:
        return count - 1, 1
    return 0, count


def add_pack_insert_index(pack, item) -> int:
    """Rogue 5.4.4 pack.c:add_pack() lp insertion point for a new pack item."""
    last_same_type = None
    for index, held in enumerate(pack):
        if held.cat == item.cat:
            last_same_type = index
            if held.kind == item.kind:
                if getattr(item, "group", 0):
                    for group_index in range(index, len(pack)):
                        grouped = pack[group_index]
                        if grouped.cat != item.cat or grouped.kind != item.kind:
                            return group_index
                        last_same_type = group_index
                        if getattr(grouped, "group", 0) == item.group:
                            return group_index + 1
                    return len(pack)
                return index + 1
        elif last_same_type is not None:
            return last_same_type + 1
    if last_same_type is not None:
        return last_same_type + 1
    return len(pack)
