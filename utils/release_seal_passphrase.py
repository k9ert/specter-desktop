#!/usr/bin/env python3
"""
release_seal_passphrase.py — one-time operator setup (run LOCALLY, never in CI).

Self-encrypts the GPG signing passphrase to your own Nostr key (NIP-44 v2) so it
can be committed as `.github/signing/passphrase.enc`. Only your signer can later
decrypt it (see release_fetch_passphrase.py). Also writes config.json.

Run this on a TRUSTED machine. Your nsec is read via prompt (getpass), used in
memory only, and never written to disk. The GPG passphrase is likewise prompted.

    python3 utils/release_seal_passphrase.py

Requires: pip install nostr-sdk
"""
import getpass
import json
import sys
from pathlib import Path

from nostr_sdk import Keys, Nip44Version, nip44_encrypt

DEFAULT_RELAY = "wss://relay.damus.io"
SIGNING_DIR = Path(__file__).resolve().parent.parent / ".github" / "signing"


def main() -> None:
    print("Seal GPG passphrase for NIP-46 release signing (local, one-time).\n")

    nsec = getpass.getpass("Operator nsec (Amber/owner key, hidden): ").strip()
    if not nsec.startswith("nsec1"):
        sys.exit("Expected an nsec1… bech32 secret key.")
    keys = Keys.parse(nsec)
    owner_npub = keys.public_key().to_bech32()

    passphrase = getpass.getpass("GPG passphrase (hidden): ")
    confirm = getpass.getpass("GPG passphrase again: ")
    if passphrase != confirm:
        sys.exit("Passphrases do not match.")
    if not passphrase:
        sys.exit("Empty passphrase — nothing to seal.")

    relay = input(f"Relay [{DEFAULT_RELAY}]: ").strip() or DEFAULT_RELAY

    # Self-encrypt: owner_sk -> owner_pk. Only the operator's signer can decrypt.
    ciphertext = nip44_encrypt(
        keys.secret_key(), keys.public_key(), passphrase, Nip44Version.V2
    )

    SIGNING_DIR.mkdir(parents=True, exist_ok=True)
    (SIGNING_DIR / "passphrase.enc").write_text(ciphertext + "\n")
    (SIGNING_DIR / "config.json").write_text(
        json.dumps({"owner_npub": owner_npub, "relay": relay}, indent=2) + "\n"
    )

    print("\n✅ Wrote:")
    print(f"   {SIGNING_DIR / 'passphrase.enc'}")
    print(f"   {SIGNING_DIR / 'config.json'}  (owner_npub={owner_npub})")
    print("\nNext:")
    print("  1. Commit both files (ciphertext + public config are safe to commit).")
    print("  2. Add the CI transport key as a powerless GitHub secret NOSTR_CI_NSEC.")
    print("  3. Pre-approve that app pubkey in Amber; set nip44_decrypt to MANUAL.")
    print("  4. Delete the old GPG_PASSPHRASE GitHub secret.")


if __name__ == "__main__":
    main()
