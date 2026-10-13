import copy
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("stitch", HERE / "stitch.py")
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class StitchTests(unittest.TestCase):
    def setUp(self):
        self.left, self.right = tool.demo_pair()

    def rebuild(self, capture):
        events, duplicates = tool.window.validate_logs(
            capture["raw_logs"], capture["decimals"], capture["token_address"],
            capture["from_block"], capture["to_block"])
        capture["transfers"] = events
        capture["transfer_count"] = len(events)
        capture["duplicate_count"] = duplicates

    def test_real_zto_projection_joins_without_double_count(self):
        result = tool.stitch(self.left, self.right)
        self.assertEqual(result["token"], "ZTO")
        self.assertEqual((result["from_block"], result["to_block"]),
                         (26177298, 26177309))
        self.assertEqual(result["join_kind"], "overlap")
        self.assertEqual(result["matching_shared_hash_blocks"], [26177309])
        self.assertEqual(result["transfer_count"], 3)
        self.assertEqual(result["transfers"], self.left["transfers"])
        self.assertEqual(tool.stitch(self.right, self.left), result)

    def test_disagreeing_overlap_events_are_refused(self):
        self.right["raw_logs"] = self.right["raw_logs"][:-1]
        self.rebuild(self.right)
        with self.assertRaisesRegex(tool.window.RpcError, "overlap Transfer"):
            tool.stitch(self.left, self.right)

    def test_saved_summary_tampering_is_refused_first(self):
        self.right["transfers"][0]["raw_value"] = "0"
        with self.assertRaisesRegex(tool.window.RpcError, "summary disagrees"):
            tool.stitch(self.left, self.right)

    def test_shared_empty_block_hash_conflict_is_refused(self):
        original = tool.ledger.read_capture(
            HERE.parent / "transfer-crosscheck" / "round-27-live-zto.json")
        other = copy.deepcopy(original)
        other["from_block_anchor"]["hash"] = "0x" + "a" * 64
        with self.assertRaisesRegex(tool.window.RpcError, "shared observed block hash"):
            tool.stitch(original, other)

    def test_adjacent_empty_windows_are_labeled_and_not_proof(self):
        # Synthetic boundaries exercise the join rule, not a claim about chain data.
        original = tool.ledger.read_capture(
            HERE.parent / "transfer-crosscheck" / "round-27-live-zto.json")
        other = copy.deepcopy(original)
        next_block = original["to_block"] + 1
        other["from_block"] = other["to_block"] = next_block
        other["decimals_block"] = next_block
        other["head_at_capture"] = max(other["head_at_capture"], next_block)
        other["from_block_anchor"] = other["to_block_anchor"] = {
            "number": next_block, "hash": "0x" + "1" * 64}
        self.rebuild(other)
        result = tool.stitch(original, other)
        self.assertEqual(result["join_kind"], "adjacent")
        self.assertEqual(result["overlap_blocks"], 0)
        self.assertEqual(result["matching_shared_hash_blocks"], [])
        self.assertEqual(result["transfer_count"], 0)
        self.assertIn("not a chain-continuity proof", result["limitations"])

    def test_adjacent_windows_union_distinct_events(self):
        # Synthetic moved block tests de-duplication boundaries, not chain facts.
        other = copy.deepcopy(self.right)
        block = self.left["to_block"] + 1
        block_hash = "0x" + "3" * 64
        other["from_block"] = other["to_block"] = block
        other["decimals_block"] = block
        other["head_at_capture"] = max(other["head_at_capture"], block)
        other["from_block_anchor"] = other["to_block_anchor"] = {
            "number": block, "hash": block_hash}
        for log in other["raw_logs"]:
            log["blockNumber"] = hex(block)
            log["blockHash"] = block_hash
        self.rebuild(other)
        result = tool.stitch(self.left, other)
        self.assertEqual(result["join_kind"], "adjacent")
        self.assertEqual(result["transfer_count"], 6)
        self.assertEqual([e["block"] for e in result["transfers"]],
                         [self.left["to_block"]] * 3 + [block] * 3)

    def test_gap_is_refused(self):
        other = copy.deepcopy(self.right)
        block = self.left["to_block"] + 2
        other["from_block"] = other["to_block"] = block
        other["decimals_block"] = block
        other["head_at_capture"] = max(other["head_at_capture"], block)
        other["from_block_anchor"] = other["to_block_anchor"] = {
            "number": block, "hash": "0x" + "2" * 64}
        other["raw_logs"] = []
        self.rebuild(other)
        with self.assertRaisesRegex(tool.window.RpcError, "gap"):
            tool.stitch(self.left, other)

    def test_decimals_disagreement_is_refused(self):
        original = tool.ledger.read_capture(
            HERE.parent / "transfer-crosscheck" / "round-27-live-zto.json")
        other = copy.deepcopy(original)
        other["decimals"] = 17
        with self.assertRaisesRegex(tool.window.RpcError, "pinned decimals"):
            tool.stitch(original, other)

    def test_demo_pair_is_validated_real_evidence(self):
        a, b = tool.demo_pair()
        self.assertEqual(tool.crosscheck.checked(a)["transfers"],
                         tool.crosscheck.checked(b)["transfers"])
        self.assertEqual(b["from_block"], b["to_block"])
        self.assertEqual(a["rpc"], "https://ethereum-rpc.publicnode.com")
        self.assertEqual(b["rpc"], "https://eth.drpc.org")


if __name__ == "__main__":
    unittest.main()
