"""Pure input interpretation helpers for Rogue controls."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

Direction = tuple[int, int]
Command = object
ItemRef = object

UP = frozenset({"up", "k"})
DOWN = frozenset({"down", "j"})
LEFT = frozenset({"left", "h"})
RIGHT = frozenset({"right", "l"})
VI_DIAGONALS: tuple[tuple[str, Direction], ...] = (
    ("y", (-1, -1)),
    ("u", (1, -1)),
    ("b", (-1, 1)),
    ("n", (1, 1)),
)
DIGITS = tuple(str(i) for i in range(10))


@dataclass
class RepeatState:
    command: Command | None = None
    direction: Direction | None = None
    item: ItemRef | None = None
    previous_command: Command | None = None
    previous_dir: Direction | None = None
    previous_item: ItemRef | None = None
    active: bool = False

    def record(self, command: Command) -> bool:
        if self.active:
            return False
        self.previous_command = self.command
        self.previous_dir = self.direction
        self.previous_item = self.item
        self.command = command
        self.direction = None
        self.item = None
        return True

    def reset(self) -> None:
        self.command = self.previous_command
        self.direction = self.previous_dir
        self.item = self.previous_item

    def remember_dir(self, direction: Direction) -> None:
        if not self.active:
            self.direction = direction

    def remember_item(self, item: ItemRef) -> None:
        if not self.active:
            self.item = item

    def clear_item_if_gone(self, item: ItemRef, inventory: Iterable[ItemRef]) -> None:
        if self.item is item and item not in inventory:
            self.item = None


@dataclass
class CountInputState:
    prefix_active: bool = False
    prefix_value: int = 0
    repeat_command: Command | None = None
    repeat_remaining: int = 0
    repeat_dir: Direction | None = None

    def start_prefix(self, digit: int) -> None:
        if not self.prefix_active:
            self.prefix_value = 0
        self.prefix_active = True
        self.prefix_value = min(255, self.prefix_value * 10 + digit)

    def take_prefix(self) -> int | None:
        if not self.prefix_active:
            return None
        value = self.prefix_value
        self.prefix_active = False
        self.prefix_value = 0
        return value

    def start_repeat(self, command: Command, count: int, direction: Direction | None = None) -> None:
        self.repeat_command = command
        self.repeat_remaining = max(0, count - 1)
        self.repeat_dir = direction

    def record_counted(
        self,
        command: Command,
        countable: bool,
        direction: Direction | None = None,
    ) -> bool:
        count = self.take_prefix()
        if count is not None and countable and count > 1:
            self.start_repeat(command, count, direction)
            return False
        return True


@dataclass
class TapButtonState:
    previous: bool = False
    frames: int = 0
    used: bool = False
    tap: bool = False

    def update(self, now: bool, tap_frames: int) -> bool:
        self.tap = False
        if now:
            self.frames = self.frames + 1 if self.previous else 1
        else:
            if self.previous and not self.used and self.frames <= tap_frames:
                self.tap = True
            self.frames = 0
            self.used = False
        self.previous = now
        return self.tap

    def mark_used(self) -> None:
        self.used = True


@dataclass
class DashState:
    active: bool = False
    direction: Direction = (0, 0)
    timer: int = 0
    steps: int = 0
    restart_guard: bool = False

    def update_release(self, run_held: bool) -> None:
        if not run_held:
            self.restart_guard = False

    def can_start(self, run_held: bool, restart_dir_pressed: bool) -> bool:
        return run_held and (not self.restart_guard or restart_dir_pressed)

    def start(self, direction: Direction) -> None:
        self.active = True
        self.direction = direction
        self.timer = 0
        self.steps = 0
        self.restart_guard = False

    def stop(self, restart_guard: bool = True) -> None:
        self.active = False
        self.restart_guard = restart_guard

    def tick(self, interval: int) -> bool:
        self.timer += 1
        if self.timer >= interval:
            self.timer = 0
            return True
        return False

    def finish_step(self, continues: bool) -> None:
        self.steps += 1
        self.active = continues
        if not continues:
            self.restart_guard = True


def _as_set(keys: Iterable[str]) -> set[str]:
    return set(keys)


def _any(keys: set[str], choices: frozenset[str]) -> bool:
    return bool(keys & choices)


def _axes(held: set[str]) -> tuple[bool, bool, bool, bool]:
    return (
        _any(held, UP),
        _any(held, DOWN),
        _any(held, LEFT),
        _any(held, RIGHT),
    )


def _axis_direction(up: bool, down: bool, left: bool, right: bool) -> Direction | None:
    dx = -1 if left and not right else 1 if right and not left else 0
    dy = -1 if up and not down else 1 if down and not up else 0
    return (dx, dy) if dx or dy else None


def _pressed_direction(pressed: set[str]) -> bool:
    return bool(pressed & (UP | DOWN | LEFT | RIGHT))


def _vi_diagonal(keys: set[str]) -> Direction | None:
    for key, direction in VI_DIAGONALS:
        if key in keys:
            return direction
    return None


def direction_press(
    held: Iterable[str],
    pressed: Iterable[str],
    pending: Direction | None,
    diag_assist: bool,
) -> tuple[Direction | None, Direction | None]:
    held_set = _as_set(held)
    pressed_set = _as_set(pressed)

    direction = _vi_diagonal(pressed_set)
    if direction is not None:
        return direction, None

    up, down, left, right = _axes(held_set)
    if _pressed_direction(pressed_set):
        direction = _axis_direction(up, down, left, right)
        if direction is not None and direction[0] and direction[1]:
            return direction, None

    if pending is not None:
        pdx, pdy = pending
        if pdy < 0 and up:
            if right and not left:
                return (1, -1), None
            if left and not right:
                return (-1, -1), None
        elif pdy > 0 and down:
            if right and not left:
                return (1, 1), None
            if left and not right:
                return (-1, 1), None
        elif pdx < 0 and left:
            if up and not down:
                return (-1, -1), None
            if down and not up:
                return (-1, 1), None
        elif pdx > 0 and right:
            if up and not down:
                return (1, -1), None
            if down and not up:
                return (1, 1), None
        return pending, None

    if diag_assist:
        return None, None

    if pressed_set & UP:
        return None, (0, -1)
    if pressed_set & DOWN:
        return None, (0, 1)
    if pressed_set & LEFT:
        return None, (-1, 0)
    if pressed_set & RIGHT:
        return None, (1, 0)
    return None, None


def prompt_direction(held: Iterable[str], pressed: Iterable[str]) -> Direction | None:
    held_set = _as_set(held)
    pressed_set = _as_set(pressed)
    direction = _vi_diagonal(pressed_set)
    if direction is not None:
        return direction
    if not _pressed_direction(pressed_set):
        return None
    return _axis_direction(*_axes(held_set))


def held_direction(held: Iterable[str], diag_assist: bool) -> Direction | None:
    held_set = _as_set(held)
    direction = _vi_diagonal(held_set)
    if direction is not None:
        return direction
    direction = _axis_direction(*_axes(held_set))
    if direction is not None and direction[0] and direction[1]:
        return direction
    if diag_assist:
        return None
    return direction


def any_direction_held(held: Iterable[str]) -> bool:
    held_set = _as_set(held)
    return any(_axes(held_set))


def select_direction(
    held: Iterable[str],
    pressed: Iterable[str],
    back_held: bool,
) -> Direction | None:
    if not back_held:
        return None
    held_set = _as_set(held)
    pressed_set = _as_set(pressed)
    if not _pressed_direction(pressed_set):
        return None
    return _axis_direction(*_axes(held_set))


def count_digit(pressed: Iterable[str], shifted: bool, controlled: bool) -> int | None:
    if shifted or controlled:
        return None
    pressed_set = _as_set(pressed)
    for digit in DIGITS:
        if digit in pressed_set:
            return int(digit)
    return None
