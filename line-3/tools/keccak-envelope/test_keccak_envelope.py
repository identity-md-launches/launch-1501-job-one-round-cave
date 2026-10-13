"""Behavioral checks for exact unsigned-envelope Keccak fingerprints."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest


PATH = Path(__file__).with_name("keccak_envelope.py")
spec = importlib.util.spec_from_file_location("keccak_envelope", PATH)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


def sample_with_data(length):
    data = bytes(range(256)) + bytes(range(4))
    fields = [1, 0, 1_000_000_000, 2_000_000_000, 100_000,
              bytes.fromhex(tool.decoder.ZTO[2:]), 0, data[:length], []]
    return "0x02" + tool.decoder.rlp_encode(fields).hex()


class KeccakEnvelopeTests(unittest.TestCase):
    def test_ethereum_keccak_is_not_sha3(self):
        self.assertEqual(tool.keccak256(b"").hex(),
                         "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470")
        self.assertEqual(tool.keccak256(b"abc").hex(),
                         "4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45")

    def test_demo_matches_public_rpc_reference(self):
        result = tool.inspect(tool.decoder.demo_transaction())
        self.assertEqual(result["keccak256"],
                         "0x80a05317b1e2aed2396959681780b051a23be59a4e98a37f126d2f370925e6fd")
        self.assertEqual(result["byteLength"], 46)
        self.assertEqual(result["transaction"]["to"], tool.decoder.ZTO)
        self.assertEqual(result["keccak256"], tool.inspect(tool.decoder.demo_transaction()[2:].upper())["keccak256"])

    def test_multiblock_envelopes_match_public_rpc_reference(self):
        self.assertEqual(tool.inspect(sample_with_data(100))["keccak256"],
                         "0xac8052927253d24f735e513d4cfcb333475c9297c51dd1ae1ebc7c4b0c34ff79")
        self.assertEqual(tool.inspect(sample_with_data(260))["keccak256"],
                         "0x6ee201ff5549edc4c9c409dd674675479a4f73e94350ca9939e971822f3ea760")

    def test_one_fee_change_changes_fingerprint_and_summary(self):
        raw = bytes.fromhex(tool.decoder.demo_transaction()[2:])
        fields, _ = tool.decoder.rlp_item(raw, 1)
        fields[3] = (3_000_000_000).to_bytes(4, "big")
        revised = "0x02" + tool.decoder.rlp_encode(fields).hex()
        before = tool.inspect(tool.decoder.demo_transaction())
        after = tool.inspect(revised)
        self.assertNotEqual(after["keccak256"], before["keccak256"])
        self.assertEqual(after["transaction"]["maxFeePerGas"], 3_000_000_000)

    def test_rejects_signed_and_malformed_envelopes(self):
        raw = bytes.fromhex(tool.decoder.demo_transaction()[2:])
        fields, end = tool.decoder.rlp_item(raw, 1)
        self.assertEqual(end, len(raw))
        signed = "0x02" + tool.decoder.rlp_encode(fields + [0, 1, 1]).hex()
        for bad in (signed, "0x01" + raw[1:].hex(),
                    tool.decoder.demo_transaction() + "00", "0x02c0", "0x02c0zz"):
            with self.subTest(bad=bad[:20]), self.assertRaises(ValueError):
                tool.inspect(bad)

    def test_cli_reports_errors_without_partial_json(self):
        good = subprocess.run([sys.executable, "-B", str(PATH), "--demo"],
                              capture_output=True, text=True, check=False)
        self.assertEqual(good.returncode, 0)
        self.assertIn('"keccak256"', good.stdout)
        bad = subprocess.run([sys.executable, "-B", str(PATH), "0x02c0"],
                             capture_output=True, text=True, check=False)
        self.assertEqual(bad.returncode, 2)
        self.assertEqual(bad.stdout, "")
        self.assertIn("error:", bad.stderr)


if __name__ == "__main__":
    unittest.main()
