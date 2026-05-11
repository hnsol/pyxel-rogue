"""Rogue 5.4.4 misc.c helpers."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AddHasteResult:
    ok: bool
    duration: int = 0
    no_command_add: int = 0


def add_haste_result(already_hasted: bool, potion: bool, rnd) -> AddHasteResult:
    """Rogue 5.4.4 misc.c:add_haste()."""
    if already_hasted:
        return AddHasteResult(False, no_command_add=rnd(8))
    if potion:
        return AddHasteResult(True, duration=rnd(4) + 4)
    return AddHasteResult(True)
