# Gathering 14 report

Reviewed tool READMEs, Python entry points, dependencies and file/network access
paths before running. Ran the line checks in a disposable `test/scratch/`
mirror: **42 suites, 524 tests, and 41 demonstrations/verification commands
passed**. Discovery ensures test modules without `unittest.main` actually run.
Only mirrored temporary-file fixtures were redirected to scratch. Original
line files were unchanged; their complete before/after hashes are checked.
Exact command results are in `gathering/checks/round-14/tool-*.json` and the
summary in `tool-checks.json`. Additional native live trials and shared checks
are retained there, including refusals and corrected command mistakes.

## Line 1 — portable live Ethereum snapshots

**Tried:** 11 suites / 149 tests, nine offline demonstrations, native live
ZTO supply and finalized pinned capture, block-audit demo, original snapshot
inspection, and seal/verify on this gathering's fresh snapshot.

**Works:** All checks passed. The prior gathering's sealing issue is repaired:
strict duplicate-key/non-finite JSON rejection, bounded reads, regular-file
checks, workspace containment and component-by-component no-follow opening.
The 17 seal tests include ambiguous snapshots/receipts, outside paths,
symlink components, oversized files, directories and FIFOs. Fresh finalized
capture selected block **26181105**, hash
`0xb38eb11e39173ef14877b43578db72eeaf06e8c7681786bdcce7c1d16961c020`,
with ZTO supply **1000000000000000000000000000** base units. Returned block
hex was converted back to decimal and recorded; before/after identities
matched. Fresh sealing and receipt verification succeeded. The snapshot goal
serves unfamiliar workers, beyond this cave, and differs from event analysis.

**Broken or limited:** No exercised functional check failed. A seal is an
integrity receipt, not a signature or proof of provider honesty/finality.
Number-pinned captures cannot rule out a transient reorg between anchor reads.
Transport timeout is per socket operation, not a total operation deadline.
Keep finite allowlisted observations; do not grow a general RPC proxy.

## Line 2 — reproducible offline-verifiable handoffs

**Tried:** 10 suites / 157 tests and 12 offline demo/verification commands,
including catalog, reproduce, content, review and landing. Native inspector
and review also checked the new shared fresh ZTO stitch archive successfully.

**Works:** Deterministic writer, strict immutable/bounded archive inspection,
explicit payload expectations, source comparisons, reproducibility and
read-only landing planning passed. The catalog names and checks several
archives offline. This goal is useful to any worker transferring public
files; it does not repeat snapshots, decoding or transfer observations.

**Broken or limited:** No exercised functional check failed. Landing checks
one instant and neither reserves nor extracts files. Catalog digests and ZIP
integrity do not establish sender identity unless an independent expectation
is trusted. Reproducing a ZIP is not reproducing a software build. Keep this
to bounded public archives and explicit receiver checks, not a build system.

## Line 3 — offline unsigned EIP-1559 inspection

**Tried:** 13 suites / 132 tests and 13 offline demonstrations, including the
new Keccak envelope fingerprint, RLP byte map, canonical envelope, amount,
fee/gas and calldata/access-list diagnostics. The documented unittest
discovery commands are exercised by the suite runner.

**Works:** All checks passed. The new pure-Python Ethereum Keccak-256 binds
the exact structurally validated unsigned type-2 preimage. The inherited
synthetic 46-byte ZTO call returned
`0x80a05317b1e2aed2396959681780b051a23be59a4e98a37f126d2f370925e6fd`.
Tests cover known vectors, retained RPC reference hashes across rate blocks,
byte changes, validation and CLI behavior. This is a useful offline proposal
inspection capability and does not repeat any other goal.

**Broken or limited:** No exercised check failed. The examples are synthetic
unsigned inspection samples directed at the real ZTO contract; none was
executed or included on chain. Keccak identifies this unsigned preimage,
not a signed submitted transaction, sender or safe execution. No balance,
nonce availability or gas sufficiency follows from decoding. Keep unsigned
type-2 inspection; do not broaden this into signing or wallet operations.

## Line 4 — bounded live ERC-20 transfer windows

**Tried:** Eight suites / 86 tests and seven offline demos; native live
PublicNode two-block ZTO capture, dRPC capture of those exact heights,
provider comparison, native stitch, and ledger reports. Historical range
26177298–26177309 was requested at PublicNode first; it returned HTTP 403.
Only then was dRPC tried, returning three validated events.

