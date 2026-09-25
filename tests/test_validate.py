"""Tests for tools/validate.py. Run: python -m unittest discover -s tests"""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import validate  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "valid_run.json"
NAME = "vendor--model-name__0a1b2c3d__p1__standard__s1001.json"


def entry() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


class CheckEntryTest(unittest.TestCase):
    def test_valid_entry_passes(self) -> None:
        self.assertEqual(validate.check_entry(entry(), NAME, True), [])

    def test_whole_number_written_as_float_passes(self) -> None:
        e = entry()
        e["seed"] = 1001.0
        self.assertEqual(validate.check_entry(e, NAME, True), [])

    def test_missing_key_is_rejected(self) -> None:
        e = entry()
        del e["commands"]
        self.assertIn("missing key `commands`", validate.check_entry(e, NAME, True))

    def test_bool_as_whole_number_is_rejected(self) -> None:
        e = entry()
        e["calls"] = True
        self.assertTrue(validate.check_entry(e, NAME, True))

    def test_wrong_file_name_is_rejected(self) -> None:
        problems = validate.check_entry(entry(), "other.json", True)
        self.assertTrue(any("file name must be" in p for p in problems))

    def test_bot_row_in_pull_request_is_rejected(self) -> None:
        e = entry()
        e["model"] = "bot:greedy"
        e["backend"] = "bot"
        name = validate.expected_name(e)
        self.assertTrue(validate.check_entry(e, name, True))
        self.assertEqual(validate.check_entry(e, name, False), [])

    def test_commands_out_of_order_are_rejected(self) -> None:
        e = entry()
        e["commands"] = [{"type": "a", "day": 5}, {"type": "b", "day": 3}]
        self.assertTrue(validate.check_entry(e, NAME, True))

    def test_command_after_the_end_is_rejected(self) -> None:
        e = entry()
        e["commands"].append({"type": "late", "day": 9999})
        self.assertTrue(validate.check_entry(e, NAME, True))

    def test_score_above_hundred_is_rejected(self) -> None:
        e = entry()
        e["score"] = 101
        self.assertTrue(validate.check_entry(e, NAME, True))

    def test_non_object_is_rejected(self) -> None:
        self.assertEqual(validate.check_entry([], NAME, True), ["the file is not a JSON object"])


class SlugTest(unittest.TestCase):
    def test_slug_follows_the_spec(self) -> None:
        self.assertEqual(validate.slug("Vendor/Model Name:free"), "vendor--model-name-free")


class ChangedPathsTest(unittest.TestCase):
    def _changes(self, text: str) -> tuple[list[str], list[str]]:
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write(text)
        return validate.changed_paths(Path(f.name))

    def test_added_run_is_accepted(self) -> None:
        paths, problems = self._changes("A\truns/%s\n" % NAME)
        self.assertEqual((paths, problems), (["runs/%s" % NAME], []))

    def test_touching_the_leaderboard_is_rejected(self) -> None:
        _, problems = self._changes("M\tleaderboard.json\n")
        self.assertTrue(problems)

    def test_touching_verified_is_rejected(self) -> None:
        _, problems = self._changes("A\tverified/x.json\n")
        self.assertTrue(problems)

    def test_deleting_a_run_is_rejected(self) -> None:
        _, problems = self._changes("D\truns/%s\n" % NAME)
        self.assertTrue(problems)

    def test_too_many_runs_are_rejected(self) -> None:
        lines = "".join("A\truns/r%d.json\n" % i for i in range(validate.MAX_FILES_PER_PR + 1))
        _, problems = self._changes(lines)
        self.assertTrue(any("at most" in p for p in problems))


class CheckFileTest(unittest.TestCase):
    def test_oversized_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / NAME
            path.write_bytes(b" " * (validate.MAX_BYTES + 1))
            self.assertTrue(validate.check_file(path, True))

    def test_broken_json_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / NAME
            path.write_text("{", encoding="utf-8")
            self.assertTrue(validate.check_file(path, True))

    def test_fixture_file_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / NAME
            path.write_text(json.dumps(copy.deepcopy(entry())), encoding="utf-8")
            self.assertEqual(validate.check_file(path, True), [])


if __name__ == "__main__":
    unittest.main()
