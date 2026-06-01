"""Sound-effect slots, loading, and playback arbitration."""

from __future__ import annotations

import os
import random

SFX_CH = 3

SFX_SELECT_LOW = 4
SFX_SELECT_HIGH = 5
SFX_MESSAGE = 6
SFX_ERROR = 7
SFX_STAIRS = 8
SFX_WARP = 10
SFX_TRAP = 12
SFX_HIT_1 = 14
SFX_HIT_2 = 15
SFX_HIT_3 = 16
SFX_HIT_4 = 17
SFX_SECRET_DOOR = 32
SFX_DEATH = 18
SFX_THROW = 19
SFX_WAND_ZAP = 19
SFX_THROW_HIT = 20
SFX_EXPLODE = 21
SFX_ESCAPE = 23
SFX_BREATH = 24
SFX_ELECTRIC = 26
SFX_ICE = 27
SFX_SPELL_USE = 28
SFX_PICKUP = SFX_MESSAGE
SFX_HEAL_SMALL = 32
SFX_HEAL_LARGE = 33
SFX_DEATH_ECHO_1 = 34
SFX_DEATH_ECHO_2 = 35
SFX_HIT_MISS = 36

HIT_SFX = (SFX_HIT_1, SFX_HIT_3, SFX_HIT_4)
DEATH_SFX_SEQUENCE = (SFX_DEATH, SFX_DEATH_ECHO_1, SFX_DEATH_ECHO_2)

SFX_PRIORITY = {
    SFX_HEAL_LARGE: 90,
    SFX_HEAL_SMALL: 90,
    SFX_TRAP: 80,
    SFX_WARP: 80,
    SFX_EXPLODE: 80,
    SFX_ELECTRIC: 80,
    SFX_ICE: 80,
    SFX_BREATH: 80,
    SFX_HIT_1: 70,
    SFX_HIT_2: 70,
    SFX_HIT_3: 70,
    SFX_HIT_4: 70,
    SFX_THROW_HIT: 70,
    SFX_DEATH: 70,
    SFX_STAIRS: 60,
    SFX_SECRET_DOOR: 60,
    SFX_SPELL_USE: 60,
    SFX_WAND_ZAP: 60,
    SFX_HIT_MISS: 50,
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


def _scaled_volumes(volumes, scale: float):
    if isinstance(volumes, str):
        return "".join(str(max(0, min(7, round(int(ch) * scale)))) for ch in volumes)
    return [max(0, min(7, round(value * scale))) for value in volumes]


def copy_sound_scaled(src, dst, volume_scale: float) -> None:
    notes = _sound_field(src, "notes")
    tones = _sound_field(src, "tones")
    volumes = _scaled_volumes(_sound_field(src, "volumes"), volume_scale)
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


def _transposed_notes(notes, semitones: int):
    if isinstance(notes, str):
        return notes
    return [note + semitones if note >= 0 else note for note in notes]


def _first_steps(value, count: int):
    if isinstance(value, str):
        return value[:count]
    values = list(value)
    return values[:count] if len(values) > count else values


def copy_sound_transposed(src, dst, semitones: int, *, note_limit: int | None = None) -> None:
    raw_notes = _sound_field(src, "notes")
    notes = _transposed_notes(_first_steps(raw_notes, note_limit), semitones) if note_limit else _transposed_notes(raw_notes, semitones)
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


def build_death_echo_sounds(pyxel_module) -> None:
    src = pyxel_module.sounds[SFX_DEATH]
    copy_sound_scaled(src, pyxel_module.sounds[SFX_DEATH_ECHO_1], 0.65)
    copy_sound_scaled(src, pyxel_module.sounds[SFX_DEATH_ECHO_2], 0.35)


def build_miss_sound(pyxel_module) -> None:
    dst = pyxel_module.sounds[SFX_HIT_MISS]
    notes = [28, 25, 27, 25, 49, 52, 52, 49]
    tones = [2, 3, 3, 3, 2, 2, 2, 2]
    volumes = [7, 7, 7, 6, 5, 5, 4, 4]
    effects = [1]
    if isinstance(getattr(dst, "notes"), str):
        dst.set(notes, tones, volumes, effects, 1)
        return
    dst.notes[:] = notes
    dst.tones[:] = tones
    dst.volumes[:] = volumes
    dst.effects[:] = effects
    dst.speed = 1


def load_se_pack(pyxel_module, path: str) -> bool:
    if not os.path.exists(path):
        return False
    pyxel_module.load(path, exclude_images=True, exclude_tilemaps=True, exclude_musics=True)
    build_death_echo_sounds(pyxel_module)
    build_miss_sound(pyxel_module)
    return True


class SfxController:
    def __init__(self, pyxel_module, bgm_ctrl=None, enabled: bool = True, rng=None):
        self.pyxel = pyxel_module
        self.bgm = bgm_ctrl
        self.enabled = bool(enabled)
        self.rng = rng or random.Random()
        self._active = False
        self._pending = None

    def request(self, slot: int) -> None:
        if not self.enabled:
            return
        if self._pending is None or sfx_priority(slot) >= sfx_priority(self._pending):
            self._pending = slot

    def request_random_hit(self) -> None:
        self.request(HIT_SFX[self.rng.randrange(len(HIT_SFX))])

    def play_immediate(self, slot: int, *, stop_bgm: bool = False) -> None:
        if not self.enabled:
            return
        self._pending = None
        if stop_bgm and self.bgm:
            self.bgm.stop()
        self.pyxel.play(SFX_CH, slot)
        self._active = True

    def play_death(self) -> None:
        self._pending = None
        if self.bgm:
            self.bgm.stop()
        if not self.enabled:
            return
        self.pyxel.play(SFX_CH, list(DEATH_SFX_SEQUENCE))
        self._active = True

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
