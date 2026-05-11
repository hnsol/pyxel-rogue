import importlib
import unittest


class FakeBackend:
    def __init__(self):
        self.randrange_calls = []
        self.randrange_values = [2, 0, 3]

    def randrange(self, n):
        self.randrange_calls.append(n)
        return self.randrange_values.pop(0)

    def randint(self, a, b):
        return a + b

    def random(self):
        return 0.25

    def choice(self, seq):
        return seq[-1]

    def shuffle(self, seq):
        seq.reverse()

    def sample(self, seq, k):
        return list(seq)[:k]


class RogueRngTest(unittest.TestCase):
    def test_module_imports_without_pyxel(self):
        module = importlib.import_module("pyxel_rogue.rogue_rng")
        self.assertTrue(hasattr(module, "RogueRng"))

    def test_rnd_matches_rogue_range_contract(self):
        from pyxel_rogue.rogue_rng import RogueRng

        backend = FakeBackend()
        rng = RogueRng(backend)

        self.assertEqual(rng.rnd(0), 0)
        self.assertEqual(rng.rnd(-1), 0)
        self.assertEqual(rng.rnd(5), 2)
        self.assertEqual(backend.randrange_calls, [5])

    def test_roll_uses_rnd_plus_one_for_each_die(self):
        from pyxel_rogue.rogue_rng import RogueRng

        backend = FakeBackend()
        rng = RogueRng(backend)

        self.assertEqual(rng.roll(2, 6), 4)
        self.assertEqual(backend.randrange_calls, [6, 6])

    def test_compatibility_wrappers_delegate_to_backend(self):
        from pyxel_rogue.rogue_rng import RogueRng

        backend = FakeBackend()
        rng = RogueRng(backend)
        values = [1, 2, 3]

        self.assertEqual(rng.randint(2, 5), 7)
        self.assertEqual(rng.random(), 0.25)
        self.assertEqual(rng.choice(values), 3)
        self.assertEqual(rng.sample(values, 2), [1, 2])
        rng.shuffle(values)
        self.assertEqual(values, [3, 2, 1])


if __name__ == "__main__":
    unittest.main()
