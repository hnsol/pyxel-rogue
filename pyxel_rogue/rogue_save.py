from __future__ import annotations

import base64
import json
import os
import sys
from typing import Any

SAVE_STORAGE_KEY = "pyxel-rogue-save-v1"
SAVE_FILE = os.environ.get(
    "PYXEL_ROGUE_SAVE_FILE",
    os.path.join(os.path.expanduser("~"), ".pyxel_rogue_save_v1.sav"),
)

_ENCSTR = b"\300k||`\251Y.'\305\321\201+\277~r\"]\240_\223=1\341)\222\212\241t;\t$\270\314/<#\201\254"
_STATLIST = b"\355kl{+\204\255\313idJ\361\214=4:\311\271\341wK<\312\321\213,,7\271/Rk%\b\312\f\246"


class SaveError(Exception):
    pass


def _crypt(data: bytes) -> bytes:
    out = bytearray()
    fb = 0
    e1 = e2 = 0
    for byte in data:
        key1 = _ENCSTR[e1]
        key2 = _STATLIST[e2]
        out.append(byte ^ key1 ^ key2 ^ fb)
        fb = (fb + (key1 * key2)) & 0xFF
        e1 = (e1 + 1) % len(_ENCSTR)
        e2 = (e2 + 1) % len(_STATLIST)
    return bytes(out)


def encode(data: dict[str, Any]) -> str:
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(_crypt(raw)).decode("ascii")


def decode(text: str) -> dict[str, Any]:
    try:
        raw = _crypt(base64.b64decode(text.encode("ascii"), validate=True))
        data = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise SaveError("invalid save data") from exc
    if not isinstance(data, dict):
        raise SaveError("invalid save data")
    return data


def _local_storage():
    if sys.platform != "emscripten":
        return None
    from js import localStorage

    return localStorage


def exists(path: str | None = None) -> bool:
    try:
        storage = _local_storage()
        if storage is not None:
            return bool(storage.getItem(SAVE_STORAGE_KEY))
        return os.path.exists(path or SAVE_FILE)
    except Exception:
        return False


def save(data: dict[str, Any], path: str | None = None) -> None:
    text = encode(data)
    storage = _local_storage()
    if storage is not None:
        storage.setItem(SAVE_STORAGE_KEY, text)
        return
    with open(path or SAVE_FILE, "w", encoding="ascii") as f:
        f.write(text)


def load(path: str | None = None) -> dict[str, Any]:
    try:
        storage = _local_storage()
        if storage is not None:
            text = storage.getItem(SAVE_STORAGE_KEY)
            if not text:
                raise SaveError("save data not found")
            return decode(str(text))
        with open(path or SAVE_FILE, encoding="ascii") as f:
            return decode(f.read())
    except SaveError:
        raise
    except Exception as exc:
        raise SaveError("save data not found") from exc


def delete(path: str | None = None) -> None:
    storage = _local_storage()
    if storage is not None:
        storage.removeItem(SAVE_STORAGE_KEY)
        return
    try:
        os.unlink(path or SAVE_FILE)
    except FileNotFoundError:
        pass
