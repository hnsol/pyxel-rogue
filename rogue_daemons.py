"""Rogue 5.4.4 daemon.c-style delayed action helpers."""
from __future__ import annotations

BEFORE = "before"
AFTER = "after"
MAXDAEMONS = 20


class FuseList:
    """Small fuse table matching daemon.c:fuse()/lengthen()/extinguish()/do_fuses()."""

    def __init__(self) -> None:
        self._fuses: dict[str, dict] = {}

    def fuse(self, name: str, time: int, when: str = AFTER) -> None:
        """Schedule name to fire after time turns in the given phase."""
        if len(self._fuses) >= MAXDAEMONS and name not in self._fuses:
            return
        self._fuses[name] = {"time": max(0, int(time)), "when": when}

    def lengthen(self, name: str, extra: int) -> None:
        """Extend an existing fuse by extra turns (daemon.c:lengthen)."""
        if name in self._fuses:
            self._fuses[name]["time"] += int(extra)

    def extinguish(self, name: str) -> None:
        """Cancel a pending fuse (daemon.c:extinguish)."""
        self._fuses.pop(name, None)

    def remaining(self, name: str) -> int:
        """Return turns remaining for the named fuse, or 0 if not set."""
        fuse = self._fuses.get(name)
        return 0 if fuse is None else fuse["time"]

    def tick(self, when: str = AFTER) -> list[str]:
        """Decrement and return names of expired fuses (daemon.c:do_fuses)."""
        due = []
        for name, fuse in list(self._fuses.items()):
            if fuse["when"] != when or fuse["time"] <= 0:
                continue
            fuse["time"] -= 1
            if fuse["time"] == 0:
                due.append(name)
                self.extinguish(name)
        return due
