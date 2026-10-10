"""Thread-safe session creation, validation, activity refresh, and expiry.

Session IDs are opaque random tokens. Expiry uses monotonic time so wall-clock
adjustments cannot unexpectedly extend or shorten a session.
"""
from __future__ import annotations

import secrets
import threading
import time
from dataclasses import dataclass
from typing import Callable


@dataclass
class Session:
    session_id: str
    username: str
    created_at: float
    last_activity: float


class SessionManager:
    """In-memory session store with idle timeout (default: 300 seconds)."""

    def __init__(
        self,
        timeout: float = 300,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")
        self.timeout = float(timeout)
        self._clock = clock
        self._sessions: dict[str, Session] = {}
        self._lock = threading.RLock()

    def create_session(self, username: str) -> str:
        """Create a session for a non-empty username and return its ID."""
        username = username.strip()
        if not username:
            raise ValueError("username must not be empty")

        now = self._clock()
        with self._lock:
            # token_hex(16) gives a 128-bit, 32-character opaque session ID.
            session_id = secrets.token_hex(16)
            while session_id in self._sessions:
                session_id = secrets.token_hex(16)
            self._sessions[session_id] = Session(
                session_id=session_id,
                username=username,
                created_at=now,
                last_activity=now,
            )
            return session_id

    def get_session(self, session_id: str, touch: bool = True) -> Session | None:
        """Return a valid session; optionally refresh its idle timer."""
        if not session_id:
            return None
        now = self._clock()
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return None
            if now - session.last_activity >= self.timeout:
                del self._sessions[session_id]
                return None
            if touch:
                session.last_activity = now
            # Return a copy so callers cannot mutate internal state.
            return Session(**vars(session))

    def validate_session(self, session_id: str, touch: bool = True) -> bool:
        """True only for an active, non-expired session."""
        return self.get_session(session_id, touch=touch) is not None

    def get_username(self, session_id: str, touch: bool = True) -> str | None:
        session = self.get_session(session_id, touch=touch)
        return session.username if session else None

    def invalidate_session(self, session_id: str) -> bool:
        """Delete a session (logout). Returns False for unknown IDs."""
        with self._lock:
            return self._sessions.pop(session_id, None) is not None

    def cleanup_expired(self) -> int:
        """Remove all expired sessions and return the number removed."""
        now = self._clock()
        with self._lock:
            expired = [
                session_id
                for session_id, session in self._sessions.items()
                if now - session.last_activity >= self.timeout
            ]
            for session_id in expired:
                del self._sessions[session_id]
            return len(expired)

    def active_count(self) -> int:
        """Return the number of currently stored sessions after cleanup."""
        self.cleanup_expired()
        with self._lock:
            return len(self._sessions)
