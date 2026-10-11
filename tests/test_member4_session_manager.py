import unittest

from integration.session_manager import SessionManager


class FakeClock:
    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class SessionManagerTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.manager = SessionManager(timeout=300, clock=self.clock)

    def test_create_and_validate_session(self):
        session_id = self.manager.create_session("vinayak")
        self.assertEqual(len(session_id), 32)
        self.assertTrue(self.manager.validate_session(session_id))
        self.assertEqual(self.manager.get_username(session_id), "vinayak")

    def test_empty_username_rejected(self):
        with self.assertRaises(ValueError):
            self.manager.create_session("   ")

    def test_unknown_session_is_invalid(self):
        self.assertFalse(self.manager.validate_session("not-a-session"))
        self.assertIsNone(self.manager.get_username("not-a-session"))

    def test_session_expires_after_300_seconds_idle(self):
        session_id = self.manager.create_session("vinayak")
        self.clock.advance(300)
        self.assertFalse(self.manager.validate_session(session_id))
        self.assertEqual(self.manager.active_count(), 0)

    def test_activity_refreshes_idle_timeout(self):
        session_id = self.manager.create_session("vinayak")
        self.clock.advance(250)
        self.assertTrue(self.manager.validate_session(session_id))
        self.clock.advance(250)
        self.assertTrue(self.manager.validate_session(session_id))
        self.clock.advance(300)
        self.assertFalse(self.manager.validate_session(session_id))

    def test_logout_invalidates_session(self):
        session_id = self.manager.create_session("vinayak")
        self.assertTrue(self.manager.invalidate_session(session_id))
        self.assertFalse(self.manager.validate_session(session_id))
        self.assertFalse(self.manager.invalidate_session(session_id))

    def test_cleanup_expired_sessions(self):
        self.manager.create_session("one")
        self.manager.create_session("two")
        self.clock.advance(301)
        self.assertEqual(self.manager.cleanup_expired(), 2)
        self.assertEqual(self.manager.active_count(), 0)


if __name__ == "__main__":
    unittest.main()
