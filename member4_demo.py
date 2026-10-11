"""Small local demonstration of Member 4 session and payload helpers."""
import json
import tempfile
from pathlib import Path

from integration.session_manager import SessionManager
from integration.data_processing import (
    calculate_file_hash, decode_payload, encode_payload,
    generate_encryption_key, verify_file_hash,
)


def main():
    manager = SessionManager(timeout=300)
    session_id = manager.create_session("vinayak")
    print(f"LOGIN_SUCCESS|{session_id}")
    print(f"SESSION_VALID|{manager.validate_session(session_id)}")

    key = generate_encryption_key()
    payload = {"type": "SEND_MESSAGE", "message": "Hello campus"}
    encoded = encode_payload(payload, key)
    decoded = decode_payload(encoded, key)
    print(f"PAYLOAD_ROUND_TRIP|{json.dumps(decoded, ensure_ascii=False)}")
    print(f"COMPRESSED_ENCRYPTED_BYTES|{len(encoded)}")

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "campus_message.txt"
        path.write_text("Hello campus", encoding="utf-8")
        digest = calculate_file_hash(path)
        print(f"FILE_SHA256|{digest}")
        print(f"FILE_INTEGRITY_OK|{verify_file_hash(path, digest)}")

    manager.invalidate_session(session_id)
    print(f"LOGOUT_SUCCESS|{not manager.validate_session(session_id)}")


if __name__ == "__main__":
    main()
