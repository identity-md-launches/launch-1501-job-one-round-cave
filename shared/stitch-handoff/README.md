# Stitch handoff

Carry two bounded ERC-20 Transfer observations and their joined report in a
reproducible HANDOFF v1 ZIP. The receiver validates both raw-log captures,
recomputes the native Line 4 stitch, and compares exact canonical report bytes
after Line 2 archive integrity checks. Original source bytes remain separate.
Rehashing a false report cannot make it pass. No extraction occurs.

One command, from the repository root, works offline:

```sh
python3 -B shared/stitch-handoff/stitch_handoff.py demo
```

Python 3.10+ standard library only. Copy this complete folder into another
workspace to use it without any line folders. Seven unchanged native modules
are included as ordinary files; source paths and SHA-256s are in PROVENANCE.json.
The copied capture module contains read-only RPC functionality, but this kit's
commands never invoke it. No environment, keys, wallets, signing, transaction
submission, payments, deployment or external posts are involved.

The demo joins dated real ZTO observations for blocks 26177298–26177309,
retaining three transfers once. Its right source is the ancestor's in-memory
projection of the dRPC capture to its final block, not a fresh RPC observation.
`examples/zto-stitch.zip` preserves both sources, 12,490 bytes.
`examples/current-zto-stitch.zip` preserves two fresh provider captures of
blocks 26181194–26181195 on 2026-10-13: both reported zero events and matching
boundary hashes. Fresh evidence is dated and is not a claim about today's head.

Package selected public workspace captures into a new file:

```sh
python3 -B shared/stitch-handoff/stitch_handoff.py pack first.json second.json new.zip
python3 -B shared/stitch-handoff/stitch_handoff.py check new.zip
```

Inputs/outputs use relative workspace paths, no `..` or symlinks. Pack refuses
existing output files. Strict JSON rejects duplicate keys, floats and non-finite
numbers. Each input, archive and combined payload is bounded to 99,000 bytes;
the manifest/metadata limits are 4096 bytes, with exactly three payload files.
This is intentionally smaller than native Line 4 captures. Overlapping sources
must agree on events and known hashes; adjacency is allowed but does not prove
chain continuity. Gaps, different tokens/decimals and oversized unions fail.
Exit 0 is success, exit 1 is invalid/inconsistent input; argparse errors exit 2.
No partial receipt is printed on failure. `--sha256 DIGEST` can compare an
independently obtained archive digest; a digest from the archive itself does
not authenticate a sender.

Tried: all eight integration tests passed, including exact source preservation,
determinism, offline operation, conflicting overlap, raw-log tampering, rehashed
false reports, payload-contract/size checks, source reversal and standalone CLI
use. A fresh archive also passed the native Line 2 inspector and review.

```sh
python3 -B shared/stitch-handoff/test_stitch_handoff.py
```

The first local test run incorrectly expected ValueError for native RpcError;
correcting that exposed the missing CLI catch, which was repaired and tested.
These checks establish byte integrity and internal observation consistency,
not independent provider infrastructure, honest/complete logs, finality,
balances, pool swaps, safety of payloads or sender identity. Keep captures
finite; this is not a full-chain indexer. Workspace path screening is not a
sandbox against concurrent parent-directory replacement.
