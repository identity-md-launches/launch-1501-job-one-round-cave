#!/usr/bin/env python3
"""Check where a verified HANDOFF v1 ZIP could land, without extracting it."""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import stat
import struct
import sys
import zipfile


def load(name, relative):
    path = Path.cwd()
    for part in Path(relative).parts:
        path /= part
        if path.is_symlink():
            raise ValueError("tool dependency is a symlink")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


INSPECT = load("landing_inspect", "line-2/tools/handoff-inspect/inspect_handoff.py")
PORTABILITY = load("landing_portability", "line-2/tools/handoff-portability/portability.py")


def destination_parts(value):
    if (not isinstance(value, str) or not value or value.startswith("/")
            or "\\" in value or ":" in value
            or any(part in ("", ".", "..") for part in value.split("/"))
            or any(ord(char) < 32 or ord(char) == 127 for char in value)):
        raise ValueError("destination must be a plain workspace-relative directory")
    return value.split("/")


def existing_type(path):
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return "missing"
    if stat.S_ISLNK(mode):
        return "symlink"
    if stat.S_ISDIR(mode):
        return "directory"
    if stat.S_ISREG(mode):
        return "file"
    return "special"


class NameScreen:
    """Bounded cached directory-name metadata; never read entry contents."""

    def __init__(self, max_names=20000, max_directory_names=4096):
        if any(type(n) is not int or n < 1 for n in
               (max_names, max_directory_names)):
            raise ValueError("name scan limits must be positive integers")
        self.max_names = max_names
        self.max_directory_names = max_directory_names
        self.names_scanned = 0
        self.cache = {}

    def names(self, parent):
        parent = tuple(parent)
        if parent:
            destination_parts("/".join(parent))
        if parent in self.cache:
            return self.cache[parent]
        # Open every directory relative to the previous descriptor, refusing
        # symlinks. A replaced ancestor cannot redirect the scan outside cwd.
        if (os.open not in os.supports_dir_fd or os.scandir not in os.supports_fd
                or not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY")):
            raise ValueError("safe directory name scanning unsupported on this platform")
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        fd = os.open(Path.cwd(), flags)
        try:
            for part in parent:
                child = os.open(part, flags, dir_fd=fd)
                os.close(fd)
                fd = child
            names = {}
            count = 0
            with os.scandir(fd) as entries:
                for entry in entries:
                    count += 1
                    self.names_scanned += 1
                    if (count > self.max_directory_names
                            or self.names_scanned > self.max_names):
                        raise ValueError("directory name scan exceeds limit")
                    names.setdefault(PORTABILITY.key(entry.name), []).append(entry.name)
            self.cache[parent] = names
            return names
        finally:
            os.close(fd)

    def alias(self, parent, component):
        matches = self.names(parent).get(PORTABILITY.key(component), [])
        aliases = sorted(name for name in matches if name != component)
        return aliases[0] if aliases else None


def first_blocker(components, leaf_file, screen=None):
    """Inspect only named components; never follow a symlink or read a file."""
    path = Path.cwd()
    for index, component in enumerate(components):
        if screen is not None:
            alias = screen.alias(components[:index], component)
            if alias is not None:
                return "existing-name-collision", "/".join(components[:index] + [alias])
        path /= component
        kind = existing_type(path)
        if kind == "missing":
            return None
        if kind != "directory":
            if kind == "file" and leaf_file and index == len(components) - 1:
                return "existing-file", "/".join(components[:index + 1])
            return kind + ("-at-leaf" if index == len(components) - 1 else "-ancestor"), "/".join(components[:index + 1])
        if leaf_file and index == len(components) - 1:
            return "directory-at-file", "/".join(components)
    return None


def plan_receipt(receipt, destination, max_names=20000, max_directory_names=4096):
    root_parts = destination_parts(destination)
    files = [INSPECT.safe_name(item["path"]) for item in receipt["files"]]
    screen = NameScreen(max_names, max_directory_names)
    root_blocker = first_blocker(root_parts, False, screen)
    occupied = set(files)
    issues = []
    for path in sorted(files):
        parts = path.split("/")
        for end in range(1, len(parts)):
            if "/".join(parts[:end]) in occupied:
                issues.append({"path": path, "kind": "archive-file-as-directory",
                               "blocking_path": "/".join(parts[:end])})
                break
        if root_blocker:
            issues.append({"path": path, "kind": root_blocker[0],
                           "blocking_path": root_blocker[1]})
            continue
        blocker = first_blocker(root_parts + parts, True, screen)
        if blocker:
            issues.append({"path": path, "kind": blocker[0],
                           "blocking_path": blocker[1]})
    portability = PORTABILITY.analyze(files)
    return {
        "format": "handoff-landing-v2",
        "destination": destination,
        "archive_sha256": receipt["archive_sha256"],
        "trusted_digest_matched": receipt["trusted_digest_matched"],
        "file_count": receipt["file_count"],
        "ready": not issues and not portability,
        "path_issues": issues,
        "portability_profile": PORTABILITY.PROFILE,
        "portability_issues": portability,
        "existing_name_profile": "NFC-casefold-trim-space-dot-v1",
        "names_scanned": screen.names_scanned,
        "name_scan_limits": {"total": max_names, "per_directory": max_directory_names},
        "note": "Read-only preflight of named workspace paths at one instant; no extraction, "
                "atomic reservation, sender authentication or payload safety claim. "
                "Existing names use a conservative NFC/casefold/trailing-space-dot screen, "
                "not every filesystem's equivalence rules. Safe scans require POSIX dir_fd support."
    }


def plan(archive, destination, expected=None):
    destination_parts(destination)
    receipt = INSPECT.inspect_path(archive, expected=expected)
    return plan_receipt(receipt, destination)


def demo():
    archive = "line-2/handoff.zip"
    fresh = plan(archive, "line-2/tools/handoff-landing/unpacked-demo")
    occupied = plan(archive, "line-2/tools/handoff")
    alias = plan(archive, "line-2/tools/HANDOFF")
    if (not fresh["ready"] or occupied["ready"] or alias["ready"]
            or not all(i["kind"] == "existing-name-collision" for i in alias["path_issues"])):
        raise ValueError("inherited archive landing demo did not behave as expected")
    return {"fresh": fresh, "occupied": occupied, "case_alias": alias,
            "demo": "real inherited archive; neither destination was changed"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("demo")
    check = commands.add_parser("check")
    check.add_argument("archive", help="workspace-relative HANDOFF v1 ZIP")
    check.add_argument("destination", help="workspace-relative landing directory")
    check.add_argument("--sha256", help="independently obtained archive SHA-256")
    args = parser.parse_args(argv)
    try:
        result = demo() if args.command == "demo" else plan(
            args.archive, args.destination, args.sha256)
        print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True))
        return 0 if args.command == "demo" or result["ready"] else 2
    except (OSError, ValueError, TypeError, UnicodeError, RecursionError,
            zipfile.BadZipFile, EOFError, NotImplementedError, struct.error) as error:
        print("handoff-landing: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
