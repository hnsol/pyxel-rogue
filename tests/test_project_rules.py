import os
import tempfile
import textwrap
import unittest

from tools import check_project_rules


ROOT = os.path.dirname(os.path.dirname(__file__))


class ProjectRulesTest(unittest.TestCase):
    def test_current_repo_rules_pass(self):
        issues = check_project_rules.check_project(ROOT)
        self.assertEqual([], [issue.format() for issue in issues])

    def test_current_message_manifest_is_complete(self):
        issues = check_project_rules.check_project(ROOT, strict_manifest=True)
        self.assertEqual([], [issue.format() for issue in issues])

    def test_root_rogue_helper_modules_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            open(os.path.join(tmp, "rogue_extra.py"), "w", encoding="utf-8").close()

            issues = check_project_rules.check_root_modules(tmp)

        self.assertEqual(["root-module: rogue_extra.py"], [issue.format() for issue in issues])

    def test_nested_term_keys_must_match_between_languages(self):
        en = {"item": {"weapon": {"mace": "mace"}}}
        ja = {"item": {"weapon": {}}}

        issues = check_project_rules.check_nested_keys("terms", en, ja)

        self.assertEqual(["terms: missing ja key item.weapon.mace"], [issue.format() for issue in issues])

    def test_unused_top_level_function_candidates_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "sample.py")
            with open(path, "w", encoding="utf-8") as f:
                f.write(textwrap.dedent(
                    """
                    def used():
                        return 1

                    def unused():
                        return 2

                    value = used()
                    """
                ))

            issues = check_project_rules.find_unused_symbol_candidates(tmp)

        self.assertEqual(["unused-candidate: sample.py:5 function unused"], [issue.format() for issue in issues])

    def test_module_attribute_function_references_are_counted(self):
        with tempfile.TemporaryDirectory() as tmp:
            sample_path = os.path.join(tmp, "sample.py")
            caller_path = os.path.join(tmp, "caller.py")
            with open(sample_path, "w", encoding="utf-8") as f:
                f.write(textwrap.dedent(
                    """
                    def used():
                        return 1
                    """
                ))
            with open(caller_path, "w", encoding="utf-8") as f:
                f.write(textwrap.dedent(
                    """
                    import sample
                    value = sample.used()
                    """
                ))

            issues = check_project_rules.find_unused_symbol_candidates(tmp)

        self.assertEqual([], [issue.format() for issue in issues])

    def test_test_references_are_counted_for_unused_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.mkdir(os.path.join(tmp, "tests"))
            sample_path = os.path.join(tmp, "sample.py")
            test_path = os.path.join(tmp, "tests", "test_sample.py")
            with open(sample_path, "w", encoding="utf-8") as f:
                f.write(textwrap.dedent(
                    """
                    def used_by_test():
                        return 1
                    """
                ))
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(textwrap.dedent(
                    """
                    import sample
                    assert sample.used_by_test() == 1
                    """
                ))

            issues = check_project_rules.find_unused_symbol_candidates(tmp)

        self.assertEqual([], [issue.format() for issue in issues])

    def test_wrapper_comparison_tests_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.mkdir(os.path.join(tmp, "tests"))
            test_path = os.path.join(tmp, "tests", "test_extracted.py")
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(textwrap.dedent(
                    """
                    import unittest

                    from tests.test_rogue_baseline import rogue
                    from pyxel_rogue import rogue_hud

                    class ExtractedTest(unittest.TestCase):
                        def test_hud_module_matches_game_wrappers(self):
                            self.assertEqual(rogue_hud.hud_weapon_bonus(item), rogue.hud_weapon_bonus(item))
                    """
                ))

            issues = check_project_rules.check_wrapper_comparison_tests(tmp)

        self.assertEqual(
            [
                "wrapper-test: tests/test_extracted.py:9 compare extracted module to rogue.py wrapper via assertEqual"
            ],
            [issue.format() for issue in issues],
        )


if __name__ == "__main__":
    unittest.main()
