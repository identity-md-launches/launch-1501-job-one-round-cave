#!/usr/bin/env python3
"""Behavior checks for destination planning; fixtures stay in test/scratch."""

import json
from pathlib import Path
import shutil
import unittest
from unittest.mock import patch

import landing


ROOT = Path("test/scratch/line2-landing-tests")
DESTINATION = str(ROOT / "received")


class LandingTests(unittest.TestCase):
    def setUp(self):
        if ROOT.exists():
            shutil.rmtree(ROOT)
        ROOT.mkdir(parents=True)
        self.receipt = landing.INSPECT.inspect_path("line-2/handoff.zip")

    def tearDown(self):
        shutil.rmtree(ROOT)

    def test_real_archive_on_new_destination(self):
        result = landing.plan("line-2/handoff.zip", DESTINATION)
        self.assertTrue(result["ready"])
        self.assertEqual(result["file_count"], 2)
        self.assertEqual(result["path_issues"], [])
        self.assertEqual(landing.main(["check", "line-2/handoff.zip", DESTINATION]), 0)

    def test_occupied_file_and_directory(self):
        target = ROOT / "received"
        target.mkdir()
        (target / "README.md").write_text("public fixture")
        (target / "handoff.py").mkdir()
        result = landing.plan_receipt(self.receipt, DESTINATION)
        self.assertFalse(result["ready"])
        self.assertEqual({issue["kind"] for issue in result["path_issues"]},
                         {"existing-file", "directory-at-file"})

    def test_symlink_and_file_ancestors(self):
        (ROOT / "received").symlink_to("elsewhere")
        result = landing.plan_receipt(self.receipt, DESTINATION)
        self.assertEqual({issue["kind"] for issue in result["path_issues"]},
                         {"symlink-at-leaf"})
        (ROOT / "received").unlink()
        (ROOT / "received").write_text("public fixture")
        result = landing.plan_receipt(self.receipt, DESTINATION)
        self.assertEqual({issue["kind"] for issue in result["path_issues"]},
                         {"file-at-leaf"})

    def test_nested_file_as_directory(self):
        target = ROOT / "received"
        target.mkdir()
        (target / "nested").write_text("public fixture")
        receipt = dict(self.receipt)
        receipt["files"] = [{"path": "nested/tool.py"}]
        result = landing.plan_receipt(receipt, DESTINATION)
        self.assertEqual(result["path_issues"][0]["kind"], "file-ancestor")

    def test_internal_collision_and_portability(self):
        receipt = dict(self.receipt)
        receipt["files"] = [{"path": "a"}, {"path": "a/b"},
                            {"path": "CON"}]
        result = landing.plan_receipt(receipt, DESTINATION)
        self.assertFalse(result["ready"])
        self.assertIn("archive-file-as-directory",
                      {issue["kind"] for issue in result["path_issues"]})
        self.assertIn("windows-device-name",
                      {issue["code"] for issue in result["portability_issues"]})

    def test_bad_archive_or_destination_has_no_report(self):
        bad = ROOT / "bad.zip"
        bad.write_bytes(Path("line-2/handoff.zip").read_bytes() + b"bad")
        with self.assertRaises(ValueError):
            landing.plan(str(bad), DESTINATION)
        for value in ("../outside", "/tmp/outside", "a/../b", "a//b", "a\\b", ""):
            with self.assertRaises(ValueError, msg=value):
                landing.destination_parts(value)

    def test_demo_is_read_only(self):
        result = landing.demo()
        self.assertTrue(result["fresh"]["ready"])
        self.assertFalse(result["occupied"]["ready"])
        self.assertFalse(Path("line-2/tools/handoff-landing/unpacked-demo").exists())

    def test_real_archive_case_alias_blocks_cli(self):
        target = ROOT / "received"
        target.mkdir()
        (target / "readme.MD").write_text("public fixture; not read")
        result = landing.plan("line-2/handoff.zip", DESTINATION)
        self.assertFalse(result["ready"])
        self.assertEqual(result["path_issues"], [{
            "path": "README.md", "kind": "existing-name-collision",
            "blocking_path": str(target / "readme.MD")}])
        self.assertEqual(landing.main(["check", "line-2/handoff.zip", DESTINATION]), 2)

    def test_unicode_and_trailing_aliases(self):
        target = ROOT / "received"
        target.mkdir()
        for existing, proposed in (("cafe\u0301.txt", "caf\u00e9.txt"),
                                   ("STRASSE", "Stra\u00dfe"),
                                   ("report. ", "report")):
            path = target / existing
            path.write_text("public fixture")
            receipt = dict(self.receipt, files=[{"path": proposed}])
            result = landing.plan_receipt(receipt, DESTINATION)
            self.assertEqual(result["path_issues"][0]["kind"], "existing-name-collision")
            path.unlink()

    def test_exact_name_does_not_hide_alias(self):
        target = ROOT / "received"
        target.mkdir()
        (target / "README.md").write_text("fixture")
        (target / "readme.md").write_text("other fixture")
        result = landing.plan_receipt(self.receipt, DESTINATION)
        self.assertEqual(result["path_issues"][0]["kind"], "existing-name-collision")

    def test_alias_ancestor_is_not_traversed(self):
        target = ROOT / "Received"
        target.symlink_to("not-a-real-directory")
        result = landing.plan_receipt(self.receipt, DESTINATION)
        self.assertFalse(result["ready"])
        self.assertTrue(all(i["kind"] == "existing-name-collision"
                            for i in result["path_issues"]))
        # Exact symlinks retain the inherited refusal; no name scan below them.
        result = landing.plan_receipt(self.receipt, str(target))
        self.assertTrue(all(i["kind"] == "symlink-at-leaf"
                            for i in result["path_issues"]))

    def test_nested_alias(self):
        target = ROOT / "received"
        target.mkdir()
        (target / "Dir").mkdir()
        receipt = dict(self.receipt, files=[{"path": "dir/tool.py"}])
        result = landing.plan_receipt(receipt, DESTINATION)
        self.assertEqual(result["path_issues"][0]["blocking_path"], str(target / "Dir"))

    def test_scans_are_cached_and_do_not_read_contents(self):
        target = ROOT / "received"
        target.mkdir()
        (target / "unrelated").write_text("never read")
        with patch("builtins.open", side_effect=AssertionError("content read")), \
                patch.object(Path, "read_bytes", side_effect=AssertionError("content read")):
            screen = landing.NameScreen()
            names = screen.names(str(target).split("/"))
            self.assertIn("unrelated", names)
            self.assertIs(screen.names(str(target).split("/")), names)
            self.assertEqual(screen.names_scanned, 1)
            self.assertTrue(landing.plan_receipt(self.receipt, DESTINATION)["ready"])

    def test_scan_limits_fail_closed(self):
        target = ROOT / "received"
        target.mkdir()
        for name in ("a", "b", "c"):
            (target / name).write_text("fixture")
        screen = landing.NameScreen(max_directory_names=2)
        with self.assertRaisesRegex(ValueError, "exceeds limit"):
            screen.names(str(target).split("/"))
        screen = landing.NameScreen(max_names=2)
        with self.assertRaisesRegex(ValueError, "exceeds limit"):
            screen.names(str(target).split("/"))
        with self.assertRaisesRegex(ValueError, "exceeds limit"):
            landing.plan_receipt(self.receipt, DESTINATION, max_names=1)
        for limits in ((0, 1), (1, -1), (True, 1)):
            with self.assertRaises(ValueError):
                landing.NameScreen(*limits)

    def test_scan_refuses_symlink_parent(self):
        (ROOT / "received").symlink_to("another-directory")
        with self.assertRaises(OSError):
            landing.NameScreen().names(DESTINATION.split("/"))

    def test_unsupported_safe_scan_fails_closed(self):
        with patch.object(landing.os, "supports_dir_fd", set()):
            with self.assertRaisesRegex(ValueError, "unsupported"):
                landing.plan_receipt(self.receipt, DESTINATION)

    def test_public_receipt_api_refuses_unsafe_names_before_open(self):
        with patch.object(landing.os, "open", side_effect=AssertionError("opened")):
            for name in ("../outside", "/outside", "dir/../../outside", "a\\b"):
                with self.assertRaises(ValueError):
                    landing.plan_receipt(dict(self.receipt, files=[{"path": name}]), DESTINATION)
            with self.assertRaises(ValueError):
                landing.NameScreen().names([".."])


if __name__ == "__main__":
    unittest.main()
