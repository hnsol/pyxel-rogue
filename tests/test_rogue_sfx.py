import unittest
from pathlib import Path


class FakeSound:
    def __init__(self, notes="", tones="", volumes="", effects="", speed=0):
        self.notes = notes
        self.tones = tones
        self.volumes = volumes
        self.effects = effects
        self.speed = speed
        self.set_calls = []

    def set(self, notes, tones, volumes, effects, speed):
        self.set_calls.append((notes, tones, volumes, effects, speed))
        self.notes = notes
        self.tones = tones
        self.volumes = volumes
        self.effects = effects
        self.speed = speed


class FakePyxel:
    def __init__(self):
        self.play_calls = []
        self.load_calls = []
        self.sounds = [FakeSound() for _ in range(64)]
        self._play_pos = None

    def play(self, *args, **kwargs):
        self.play_calls.append((args, kwargs))

    def play_pos(self, ch):
        return self._play_pos

    def load(self, *args, **kwargs):
        self.load_calls.append((args, kwargs))


class FakeBgm:
    def __init__(self):
        self.resume_calls = []
        self.stop_calls = 0

    def resume_ch(self, ch):
        self.resume_calls.append(ch)

    def stop(self):
        self.stop_calls += 1


class TestSfxController(unittest.TestCase):
    def test_request_plays_highest_priority_sound_on_update(self):
        from pyxel_rogue.rogue_sfx import SFX_CH, SFX_HEAL_LARGE, SFX_TRAP, SfxController

        px = FakePyxel()
        ctrl = SfxController(px)
        ctrl.request(SFX_TRAP)
        ctrl.request(SFX_HEAL_LARGE)

        ctrl.update()

        self.assertEqual(px.play_calls, [((SFX_CH, SFX_HEAL_LARGE), {})])

    def test_update_resumes_bgm_after_active_sound_finishes(self):
        from pyxel_rogue.rogue_sfx import SFX_CH, SFX_TRAP, SfxController

        px = FakePyxel()
        bgm = FakeBgm()
        ctrl = SfxController(px, bgm)
        ctrl.request(SFX_TRAP)
        ctrl.update()
        px._play_pos = None

        ctrl.update()

        self.assertEqual(bgm.resume_calls, [SFX_CH])
        self.assertFalse(ctrl.is_active())

    def test_update_does_not_resume_bgm_while_sound_is_playing(self):
        from pyxel_rogue.rogue_sfx import SFX_TRAP, SfxController

        px = FakePyxel()
        bgm = FakeBgm()
        ctrl = SfxController(px, bgm)
        ctrl.request(SFX_TRAP)
        ctrl.update()
        px._play_pos = (22, 3)

        ctrl.update()

        self.assertEqual(bgm.resume_calls, [])
        self.assertTrue(ctrl.is_active())

    def test_disabled_controller_ignores_requests(self):
        from pyxel_rogue.rogue_sfx import SFX_TRAP, SfxController

        px = FakePyxel()
        ctrl = SfxController(px, enabled=False)

        ctrl.request(SFX_TRAP)
        ctrl.update()

        self.assertEqual(px.play_calls, [])

    def test_play_immediate_stops_bgm_and_starts_sound_now(self):
        from pyxel_rogue.rogue_sfx import SFX_CH, SFX_STAIRS, SfxController

        px = FakePyxel()
        bgm = FakeBgm()
        ctrl = SfxController(px, bgm)

        ctrl.play_immediate(SFX_STAIRS, stop_bgm=True)

        self.assertEqual(bgm.stop_calls, 1)
        self.assertEqual(px.play_calls, [((SFX_CH, SFX_STAIRS), {})])
        self.assertTrue(ctrl.is_active())

    def test_play_death_stops_bgm_and_plays_three_step_sequence(self):
        from pyxel_rogue.rogue_sfx import DEATH_SFX_SEQUENCE, SFX_CH, SfxController

        px = FakePyxel()
        bgm = FakeBgm()
        ctrl = SfxController(px, bgm)

        ctrl.play_death()

        self.assertEqual(bgm.stop_calls, 1)
        self.assertEqual(px.play_calls, [((SFX_CH, list(DEATH_SFX_SEQUENCE)), {})])
        self.assertTrue(ctrl.is_active())

    def test_random_hit_uses_se14_se16_se17_without_game_rng(self):
        from pyxel_rogue.rogue_sfx import HIT_SFX, SFX_CH, SfxController

        class FakeRng:
            def __init__(self):
                self.values = [0, 2]
                self.limits = []

            def randrange(self, limit):
                self.limits.append(limit)
                return self.values.pop(0)

        rng = FakeRng()
        px = FakePyxel()
        ctrl = SfxController(px, rng=rng)

        ctrl.request_random_hit()
        ctrl.update()
        px._play_pos = None
        ctrl.update()
        ctrl.request_random_hit()
        ctrl.update()

        self.assertEqual(px.play_calls, [((SFX_CH, HIT_SFX[0]), {}), ((SFX_CH, HIT_SFX[2]), {})])
        self.assertEqual(rng.limits, [len(HIT_SFX), len(HIT_SFX)])

    def test_sound_constants_match_rpg_sepack_numbers(self):
        from pyxel_rogue import rogue_sfx

        self.assertEqual(rogue_sfx.SFX_SELECT_LOW, 4)
        self.assertEqual(rogue_sfx.SFX_SELECT_HIGH, 5)
        self.assertEqual(rogue_sfx.SFX_HIT_MISS, 36)
        self.assertEqual(rogue_sfx.SFX_PICKUP, 6)
        self.assertEqual(rogue_sfx.SFX_STAIRS, 8)
        self.assertEqual(rogue_sfx.SFX_SECRET_DOOR, 32)
        self.assertEqual(rogue_sfx.HIT_SFX, (14, 16, 17))
        self.assertEqual(rogue_sfx.SFX_DEATH, 18)
        self.assertEqual(rogue_sfx.DEATH_SFX_SEQUENCE, (18, 34, 35))
        self.assertEqual(rogue_sfx.SFX_THROW, 19)
        self.assertEqual(rogue_sfx.SFX_THROW_HIT, 20)

    def test_miss_sound_uses_short_present_churun_phrase(self):
        from pyxel_rogue.rogue_sfx import build_miss_sound

        px = FakePyxel()
        px.sounds[7] = FakeSound([40, 28, 40, 28, 40, 28, 40, 28, 40, 28, 40, 28, 40, 28, 40, 28], [2], [], [3], 1)
        px.sounds[36] = FakeSound([], [], [], [], 0)

        build_miss_sound(px)

        self.assertEqual(px.sounds[36].notes, [28, 25, 27, 25, 49, 52, 52, 49])
        self.assertEqual(px.sounds[36].tones, [2, 3, 3, 3, 2, 2, 2, 2])
        self.assertEqual(px.sounds[36].volumes, [7, 7, 7, 6, 5, 5, 4, 4])
        self.assertEqual(px.sounds[36].effects, [1])
        self.assertEqual(px.sounds[36].speed, 1)

    def test_death_echo_sounds_copy_se18_with_lower_volumes(self):
        from pyxel_rogue.rogue_sfx import build_death_echo_sounds

        px = FakePyxel()
        px.sounds[18] = FakeSound("cde", "nnn", "765", "fff", 4)

        build_death_echo_sounds(px)

        self.assertEqual(px.sounds[34].set_calls, [("cde", "nnn", "543", "fff", 4)])
        self.assertEqual(px.sounds[35].set_calls, [("cde", "nnn", "222", "fff", 4)])

    def test_copy_sound_uses_pyxel_set_api(self):
        from pyxel_rogue.rogue_sfx import copy_sound

        src = FakeSound("cde", "sqp", "765", "nff", 7)
        dst = FakeSound()

        copy_sound(src, dst)

        self.assertEqual(dst.set_calls, [("cde", "sqp", "765", "nff", 7)])

    def test_copy_sound_copies_pyxel_list_fields_without_set_strings(self):
        from pyxel_rogue.rogue_sfx import copy_sound

        src = FakeSound([1, 2], [3, 4], [5, 6], [0, 1], 9)
        dst = FakeSound([], [], [], [], 0)

        copy_sound(src, dst)

        self.assertEqual(dst.notes, [1, 2])
        self.assertEqual(dst.tones, [3, 4])
        self.assertEqual(dst.volumes, [5, 6])
        self.assertEqual(dst.effects, [0, 1])
        self.assertEqual(dst.speed, 9)
        self.assertEqual(dst.set_calls, [])

    def test_load_se_pack_keeps_upstream_sound_numbers(self):
        from pyxel_rogue.rogue_sfx import load_se_pack

        px = FakePyxel()

        self.assertTrue(load_se_pack(px, "assets/rpg-sepack.pyxres"))

        self.assertEqual(
            px.load_calls,
            [(("assets/rpg-sepack.pyxres",), {"exclude_images": True, "exclude_tilemaps": True, "exclude_musics": True})],
        )
        self.assertEqual(px.sounds[8].set_calls, [])


