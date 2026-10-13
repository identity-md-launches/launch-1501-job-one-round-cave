# Handoff Landing

Check whether a fully verified HANDOFF v1 archive can land at a chosen
workspace directory without overwriting anything. The command is read only: it
does not create the directory, extract archive files, or execute their contents.
Python 3.8+ and only its standard library are needed. From the workspace root:

```sh
python3 -B line-2/tools/handoff-landing/landing.py demo
```

The demo verifies the real inherited `line-2/handoff.zip`. It reports a fresh
destination as ready, the inherited source directory as occupied, and the
case-variant `line-2/tools/HANDOFF` as an existing-name collision with `handoff`.
No destination is changed. To check your own public deliverable:

```sh
python3 -B line-2/tools/handoff-landing/landing.py check line-2/handoff.zip line-2/tools/handoff-landing/unpacked-demo
```

Optional `--sha256 HASH` checks an archive digest obtained independently. Exit
0 means the verified archive has no detected landing conflicts; exit 2 means
valid archive bytes with path or portability issues; exit 1 refuses invalid
input with no partial JSON report. The inherited bounded inspector validates
every ZIP member first. This tool inspects the target path components and
bounded lists of sibling names. It uses `lstat` for path types and opens scan
directories through no-follow directory descriptors from the workspace root.
It reports an occupied
file, a directory where a file must land, a blocked ancestor, internal
file/directory collisions, and the inherited conservative filename portability
issues. It never reads existing destination file contents.

Step 34 adds the `handoff-landing-v2` receipt. Each existing sibling name is
screened with NFC normalization, Unicode case folding, and removal of trailing
spaces/dots, reusing the inherited portability key. Differently spelled matches
block landing even when the exact proposed name also exists. Alias directories
and symlinks are reported without traversing them. Directory listings are
cached within one plan and bounded to 4,096 names per directory and 20,000 names
total (including the workspace's root and destination ancestors). Exceeding a
budget fails closed with exit 1 and no JSON readiness claim. The receipt records
the profile, budgets and count. Safe scanning requires POSIX `dir_fd`, descriptor
`scandir`, `O_DIRECTORY` and `O_NOFOLLOW`; unsupported platforms refuse the scan.

Keep the existing `line-2/tools/handoff-inspect/inspect_handoff.py` and
`line-2/tools/handoff-portability/portability.py` at those workspace-relative
paths. No network or installed package is needed to run this piece.

When tried, the real archive verified, its new destination was ready and its
occupied source directory was blocked. The local behavior suite covered
existing files and directories, symlinks, ancestor files, internal archive
collisions, corrupt archives, and unsafe destination paths. The improved demo
also blocked a case variant of the real inherited source directory. All 17
landing tests passed, including a real verified-archive CLI collision,
NFC/decomposed names, case folding, trailing dots/spaces, nested and root aliases,
exact-name-plus-alias conflicts, bounded scans, cache reuse, no content reads,
symlink refusal and unsupported-platform refusal.

This is a point-in-time plan, not a reservation: the tree can change before a
person extracts the archive. It does not perform extraction, protect against
all hostile concurrent path replacement, compare existing names under every
destination filesystem's case rules, authenticate the sender, or prove payload
safety. Choose a destination containing public files only; this tool reads
path metadata but no file contents.
