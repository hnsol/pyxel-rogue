"""Rogue 5.4.4 daemon.c-style delayed action helpers."""
from __future__ import annotations

BEFORE = "before"
AFTER = "after"
MAXDAEMONS = 20


def doctor_tick(player, rng, regeneration_count: int = 0) -> None:
    """Rogue 5.4.4 daemons.c:doctor()."""
    level = player.level
    old_hp = player.hp
    player.quiet += 1
    if level < 8:
        if player.quiet + (level << 1) > 20:
            player.hp += 1
    elif player.quiet >= 3:
        player.hp += rng.rnd(level - 7) + 1
    player.hp += regeneration_count
    if player.hp != old_hp:
        player.hp = min(player.hp, player.max_hp)
        player.quiet = 0


def stomach_tick(player, rng, food_cost: int, moretime: int, starvetime: int):
    """Rogue 5.4.4 daemons.c:stomach()."""
    previous_state = player.state
    if player.food <= 0:
        old_food = player.food
        player.food -= 1
        if old_food < -starvetime:
            player.hp = 0
            player.state = "faint"
            return "pyxel.starve_to_death"
        if player.no_command or rng.randrange(5) != 0:
            return None
        player.state = "faint"
        player.no_command += rng.rnd(8) + 4
        return "pyxel.faint_from_lack_of_food"

    old_food = player.food
    player.food -= food_cost
    if player.food <= 0:
        return None
    if player.food < moretime and old_food >= moretime:
        player.state = "weak"
        return "pyxel.are_weak" if previous_state != "weak" else None
    if player.food < 2 * moretime and old_food >= 2 * moretime:
        player.state = "hungry"
        return "pyxel.feel_hungry" if previous_state != "hungry" else None
    player.state = "normal"
    return None


def swander(actions) -> None:
    """Rogue 5.4.4 daemons.c:swander()."""
    actions.daemons.start("rollwand", BEFORE)


def rollwand(actions, rng, between: int, wander_time: int, wanderer) -> int:
    """Rogue 5.4.4 daemons.c:rollwand()."""
    between += 1
    if between < 4:
        return between
    between = 0
    if rng.roll(1, 6) == 4:
        wanderer()
        actions.daemons.kill("rollwand")
        actions.fuses.fuse("swander", wander_time, BEFORE)
    return between


class FuseList:
    """Small fuse table matching daemon.c:fuse()/lengthen()/extinguish()/do_fuses()."""

    def __init__(self, slots: list[dict] | None = None) -> None:
        self._fuses = [] if slots is None else slots

    def fuse(self, name: str, time: int, when: str = AFTER) -> None:
        """Schedule name to fire after time turns in the given phase."""
        if len(self._fuses) >= MAXDAEMONS:
            return
        self._fuses.append({"kind": "fuse", "name": name, "time": max(0, int(time)), "when": when})

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
            if fuse.get("kind") != "fuse" or fuse["when"] != when or fuse["time"] <= 0:
                continue
            fuse["time"] -= 1
            if fuse["time"] == 0:
                due.append(fuse["name"])
                if fuse in self._fuses:
                    self._fuses.remove(fuse)
        return due

    def _find(self, name: str) -> dict | None:
        for fuse in self._fuses:
            if fuse.get("kind") == "fuse" and fuse["name"] == name:
                return fuse
        return None


class DaemonList:
    """Small daemon table matching daemon.c:start_daemon()/kill_daemon()/do_daemons()."""

    def __init__(self, slots: list[dict] | None = None) -> None:
        self._daemons = [] if slots is None else slots

    def start(self, name: str, when: str = AFTER) -> None:
        """Start name as a daemon in the given phase."""
        if len(self._daemons) >= MAXDAEMONS:
            return
        self._daemons.append({"kind": "daemon", "name": name, "when": when})

    def kill(self, name: str) -> None:
        """Remove a daemon from the table (daemon.c:kill_daemon)."""
        for idx, daemon in enumerate(self._daemons):
            if daemon.get("kind") == "daemon" and daemon["name"] == name:
                del self._daemons[idx]
                return

    def running(self, name: str, when: str | None = None) -> bool:
        """Return whether name is active, optionally limited to a phase."""
        return any(
            daemon.get("kind") == "daemon"
            and daemon["name"] == name
            and (when is None or daemon["when"] == when)
            for daemon in self._daemons
        )

    def tick(self, when: str = AFTER) -> list[str]:
        """Return active daemon names for the given phase (daemon.c:do_daemons)."""
        return [
            daemon["name"]
            for daemon in list(self._daemons)
            if daemon.get("kind") == "daemon" and daemon["when"] == when
        ]


class DelayedActionTable:
    """Shared daemon.c d_list backing both daemons and fuses."""

    def __init__(self) -> None:
        self._slots: list[dict] = []
        self.fuses = FuseList(self._slots)
        self.daemons = DaemonList(self._slots)
