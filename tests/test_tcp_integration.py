
import unittest
import socket
import subprocess
import sys
import time
from pathlib import Path

from tcp.tcp_server import process_request, sessions

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "tcp" / "tcp_server.py"
HOST = "127.0.0.1"
PORT = 5001


class TCPIntegrationTests(unittest.TestCase):

    def setUp(self):
        sessions.clear()

    def test_login_success(self):
        response = process_request("LOGIN|vinayak|1234")
        self.assertTrue(response.startswith("LOGIN_SUCCESS|"))

    def test_login_failure(self):
        self.assertEqual(
            process_request("LOGIN|vinayak|wrong"),
            "LOGIN_FAILED"
        )

    def test_send_message(self):
        response = process_request("LOGIN|vinayak|1234")
        session_id = response.split("|")[1]

        response = process_request(
            f"SEND_MESSAGE|{session_id}|Hello campus"
        )

        self.assertEqual(response, "MESSAGE_RECEIVED")

    def test_logout(self):
        response = process_request("LOGIN|vinayak|1234")
        session_id = response.split("|")[1]

        response = process_request(f"LOGOUT|{session_id}")

        self.assertEqual(response, "LOGOUT_SUCCESS")
        self.assertNotIn(session_id, sessions)

    def test_invalid_session(self):
        self.assertEqual(
            process_request("SEND_MESSAGE|invalid|Hello"),
            "ERROR|Invalid session"
        )

    def test_invalid_logout(self):
        self.assertEqual(
            process_request("LOGOUT|invalid"),
            "ERROR|Invalid session"
        )


class TCPSocketIntegrationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = subprocess.Popen(
            [sys.executable, str(SERVER)],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        deadline = time.time() + 8

        while time.time() < deadline:
            if cls.server.poll() is not None:
                raise RuntimeError(
                    "TCP server stopped before becoming ready. "
                    "Check whether port 5001 is already in use."
                )

            try:
                with socket.create_connection(
                    (HOST, PORT), timeout=0.3
                ):
                    break
            except OSError:
                time.sleep(0.1)
        else:
            cls.server.terminate()
            try:
                cls.server.wait(timeout=3)
            except subprocess.TimeoutExpired:
                cls.server.kill()
                cls.server.wait()

            raise RuntimeError(
                "TCP server did not start on port 5001"
            )

    @classmethod
    def tearDownClass(cls):
        if cls.server.poll() is None:
            cls.server.terminate()

            try:
                cls.server.wait(timeout=3)
            except subprocess.TimeoutExpired:
                cls.server.kill()
                cls.server.wait()

    def send_request(self, message):
        with socket.create_connection(
            (HOST, PORT), timeout=3
        ) as client:
            client.settimeout(3)
            client.sendall(message.encode("utf-8"))
            return client.recv(1024).decode("utf-8")

    def test_socket_login_success(self):
        response = self.send_request("LOGIN|vinayak|1234")

        self.assertTrue(response.startswith("LOGIN_SUCCESS|"))

        session_id = response.split("|")[1]
        self.assertTrue(session_id)

    def test_socket_login_failure(self):
        response = self.send_request("LOGIN|vinayak|wrong")
        self.assertEqual(response, "LOGIN_FAILED")

    def test_socket_send_message(self):
        response = self.send_request("LOGIN|vinayak|1234")
        session_id = response.split("|")[1]

        response = self.send_request(
            f"SEND_MESSAGE|{session_id}|Hello campus"
        )

        self.assertEqual(response, "MESSAGE_RECEIVED")

    def test_socket_logout(self):
        response = self.send_request("LOGIN|vinayak|1234")
        session_id = response.split("|")[1]

        response = self.send_request(f"LOGOUT|{session_id}")
        self.assertEqual(response, "LOGOUT_SUCCESS")

        response = self.send_request(
            f"SEND_MESSAGE|{session_id}|Hello again"
        )

        self.assertEqual(response, "ERROR|Invalid session")

    def test_connection_refused(self):
        with socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        ) as temp:
            temp.bind((HOST, 0))
            unused_port = temp.getsockname()[1]

        with self.assertRaises(OSError):
            socket.create_connection(
                (HOST, unused_port), timeout=1
            )


if __name__ == "__main__":
    unittest.main()
