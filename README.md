# VOIDWING INFRASTRUCTURE // PURE RAM CASCADE ENFORCER v3.5

A zero-dependency, memory-only password-deterministic cryptographic monolith featuring 3-layer AEAD cascading and word-spreading steganography.

## Core Architecture Specifications

* **100% Memory-Only Core:** Eradicated ALL disk-written key files. Security credentials exist strictly in active RAM.
* **Hardened KDF Protocol:** Implements password-deterministic key derivation via PBKDF2-HMAC-SHA256 with 100,000 iterations and hardcoded static salt material.
* **Triple Vault AEAD Cascade:** Serial execution of ChaCha20Poly1305 -> AES-GCM -> ChaCha20Poly1305 with mandatory static contextual AAD signature metadata.
* **Sonnet's Word-Spreading Engine:** Dissects Base64 ciphertext chunks and evenly distributes invisible zero-width stego strings inside standard word intervals, completely bypassing systemic word-length triggers and context trimming algorithms.
* **On-the-fly Shell Rewrapping:** Built-in context container swapping allowing immediate core payload re-masking into new cover strings without altering the underlying cryptographic matrix.

## Deployment & Compilation Requirements

* **Operating System:** Linux Environment (Tested and verified natively on Manjaro Linux).
* **Engine:** Python 3.10+ containing standard `tkinter` support.

## Quick Start / Launch Sequence

* Install core dependency: `pip install -r requirements.txt`
* Execute the secure runtime: `python void_cipher.py`

## User Interface Operational Logics

* **MASTER PASSPHRASE:** Input session key passphrase. Derivation fires dynamically on execution.
* **SOURCE INPUT:** Target string for plaintext payload operations or rewrapping targets.
* **COVER TEXT:** Masking host string container. If left blank, defaults to pre-configured technical dictionaries.
* **FINAL OUTPUT:** Immutable readout module displaying operation logs and payload structures.