#!/usr/bin/env python3
"""Exact per-address event flows from a validated bounded ERC-20 capture."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location(
    "line4_activity_for_ledger", HERE.parent / "transfer-window-activity" / "activity.py")
activity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(activity)
window = activity.crosscheck.window
ZERO = "0x" + "0" * 40
MAX_BYTES = 16 * 1024 * 1024


def read_capture(path):
    """Resolve before opening; bound the actual read, including growing files."""
    resolved = Path(path).resolve()
    if not resolved.is_relative_to(ROOT):
        raise ValueError("capture must be inside this workspace")
    with resolved.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("capture exceeds 16 MiB limit")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=activity.no_duplicate_object)


def units(raw, decimals):
    return ("-" if raw < 0 else "") + window.display_units(abs(raw), decimals)


def report(capture):
    """Rebuild from raw logs, then account for each unique event once."""
    checked = activity.crosscheck.checked(capture)
    rows = {}
    total = 0
    for event in checked["transfers"]:
        sender, recipient = event["from"], event["to"]
        value = int(event["raw_value"])
        total += value
        for address in sorted({sender, recipient}):
            row = rows.setdefault(address, {
                "address": address, "is_zero_address": address == ZERO,
                "touching_count": 0, "received_count": 0, "sent_count": 0,
                "self_transfer_count": 0, "received_raw": 0, "sent_raw": 0,
                "self_transfer_raw": 0, "first_block": event["block"],
                "last_block": event["block"]})
            row["touching_count"] += 1
            row["last_block"] = event["block"]
            if address == recipient:
                row["received_count"] += 1
                row["received_raw"] += value
            if address == sender:
                row["sent_count"] += 1
                row["sent_raw"] += value
            if sender == recipient:
                row["self_transfer_count"] += 1
                row["self_transfer_raw"] += value
    output = []
    for address in sorted(rows):
        row = rows[address]
        row["net_raw"] = row["received_raw"] - row["sent_raw"]
        for name in ("received", "sent", "self_transfer", "net"):
            raw = row[name + "_raw"]
            row[name] = units(raw, checked["decimals"])
            row[name + "_raw"] = str(raw)
        output.append(row)
    return {
        "kind": "erc20-transfer-window-ledger", "schema_version": 1,
        "read_only": True, "validated": True, "chain_id": 1,
        "token": capture["token"], "token_address": checked["token_address"],
        "decimals": checked["decimals"], "from_block": checked["from_block"],
        "to_block": checked["to_block"],
        "from_block_anchor": checked["from_block_anchor"],
        "to_block_anchor": checked["to_block_anchor"],
        "transfer_count": len(checked["transfers"]), "address_count": len(output),
        "event_total_raw": str(total), "event_total": units(total, checked["decimals"]),
        "sum_net_raw": str(sum(int(row["net_raw"]) for row in output)),
        "addresses": output,
        "limitations": "Per-address Transfer-event flows in one bounded provider window; "
        "not balances, holders, complete history, trades, pool volume or finality. "
        "Self-transfers count once as touching and once in each direction, with zero net. "
        "Zero address is retained as an event endpoint, not a holder; mint/burn behavior "
        "is not independently verified. Sum of net flows is zero by construction, "
        "including zero address, and does not prove completeness or provider honesty."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--demo", action="store_true", help="retained real ZTO evidence, offline")
    source.add_argument("--capture", type=Path, help="workspace JSON from the transfer-window reader")
    args = parser.parse_args(argv)
    path = HERE.parent / "transfer-crosscheck" / "publicnode.json" if args.demo else args.capture
    print(json.dumps(report(read_capture(path)), indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, window.RpcError) as exc:
        print("transfer-window-ledger: " + str(exc), file=sys.stderr)
        raise SystemExit(2)
