# Release signing — passphrase via NIP-46

The GPG **passphrase is no longer stored on GitHub.** Instead, this directory
holds `passphrase.enc` — the passphrase NIP-44-encrypted to the operator's own
Nostr key. During a release the CI runner asks the operator's signer (Amber /
nsec.app) to decrypt it over NIP-46, which **requires a live tap on the phone**.
The runner cannot decrypt it on its own.

```
runner: import GPG_PRIVATE_KEY
   │  NIP-46 connect via NOSTR_CI_NSEC (powerless transport key)
   ▼
phone (Amber): "decrypt passphrase?"  [Approve ✓]  ── self-decrypts owner→owner
   │  passphrase (RAM only on runner)
   ▼
gpg --detach-sign SHA256SUMS  →  SHA256SUMS.asc
```

## Files here

| File | Contents | Safe to commit? |
|------|----------|-----------------|
| `config.json` | `owner_npub`, `relay` | ✅ public info |
| `passphrase.enc` | GPG passphrase, NIP-44 self-encrypted to operator | ✅ ciphertext only |

## GitHub secrets

| Secret | Role |
|--------|------|
| `GPG_PRIVATE_KEY` | armored signing key (unchanged) |
| `NOSTR_CI_NSEC` | **powerless** NIP-46 transport identity — opens the channel, cannot decrypt anything |
| ~~`GPG_PASSPHRASE`~~ | **delete this** after migration |

`NOSTR_CI_NSEC` leaking is not catastrophic: it cannot decrypt the passphrase
(only the operator's key can), and any decrypt request still prompts the phone,
where an unexpected one is simply declined / the app revoked in Amber.

## One-time setup

1. Generate a dedicated CI transport keypair (any Nostr key; treat it as the app
   identity, not a vault). Save the nsec as the `NOSTR_CI_NSEC` GitHub secret.
2. On a **trusted local machine** (`pip install nostr-sdk`):
   ```bash
   python3 utils/release_seal_passphrase.py
   ```
   Enter the operator nsec (used in RAM only, never written) and the GPG
   passphrase. This writes `passphrase.enc` + `config.json`. Commit both.
3. In **Amber**: enable the relay from `config.json`, approve the CI app pubkey
   once, and set its **nip44_decrypt** permission to **manual approve** (so each
   release prompts you — that's the human gate).
4. **Delete** the `GPG_PASSPHRASE` GitHub secret.

## Rotating

- **Passphrase**: re-run `release_seal_passphrase.py`, re-commit `passphrase.enc`.
- **Transport key**: revoke the old app in Amber, set a new `NOSTR_CI_NSEC`,
  re-approve. No repo change needed.
- **Operator key**: re-run the seal script (new `owner_npub`), re-approve in the
  new signer.

## Failure behaviour

If the operator does not approve within the timeout (default 300s), the signing
step **fails the release** — it never ships an unsigned `SHA256SUMS`.
See [`utils/release_fetch_passphrase.py`](../../utils/release_fetch_passphrase.py).
