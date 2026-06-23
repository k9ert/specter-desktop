#!/usr/bin/env python3
"""
release_fetch_passphrase.py — fetch the GPG signing passphrase via NIP-46.

Runs on the CI runner during a release. The passphrase is NOT stored on GitHub;
only `passphrase.enc` (NIP-44 ciphertext, self-encrypted to the operator's npub)
lives in the repo. This script opens a NIP-46 session to the operator's Nostr
signer (e.g. Amber) and asks it to decrypt that ciphertext. The operator must
approve on their phone — so every release requires a live human tap.

Security note: the transport key (NOSTR_CI_NSEC) is *powerless*. The ciphertext
is self-encrypted to the operator (owner_sk -> owner_pk), so only the operator's
key can decrypt it. The runner never holds that key; it cannot decrypt locally.

stdout: the passphrase, and nothing else (so it can be captured directly).
stderr: all progress/diagnostics.
exit:   non-zero on any failure (a release must not silently ship unsigned).
"""
import argparse
import asyncio
import json
import os
import secrets as secrets_mod
import sys
from datetime import timedelta
from pathlib import Path

from nostr_sdk import Keys, NostrConnect, NostrConnectUri, PublicKey

DEFAULT_RELAY = "wss://relay.damus.io"


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


async def fetch_passphrase(config: dict, ciphertext: str, transport_nsec: str,
                           timeout_secs: int) -> str:
    owner_npub = config["owner_npub"]
    owner_hex = PublicKey.parse(owner_npub).to_hex()
    relay = config.get("relay", DEFAULT_RELAY)

    # Fresh per-run secret forces a clean NIP-46 handshake (already-paired
    # signers otherwise reply "ack" instead of the connect response).
    secret = secrets_mod.token_hex(16)
    uri = NostrConnectUri.parse(f"bunker://{owner_hex}?relay={relay}&secret={secret}")

    # Pre-approved transport identity — only opens the encrypted channel.
    app_keys = Keys.parse(transport_nsec)
    nc = NostrConnect(uri, app_keys, timedelta(seconds=timeout_secs), None)

    log(f"⏳ NIP-46 connect  relay={relay}  owner={owner_npub}")
    log("   Approve the decrypt request in your signer app…")

    # Triggers the handshake; an already-paired signer may answer "ack".
    try:
        await nc.get_public_key()
        log("✅ Signer connected")
    except Exception as e:
        if "ack" in str(e).lower():
            log("✅ Signer acknowledged (already paired)")
        else:
            raise

    # owner_pk == third-party pubkey: ciphertext was self-encrypted, so the
    # signer computes ECDH(owner_sk, owner_pk) and returns the plaintext.
    owner_pk = PublicKey.parse(owner_npub)
    passphrase = await nc.nip44_decrypt(owner_pk, ciphertext)
    log("✅ Passphrase decrypted by signer (never stored on GitHub)")
    return passphrase


def main() -> None:
    ap = argparse.ArgumentParser(description="Fetch GPG passphrase via NIP-46")
    ap.add_argument("--config", required=True, help="path to config.json (owner_npub, relay)")
    ap.add_argument("--ciphertext", required=True, help="path to passphrase.enc")
    ap.add_argument("--timeout", type=int, default=300, help="seconds to wait for approval")
    args = ap.parse_args()

    transport_nsec = os.environ.get("NOSTR_CI_NSEC", "").strip()
    if not transport_nsec:
        sys.exit("NOSTR_CI_NSEC env var is empty — transport identity required")

    cfg_path = Path(args.config)
    if not cfg_path.is_file():
        sys.exit(f"config not found: {args.config}")
    config = json.loads(cfg_path.read_text())
    if not config.get("owner_npub"):
        sys.exit(f"owner_npub missing from {args.config}")

    ct_path = Path(args.ciphertext)
    if not ct_path.is_file():
        sys.exit(f"ciphertext not found: {args.ciphertext}")
    ciphertext = ct_path.read_text().strip()
    if not ciphertext:
        sys.exit(f"{args.ciphertext} is empty")

    passphrase = asyncio.run(
        fetch_passphrase(config, ciphertext, transport_nsec, args.timeout)
    )
    # ONLY the passphrase on stdout — captured by the workflow, then masked.
    sys.stdout.write(passphrase)


if __name__ == "__main__":
    main()
