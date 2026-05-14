"""Message and term catalog access."""

from __future__ import annotations

import json
import os
import sys

from pyxel_rogue.rogue_items import (
    CAT_AMULET,
    CAT_ARM,
    CAT_FOOD,
    CAT_POT,
    CAT_RING,
    CAT_SCR,
    CAT_STICK,
    CAT_WPN,
)
from pyxel_rogue.rogue_lang import LANG_EN, LANG_JA


class TextCatalog:
    _catalogs = None
    _terms = None
    _missing_warned = set()
    _message_aliases = {
        "pixel.nyandor_cat_recovered": "pyxel.nyandor_cat_recovered",
        "pixel.nyandor_vitory_line1": "ui.nyandor_victory_line_1",
        "pixel.nyandor_vitory_line2": "ui.nyandor_victory_line_2",
    }

    @classmethod
    def _asset_path(cls, *parts):
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", *parts)

    @classmethod
    def _load_catalogs(cls):
        if cls._catalogs is not None:
            return cls._catalogs
        base = cls._asset_path("messages")
        catalogs = {}
        try:
            if sys.platform == "emscripten":
                import pyodide.http as _ph

                _base = "https://raw.githubusercontent.com/hnsol/pyxel-rogue/master"
                for lang in (LANG_EN, LANG_JA):
                    resp = _ph.open_url(f"{_base}/assets/messages/{lang}.json")
                    catalogs[lang] = json.load(resp)
            else:
                for lang in (LANG_EN, LANG_JA):
                    path = os.path.join(base, f"{lang}.json")
                    with open(path, encoding="utf-8") as f:
                        catalogs[lang] = json.load(f)
        except Exception:
            from pyxel_rogue.rogue_message_catalogs import EN_MESSAGES, JA_MESSAGES

            catalogs = {LANG_EN: EN_MESSAGES, LANG_JA: JA_MESSAGES}
        cls._catalogs = catalogs
        return cls._catalogs

    @classmethod
    def _load_terms(cls):
        if cls._terms is not None:
            return cls._terms
        base = cls._asset_path("terms")
        terms = {}
        try:
            if sys.platform == "emscripten":
                import pyodide.http as _ph

                _base = "https://raw.githubusercontent.com/hnsol/pyxel-rogue/master"
                for lang in (LANG_EN, LANG_JA):
                    resp = _ph.open_url(f"{_base}/assets/terms/{lang}.json")
                    terms[lang] = json.load(resp)
            else:
                for lang in (LANG_EN, LANG_JA):
                    path = os.path.join(base, f"{lang}.json")
                    with open(path, encoding="utf-8") as f:
                        terms[lang] = json.load(f)
        except Exception:
            from pyxel_rogue.rogue_terms import EN_TERMS, JA_TERMS

            terms = {LANG_EN: EN_TERMS, LANG_JA: JA_TERMS}
        cls._terms = terms
        return cls._terms

    @classmethod
    def _warn_missing(cls, key):
        if key in cls._missing_warned:
            return
        cls._missing_warned.add(key)
        print(f"[TextCatalog] missing message key: {key}", file=sys.stderr)

    @staticmethod
    def msg(lang, key, **kw):
        key = TextCatalog._message_aliases.get(key, key)
        catalogs = TextCatalog._load_catalogs()
        lang = lang if lang in (LANG_EN, LANG_JA) else LANG_EN
        s = catalogs.get(lang, {}).get(key)
        if s is None and lang != LANG_EN:
            s = catalogs.get(LANG_EN, {}).get(key)
        if s is None:
            from pyxel_rogue.rogue_message_catalogs import EN_MESSAGES, JA_MESSAGES

            builtins = {LANG_EN: EN_MESSAGES, LANG_JA: JA_MESSAGES}
            s = builtins.get(lang, {}).get(key)
            if s is None and lang != LANG_EN:
                s = builtins.get(LANG_EN, {}).get(key)
        if s is None:
            TextCatalog._warn_missing(key)
            s = f"[missing:{key}]"
        return s.format(**kw) if kw else s

    @staticmethod
    def menu(lang, key):
        msg_key = "menu." + key.lower().replace(" ", "_")
        return TextCatalog.msg(lang, msg_key)

    @staticmethod
    def trap(lang, key):
        msg_key = "trap." + key.lower().replace(" ", "_")
        return TextCatalog.msg(lang, msg_key)

    @staticmethod
    def monster(lang, name):
        return TextCatalog.term(lang, ("monster",), name)

    @staticmethod
    def hud_item_kind(lang, cat, name):
        lang = lang if lang in (LANG_EN, LANG_JA) else LANG_EN
        if cat == CAT_WPN:
            return TextCatalog.term(
                lang, ("hud", "weapon"), name, TextCatalog.item_kind(lang, cat, name)
            )
        if cat == CAT_ARM:
            return TextCatalog.term(
                lang, ("hud", "armor"), name, TextCatalog.item_kind(lang, cat, name)
            )
        return TextCatalog.item_kind(lang, cat, name)

    @staticmethod
    def hud_label(lang, name):
        return TextCatalog.term(lang, ("hud", "label"), name)

    @staticmethod
    def item_kind(lang, cat, name):
        cat_key = {
            CAT_POT: "potion",
            CAT_SCR: "scroll",
            CAT_FOOD: "food",
            CAT_WPN: "weapon",
            CAT_ARM: "armor",
            CAT_RING: "ring",
            CAT_STICK: "stick",
            CAT_AMULET: "amulet",
        }.get(cat)
        return TextCatalog.term(lang, ("item", cat_key), name) if cat_key else name

    @staticmethod
    def potion_color(lang, color):
        return TextCatalog.term(lang, ("potion_color",), color)

    @staticmethod
    def color(lang, name, form="noun"):
        return TextCatalog.term(lang, ("color", form), name)

    @staticmethod
    def action(lang, name):
        return TextCatalog.term(lang, ("action",), name)

    @staticmethod
    def bolt(lang, name):
        return TextCatalog.term(lang, ("bolt",), name)

    @staticmethod
    def material(lang, cat, name):
        return TextCatalog.term(lang, ("material", cat), name)

    @staticmethod
    def stick_type(lang, name):
        return TextCatalog.term(lang, ("stick_type",), name)

    @staticmethod
    def term(lang, path, key, default=None):
        terms = TextCatalog._load_terms()
        lang = lang if lang in (LANG_EN, LANG_JA) else LANG_EN
        node = terms.get(lang, {})
        for part in path:
            node = node.get(part, {}) if isinstance(node, dict) else {}
        value = node.get(key) if isinstance(node, dict) else None
        if value is None and lang != LANG_EN:
            node = terms.get(LANG_EN, {})
            for part in path:
                node = node.get(part, {}) if isinstance(node, dict) else {}
            value = node.get(key) if isinstance(node, dict) else None
        return value if value is not None else (key if default is None else default)
