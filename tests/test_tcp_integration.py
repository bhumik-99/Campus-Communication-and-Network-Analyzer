import unittest

from tcp.tcp_server import process_request, sessions


class TCPIntegrationTests(unittest.TestCase):

    def setUp(self):
        sessions.clear()

    def test_login_success(self):
        response = process_request("LOGIN|vinayak|1234")

        self.assertTrue(response.startswith("LOGIN_SUCCESS|"))
        session_id = response.split("|")[1]
        self.assertIn(session_id, sessions)

    def test_login_failure(self):
        response = process_request("LOGIN|vinayak|wrong")

        self.assertEqual(response, "LOGIN_FAILED")

    def test_send_message(self):
        response = process_request("LOGIN|vinayak|1234")
        session_id = response.split("|")[1]

        response = process_request(
            f"SEND_MESSAGE|{session_id}|Hello campus"
        )

        self.assertEqual(response, "MESSAGE_RECEIVED")

    def test_invalid_session(self):
        response = process_request(
            "SEND_MESSAGE|invalid123|Hello campus"
        )

        self.assertEqual(response, "ERROR|Invalid session")

    def test_logout(self):
        response = process_request("LOGIN|vinayak|1234")
        session_id = response.split("|")[1]

        response = process_request(f"LOGOUT|{session_id}")

        self.assertEqual(response, "LOGOUT_SUCCESS")
        self.assertNotIn(session_id, sessions)

    def test_invalid_logout(self):
        response = process_request("LOGOUT|invalid123")

        self.assertEqual(response, "ERROR|Invalid session")


if __name__ == "__main__":
    unittest.main()