class TestRogueSfxCallSites(unittest.TestCase):
    def test_gameplay_and_ui_events_request_sfx(self):
        source = Path("rogue.py").read_text(encoding="utf-8")
        expected = [
            "self.request_hit_sfx()",
            "self.request_sfx(rogue_sfx.SFX_HIT_MISS)",
            "self.request_sfx(rogue_sfx.SFX_THROW)",
            "self.request_sfx(rogue_sfx.SFX_THROW_HIT)",
            "self.request_sfx(rogue_sfx.SFX_HEAL_LARGE)",
            "self.play_sfx_immediate(rogue_sfx.SFX_STAIRS, stop_bgm=True)",
            "self.request_sfx(rogue_sfx.SFX_WARP)",
            "self.request_sfx(rogue_sfx.SFX_PICKUP)",
            "self.request_sfx(rogue_sfx.SFX_SECRET_DOOR)",
            "self.play_death_sfx()",
            "self.msg_bad(",
            "self.request_sfx(rogue_sfx.SFX_SPELL_USE)",
            "self.request_sfx(rogue_sfx.SFX_HEAL_SMALL)",
            "self.request_sfx(rogue_sfx.SFX_WAND_ZAP)",
            "self.request_sfx(rogue_sfx.SFX_ELECTRIC)",
            "self.request_sfx(rogue_sfx.SFX_ICE)",
            "self.request_sfx(rogue_sfx.SFX_SELECT_LOW)",
            "self.request_sfx(rogue_sfx.SFX_SELECT_HIGH)",
            "self.request_sfx(rogue_sfx.SFX_ERROR)",
        ]
        missing = [text for text in expected if text not in source]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
