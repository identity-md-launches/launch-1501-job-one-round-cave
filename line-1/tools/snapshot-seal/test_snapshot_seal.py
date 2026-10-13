#!/usr/bin/env python3
"""Offline regression checks for snapshot-seal."""
import importlib.util
import json
from pathlib import Path
import tempfile
import os
from unittest import mock
import unittest

SOURCE = Path(__file__).with_name('snapshot_seal.py')
spec = importlib.util.spec_from_file_location('snapshot_seal', SOURCE)
seal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seal)
SCRATCH = Path(__file__).resolve().parents[3] / 'test' / 'scratch' / 'snapshot-seal'
SCRATCH.mkdir(parents=True, exist_ok=True)


def temporary_directory():
    return tempfile.TemporaryDirectory(dir=SCRATCH)


EXAMPLE = Path(__file__).parents[1] / 'pinned-snapshot' / 'example-zto.json'


class SnapshotSealTests(unittest.TestCase):
    def write(self, directory, name, value):
        path = Path(directory) / name
        path.write_text(json.dumps(value, indent=2) + '\n')
        return path

    def test_seal_is_deterministic_and_has_pinned_facts(self):
        first = seal.seal(EXAMPLE)
        self.assertEqual(first, seal.seal(EXAMPLE))
        self.assertEqual(first['schema'], 'pinned-zto-seal/1')
        self.assertEqual(first['observation']['token'], seal.pinned.ZTO)
        self.assertEqual(first['observation']['block_number'], '26177368')

    def test_verify_accepts_exact_receipt(self):
        with temporary_directory() as directory:
            receipt = self.write(directory, 'receipt.json', seal.seal(EXAMPLE))
            self.assertTrue(seal.verify(EXAMPLE, receipt)['verified'])

    def test_verify_rejects_changed_receipt(self):
        with temporary_directory() as directory:
            receipt = seal.seal(EXAMPLE)
            receipt['observation']['block_number'] = '0'
            receipt_path = self.write(directory, 'receipt.json', receipt)
            with self.assertRaises(ValueError):
                seal.verify(EXAMPLE, receipt_path)

    def test_rejects_non_pinned_snapshot(self):
        with temporary_directory() as directory:
            snapshot = self.write(directory, 'not-pinned.json', {'schema': 'nope'})
            with self.assertRaises(ValueError):
                seal.seal(snapshot)

    def test_rejects_malformed_receipt_json(self):
        with temporary_directory() as directory:
            receipt = Path(directory) / 'receipt.json'
            receipt.write_text('{')
            with self.assertRaises(ValueError):
                seal.verify(EXAMPLE, receipt)


    def test_rejects_duplicate_result_even_when_last_value_is_valid(self):
        raw = EXAMPLE.read_bytes()
        value = json.loads(raw)['result']
        ambiguous = raw.replace(b'"result":', b'"result": "conflict", "result":', 1)
        self.assertEqual(json.loads(ambiguous)['result'], value)
        with temporary_directory() as directory:
            path = Path(directory) / 'ambiguous.json'
            path.write_bytes(ambiguous)
            with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
                seal.seal(path)

    def test_rejects_duplicate_nested_keys(self):
        with temporary_directory() as directory:
            path = Path(directory) / 'nested.json'
            path.write_bytes(b'{"block":{"hash":"a","hash":"b"}}')
            with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
                seal.seal(path)

    def test_rejects_duplicate_receipt_keys(self):
        receipt = seal.seal(EXAMPLE)
        raw = json.dumps(receipt).replace('"schema":', '"schema":"conflict","schema":', 1)
        with temporary_directory() as directory:
            path = Path(directory) / 'receipt.json'
            path.write_text(raw)
            with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
                seal.verify(EXAMPLE, path)

    def test_refuses_outside_before_any_open(self):
        # No outside file is created, opened or read by this check.
        with mock.patch.object(seal.os, 'open', side_effect=AssertionError('opened')):
            with self.assertRaisesRegex(ValueError, 'inside this workspace'):
                seal.read_bytes(seal.WORKSPACE.parent / 'never-open-this')

    def test_refuses_traversal_before_any_open(self):
        with mock.patch.object(seal.os, 'open', side_effect=AssertionError('opened')):
            with self.assertRaises(ValueError):
                seal.read_bytes(seal.WORKSPACE / '..' / 'never-open-this')

    def test_refuses_leaf_symlink_before_opening_leaf(self):
        with temporary_directory() as directory:
            path = Path(directory) / 'link.json'
            path.symlink_to(EXAMPLE)
            original = seal.os.open
            def guarded(name, flags, **kwargs):
                if name == 'link.json':
                    self.fail('symlink leaf opened')
                return original(name, flags, **kwargs)
            with mock.patch.object(seal.os, 'open', side_effect=guarded):
                with self.assertRaises(ValueError):
                    seal.read_bytes(path)

    def test_refuses_symlink_directory(self):
        with temporary_directory() as directory:
            path = Path(directory) / 'alias'
            path.symlink_to(EXAMPLE.parent, target_is_directory=True)
            with self.assertRaises(OSError):
                seal.read_bytes(path / EXAMPLE.name)

    def test_refuses_oversize_before_opening_leaf(self):
        with temporary_directory() as directory:
            path = Path(directory) / 'large.json'
            with path.open('wb') as stream:
                stream.truncate(seal.MAX_BYTES + 1)
            original = seal.os.open
            def guarded(name, flags, **kwargs):
                if name == 'large.json':
                    self.fail('oversize leaf opened')
                return original(name, flags, **kwargs)
            with mock.patch.object(seal.os, 'open', side_effect=guarded):
                with self.assertRaises(ValueError):
                    seal.read_bytes(path)

    def test_refuses_fifo_without_opening_it(self):
        with temporary_directory() as directory:
            path = Path(directory) / 'pipe'
            os.mkfifo(path)
            with self.assertRaises(ValueError):
                seal.read_bytes(path)

    def test_boundary_and_bounded_read(self):
        with temporary_directory() as directory:
            path = Path(directory) / 'boundary'
            path.write_bytes(b'x' * 64)
            with mock.patch.object(seal, 'MAX_BYTES', 64):
                self.assertEqual(len(seal.read_bytes(path)), 64)
                path.write_bytes(b'x' * 65)
                with self.assertRaises(ValueError):
                    seal.read_bytes(path)

    def test_nonfinite_json_rejected(self):
        with temporary_directory() as directory:
            path = Path(directory) / 'nonfinite.json'
            for raw in ('{"a":NaN}', '{"a":Infinity}', '{"a":1e9999}'):
                path.write_text(raw)
                with self.assertRaises(ValueError):
                    seal.seal(path)

    def test_whitespace_changes_exact_digest_only(self):
        with temporary_directory() as directory:
            path = self.write(directory, 'reformatted.json', json.loads(EXAMPLE.read_bytes()))
            path.write_bytes(path.read_bytes() + b' \n')
            original, reformatted = seal.seal(EXAMPLE), seal.seal(path)
            self.assertNotEqual(original['snapshot_sha256'], reformatted['snapshot_sha256'])
            self.assertEqual(original['canonical_snapshot_sha256'], reformatted['canonical_snapshot_sha256'])


if __name__ == '__main__':
    unittest.main()
