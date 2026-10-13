"""Receiver tests for preserved sources, false reports, bounds and portability."""
import copy
import hashlib
import io
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import stitch_handoff as kit

LEFT = (kit.HERE / 'examples/left.json').read_bytes()
RIGHT = (kit.HERE / 'examples/right.json').read_bytes()


def payloads(data):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        return {p: archive.read(p) for p in archive.namelist() if p != 'HANDOFF.json'}


class Tests(unittest.TestCase):
    def test_exact_sources_recomputed_deterministic_offline(self):
        with patch.object(kit.stitch.window, 'rpc', side_effect=AssertionError('network')):
            data = kit.build(LEFT, RIGHT)
            self.assertEqual(data, kit.build(LEFT, RIGHT))
            result = kit.inspect_bytes(data)
        self.assertEqual(payloads(data)[kit.LEFT], LEFT)
        self.assertEqual(payloads(data)[kit.RIGHT], RIGHT)
        self.assertEqual(result['stitch']['transfer_count'], 3)
        self.assertEqual(result['stitch']['overlap_blocks'], 1)
        self.assertFalse(result['network_used'])
        self.assertFalse(result['trusted_digest_matched'])

    def test_rehashed_false_report(self):
        files = payloads(kit.build(LEFT, RIGHT))
        report = kit.parse(files[kit.REPORT]); report['transfer_count'] = 99
        files[kit.REPORT] = kit.canonical(report)
        lie = kit.writer.build(files)
        kit.inspector.inspect_stream(io.BytesIO(lie))
        with self.assertRaisesRegex(ValueError, 'recomputed'):
            kit.inspect_bytes(lie)

    def test_conflicting_overlap(self):
        right = kit.parse(RIGHT)
        right['raw_logs'][0]['data'] = '0x' + format(1, '064x')
        right['transfers'],right['duplicate_count'] = kit.stitch.window.validate_logs(
            right['raw_logs'],right['decimals'],right['token_address'],right['from_block'],right['to_block'])
        with self.assertRaisesRegex(kit.stitch.window.RpcError, 'disagree'):
            kit.build(LEFT, kit.canonical(right))

    def test_raw_log_and_summary_tampering(self):
        for side in ('left', 'right'):
            value = kit.parse(LEFT if side == 'left' else RIGHT)
            value['raw_logs'][0]['removed'] = True
            with self.subTest(side=side),self.assertRaises(kit.stitch.window.RpcError):
                kit.build(kit.canonical(value) if side == 'left' else LEFT,
                          kit.canonical(value) if side == 'right' else RIGHT)

    def test_digest_and_exact_payload_contract(self):
        data = kit.build(LEFT, RIGHT)
        self.assertTrue(kit.inspect_bytes(data,hashlib.sha256(data).hexdigest())['trusted_digest_matched'])
        with self.assertRaises(ValueError): kit.inspect_bytes(data, 'a'*64)
        files = payloads(data)
        for name in (kit.LEFT,kit.RIGHT,kit.REPORT):
            fewer = dict(files); del fewer[name]
            with self.assertRaises(ValueError): kit.inspect_bytes(kit.writer.build(fewer))
        with self.assertRaises(ValueError): kit.inspect_bytes(kit.writer.build(dict(files,extra=b'x')))

    def test_strict_json_and_size_bounds(self):
        for raw in (b'{"x":1,"x":2}',b'NaN',b'1.0',b'1e400',b'\xff',b'x'*(kit.MAX_BYTES+1)):
            with self.subTest(raw=raw[:30]),self.assertRaises(ValueError): kit.parse(raw)
        with self.assertRaises(ValueError): kit.inspect_bytes(b'x'*(kit.MAX_BYTES+1))

    def test_reversed_sources_preserved(self):
        a = kit.inspect_bytes(kit.build(LEFT,RIGHT))
        b = kit.inspect_bytes(kit.build(RIGHT,LEFT))
        self.assertEqual(a['stitch'],b['stitch'])
        self.assertNotEqual(a['archive_sha256'],b['archive_sha256'])

    def test_standalone_cli_and_no_overwrite_or_extraction(self):
        scratch = Path('test/scratch').resolve(); scratch.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as raw:
            stage=Path(raw)
            shutil.copytree(kit.HERE,stage/'kit',ignore=shutil.ignore_patterns('__pycache__'))
            command=[sys.executable,'-B','kit/stitch_handoff.py']
            def run(*args):
                return subprocess.run(command+list(args),cwd=stage,capture_output=True,text=True,timeout=20)
            self.assertEqual(run('demo').returncode,0)
            self.assertEqual(run('pack','kit/examples/left.json','kit/examples/right.json','bundle.zip').returncode,0)
            invalid=kit.parse(LEFT); invalid['raw_logs'][0]['removed']=True
            (stage/'invalid.json').write_bytes(kit.canonical(invalid))
            rejected=run('pack','invalid.json','kit/examples/right.json','invalid.zip')
            self.assertEqual(rejected.returncode,1); self.assertNotIn('Traceback',rejected.stderr)
            self.assertFalse((stage/'invalid.zip').exists())
            before=(stage/'bundle.zip').read_bytes()
            self.assertEqual(run('check','bundle.zip').returncode,0)
            self.assertFalse((stage/'evidence').exists())
            self.assertEqual(run('pack','kit/examples/left.json','kit/examples/right.json','bundle.zip').returncode,1)
            self.assertEqual(before,(stage/'bundle.zip').read_bytes())
            (stage/'link.zip').symlink_to('bundle.zip')
            for args in [('check','link.zip'),('check','../outside'),('check','bundle.zip','--sha256','bad')]:
                result=run(*args); self.assertEqual(result.returncode,1,result.stderr)
                self.assertEqual(result.stdout,''); self.assertNotIn('Traceback',result.stderr)


if __name__ == '__main__': unittest.main(verbosity=2)