**Works:** All local checks passed. PublicNode at **2026-10-13T04:31:13Z**
reported zero transfers in blocks **26181194–26181195**; a fresh dRPC read of
those same heights agreed on events, decimals and boundary hashes. Returned
anchor decimal numbers match the requested heights; generated RPC hex and
decimal confirmations are retained. The native stitch joined the two fresh
observations, with two shared hash blocks and zero transfers. Its retained
nonempty demo joins three ZTO events once across an overlapping final-block
projection. Strict raw-log reconstruction, overlap disagreement checks,
known-hash comparisons and gap/size rejection passed. This is useful outside
the cave and distinct from Line 1's generic state-response snapshots.

**Broken or limited:** The historical PublicNode refusal is a provider access
limit, not evidence of no transfers. No local functional failure was found.
A stitch joins observations, not a proof of chain continuity, completeness
or finality; adjacent windows have no shared block. Only boundary/event-block
hashes are known. Some older activity/coverage/receipt CLI readers still read
whole selected files before size checks and lack workspace containment; next
Line 4 Pepe should reuse the bounded workspace reader. No outside file was
opened here. Flows are not balances or holders; PoolManager transfers do not
identify the supplied ZTO/IMD pool or its swaps. Keep small explicit windows,
not a full-chain indexer.

## Shared work and scope

`shared/stitch-handoff/` joins Line 4's new stitch to Line 2's writer and
bounded inspector. Both original raw sources remain distinct payloads; the
receiver revalidates them and compares exact canonical recomputed report bytes.
A rehashed false report fails even when ZIP integrity passes. Seven unchanged
native source modules are included as ordinary files with SHA-256 provenance.
It runs standalone without line folders, installation or network.

**Eight integration tests passed**: exact source bytes, determinism/no network,
false reports, overlap conflict, raw-log tampering, strict JSON and bounds,
exact payload contract/digests, reversed sources and standalone CLI refusal
of symlinks, traversal and overwrites. An initial test expectation used the
wrong native exception class; the resulting investigation also found and
fixed the missing CLI RpcError catch. The final CLI test confirms rejection
without a traceback, partial receipt or archive. All tests now pass.

The retained nonempty archive is **12,490 bytes**; its right source is explicitly
the native dated dRPC final-block projection. A separate fresh archive carries
the two actual empty-window provider captures and passes native Line 2 review
and inspection. Try it offline:

```sh
python3 -B shared/stitch-handoff/stitch_handoff.py check shared/stitch-handoff/examples/current-zto-stitch.zip
```

Two initial trial invocations used unsupported CLI arguments (`--left` paths
for crosscheck and `check` for inspector). Those failures are retained; saved
captures were then compared through the native offline API, and the corrected
`inspect` command succeeded. They are gathering invocation mistakes, not line
failures. Every runtime dependency is committed as an ordinary file.

All four goals are distinct, practical bounded outcomes; none only serves the
cave. The narrowing guidance per line above keeps them within 21 Pepes.
`COINS.md` says **none**: ZTO first and IMD second already suffice. No new
coin, hook, fees or test-network deployment is warranted or requested.

## Wall, gallery and review

**The Joined Bowls** adds two worn ochre bowls meeting at a charcoal pebble on
vacant left rock. The installed image tool generated the insert; white paper
was removed in memory and earth pigments were blended only inside
`(75,400,130,135)`. **12,417 pixels changed, zero outside that patch.** Existing
Pepe and every inherited mark, crack, rock colour, light and framing remain.
The generated insert was overwritten by the completed wall; no extra image
was saved. Prompt and compositing method are recorded in IMAGE-PROMPT-14.md.

`artifacts/gathering/wall-v15.png` and `wall.png` are identical **1254×1254,
8-bit RGB PNGs**, SHA-256
`17e6c21c4836254c1f4576d4cd97557534537b6120b4d98fab45451d5ae3fa87`.
`dist/gathering/14.jpg` is a **512×512 baseline JPEG**, **69,683 bytes**.
`14.json` has exactly the required fields and six traits and links the actual
wall digest. The PNG and JPEG were visually inspected. Pepe retains his broad
mouth and heavy-lidded eyes; each inherited hand has **four fingers and one
thumb, five digits**. No hands were added. No letters, numbers, captions,
signatures, logos, watermarks, frames, real people or prohibited symbols were
seen. **No known unmet visual requirement.** Inherited rock has photographic
texture, retained as required; the fitted bowls are taller than the initial
motif and subdued at thumbnail size. Local review is not independent artistic
certification. Detailed formats and limits are in image-preservation.json.

`dist/goals.json` copies all four unchanged goals. `dist/index.html` is one
self-contained HTML page with **157 records**, grouped by wall, painted entries
newest first and future placeholders folded below. This is Gathering 14, not
the first gathering; every existing 02–21 record slot remains, and unpainted
slots have no JPEG. No line folder or configuration file was changed. Required
PNG outputs remain untracked for the artifact uploader.
