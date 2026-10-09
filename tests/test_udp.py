"""Real localhost UDP tests; no external packages or fixed ports needed."""

import socket
import threading
import time
import unittest
from unittest.mock import patch

from udp.go_back_n import send_packets, send_stop_and_wait
from udp.udp_server import UDPServer


class UDPTests(unittest.TestCase):
    def start_server(self, **kwargs):
        delivered = []
        logs = []
        complete = threading.Event()

        def on_complete(payloads, address, transfer_id):
            delivered.append(payloads)
            complete.set()

        server = UDPServer(port=0, on_complete=on_complete,
                           log=logs.append, **kwargs)
        server.test_complete = complete
        stop = threading.Event()
        thread = threading.Thread(target=server.serve, args=(stop,), daemon=True)
        thread.start()

        def cleanup():
            stop.set()
            thread.join(2)
            server.close()
            self.assertFalse(thread.is_alive())

        self.addCleanup(cleanup)
        return server, delivered, logs

    def send(self, server, payloads, **kwargs):
        server.test_complete.clear()
        result = send_packets(payloads, port=server.address[1], timeout=0.05,
                              log=lambda _: None, **kwargs)
        self.assertTrue(server.test_complete.wait(2))
        return result

    def test_t4_stop_and_wait_unicode_and_pipe(self):
        server, delivered, _ = self.start_server()
        result = send_stop_and_wait(["Hello | campus", "नमस्ते"],
                                    port=server.address[1], timeout=0.05, log=lambda _: None)
        self.assertTrue(server.test_complete.wait(2))
        self.assertEqual(delivered, [["Hello | campus", "नमस्ते"]])
        self.assertEqual(result.retransmissions, 0)

    def test_gbn_no_loss(self):
        server, delivered, _ = self.start_server()
        payloads = [str(i) for i in range(8)]
        result = self.send(server, payloads)
        self.assertEqual(delivered, [payloads])
        self.assertEqual(result.transmissions, 8)

    def test_t6_gbn_middle_packet_loss(self):
        server, delivered, logs = self.start_server(drop_once=2)
        payloads = [str(i) for i in range(8)]
        result = self.send(server, payloads)
        self.assertEqual(delivered, [payloads])
        self.assertGreaterEqual(result.retransmissions, 2)
        self.assertGreaterEqual(result.timeouts, 1)
        self.assertTrue(any("DISCARD packet=3" in line for line in logs))

    def test_first_packet_loss(self):
        server, delivered, _ = self.start_server(drop_once=0)
        result = self.send(server, ["a", "b", "c"])
        self.assertEqual(delivered, [["a", "b", "c"]])
        self.assertGreaterEqual(result.retransmissions, 3)

    def test_final_ack_loss_does_not_redeliver(self):
        server, delivered, _ = self.start_server(drop_ack_once=2)
        result = self.send(server, ["a", "b", "c"])
        self.assertEqual(delivered, [["a", "b", "c"]])
        self.assertGreater(result.retransmissions, 0)

    def test_stop_and_wait_ack_loss(self):
        server, delivered, _ = self.start_server(drop_ack_once=0)
        result = self.send(server, ["a", "b"], window_size=1)
        self.assertEqual(delivered, [["a", "b"]])
        self.assertEqual(result.retransmissions, 1)

    def test_independent_transfers(self):
        server, delivered, _ = self.start_server()
        first = self.send(server, ["first"])
        second = self.send(server, ["second"])
        self.assertNotEqual(first.transfer_id, second.transfer_id)
        self.assertEqual(delivered, [["first"], ["second"]])

    def test_malformed_datagrams_do_not_crash_receiver(self):
        server, delivered, _ = self.start_server()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            for packet in (b"bad", b"\xff", b"DATA|oops|id|1|hello", b"x" * 4097):
                s.sendto(packet, server.address)
        self.send(server, ["valid"])
        self.assertEqual(delivered, [["valid"]])

    def test_silent_receiver_has_bounded_retries(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sink:
            sink.bind(("127.0.0.1", 0))
            with self.assertRaises(TimeoutError):
                send_packets(["a"], port=sink.getsockname()[1], timeout=0.02,
                             max_retries=1, log=lambda _: None)

    def test_validation(self):
        for payloads, kwargs in (([], {}), (["a"], {"window_size": 0}),
                                 (["a"], {"timeout": 0}), (["a"], {"max_retries": -1}),
                                 (["a" * 1200], {}), ([123], {})):
            with self.subTest(payloads=payloads, kwargs=kwargs):
                with self.assertRaises(ValueError):
                    send_packets(payloads, log=lambda _: None, **kwargs)

    def test_wrong_transfer_and_unsent_ack_ignored(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as fake:
            fake.bind(("127.0.0.1", 0))
            fake.settimeout(2)
            errors = []

            def receiver():
                try:
                    raw, peer = fake.recvfrom(4096)
                    transfer_id = raw.decode().split("|", 4)[2]
                    for ack in (b"garbage", b"ACK|0|" + b"0" * 32,
                                f"ACK|99|{transfer_id}".encode()):
                        fake.sendto(ack, peer)
                    # Only acknowledge after the sender's first timeout.
                    raw, peer = fake.recvfrom(4096)
                    fake.sendto(f"ACK|0|{transfer_id}".encode(), peer)
                except Exception as exc:
                    errors.append(exc)

            thread = threading.Thread(target=receiver, daemon=True)
            thread.start()
            result = send_packets(["a"], port=fake.getsockname()[1], timeout=0.05,
                                  log=lambda _: None)
            thread.join(2)
            self.assertFalse(thread.is_alive())
            self.assertEqual(errors, [])
            self.assertEqual(result.retransmissions, 1)

    def test_receiver_state_capacity_and_expiry(self):
        server = UDPServer(port=0, log=lambda _: None)
        self.addCleanup(server.close)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
            client.bind(("127.0.0.1", 0))
            peer = client.getsockname()
            with patch("udp.udp_server.UDP_MAX_TRANSFERS", 1):
                server.handle_packet(f"DATA|0|{'a' * 32}|1|one".encode(), peer)
                server.handle_packet(f"DATA|0|{'b' * 32}|1|two".encode(), peer)
                self.assertEqual(len(server.states), 1)
                next(iter(server.states.values())).last_seen = time.monotonic() - 301
                server.handle_packet(f"DATA|0|{'b' * 32}|1|two".encode(), peer)
                self.assertIn((peer, "b" * 32), server.states)


if __name__ == "__main__":
    unittest.main()
