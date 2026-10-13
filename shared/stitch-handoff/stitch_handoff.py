#!/usr/bin/env python3
"""Carry both ERC-20 windows and recompute their bounded join offline."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import struct
import sys
import zipfile

HERE = Path(__file__).resolve().parent
MAX_BYTES = 99_000
LEFT = 'evidence/left.json'
RIGHT = 'evidence/right.json'
REPORT = 'review/stitch.json'
SCHEMA = 'erc20-stitch-handoff/1'


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, HERE / 'vendor' / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


stitch = load('stitch_handoff_stitch', 'transfer-window-stitch/stitch.py')
ledger = stitch.ledger
writer = load('ledger_handoff_writer', 'handoff/handoff.py')
inspector = load('ledger_handoff_inspector', 'handoff-inspect/inspect_handoff.py')
LIMITS = inspector.Limits(archive_bytes=MAX_BYTES, payload_bytes=MAX_BYTES,
                         manifest_bytes=4096, metadata_bytes=4096, files=3)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def reject_number(value):
    raise ValueError('floating point and non-finite JSON numbers are refused')


def parse(raw):
    if len(raw) > MAX_BYTES:
        raise ValueError('JSON exceeds 99000 bytes')
    return json.loads(raw.decode('utf-8'),
                      object_pairs_hook=ledger.activity.no_duplicate_object,
                      parse_float=reject_number, parse_constant=reject_number)


def recompute(left, right):
    return stitch.stitch(parse(left), parse(right))


def inspect_bytes(data, expected=None):
    """Verify one immutable archive, then recompute the join from both sources."""
    receipt = inspector.inspect_stream(io.BytesIO(data), LIMITS, expected)
    if {item['path'] for item in receipt['files']} != {LEFT, RIGHT, REPORT}:
        raise ValueError('exact two evidence sources and stitch report required')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        files = {item['path']: archive.read(item['path']) for item in receipt['files']}
    if writer.build(files) != data:
        raise ValueError('archive does not reproduce under the original writer')
    report = recompute(files[LEFT], files[RIGHT])
    if files[REPORT] != canonical(report):
        raise ValueError('saved stitch differs from recomputed raw logs')
    result = {'schema': SCHEMA, 'verified': True, 'network_used': False,
              'archive_sha256': receipt['archive_sha256'],
              'archive_bytes': receipt['archive_bytes'],
              'trusted_digest_matched': receipt['trusted_digest_matched'],
              'source_bytes_sha256': {key: hashlib.sha256(files[key]).hexdigest() for key in (LEFT, RIGHT)},
              'byte_reproducible': True, 'stitch_recomputed': True,
              'stitch': report,
              'limitations': 'Integrity and event accounting only; not sender identity, '
              'balances, completeness, finality, provider honesty or payload safety. '
              'Joining observations does not prove chain continuity; nothing is extracted.'}
    return result


def build(left, right):
    report = recompute(left, right)
    data = writer.build({LEFT: left, RIGHT: right, REPORT: canonical(report)})
    inspect_bytes(data)
    return data


def read_workspace(raw):
    return writer.regular_bytes(writer.workspace_path(raw), MAX_BYTES)


def demo():
    left = (HERE / 'examples/left.json').read_bytes()
    right = (HERE / 'examples/right.json').read_bytes()
    data = build(left, right)
    if data != build(left, right):
        raise ValueError('nondeterministic packaging')
    result = inspect_bytes(data)
    result['demo'] = 'Dated ZTO evidence: right is a final-block projection, not a fresh independent capture.'
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('demo')
    pack = commands.add_parser('pack')
    pack.add_argument('left')
    pack.add_argument('right')
    pack.add_argument('archive', help='new workspace-relative ZIP; never overwritten')
    check = commands.add_parser('check')
    check.add_argument('archive')
    check.add_argument('--sha256', help='independently trusted archive SHA-256')
    args = parser.parse_args(argv)
    try:
        if args.command == 'demo':
            result = demo()
        elif args.command == 'pack':
            target = writer.workspace_path(args.archive, must_exist=False)
            data = build(read_workspace(args.left), read_workspace(args.right))
            result = inspect_bytes(data)
            with target.open('xb') as output:
                output.write(data)
            result['output'] = args.archive
        else:
            result = inspect_bytes(read_workspace(args.archive), args.sha256)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (stitch.window.RpcError, OSError, ValueError, TypeError, KeyError, RuntimeError, UnicodeError,
            RecursionError, OverflowError, zipfile.BadZipFile, EOFError,
            NotImplementedError, struct.error):
        print('stitch-handoff: invalid, over-limit or inconsistent evidence; no receipt emitted',
              file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
