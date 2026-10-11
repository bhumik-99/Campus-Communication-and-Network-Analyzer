
import unittest
import socket
import subprocess
import sys
import time
import threading
import io
from pathlib import Path
from unittest.mock import patch
from contextlib import redirect_stdout

from tcp.tcp_server import process_request, sessions

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "tcp" / "tcp_server.py"
CLIENT = ROOT / "tcp" / "tcp_client.py"

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

    def test_empty_request(self):
        self.assertEqual(
            process_request(""),
            "ERROR|Empty request"
        )

    def test_invalid_login_format(self):
        self.assertEqual(
            process_request("LOGIN|vinayak"),
            "ERROR|Invalid LOGIN format"
        )

    def test_invalid_message_format(self):
        self.assertEqual(
            process_request("SEND_MESSAGE|session"),
            "ERROR|Invalid SEND_MESSAGE format"
        )

    def test_invalid_logout_format(self):
        self.assertEqual(
            process_request("LOGOUT"),
            "ERROR|Invalid LOGOUT format"
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
            cls.stop_server()
            raise RuntimeError(
                "TCP server did not start on port 5001"
            )

    @classmethod
    def stop_server(cls):
        if cls.server.poll() is None:
            cls.server.terminate()
            try:
                cls.server.wait(timeout=3)
            except subprocess.TimeoutExpired:
                cls.server.kill()
                cls.server.wait()

    @classmethod
    def tearDownClass(cls):
        cls.stop_server()

    def send_request(self, message):
        response = bytearray()

        with socket.create_connection(
            (HOST, PORT), timeout=3
        ) as client:
            client.settimeout(3)
            client.sendall(message.encode("utf-8"))

            while True:
                data = client.recv(1024)
                if not data:
                    break
                response.extend(data)

        return response.decode("utf-8")

    def test_socket_login_success(self):
        response = self.send_request("LOGIN|vinayak|1234")
        self.assertTrue(response.startswith("LOGIN_SUCCESS|"))

    def test_socket_login_failure(self):
        self.assertEqual(
            self.send_request("LOGIN|vinayak|wrong"),
            "LOGIN_FAILED"
        )

    def test_socket_send_message(self):
        response = self.send_request("LOGIN|vinayak|1234")
        session_id = response.split("|")[1]

        self.assertEqual(
            self.send_request(
                f"SEND_MESSAGE|{session_id}|Hello campus"
            ),
            "MESSAGE_RECEIVED"
        )

    def test_socket_logout(self):
        response = self.send_request("LOGIN|vinayak|1234")
        session_id = response.split("|")[1]

        self.assertEqual(
            self.send_request(f"LOGOUT|{session_id}"),
            "LOGOUT_SUCCESS"
        )

        self.assertEqual(
            self.send_request(
                f"SEND_MESSAGE|{session_id}|Hello again"
            ),
            "ERROR|Invalid session"
        )

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

    def test_response_framing(self):
        self.assertEqual(
            self.send_request("LOGIN|vinayak|wrong"),
            "LOGIN_FAILED"
        )

    def test_socket_timeout(self):
        with socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        ) as listener:
            listener.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1
            )
            listener.bind((HOST, 0))
            listener.listen(1)
            listener.settimeout(2)

            test_port = listener.getsockname()[1]

            def slow_server():
                try:
                    conn, _ = listener.accept()
                    with conn:
                        conn.recv(1024)
                        time.sleep(0.5)
                except OSError:
                    pass

            thread = threading.Thread(
                target=slow_server,
                daemon=True
            )
            thread.start()

            try:
                with socket.create_connection(
                    (HOST, test_port), timeout=1
                ) as client:
                    client.settimeout(0.1)
                    client.sendall(b"LOGIN|vinayak|1234")

                    with self.assertRaises(socket.timeout):
                        client.recv(1024)
            finally:
                thread.join(timeout=2)

    def test_actual_tcp_client(self):
        if not CLIENT.exists():
            self.skipTest("tcp/tcp_client.py not found")

        result = subprocess.run(
            [sys.executable, str(CLIENT)],
            input="1\nvinayak\n1234\n",
            text=True,
            capture_output=True,
            timeout=5,
            cwd=ROOT
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("LOGIN_SUCCESS|", result.stdout)


if __name__ == "__main__":
    unittest.main()
