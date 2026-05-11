from __future__ import annotations

from dataclasses import dataclass


DIFF_EASY = "easy"
DIFF_NORMAL = "normal"
DIFF_CLASSIC = "classic"
DIFF_STRICT = "strict"

DEFAULT_DIFFICULTY = DIFF_NORMAL
DIFFICULTY_ORDER = (DIFF_EASY, DIFF_NORMAL, DIFF_CLASSIC, DIFF_STRICT)


@dataclass(frozen=True)
class DifficultyProfile:
    id: str
    label: str
    description_en: str
    description_ja: str
    score_multiplier: float
    scoreboard_key: str
    easy_type_known: bool
    idscrl: bool
    show_status_hud: bool


PROFILES = {
    DIFF_EASY: DifficultyProfile(
        DIFF_EASY,
        "Easy",
        "A gentler start for first runs.",
        "初めてでも探索を楽しみやすい",
        1.0,
        DIFF_EASY,
        True,
        True,
        True,
    ),
    DIFF_NORMAL: DifficultyProfile(
        DIFF_NORMAL,
        "Normal",
        "The intended Rogue V5 experience.",
        "Rogue V5の標準体験",
        1.0,
        DIFF_NORMAL,
        False,
        True,
        True,
    ),
    DIFF_CLASSIC: DifficultyProfile(
        DIFF_CLASSIC,
        "Classic",
        "Closer to original Rogue 5.4.4.",
        "Rogue 5.4.4の手触り重視",
        1.0,
        DIFF_CLASSIC,
        False,
        False,
        True,
    ),
    DIFF_STRICT: DifficultyProfile(
        DIFF_STRICT,
        "Strict",
        "Rogue 5.4.4 challenge.",
        "Rogue 5.4.4 準拠チャレンジ",
        1.0,
        DIFF_STRICT,
        False,
        False,
        False,
    ),
}


def normalize(value: str | None) -> str:
    return value if value in PROFILES else DEFAULT_DIFFICULTY


def profile(value: str | None) -> DifficultyProfile:
    return PROFILES[normalize(value)]
