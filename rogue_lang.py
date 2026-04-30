import os
from dataclasses import dataclass

from rogue_palettes import DEFAULT_PALETTE, PALETTE_IDS

LANG_EN = "en"
LANG_JA = "ja"
DEFAULT_LANG = os.environ.get("PYXEL_ROGUE_LANG", LANG_EN).lower()
if DEFAULT_LANG not in (LANG_EN, LANG_JA):
    DEFAULT_LANG = LANG_EN


@dataclass
class Settings:
    language: str = DEFAULT_LANG
    auto_pickup: bool = True
    palette: str = DEFAULT_PALETTE
    show_run_steps: bool = True

    def __post_init__(self):
        if self.language not in (LANG_EN, LANG_JA):
            self.language = LANG_EN
        if self.palette not in PALETTE_IDS:
            self.palette = DEFAULT_PALETTE
