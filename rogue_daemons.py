"""Rogue 5.4.4 daemon.c-style delayed action helpers."""
from __future__ import annotations

BEFORE = "before"
AFTER = "after"
MAXDAEMONS = 20


class FuseList:
    """Small fuse table matching daemon.c:fuse()/lengthen()/extinguish()/do_fuses()."""

    def __init__(self) -> None:
        self._fuses: list[dict] = []

    def fuse(self, name: str, time: int, when: str = AFTER) -> None:
        """Schedule name to fire after time turns in the given phase."""
        if len(self._fuses) >= MAXDAEMONS:
            return
        self._fuses.append({"name": name, "time": max(0, int(time)), "when": when})

    def lengthen(self, name: str, extra: int) -> None:
        """Extend an existing fuse by extra turns (daemon.c:lengthen)."""
        fuse = self._find(name)
        if fuse is not None:
            fuse["time"] += int(extra)

    def extinguish(self, name: str) -> None:
        """Cancel a pending fuse (daemon.c:extinguish)."""
        for idx, fuse in enumerate(self._fuses):
            if fuse["name"] == name:
                del self._fuses[idx]
                return

    def remaining(self, name: str) -> int:
        """Return turns remaining for the named fuse, or 0 if not set."""
        fuse = self._find(name)
        return 0 if fuse is None else fuse["time"]

    def tick(self, when: str = AFTER) -> list[str]:
        """Decrement and return names of expired fuses (daemon.c:do_fuses)."""
        due = []
        for fuse in list(self._fuses):
            if fuse["when"] != when or fuse["time"] <= 0:
                continue
            fuse["time"] -= 1
            if fuse["time"] == 0:
                due.append(fuse["name"])
                if fuse in self._fuses:
                    self._fuses.remove(fuse)
        return due

    def _find(self, name: str) -> dict | None:
        for fuse in self._fuses:
            if fuse["name"] == name:
                return fuse
        return None


class DaemonList:
    """Small daemon table matching daemon.c:start_daemon()/kill_daemon()/do_daemons()."""

    def __init__(self) -> None:
        self._daemons: list[dict] = []

    def start(self, name: str, when: str = AFTER) -> None:
        """Start name as a daemon in the given phase."""
        if len(self._daemons) >= MAXDAEMONS:
            return
        self._daemons.append({"name": name, "when": when})

    def kill(self, name: str) -> None:
        """Remove a daemon from the table (daemon.c:kill_daemon)."""
        for idx, daemon in enumerate(self._daemons):
            if daemon["name"] == name:
                del self._daemons[idx]
                return

    def running(self, name: str, when: str | None = None) -> bool:
        """Return whether name is active, optionally limited to a phase."""
        return any(
            daemon["name"] == name and (when is None or daemon["when"] == when)
            for daemon in self._daemons
        )

    def tick(self, when: str = AFTER) -> list[str]:
        """Return active daemon names for the given phase (daemon.c:do_daemons)."""
        return [daemon["name"] for daemon in list(self._daemons) if daemon["when"] == when]
