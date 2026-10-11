"""JSON serialization, compression, Fernet encryption, and file integrity helpers.

Install the optional runtime dependency with:
    python -m pip install -r requirements-member4.txt

The encryption helpers use Fernet (authenticated symmetric encryption), rather
than a home-grown cipher. Keep the encryption key secret and outside source control.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import zlib
from pathlib import Path
from typing import Any, BinaryIO

from cryptography.fernet import Fernet, InvalidToken


CHUNK_SIZE = 1024 * 1024


def json_dumps(value: Any, *, pretty: bool = False) -> str:
    """Convert a JSON-compatible Python value into UTF-8-ready JSON text."""
    if pretty:
        return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    )


def json_loads(text: str | bytes) -> Any:
    """Parse JSON text or UTF-8 JSON bytes."""
    if isinstance(text, bytes):
        text = text.decode("utf-8")
    return json.loads(text)


def compress_data(data: bytes | str) -> bytes:
    """Compress bytes or UTF-8 text using zlib."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes or str")
    return zlib.compress(data)


def decompress_data(data: bytes, *, as_text: bool = False) -> bytes | str:
    """Decompress zlib data, optionally decoding the result as UTF-8."""
    if not isinstance(data, bytes):
        raise TypeError("compressed data must be bytes")
    result = zlib.decompress(data)
    return result.decode("utf-8") if as_text else result


def generate_encryption_key() -> bytes:
    """Generate a new Fernet key. Store it securely; do not commit it."""
    return Fernet.generate_key()


def encrypt_data(data: bytes | str, key: bytes) -> bytes:
    """Encrypt and authenticate data using a Fernet key."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes or str")
    try:
        return Fernet(key).encrypt(data)
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid Fernet encryption key") from exc


def decrypt_data(token: bytes, key: bytes) -> bytes:
    """Decrypt authenticated Fernet ciphertext; reject tampered/invalid data."""
    try:
        return Fernet(key).decrypt(token)
    except InvalidToken as exc:
        raise ValueError("ciphertext is invalid or has been modified") from exc
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid Fernet key or ciphertext") from exc


def encode_payload(value: Any, encryption_key: bytes | None = None) -> bytes:
    """Serialize JSON -> UTF-8 -> zlib compression -> optional encryption."""
    serialized = json_dumps(value).encode("utf-8")
    compressed = compress_data(serialized)
    if encryption_key is not None:
        return encrypt_data(compressed, encryption_key)
    return compressed


def decode_payload(data: bytes, encryption_key: bytes | None = None) -> Any:
    """Reverse encode_payload and return the decoded JSON value."""
    compressed = (
        decrypt_data(data, encryption_key)
        if encryption_key is not None
        else data
    )
    serialized = decompress_data(compressed, as_text=True)
    return json_loads(serialized)


def calculate_file_hash(
    file_path: str | Path, algorithm: str = "sha256"
) -> str:
    """Return a lowercase hex digest for a file, reading it in bounded chunks."""
    try:
        digest = hashlib.new(algorithm)
    except ValueError as exc:
        raise ValueError(f"unsupported hash algorithm: {algorithm}") from exc

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_file_hash(
    file_path: str | Path,
    expected_hash: str,
    algorithm: str = "sha256",
) -> bool:
    """Compare a file's digest to an expected hex digest without timing leaks."""
    actual = calculate_file_hash(file_path, algorithm=algorithm)
    return hmac.compare_digest(actual.lower(), expected_hash.strip().lower())
