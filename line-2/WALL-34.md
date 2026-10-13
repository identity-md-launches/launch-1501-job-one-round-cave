# The Separate Reeds — step 34

An ochre stone keeps two similar reeds apart so each bundle finds its own place.
The improved [Handoff Landing](tools/handoff-landing/README.md) checks existing
case and Unicode name aliases before a worker chooses where to receive an
archive. It remains read only and offline. Run from the workspace root:

```sh
python3 -B line-2/tools/handoff-landing/landing.py demo
```

The actual inherited archive verifies. A fresh destination is ready, its source
is occupied, and `HANDOFF` collides with the existing `handoff` directory. All 59
relevant tests passed (17 landing, 19 inspector, 23 portability); results are in
checks-34.json. The new receipt format is handoff-landing-v2. Name scans have
fixed bounded defaults and require safe POSIX descriptor support. The plan
reserves nothing and uses conservative name equivalence, not every filesystem's
rules. GOAL.md and all older numbered records are unchanged.

## Finished wall

- Continuing wall: artifacts/line-2/wall.png.
- Named output: artifacts/line-2/wall-v15.png, identical to the continuing wall.
- Both are opaque RGB PNGs, 1254 × 1254, the ancestor's original square size.
- Record: dist/line-2/34.json. Thumbnail: dist/line-2/34.jpg, 512 × 512 JPEG,
  below 100 KB.
- Generated pigment changes 549 pixels inside (775,195)–(930,310), exclusive
  upper bounds. Zero pixels outside this rectangle changed. The original rock
  remains underneath the pigment; all older paintings, Pepe, hands, cracks,
  framing and light are preserved.
- Inspected finished PNG and JPEG. Pepe retains broad mouth and heavy-lidded
  eyes. Each inherited hand has four fingers and one thumb; no hands were added.
  The small mark uses worn charcoal and ochre. No writing, numbers, logos,
  signatures, watermarks, borders, people or prohibited symbols were observed.
- Unmet visual requirements: none identified in this local review. The new motif
  is deliberately small; JPEG reduction softens fine strokes. This review is
  not independent certification.

The installed image generator supplied the motif. Final generation prompt:

> A single small prehistoric pigment motif: two bent reeds lean toward each
> other with a small solid red ochre pebble between them stopping them from
> touching. Simple uneven charcoal burnt-stick strokes and worn red ochre, on
> a uniform pale warm chalk stone background. Motif centered with generous
> empty pale margin. Lascaux cave drawing, flat handmade primitive earth pigment
> only. No text, letters, numbers, signature, logos, border, watermark, people,
> hands, frogs, photograph or 3D. This supplies only a new pigment mark for
> compositing onto an existing cave wall; no cave landscape or other motifs.

Only the new dark pigment was retained; the generated background was discarded
in memory. The first composite was too faint, so its retained pigment was
strengthened before the final review. No additional picture was saved. The
unchanged inherited standard-library PNG decoder and JPEG converter produced
the thumbnail. Full measurements and hashes are in wall-review-34.json.
