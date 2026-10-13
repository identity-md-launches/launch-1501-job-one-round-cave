#!/usr/bin/env python3
"""Join two validated, overlapping or adjacent ERC-20 Transfer observations."""

import argparse
import copy
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "line4_ledger_for_stitch", HERE.parent / "transfer-window-ledger" / "ledger.py")
ledger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ledger)
crosscheck = ledger.activity.crosscheck
window = crosscheck.window


def observations(validated):
    """Known hashes only: boundary blocks and blocks containing Transfer logs."""
    result = {}
    for anchor in (validated["from_block_anchor"], validated["to_block_anchor"]):
        result[anchor["number"]] = anchor["hash"]
    for event in validated["transfers"]:
        block, block_hash = event["block"], event["block_hash"]
        if block in result and result[block] != block_hash:
            raise window.RpcError("one capture has conflicting observed block hashes")
        result[block] = block_hash
    return result


def stitch(left, right):
    """Validate both raw captures, then join only a continuous bounded range."""
    a, b = crosscheck.checked(left), crosscheck.checked(right)
    if (left["token"] != right["token"] or
            a["token_address"] != b["token_address"] or
            a["decimals"] != b["decimals"]):
        raise window.RpcError("token or pinned decimals differ")
    if (b["from_block"], -b["to_block"]) < (a["from_block"], -a["to_block"]):
        a, b = b, a
        left, right = right, left
    start, end = a["from_block"], max(a["to_block"], b["to_block"])
    if b["from_block"] > a["to_block"] + 1:
        raise window.RpcError("gap between windows; no continuous join")
    if end - start + 1 > window.MAX_WINDOW:
        raise window.RpcError("joined range exceeds 2000 blocks")

    overlap_start, overlap_end = b["from_block"], min(a["to_block"], b["to_block"])
    overlap_blocks = max(0, overlap_end - overlap_start + 1)
    if overlap_blocks:
        in_overlap = lambda events: [event for event in events
                                      if overlap_start <= event["block"] <= overlap_end]
        if in_overlap(a["transfers"]) != in_overlap(b["transfers"]):
            raise window.RpcError("overlap Transfer observations disagree")
    hashes_a, hashes_b = observations(a), observations(b)
    common = hashes_a.keys() & hashes_b.keys()
    if any(hashes_a[number] != hashes_b[number] for number in common):
        raise window.RpcError("shared observed block hash disagrees")

    slots = {(event["block"], event["log_index"]): event for event in a["transfers"]}
    slots.update({(event["block"], event["log_index"]): event for event in b["transfers"]})
    if len(slots) > window.MAX_LOGS:
        raise window.RpcError("joined range exceeds 20000 unique Transfer logs")
    events = [slots[key] for key in sorted(slots)]
    final_anchor = (b if b["to_block"] > a["to_block"] else a)["to_block_anchor"]
    return {
        "kind": "erc20-transfer-window-stitch", "schema_version": 1,
        "read_only": True, "status": "joined", "chain_id": 1,
        "token": left["token"], "token_address": a["token_address"],
        "decimals": a["decimals"], "from_block": start, "to_block": end,
        "from_block_anchor": a["from_block_anchor"],
        "to_block_anchor": final_anchor,
        "sources": [
            {"rpc": capture["rpc"], "from_block": checked["from_block"],
             "to_block": checked["to_block"],
             "transfer_count": len(checked["transfers"])}
            for capture, checked in ((left, a), (right, b))],
        "join_kind": "overlap" if overlap_blocks else "adjacent",
        "overlap_blocks": overlap_blocks,
        "matching_shared_hash_blocks": sorted(common),
        "transfer_count": len(events), "transfers": events,
        "limitations": "A join combines two bounded provider observations. Matching overlap "
        "events and any shared observed block hashes do not prove that unobserved "
        "blocks share a chain, that a provider returned every log, finality, "
        "a token balance, or complete history. Adjacent windows have no shared "
        "block; a join is not a chain-continuity proof."
    }


def demo_pair():
    """Real ZTO captures; project dRPC's observed final block without inventing logs."""
    left = ledger.read_capture(HERE.parent / "transfer-crosscheck" / "publicnode.json")
    right = ledger.read_capture(HERE.parent / "transfer-crosscheck" / "drpc.json")
    last = right["to_block"]
    right = copy.deepcopy(right)
    right["from_block"] = last
    right["from_block_anchor"] = copy.deepcopy(right["to_block_anchor"])
    right["raw_logs"] = [log for log in right["raw_logs"]
                         if window.quantity(log["blockNumber"], "blockNumber") == last]
    events, duplicates = window.validate_logs(
        right["raw_logs"], right["decimals"], right["token_address"], last, last)
    right["transfers"] = events
    right["transfer_count"] = len(events)
    right["duplicate_count"] = duplicates
    return left, right


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true",
                        help="offline real ZTO observations, one projected to its final block")
    parser.add_argument("--left", type=Path, help="first saved workspace capture")
    parser.add_argument("--right", type=Path, help="second saved workspace capture")
    args = parser.parse_args(argv)
    if args.demo:
        if args.left or args.right:
            parser.error("--demo does not take capture paths")
        pair = demo_pair()
    else:
        if args.left is None or args.right is None:
            parser.error("provide both --left and --right")
        pair = ledger.read_capture(args.left), ledger.read_capture(args.right)
    print(json.dumps(stitch(*pair), indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, window.RpcError) as exc:
        print("transfer-window-stitch: " + str(exc), file=sys.stderr)
        raise SystemExit(2)
