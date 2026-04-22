"""Rogue 5.4.4 daemon.c-style delayed action helpers."""

BEFORE = "before"
AFTER = "after"
MAXDAEMONS = 20


class FuseList:
    """Small fuse table matching daemon.c:fuse()/lengthen()/extinguish()/do_fuses()."""

    def __init__(self):
        self._fuses = {}

    def fuse(self, name, time, when=AFTER):
        if len(self._fuses) >= MAXDAEMONS and name not in self._fuses:
            return
        self._fuses[name] = {"time": max(0, int(time)), "when": when}

    def lengthen(self, name, extra):
        if name in self._fuses:
            self._fuses[name]["time"] += int(extra)

    def extinguish(self, name):
        self._fuses.pop(name, None)

    def remaining(self, name):
        fuse = self._fuses.get(name)
        return 0 if fuse is None else fuse["time"]

    def tick(self, when=AFTER):
        due = []
        for name, fuse in list(self._fuses.items()):
            if fuse["when"] != when or fuse["time"] <= 0:
                continue
            fuse["time"] -= 1
            if fuse["time"] == 0:
                due.append(name)
                self.extinguish(name)
        return due
