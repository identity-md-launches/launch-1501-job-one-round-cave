# Transfer-window stitch

Join two saved, bounded Ethereum ERC-20 Transfer observations when their block
ranges overlap or meet. Each capture is first revalidated from raw logs by the
line's strict reader. The result contains the continuous observed range,
boundary hashes, one copy of each Transfer event, and the blocks for which
both inputs contain matching observed hashes. A gap, conflicting overlap event,
shared hash conflict, token or decimals mismatch, or joined range above 2,000
blocks is refused. ZTO is the offline demo token; valid IMD captures also work.

From the repository root, one command shows it working without a network or
installation:

```sh
python3 -B line-4/tools/transfer-window-stitch/stitch.py --demo
```

Tried on 2026-10-13: the command returned a joined ZTO window at blocks
26177298–26177309, with three events counted once and the shared block hash
at 26177309 matching. The left input is the retained PublicNode observation;
the right input is the retained dRPC observation projected **in memory** to
its final block. This projection retains actual observed logs and the actual
boundary hash; it is not a new independent RPC read. The captures were made
earlier and are dated evidence, not a claim about the current chain head.

Use your own captures from the existing reader:

```sh
python3 -B line-4/tools/transfer-window-stitch/stitch.py --left first.json --right second.json
```

Both paths must resolve inside this workspace; the inherited 16 MiB input
limit and duplicate-key rejection apply. A result joins observations, not token
balances or a complete history. Even a matching overlap does not prove provider
honesty, completeness or finality. Adjacent windows share no block, so their
joined range is explicitly not a chain-continuity proof. Only boundary and
event-containing block hashes are available from the saved captures.

Nine tests passed with:

```sh
python3 -B line-4/tools/transfer-window-stitch/test_stitch.py
```

They cover the real ZTO demo, reversal, tampered summaries, disagreeing overlap
events, a hash conflict in an empty window, adjacent empty and populated
unions, a gapped range, and decimals disagreement. The synthetic boundary
changes in those tests exercise
rejection logic and are not represented as chain observations. Attempts to
refresh the small historical ZTO window directly through dRPC and PublicNode
returned HTTP 429 and 403 respectively, so no fresh capture was retained.

This tool uses only Python's standard library and its sibling line tools. It
reads selected workspace JSON and Python files only. It accesses no key,
wallet, secret or environment variable, and does not sign, send, pay or post.
