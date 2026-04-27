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
