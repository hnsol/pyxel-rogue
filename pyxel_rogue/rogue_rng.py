from __future__ import annotations
from typing import Any, Sequence, TypeVar

T = TypeVar("T")

class RogueRng:
    """Small RNG facade matching Rogue 5.4.4 helper names."""

    def __init__(self, backend: Any) -> None:
        self.backend = backend

    def rnd(self, n: int) -> int:
        """Rogue 5.4.4 rnd(n) — random int in [0, n-1]."""
        return self.randrange(n) if n > 0 else 0

    def roll(self, number: int, sides: int) -> int:
        """Rogue 5.4.4 roll(number, sides) — sum of number d-sided dice."""
        return sum(self.rnd(sides) + 1 for _ in range(number))

    def spread(self, nm: int) -> int:
        """Rogue 5.4.4 spread(nm) — slightly randomised value near nm."""
        return nm - nm // 20 + self.rnd(nm // 10)

    def randint(self, a: int, b: int) -> int:
        return self.backend.randint(a, b)

    def randrange(self, n: int) -> int:
        return self.backend.randrange(n)

    def random(self) -> float:
        return self.backend.random()

    def choice(self, seq: Sequence[T]) -> T:
        return self.backend.choice(seq)

    def shuffle(self, seq: list) -> None:
        self.backend.shuffle(seq)

    def sample(self, seq: Sequence[T], k: int) -> list[T]:
        return self.backend.sample(seq, k)

    def getstate(self) -> Any:
        return self.backend.getstate()

    def setstate(self, state: Any) -> None:
        self.backend.setstate(state)
