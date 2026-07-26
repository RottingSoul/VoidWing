# VOIDWING INFRASTRUCTURE // PURE RAM CASCADE ENFORCER v3.5

> A minimal-dependency, memory-only password-deterministic cryptographic monolith featuring a 3-layer AEAD cascade and word-spreading steganography.

## ⚙️ Core Architecture Specifications

* **100% Memory-Only Core:** Eradicated ALL disk-written key files. Security credentials exist strictly in active RAM and are wiped upon process termination.
* **Hardened KDF Protocol:** Implements password-deterministic key derivation via PBKDF2-HMAC-SHA256 (100,000 iterations) with static salt integration.
* **Triple Vault AEAD Cascade:** Serial execution of `ChaCha20Poly1305 -> AES-GCM -> ChaCha20Poly1305` with mandatory static contextual AAD signature metadata.
* **VOID Word-Spreading Stego Engine:** Dissects Base64 ciphertext chunks and evenly distributes invisible zero-width stego strings inside standard word intervals. Completely bypasses systemic word-length triggers and context trimming algorithms.
* **On-the-fly Shell Rewrapping:** Built-in context container swapping allows immediate core payload re-masking into new cover strings without altering the underlying cryptographic matrix.

## 🚀 Deployment & Compilation Requirements

* **Operating System:** Linux Environment (Tested and natively verified on Manjaro Linux).
* **Engine:** Python 3.10+ (requires standard `tkinter` support for the GUI).

### Quick Start / Launch Sequence

1. Install the core cryptographic dependency:
   ```bash
   pip install cryptography

    Execute the secure runtime:

    Bash

    python void_cipher.py

🎛️ User Interface Operational Logics

    [ MASTER PASSPHRASE ] — Input session key passphrase. Derivation fires dynamically on execution.
    [ SOURCE INPUT ] — Target string for plaintext payload operations or rewrapping targets.
    [ COVER TEXT ] — Masking host string container. If left blank, defaults to pre-configured technical dictionaries.
    [ FINAL OUTPUT ] — Immutable readout module displaying operation logs and payload structures.

📊 Platform Compatibility Status
Platform	Steganography Survival	Notes
Telegram	✅ Verified	Passes zero-width characters perfectly.
VKontakte	⚠️ In Progress	Aggressive HTML-entity normalization and padding trims observed. Work in progress.

Disclaimer: This software is provided for educational and personal experimentation purposes. Not audited for enterprise production-grade cryptography.
