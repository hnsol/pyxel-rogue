"""Dungeon BGM selection and playback."""
from __future__ import annotations

import hashlib
import random
import time
from dataclasses import dataclass

from pyxel_rogue.rogue_bgm_generator import BGMGenerator


@dataclass(frozen=True)
class BgmFloorProfile:
    chord: int
    base: int


FLOOR_PROFILES = (
    (1, 4, BgmFloorProfile(8, 9)),
    (5, 9, BgmFloorProfile(9, 9)),
    (10, 14, BgmFloorProfile(10, 10)),
    (15, 19, BgmFloorProfile(11, 11)),
    (20, 24, BgmFloorProfile(12, 11)),
    (25, 25, BgmFloorProfile(12, 12)),
    (26, 999, BgmFloorProfile(10, 12)),
)

DANGER_PARAMS = {
    0: {"speed": 312, "instrumentation": 3, "melo_density": 2},
    1: {"speed": 312, "instrumentation": 2, "melo_density": 2},
    2: {"speed": 276, "instrumentation": 0, "melo_density": 2},
    3: {"speed": 240, "instrumentation": 0, "melo_density": 4},
}


def floor_profile(depth: int) -> BgmFloorProfile:
    depth = max(1, int(depth))
    for lo, hi, profile in FLOOR_PROFILES:
        if lo <= depth <= hi:
            return profile
    return FLOOR_PROFILES[-1][2]


def danger_state(hp: int, max_hp: int, hunger_state: str) -> int:
    ratio = 1.0 if max_hp <= 0 else hp / max_hp
    hunger = {"normal": 0, "hungry": 1, "weak": 2, "faint": 3}.get(hunger_state, 0)
    if ratio > 0.5:
        return min(3, hunger)
    if ratio >= 0.25:
        return (1, 1, 2, 3)[hunger]
    return (2, 2, 3, 3)[hunger]


def exploration_params(depth: int, hp: int, max_hp: int, hunger_state: str) -> dict:
    profile = floor_profile(depth)
    params = dict(DANGER_PARAMS[danger_state(hp, max_hp, hunger_state)])
    params.update({"chord": profile.chord, "base": profile.base})
    return params


def result_params(previous_params: dict | None) -> dict:
    params = dict(previous_params or exploration_params(1, 1, 1, "normal"))
    params["speed"] = 360
    return params


class DungeonBgmController:
    def __init__(
        self,
        pyxel_module,
        generator_factory=BGMGenerator,
        seed: int | None = None,
        first_channel: int = 0,
        first_sound: int = 4,
    ):
        self.pyxel = pyxel_module
        self.generator_factory = generator_factory
        self.seed = int(time.time_ns() if seed is None else seed)
        self.first_channel = first_channel
        self.first_sound = first_sound
        self.cache = {}
        self.current_key = None
        self.last_exploration_params = None

    def play_exploration(self, *, depth: int, hp: int, max_hp: int, hunger_state: str, enabled: bool) -> None:
        if not enabled:
            self.stop()
            return
        depth_key = max(1, int(depth))
        params = exploration_params(depth, hp, max_hp, hunger_state)
        self.last_exploration_params = dict(params)
        self._play_key(("explore", depth_key, self._params_key(params)), params)

    def play_result(self, enabled: bool = True) -> None:
        if not enabled:
            self.stop()
            return
        params = result_params(self.last_exploration_params)
        self._play_key(("result", self._params_key(params)), params)

    def stop(self) -> None:
        for ch in range(4):
            self.pyxel.stop(self.first_channel + ch)
        self.current_key = None

    def _play_key(self, key, params) -> None:
        if key == self.current_key:
            return
        music = self.cache.get(key)
        if music is None:
            music = self._generate_music(key, params)
            self.cache[key] = music
        self._play_music(music)
        self.current_key = key

    def _generate_music(self, key, params):
        generator = self.generator_factory(rng=random.Random(self._seed_for(key)))
        generator.set_parm(params)
        generator.generate_music()
        return generator.music

    def _play_music(self, music) -> None:
        self.stop()
        for ch, sound in enumerate(music[:4]):
            channel = self.first_channel + ch
            slot = self.first_sound + ch
            if sound:
                self.pyxel.sounds[slot].set(*sound)
                self.pyxel.play(channel, slot, loop=True)

    def _seed_for(self, key) -> int:
        raw = f"{self.seed}:{key!r}".encode("utf-8")
        return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big")

    @staticmethod
    def _params_key(params):
        return tuple((key, params[key]) for key in sorted(params))
