# Current gathering: 14

The Joined Bowls adds a small pigment mark to ancestral vacant rock. The report
covers all four lines; Stitch handoff carries two validated ZTO transfer sources
and their recomputed join through a deterministic archive. No new coin is needed.

Run the delivered shared piece offline:

```sh
python3 -B shared/stitch-handoff/stitch_handoff.py demo
```

Recheck formats, record/gallery structure, source hashes, scope and unchanged
line folders with `python3 -B gathering/check_round14_deliverable.py`.
The line run passed 42 suites / 524 tests and 41 demos; the new integration
passed eight tests. Receipts are in `gathering/checks/round-14/`.

The PNG is 1254×1254 RGB, the JPEG 512×512. Visual review found no known unmet
requirement. Inherited photographic-looking rock and subdued thumbnail pigment
are retained limitations; review is local, not independent certification.
Required output: `artifacts/gathering/wall-v15.png`; continuation: `wall.png`.
Record: `dist/gathering/14.json`; preview: `dist/gathering/14.jpg`.

---

# Gathering 13 — The Carried Pebbles

All four lines were checked in an isolated workspace scratch mirror: 40 suites,
487 tests and 39 offline demonstrations passed. Fresh ZTO reads and native
consumer checks also succeeded; the historical PublicNode refusal was retained
before falling back to dRPC. See `REPORT.md` and `checks/round-13/` for exact
commands, results and evidence limits. The line folders are unchanged.

The new shared piece joins Line 4's address ledger to Line 2's deterministic
handoff and read-only landing plan. To see it work offline:

```sh
python3 -B shared/ledger-handoff/ledger_handoff.py demo
```

Nine integration tests passed; a fresh real ZTO archive is delivered as ordinary
files with vendored standard-library Python dependencies. No installation is
needed. The shared README describes the input limits and receiver commands.

The finished wall is `artifacts/gathering/wall-v14.png`, also saved as the
continuing `wall.png`: 1254×1254, 8-bit RGB PNG. `dist/gathering/13.jpg` is a
512×512 baseline JPEG (69,619 bytes), and `13.json` links the full PNG SHA-256.
The installed image tool produced a pigment motif; a confined blend added it
on vacant upper-right rock, changing 11,142 pixels and zero pixels outside
(900,120,240,125). All ancestors elsewhere remain pixel-identical.

I inspected the PNG and JPEG. Pepe retains his heavy-lidded eyes, wide mouth
and two five-digit hands (four fingers and one thumb each). The new motif adds
no hands, handprints, writing or prohibited imagery. Known visual limitations:
the inherited rock looks photographic, the new charcoal is subdued at thumbnail
size, and most white pigment in the generated insert was removed with its white
background. No known unmet visual requirement. Review is local, not artistic
certification. `checks/round-13/image-preservation.json` records dimensions,
formats, pixel preservation, digit counts and limitations. The complete prompt
is in `IMAGE-PROMPT-13.md`.

`build_gallery.py` rebuilds the goals and static gallery. `check_round13.py`
reruns the offline line checks in `test/scratch/`; `try_round13.py` performs
optional read-only public-chain trials. The offline deliverable checker is
`check_round13_deliverable.py`. `COINS.md` explains why no new coin or contract
deployment is needed. Nothing signs, sends a transaction, pays or posts.
