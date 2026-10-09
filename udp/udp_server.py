"""In-order UDP receiver with cumulative ACKs and loss-demo switches."""

import argparse
import socket
import time
from dataclasses import dataclass, field

from integration.config import (
    BUFFER_SIZE, SERVER_HOST, SESSION_TIMEOUT, UDP_MAX_PACKETS,
    UDP_MAX_TRANSFERS, UDP_PORT,
)


@dataclass
class ReceiverState:
    total: int
    expected: int = 0
    payloads: list = field(default_factory=list)
    last_seen: float = field(default_factory=time.monotonic)
    data_dropped: bool = False
    ack_dropped: bool = False


class UDPServer:
    """Member 5 may run serve(stop_event) in a thread.

    on_complete(payloads, address, transfer_id) is called once per transfer.
    Keep the callback quick; ACK means accepted by this transport, not a
    guarantee that downstream business processing succeeded.
    """

    def __init__(self, host=SERVER_HOST, port=UDP_PORT, drop_once=None,
                 drop_ack_once=None, on_complete=None, log=print):
        if any(n is not None and n < 0 for n in (drop_once, drop_ack_once)):
            raise ValueError("Loss-demo sequence numbers must be nonnegative")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.socket.bind((host, port))
        except OSError:
            self.socket.close()
            raise
        self.socket.settimeout(0.1)
        self.address = self.socket.getsockname()
        self.states = {}
        self.drop_once = drop_once
        self.drop_ack_once = drop_ack_once
        self.on_complete = on_complete
        self.log = log

    def close(self):
        self.socket.close()

    def handle_packet(self, data, address):
        try:
            if len(data) > min(BUFFER_SIZE, 1200):
                raise ValueError("oversized datagram")
            kind, seq, transfer_id, total, payload = data.decode("utf-8").split("|", 4)
            seq, total = int(seq), int(total)
            if (kind != "DATA" or len(transfer_id) != 32
                    or any(c not in "0123456789abcdef" for c in transfer_id)
                    or not 1 <= total <= UDP_MAX_PACKETS or not 0 <= seq < total):
                raise ValueError("invalid header")
        except (UnicodeDecodeError, ValueError):
            self.log(f"IGNORE malformed packet from {address}")
            return

        now = time.monotonic()
        for key in list(self.states):
            if now - self.states[key].last_seen > SESSION_TIMEOUT:
                del self.states[key]
        key = (address, transfer_id)
        if key not in self.states:
            if len(self.states) >= UDP_MAX_TRANSFERS:
                self.log("IGNORE: receiver transfer capacity reached")
                return
            self.states[key] = ReceiverState(total)
        state = self.states[key]
        if state.total != total:
            self.log("IGNORE: total packet count changed")
            return
        state.last_seen = now
        if seq == self.drop_once and not state.data_dropped:
            state.data_dropped = True
            self.log(f"SIMULATED DATA LOSS packet={seq}")
            return

        completed = False
        if seq == state.expected:
            state.payloads.append(payload)
            state.expected += 1
            self.log(f"ACCEPT packet={seq} payload={payload}")
            completed = state.expected == state.total
        else:
            self.log(f"DISCARD packet={seq}; expected={state.expected} (duplicate or out of order)")
        # -1 reports that no packet has been accepted yet.
        ack_seq = state.expected - 1
        if ack_seq == self.drop_ack_once and not state.ack_dropped:
            state.ack_dropped = True
            self.log(f"SIMULATED ACK LOSS packet={ack_seq}")
        else:
            self.socket.sendto(f"ACK|{ack_seq}|{transfer_id}".encode(), address)
            self.log(f"SEND ACK packet={ack_seq}")
        if completed:
            self.log(f"COMPLETE transfer={transfer_id} packets={state.total}")
            if self.on_complete:
                try:
                    self.on_complete(list(state.payloads), address, transfer_id)
                except Exception as exc:
                    self.log(f"Downstream callback failed: {exc}")
            # Keep expected/total for duplicate ACKs, release delivered payloads.
            state.payloads.clear()

    def serve(self, stop_event=None):
        self.log(f"UDP server listening on {self.address[0]}:{self.address[1]}")
        while stop_event is None or not stop_event.is_set():
            try:
                data, address = self.socket.recvfrom(BUFFER_SIZE + 1)
            except socket.timeout:
                continue
            self.handle_packet(data, address)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=SERVER_HOST)
    parser.add_argument("--port", type=int, default=UDP_PORT)
    parser.add_argument("--drop-once", type=int, help="Discard this DATA sequence once per transfer")
    parser.add_argument("--drop-ack-once", type=int, help="Discard this ACK sequence once per transfer")
    args = parser.parse_args()
    server = None
    try:
        server = UDPServer(args.host, args.port, args.drop_once, args.drop_ack_once)
        server.serve()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Server error: {exc}\n")
    finally:
        if server:
            server.close()


if __name__ == "__main__":
    main()
