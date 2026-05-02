"""Rogue 5.4.4 init.c helpers."""
from __future__ import annotations


def initial_arrow_count(rnd) -> int:
    """Rogue 5.4.4 init.c:init_player() arrows use rnd(15)+25."""
    return rnd(15) + 25


def initial_pack_order(food, armor, mace, bow, arrows):
    """Rogue 5.4.4 init.c:init_player() add_pack order."""
    return [food, armor, mace, bow, arrows]


def scroll_title(syllables, rnd, max_name: int = 40) -> str:
    """Rogue 5.4.4 init.c:init_names() scroll title generator."""
    words = []
    for _ in range(rnd(3) + 2):
        word = ""
        for _ in range(rnd(3) + 1):
            syllable = syllables[rnd(len(syllables))]
            if len(word) + len(syllable) > max_name:
                break
            word += syllable
        words.append(word)
    return " ".join(words)
