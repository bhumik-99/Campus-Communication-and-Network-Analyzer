# Member 4 — Session and Data Processing

## Scope

Member 4 implements the session and application-data helpers used by the TCP/UDP
communication components. The transport owners should import these helpers rather
than independently reimplementing them.

- Login session creation and random session IDs
- Session validation and idle expiration (300 seconds)
- Session activity refresh and logout invalidation
- JSON serialization/deserialization
- Payload compression/decompression
- Authenticated encryption/decryption (Fernet)
- SHA-256 file integrity hashing and verification

## Files

- `integration/session_manager.py`
- `integration/data_processing.py`
- `tests/test_member4_session_manager.py`
- `tests/test_member4_data_processing.py`
- `requirements-member4.txt`

## Install and test

Run from the repository root:

```bash
python -m pip install -r requirements-member4.txt
python -m unittest tests.test_member4_session_manager tests.test_member4_data_processing -v
```

## Session usage

```python
from integration.config import SESSION_TIMEOUT
from integration.session_manager import SessionManager

sessions = SessionManager(timeout=SESSION_TIMEOUT)
session_id = sessions.create_session("vinayak")

if sessions.validate_session(session_id):
    username = sessions.get_username(session_id)
    # Process the authenticated request for username.

sessions.invalidate_session(session_id)  # logout
```

The timeout is an idle timeout: successful validation/activity refreshes the
last-activity timestamp. A session is expired once 300 seconds pass without
activity. IDs are random 128-bit values; they are not usernames or passwords.

## Data processing usage

```python
from integration.data_processing import (
    generate_encryption_key, encode_payload, decode_payload,
    calculate_file_hash, verify_file_hash,
)

key = generate_encryption_key()  # create once; store securely, don't commit it
wire_bytes = encode_payload({"type": "SEND_MESSAGE", "message": "Hello"}, key)
decoded = decode_payload(wire_bytes, key)

digest = calculate_file_hash("file_to_send.bin")
assert verify_file_hash("file_to_send.bin", digest)
```

The payload pipeline is JSON -> UTF-8 -> zlib compression -> optional Fernet
authenticated encryption. Decode reverses that order. Fernet keys must be shared
securely by authorized peers; never hard-code real keys into the repository.

File hashes verify integrity only when the expected digest comes from a trusted
source. A hash alone does not authenticate who sent a file.

## Integration notes

- Import `SESSION_TIMEOUT` from `integration.config`; do not create a second timeout
  constant in a transport module.
- The current TCP server uses a simple `COMMAND|field|field` protocol. The JSON/
  compression/encryption pipeline is provided as a reusable processing layer; wire
  format changes should be coordinated with the TCP/UDP owners before integration.
- This module is intentionally separate from `tcp/tcp_server.py` and `udp/udp_server.py`
  so Member 4 can be integrated without overwriting other members' transport code.
