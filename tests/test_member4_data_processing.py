import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from integration.data_processing import (
    calculate_file_hash,
    compress_data,
    decode_payload,
    decrypt_data,
    decompress_data,
    encode_payload,
    encrypt_data,
    generate_encryption_key,
    json_dumps,
    json_loads,
    verify_file_hash,
)


class DataProcessingTests(unittest.TestCase):
    def test_json_round_trip_unicode(self):
        value = {"message": "Hello campus 🌏", "count": 3}
        self.assertEqual(json_loads(json_dumps(value)), value)
        self.assertIn("🌏", json_dumps(value, pretty=True))

    def test_compression_round_trip(self):
        text = "campus network payload " * 100
        compressed = compress_data(text)
        self.assertEqual(decompress_data(compressed, as_text=True), text)
        self.assertLess(len(compressed), len(text.encode("utf-8")))

    def test_encryption_round_trip(self):
        key = generate_encryption_key()
        token = encrypt_data("confidential", key)
        self.assertNotIn(b"confidential", token)
        self.assertEqual(decrypt_data(token, key), b"confidential")

    def test_encryption_detects_tampering(self):
        key = generate_encryption_key()
        token = encrypt_data(b"message", key)
        tampered = token[:-1] + (b"A" if token[-1:] != b"A" else b"B")
        with self.assertRaises(ValueError):
            decrypt_data(tampered, key)

    def test_combined_payload_pipeline_without_encryption(self):
        value = {"type": "SEND_MESSAGE", "message": "hello", "seq": 4}
        self.assertEqual(decode_payload(encode_payload(value)), value)

    def test_combined_payload_pipeline_with_encryption(self):
        key = generate_encryption_key()
        value = {"type": "LOGIN", "username": "vinayak"}
        self.assertEqual(decode_payload(encode_payload(value, key), key), value)

    def test_file_sha256_and_integrity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "payload.bin"
            path.write_bytes(b"campus network")
            expected = hashlib.sha256(b"campus network").hexdigest()
            self.assertEqual(calculate_file_hash(path), expected)
            self.assertTrue(verify_file_hash(path, expected))
            self.assertFalse(verify_file_hash(path, "0" * 64))
            path.write_bytes(b"tampered payload")
            self.assertFalse(verify_file_hash(path, expected))


if __name__ == "__main__":
    unittest.main()
