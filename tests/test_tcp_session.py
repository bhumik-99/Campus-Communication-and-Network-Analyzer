
import unittest

from tcp.tcp_server import process_request, sessions


class TCPSessionTests(unittest.TestCase):

    def setUp(self):
        sessions.clear()

    def test_valid_login(self):
        response = process_request("LOGIN|vinayak|1234")

        self.assertTrue(response.startswith("LOGIN_SUCCESS|"))

        session_id = response.split("|", 1)[1]
        self.assertEqual(sessions[session_id], "vinayak")

    def test_invalid_login(self):
        response = process_request("LOGIN|vinayak|wrong")

        self.assertEqual(response, "LOGIN_FAILED")
        self.assertEqual(sessions, {})

    def test_send_message_with_valid_session(self):
        login = process_request("LOGIN|vinayak|1234")
        session_id = login.split("|", 1)[1]

        response = process_request(
            f"SEND_MESSAGE|{session_id}|Hello campus"
        )

        self.assertEqual(response, "MESSAGE_RECEIVED")

    def test_send_message_with_invalid_session(self):
        response = process_request(
            "SEND_MESSAGE|invalid123|Hello"
        )

        self.assertEqual(response, "ERROR|Invalid session")

    def test_logout(self):
        login = process_request("LOGIN|vinayak|1234")
        session_id = login.split("|", 1)[1]

        response = process_request(f"LOGOUT|{session_id}")

        self.assertEqual(response, "LOGOUT_SUCCESS")
        self.assertNotIn(session_id, sessions)

    def test_logout_invalidates_session(self):
        login = process_request("LOGIN|vinayak|1234")
        session_id = login.split("|", 1)[1]

        process_request(f"LOGOUT|{session_id}")

        response = process_request(
            f"SEND_MESSAGE|{session_id}|Hello again"
        )

        self.assertEqual(response, "ERROR|Invalid session")

    def test_unknown_command(self):
        response = process_request("UNKNOWN|test")

        self.assertEqual(response, "ERROR|Unknown command")


if __name__ == "__main__":
    unittest.main()
