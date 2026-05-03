"""Rogue 5.4.4 passages.c helpers."""
from __future__ import annotations


def is_number_cell(tile: int, hidden_tile: int | None, corridor_tile: int, door_tile: int) -> bool:
    """Rogue 5.4.4 passages.c:numpass() F_PASS / door cell gate."""
    return tile in (corridor_tile, door_tile) or hidden_tile in (corridor_tile, door_tile)


def is_exit_cell(tile: int, hidden_tile: int | None, door_tile: int) -> bool:
    """Rogue 5.4.4 passages.c:numpass() visible/secret door exit gate."""
    return tile == door_tile or hidden_tile == door_tile


class PassageComponent:
    """Passage identity plus passages.c:numpass() traversal order."""

    def __init__(self, cells, order):
        self.cells = frozenset(cells)
        self.order = tuple(order)

    def __contains__(self, pos):
        return pos in self.cells

    def __iter__(self):
        return iter(self.cells)

    def __len__(self):
        return len(self.cells)

    def __eq__(self, other):
        if isinstance(other, PassageComponent):
            return self.cells == other.cells
        return self.cells == other

    def __hash__(self):
        return hash(self.cells)


def passage_component(start, in_bounds, is_number_cell_at):
    """Return the 4-way passage component numbered by passages.c:numpass()."""
    x, y = start
    if not in_bounds(x, y) or not is_number_cell_at(x, y):
        return None
    seen = set()
    order = []
    stack = [(x, y)]
    while stack:
        cx, cy = stack.pop()
        if (cx, cy) in seen:
            continue
        if not in_bounds(cx, cy) or not is_number_cell_at(cx, cy):
            continue
        seen.add((cx, cy))
        order.append((cx, cy))
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            stack.append((cx + dx, cy + dy))
    return PassageComponent(seen, order)


def passage_exits(component, is_exit_cell_at):
    """Return visible/secret door exits in a numbered passage component."""
    cells = getattr(component, "order", component)
    return [pos for pos in cells if is_exit_cell_at(pos[0], pos[1])]
