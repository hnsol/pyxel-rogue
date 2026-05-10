"""Rogue 5.4.4 init.c helpers."""
from __future__ import annotations


def initial_arrow_count(rnd) -> int:
    """Rogue 5.4.4 init.c:init_player() arrows use rnd(15)+25."""
    return rnd(15) + 25


def initial_pack_order(food, armor, mace, bow, arrows):
    """Rogue 5.4.4 init.c:init_player() add_pack order."""
    return [food, armor, mace, bow, arrows]


def scroll_title_recipe(syllable_count: int, rnd, max_name: int = 40, syllables=None):
    """Rogue 5.4.4 init.c:init_names() scroll title index recipe."""
    title_len = 0
    recipe = []
    for _ in range(rnd(3) + 2):
        word = []
        for _ in range(rnd(3) + 1):
            idx = rnd(syllable_count)
            syllable_len = len(syllables[idx]) if syllables is not None else 0
            if syllables is not None and title_len + syllable_len > max_name:
                break
            word.append(idx)
            title_len += syllable_len
        recipe.append(tuple(word))
        title_len += 1
    return tuple(recipe)


def render_scroll_title(recipe, syllables) -> str:
    """Render a scroll title recipe with a language-specific syllable table."""
    return " ".join("".join(syllables[idx] for idx in word) for word in recipe)


def scroll_title(syllables, rnd, max_name: int = 40) -> str:
    """Rogue 5.4.4 init.c:init_names() scroll title generator."""
    recipe = scroll_title_recipe(len(syllables), rnd, max_name, syllables)
    return render_scroll_title(recipe, syllables)
