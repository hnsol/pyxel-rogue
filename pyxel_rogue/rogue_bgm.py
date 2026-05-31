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


@dataclass(frozen=True)
class BgmFloorBand:
    lo: int
    hi: int
    profiles: tuple[BgmFloorProfile, ...]


FLOOR_PROFILE_BANDS = (
    (1, 4, (BgmFloorProfile(8, 9), BgmFloorProfile(9, 9), BgmFloorProfile(11, 9))),
    (5, 9, (BgmFloorProfile(8, 10), BgmFloorProfile(9, 10), BgmFloorProfile(11, 10))),
    (10, 14, (BgmFloorProfile(9, 10), BgmFloorProfile(10, 10), BgmFloorProfile(11, 11))),
    (15, 19, (BgmFloorProfile(10, 11), BgmFloorProfile(11, 11), BgmFloorProfile(12, 11))),
    (20, 24, (BgmFloorProfile(10, 11), BgmFloorProfile(12, 11), BgmFloorProfile(12, 12))),
    (25, 999, (BgmFloorProfile(10, 12),)),
)

DANGER_PARAMS = {
    0: {"speed": 312, "instrumentation": 3, "melo_density": 2},
    1: {"speed": 312, "instrumentation": 2, "melo_density": 2},
    2: {"speed": 276, "instrumentation": 0, "melo_density": 2},
    3: {"speed": 240, "instrumentation": 0, "melo_density": 4},
}


def floor_band(depth: int) -> tuple[int, BgmFloorBand]:
    depth = max(1, int(depth))
    for idx, (lo, hi, profiles) in enumerate(FLOOR_PROFILE_BANDS):
        if lo <= depth <= hi:
            return idx, BgmFloorBand(lo, hi, profiles)
    lo, hi, profiles = FLOOR_PROFILE_BANDS[-1]
    return len(FLOOR_PROFILE_BANDS) - 1, BgmFloorBand(lo, hi, profiles)


def floor_profile_candidates(depth: int) -> tuple[BgmFloorProfile, ...]:
    return floor_band(depth)[1].profiles


def floor_profile(depth: int) -> BgmFloorProfile:
    return floor_profile_candidates(depth)[0]


def danger_state(hp: int, max_hp: int, hunger_state: str) -> int:
    ratio = 1.0 if max_hp <= 0 else hp / max_hp
    hunger = {"normal": 0, "hungry": 1, "weak": 2, "faint": 3}.get(hunger_state, 0)
    if ratio > 0.5:
        return min(3, hunger)
    if ratio >= 0.25:
        return (1, 1, 2, 3)[hunger]
    return (2, 2, 3, 3)[hunger]


def exploration_params(depth: int, hp: int, max_hp: int, hunger_state: str, profile: BgmFloorProfile | None = None) -> dict:
    profile = profile or floor_profile(depth)
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
        self.profile_rng = random.Random(self._seed_for(("floor-profile",)))
        self.band_profiles = {}
        self.last_band_id = None
        self.last_band_profile = None
        self.cache = {}
        self.current_key = None
        self.last_exploration_params = None

    def play_exploration(self, *, depth: int, hp: int, max_hp: int, hunger_state: str, enabled: bool) -> None:
        if not enabled:
            self.stop()
            return
        depth_key = max(1, int(depth))
        profile = self._profile_for_depth(depth_key)
        params = exploration_params(depth, hp, max_hp, hunger_state, profile=profile)
        self.last_exploration_params = dict(params)
        self._play_key(("explore", depth_key, self._params_key(params)), params)

    def _profile_for_depth(self, depth: int) -> BgmFloorProfile:
        band_id, band = floor_band(depth)
        profile = self.band_profiles.get(band_id)
        if profile is None:
            candidates = band.profiles
            if self.last_band_profile in candidates and len(candidates) > 1:
                candidates = tuple(profile for profile in candidates if profile != self.last_band_profile)
            profile = candidates[self.profile_rng.randrange(len(candidates))]
            self.band_profiles[band_id] = profile
        self.last_band_id = band_id
        self.last_band_profile = profile
        return profile

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
