import os
import tempfile
import unittest


class RogueSaveTest(unittest.TestCase):
    def test_save_file_is_obfuscated_and_round_trips(self):
        from pyxel_rogue import rogue_save

        data = {"version": 1, "player": {"hp": 9, "name": "guest"}}
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "rogue.sav")
            rogue_save.save(data, path=path)

            with open(path, encoding="ascii") as f:
                raw = f.read()
            self.assertNotIn('"player"', raw)
            self.assertNotIn("guest", raw)
            self.assertTrue(rogue_save.exists(path=path))
            self.assertEqual(rogue_save.load(path=path), data)

            rogue_save.delete(path=path)
            self.assertFalse(rogue_save.exists(path=path))

    def test_corrupt_save_data_is_not_deleted_by_failed_load(self):
        from pyxel_rogue import rogue_save

        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "rogue.sav")
            with open(path, "w", encoding="ascii") as f:
                f.write("not a save")

            with self.assertRaises(rogue_save.SaveError):
                rogue_save.load(path=path)
            self.assertTrue(rogue_save.exists(path=path))


if __name__ == "__main__":
    unittest.main()
