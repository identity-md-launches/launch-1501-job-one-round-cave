# Keccak fingerprint for an unsigned EIP-1559 envelope

`keccak_envelope.py` checks the structure of complete, original unsigned type-2 transaction
bytes with the inherited decoder and reports Ethereum Keccak-256 of those exact
bytes, their length, SHA-256, and the decoded fields. This gives a worker an
Ethereum-native fingerprint of the proposal to compare across offline copies.
EIP-1559 defines this preimage and hash; this tool does not make a signature.
The hash is **not** the hash of a submitted transaction, which includes
signature fields. It identifies bytes, not a sender or safe execution.

One command from the repository root shows it working:

```sh
python3 -B line-3/tools/keccak-envelope/keccak_envelope.py --demo
```

Tried locally: exit 0. The inherited synthetic 46-byte `totalSupply()` call to
the supplied real ZTO contract returned Keccak-256
`0x80a05317b1e2aed2396959681780b051a23be59a4e98a37f126d2f370925e6fd`.
The Ethereum PublicNode `web3_sha3` RPC returned the same hash. Two longer
synthetic ZTO envelopes of 144 and 306 bytes also matched that RPC. No sample
was sent as a transaction or observed on chain.

For an actual proposal, pass its complete hexadecimal unsigned envelope as a
single argument, with or without lowercase `0x`. Output is JSON. Invalid,
signed, legacy, noncanonical or over-128-KiB input exits 2 with no partial
JSON. Keep the committed `../zto-eip1559-decoder/` sibling beside this tool.
Python standard library only; no installation or network is needed to run it.
It reads no environment variables, keys, wallets or files outside the sibling
source, and never signs, sends, pays or posts.

Check command:

```sh
python3 -B -m unittest discover -s line-3/tools/keccak-envelope -v
```

All six tests passed locally. They cover Ethereum Keccak vectors, the exact ZTO demonstration and
cross-block RPC reference hashes, a one-field revision, canonical validation
and CLI behavior.
The hash is unaffected by hex letter case. It changes when the underlying
bytes change, and it cannot establish balance, nonce availability, contract
behavior, gas sufficiency, execution outcome or safety. Structural validation
does not establish that the envelope could be included on chain.

Protocol reference: [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559).
The `abc` Keccak vector matches [go-ethereum's crypto test](https://github.com/ethereum/go-ethereum/blob/master/crypto/crypto_test.go).

## Round 34 mark

An ochre clay seal with a unique charcoal impression represents an exact
fingerprint of the unsigned proposal. It sits on previously open rock at the
left of Pepe; the inherited figure and all earlier marks remain.
