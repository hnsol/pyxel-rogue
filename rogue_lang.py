import json
import os
import sys
from dataclasses import dataclass

from rogue_palettes import DEFAULT_PALETTE, PALETTE_IDS

LANG_EN = "en"
LANG_JA = "ja"
SETTINGS_STORAGE_KEY = "pyxel-rogue-settings-v1"
SETTINGS_FILE = os.environ.get(
    "PYXEL_ROGUE_SETTINGS_FILE",
    os.path.join(os.path.expanduser("~"), ".pyxel_rogue_settings_v1.json"),
)
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
        self.auto_pickup = bool(self.auto_pickup)
        self.show_run_steps = bool(self.show_run_steps)


def settings_to_dict(settings):
    settings = settings if isinstance(settings, Settings) else Settings()
    return {
        "language": settings.language,
        "auto_pickup": bool(settings.auto_pickup),
        "palette": settings.palette,
        "show_run_steps": bool(settings.show_run_steps),
    }


def settings_from_dict(data):
    data = data if isinstance(data, dict) else {}
    return Settings(
        language=str(data.get("language", DEFAULT_LANG)),
        auto_pickup=bool(data.get("auto_pickup", True)),
        palette=str(data.get("palette", DEFAULT_PALETTE)),
        show_run_steps=bool(data.get("show_run_steps", True)),
    )


def load_settings():
    try:
        if sys.platform == "emscripten":
            from js import localStorage

            raw = localStorage.getItem(SETTINGS_STORAGE_KEY)
            return settings_from_dict(json.loads(str(raw))) if raw else Settings()
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, encoding="utf-8") as f:
                return settings_from_dict(json.load(f))
    except Exception:
        pass
    return Settings()


def settings_exists():
    try:
        if sys.platform == "emscripten":
            from js import localStorage

            return bool(localStorage.getItem(SETTINGS_STORAGE_KEY))
        return os.path.exists(SETTINGS_FILE)
    except Exception:
        return False


def save_settings(settings):
    normalized = settings_from_dict(settings_to_dict(settings))
    data = settings_to_dict(normalized)
    try:
        if sys.platform == "emscripten":
            from js import localStorage

            localStorage.setItem(SETTINGS_STORAGE_KEY, json.dumps(data, ensure_ascii=False))
        else:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
    except Exception:
        pass
    return normalized
