# Snapshot Seal

Make a deterministic, offline-verifiable receipt for a saved `pinned-zto-snapshot/1` observation. The receipt binds both the exact JSON bytes and the canonical JSON form to the observation's inspected Ethereum block identity, ZTO address, and exact `totalSupply()` quantity. It gives a worker a compact handoff check without opening a network connection.

From the repository root, this command works offline and prints a receipt for the retained real ZTO observation:

```sh
python3 -B line-1/tools/snapshot-seal/snapshot_seal.py seal line-1/tools/pinned-snapshot/example-zto.json
```

I ran it against the included PublicNode observation from `2026-10-12T16:02:50Z`; it reported block `26177368`, hash `0xf76539e08b42037cad963c2af646774753fce06ad37245bd1487b9e6ffa549ba`, the real ZTO address, and supply `1000000000000000000000000000` base units. To save and later verify a receipt, redirect the `seal` output and use `verify SNAPSHOT RECEIPT`; both operations are offline.

Run the offline checks with:

```sh
python3 -B line-1/tools/snapshot-seal/test_snapshot_seal.py
```

The tool reuses the sibling `pinned-snapshot` inspector, so it refuses malformed, changed-chain, changed-call, or inconsistent-before/after block snapshots before producing a receipt. A matching receipt establishes byte and structural consistency only. It is not a signature, proof of provider honesty, independent corroboration, finalization proof, current-state claim, or permission to sign or send anything. Standard-library Python only; it never accesses a key, wallet, secret, environment setting, or network.


Round 34 repair: snapshots and receipts now use the inherited strict JSON parser.
Conflicting or identical duplicate keys at any nesting depth, NaN, Infinity,
and overflowing float literals are refused. Inputs must be regular files inside
this checkout. The reader rejects oversized files before opening the leaf,
reads at most 4 MiB plus one byte, and checks the opened descriptor again.
Descriptor-relative traversal with `O_NOFOLLOW` rejects file and directory
symlinks, including links whose targets remain inside the workspace. It refuses
FIFOs and devices. This implementation needs Python on a POSIX system with
`dir_fd`, `O_DIRECTORY` and `O_NOFOLLOW` (tested on Linux). Relative input paths
are relative to the command's current directory; the workspace boundary is the
checkout containing this tool. No environment settings are read. Tests keep
temporary fixtures in this checkout's `test/scratch/`, and `-B` avoids caches.

Try the new retained real observation and receipt together, fully offline:

```sh
python3 -B line-1/tools/snapshot-seal/snapshot_seal.py verify line-1/tools/snapshot-seal/current-zto.json line-1/tools/snapshot-seal/current-zto-seal.json
```

On 2026-10-13 at 04:05:17 UTC, four read-only requests through the assignment's
Ethereum relay captured finalized ZTO supply at block `26180977`, hash
`0xfffa2f6981064c0c17c939eae510a1d8e9add2b9775e1dab07cf4f2b196dae27`.
The saved snapshot names the assignment's advertised PublicNode source, rather
than the machine-local relay. Before/after identities agreed and supply was
`1000000000000000000000000000` base units. The offline command printed
`"verified": true`. All 17 seal regression tests, 11 pinned-snapshot tests and
14 direct-capture tests passed. Receipt schema and digests of previously valid
observations remain compatible. Neither workspace checks nor these hashes
authenticate the provider or a sender. File containment is a path and symlink
policy, not a sandbox against hostile hard links or a malicious checkout.
