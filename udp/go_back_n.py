"""Real Go-Back-N sender. Window size 1 implements Stop-and-Wait."""

import socket
import time
import uuid
from dataclasses import dataclass

from integration.config import (
    BUFFER_SIZE, SERVER_HOST, UDP_MAX_PACKETS, UDP_MAX_RETRIES,
    UDP_PORT, UDP_TIMEOUT, WINDOW_SIZE,
)


@dataclass
class TransferResult:
    transfer_id: str
    packets: int
    transmissions: int
    retransmissions: int
    timeouts: int
    elapsed_seconds: float
    payload_bytes: int


def send_packets(payloads, host=SERVER_HOST, port=UDP_PORT,
                 window_size=WINDOW_SIZE, timeout=UDP_TIMEOUT,
                 max_retries=UDP_MAX_RETRIES, log=print):
    """Send strings in order; return metrics after all are acknowledged.

    ACK n means every packet through n has been accepted. A single timer
    covers the oldest unacknowledged packet. Timeout resends ALL outstanding
    packets. A fresh transfer ID prevents stale ACKs affecting another send.
    This is transport only; session validation belongs to Member 4.
    """
    payloads = list(payloads)
    if not 1 <= len(payloads) <= UDP_MAX_PACKETS:
        raise ValueError(f"Supply 1 to {UDP_MAX_PACKETS} packets")
    if not isinstance(window_size, int) or window_size < 1:
        raise ValueError("Window size must be a positive integer")
    if timeout <= 0 or not isinstance(max_retries, int) or max_retries < 0:
        raise ValueError("Timeout must be positive and retries nonnegative")
    if any(not isinstance(payload, str) for payload in payloads):
        raise ValueError("Each payload must be a string")
    transfer_id = uuid.uuid4().hex
    total = len(payloads)
    packets = [f"DATA|{i}|{transfer_id}|{total}|{p}".encode("utf-8")
               for i, p in enumerate(payloads)]
    if any(len(packet) > min(BUFFER_SIZE, 1200) for packet in packets):
        raise ValueError("Packet exceeds 1200 bytes (including protocol headers)")

    base = next_seq = transmissions = retransmissions = timeouts = retries = 0
    deadline = None
    started = time.monotonic()
    # UDP connect does not perform a handshake. It filters other source peers.
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        client.connect((host, port))
        while base < total:
            while next_seq < min(base + window_size, total):
                client.send(packets[next_seq])
                log(f"SEND packet={next_seq} window=[{base}, {min(base + window_size, total) - 1}]")
                transmissions += 1
                if deadline is None:
                    deadline = time.monotonic() + timeout
                next_seq += 1

            remaining = deadline - time.monotonic()
            ack_seq = None
            if remaining > 0:
                client.settimeout(remaining)
                try:
                    raw = client.recv(BUFFER_SIZE + 1)
                    parts = raw.decode("utf-8").split("|")
                    if len(parts) == 3 and parts[0] == "ACK" and parts[2] == transfer_id:
                        candidate = int(parts[1])
                        if base <= candidate < next_seq:
                            ack_seq = candidate
                except (UnicodeDecodeError, ValueError):
                    pass  # Bad ACKs never move the window or reset the timer.
                except socket.timeout:
                    pass
            if ack_seq is not None:
                log(f"ACK packet={ack_seq} (cumulative)")
                base = ack_seq + 1
                retries = 0
                deadline = time.monotonic() + timeout if base < next_seq else None
                continue
            if time.monotonic() < deadline:
                continue
            timeouts += 1
            if retries >= max_retries:
                raise TimeoutError(f"No progress after {max_retries} retries; packet {base} unacknowledged")
            retries += 1
            log(f"TIMEOUT: retransmit packets {base}..{next_seq - 1}")
            for seq in range(base, next_seq):
                client.send(packets[seq])
                transmissions += 1
                retransmissions += 1
                log(f"RESEND packet={seq}")
            deadline = time.monotonic() + timeout

    result = TransferResult(transfer_id, total, transmissions, retransmissions,
                            timeouts, time.monotonic() - started,
                            sum(len(p.encode("utf-8")) for p in payloads))
    log(f"SUCCESS: {total} packets acknowledged; retransmissions={retransmissions}; "
        f"elapsed={result.elapsed_seconds:.3f}s")
    return result


def send_stop_and_wait(payloads, **kwargs):
    """Use the same tested transport with only one packet in flight."""
    return send_packets(payloads, window_size=1, **kwargs)
