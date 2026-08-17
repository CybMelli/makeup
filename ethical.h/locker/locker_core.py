"""
locker_core.py
Author: Melina Sunar

Shared encryption logic for the Locker / Unlocker apps.

This does NOT use native PDF passwords or zip encryption. Instead it wraps
ANY file (PDF, image, whatever) into a custom encrypted container format,
using a password-derived AES key. Only someone running the Unlocker app
with the correct password can turn it back into the original file.

--------------------------------------------------------------------------
Crypto design (for explaining to a lecturer)
--------------------------------------------------------------------------
1. PBKDF2-HMAC-SHA256 turns the human password into a 32-byte AES key.
   - A random 16-byte "salt" is generated per file, so the same password
     never produces the same key twice -> protects against rainbow-table
     / precomputed dictionary attacks.
   - 480,000 iterations (OWASP's 2023+ recommendation for PBKDF2-SHA256)
     deliberately slows down brute-force password guessing.
2. The derived key is used to build a Fernet token. Fernet = AES-128 in
   CBC mode for confidentiality + HMAC-SHA256 for integrity, combined
   into one authenticated encryption scheme. If even one byte of the
   locked file is altered (corruption, tampering) or the password is
   wrong, decryption fails loudly instead of returning garbage.
3. The original file extension is stored (unencrypted) in the header, so
   the Unlocker app knows to save the result as .pdf, .png, etc. Only the
   file's *content* is encrypted, not its type.

--------------------------------------------------------------------------
Container file format (.locked)
--------------------------------------------------------------------------
 4 bytes   magic header   b"MSL1"
 1 byte    extension length (N)
 N bytes   original extension, e.g. b"pdf" or b"png" (no dot)
16 bytes   PBKDF2 salt
 remainder Fernet token (the encrypted file content)
"""

import os
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

MAGIC = b"MSL1"
PBKDF2_ITERATIONS = 480_000
SALT_SIZE = 16
LOCKED_EXT = ".locked"


def _derive_key(password: str, salt: bytes) -> bytes:
    """Turns a password + salt into a 32-byte key, base64-encoded for Fernet."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    key = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(key)


def lock_file(input_path: str, password: str, output_dir: str) -> str:
    """Encrypts input_path into a .locked file inside output_dir. Returns output path."""
    with open(input_path, "rb") as f:
        original_data = f.read()

    ext = os.path.splitext(input_path)[1].lstrip(".").lower().encode()
    if len(ext) > 255:
        raise ValueError("File extension too long.")

    salt = os.urandom(SALT_SIZE)
    key = _derive_key(password, salt)
    token = Fernet(key).encrypt(original_data)

    base = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, f"{base}{LOCKED_EXT}")

    with open(output_path, "wb") as f:
        f.write(MAGIC)
        f.write(len(ext).to_bytes(1, "big"))
        f.write(ext)
        f.write(salt)
        f.write(token)

    return output_path


def unlock_file(input_path: str, password: str, output_dir: str) -> str:
    """Decrypts a .locked file back into its original form inside output_dir."""
    with open(input_path, "rb") as f:
        data = f.read()

    if data[:4] != MAGIC:
        raise ValueError("This doesn't look like a valid locked file.")

    pos = 4
    ext_len = data[pos]
    pos += 1
    ext = data[pos:pos + ext_len].decode()
    pos += ext_len
    salt = data[pos:pos + SALT_SIZE]
    pos += SALT_SIZE
    token = data[pos:]

    key = _derive_key(password, salt)
    try:
        original_data = Fernet(key).decrypt(token)
    except InvalidToken:
        raise ValueError("Wrong password (or the file is corrupted).")

    base = os.path.splitext(os.path.basename(input_path))[0]
    suffix = f".{ext}" if ext else ""
    output_path = os.path.join(output_dir, f"{base}_unlocked{suffix}")

    with open(output_path, "wb") as f:
        f.write(original_data)

    return output_path