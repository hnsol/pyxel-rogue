"""Sound-effect slots, loading, and playback arbitration."""

from __future__ import annotations

import os

SFX_CH = 3

SFX_SELECT_LOW = 8
SFX_SELECT_HIGH = 9
SFX_ERROR = 11
SFX_STAIRS = 12
SFX_WARP = 14
SFX_TRAP = 16
SFX_HIT_PLAYER = 18
SFX_HIT_MISS = 19
SFX_HIT_MONSTER = 20
SFX_KILL = 22
SFX_WAND_ZAP = 23
SFX_EXPLODE = 25
SFX_ESCAPE = 27
SFX_BREATH = 28
SFX_ELECTRIC = 30
SFX_ICE = 31
SFX_SPELL_USE = 32
SFX_PICKUP = 34
SFX_HEAL_SMALL = 36
SFX_HEAL_LARGE = 37

SFX_PRIORITY = {
    SFX_HEAL_LARGE: 90,
    SFX_HEAL_SMALL: 90,
    SFX_KILL: 80,
    SFX_TRAP: 80,
    SFX_WARP: 80,
    SFX_EXPLODE: 80,
    SFX_ELECTRIC: 80,
    SFX_ICE: 80,
    SFX_BREATH: 80,
    SFX_HIT_PLAYER: 70,
    SFX_HIT_MISS: 70,
    SFX_HIT_MONSTER: 70,
    SFX_STAIRS: 60,
    SFX_PICKUP: 60,
    SFX_SPELL_USE: 60,
    SFX_WAND_ZAP: 60,
    SFX_SELECT_HIGH: 50,
    SFX_ERROR: 50,
    SFX_SELECT_LOW: 40,
}


def sfx_priority(slot: int) -> int:
    return SFX_PRIORITY.get(slot, 0)


def _sound_field(sound, name):
    value = getattr(sound, name)
    return value() if callable(value) else value


def copy_sound(src, dst) -> None:
    notes = _sound_field(src, "notes")
    tones = _sound_field(src, "tones")
    volumes = _sound_field(src, "volumes")
    effects = _sound_field(src, "effects")
    speed = _sound_field(src, "speed")
    if isinstance(notes, str):
        dst.set(notes, tones, volumes, effects, speed)
        return
    dst.notes[:] = list(notes)
    dst.tones[:] = list(tones)
    dst.volumes[:] = list(volumes)
    dst.effects[:] = list(effects)
    dst.speed = speed


def copy_se_pack_slots(pyxel_module) -> None:
    copied = []
    for i in range(30):
        sound = pyxel_module.sounds[4 + i]
        copied.append(
            (
                _sound_field(sound, "notes"),
                _sound_field(sound, "tones"),
                _sound_field(sound, "volumes"),
                _sound_field(sound, "effects"),
                _sound_field(sound, "speed"),
            )
        )
    for i, sound in enumerate(copied):
        notes, tones, volumes, effects, speed = sound
        if isinstance(notes, str):
            pyxel_module.sounds[8 + i].set(notes, tones, volumes, effects, speed)
        else:
            dst = pyxel_module.sounds[8 + i]
            dst.notes[:] = list(notes)
            dst.tones[:] = list(tones)
            dst.volumes[:] = list(volumes)
            dst.effects[:] = list(effects)
            dst.speed = speed


def load_se_pack(pyxel_module, path: str) -> bool:
    if not os.path.exists(path):
        return False
    pyxel_module.load(path, exclude_images=True, exclude_tilemaps=True, exclude_musics=True)
    copy_se_pack_slots(pyxel_module)
    return True


class SfxController:
    def __init__(self, pyxel_module, bgm_ctrl=None, enabled: bool = True):
        self.pyxel = pyxel_module
        self.bgm = bgm_ctrl
        self.enabled = bool(enabled)
        self._active = False
        self._pending = None

    def request(self, slot: int) -> None:
        if not self.enabled:
            return
        if self._pending is None or sfx_priority(slot) >= sfx_priority(self._pending):
            self._pending = slot

    def is_active(self) -> bool:
        return self._active

    def update(self) -> None:
        if not self.enabled:
            self._pending = None
            return
        if self._active and self.pyxel.play_pos(SFX_CH) is None:
            self._active = False
            if self._pending is None and self.bgm:
                self.bgm.resume_ch(SFX_CH)
        if self._pending is not None and not self._active:
            slot = self._pending
            self._pending = None
            self.pyxel.play(SFX_CH, slot)
            self._active = True
