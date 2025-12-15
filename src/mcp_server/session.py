"""Session and conversation management for MCP server.

Handles conversation history tracking, session state, and message storage.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4


@dataclass
class ConversationMessage:
    """A single message in a conversation."""
    role: str  # 'user' or 'assistant'
    content: str
    narration: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "role": self.role,
            "content": self.content,
            "narration": self.narration,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Session:
    """A conversation session with state and history."""
    session_id: str = field(default_factory=lambda: str(uuid4()))
    history: List[ConversationMessage] = field(default_factory=list)
    voice_settings: Dict[str, any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Initialize default voice settings."""
        if not self.voice_settings:
            self.voice_settings = {
                "tts_provider": "local",  # Default to local for safety
                "stt_provider": "openai",
                "tts_voice": "default",
                "tts_speed": 1.0,
                "auto_speak": True,
                "narration_enabled": True,
                "verbosity": "medium",
            }

    def add_message(self, role: str, content: str, narration: Optional[str] = None) -> ConversationMessage:
        """Add a message to the conversation history.

        Args:
            role: 'user' or 'assistant'
            content: Message content
            narration: Optional narration text for voice output

        Returns:
            The created ConversationMessage
        """
        message = ConversationMessage(
            role=role,
            content=content,
            narration=narration,
        )
        self.history.append(message)
        self.last_activity = datetime.now()
        return message

    def get_history(self, limit: Optional[int] = None) -> List[ConversationMessage]:
        """Get conversation history.

        Args:
            limit: Maximum number of recent messages to return (None = all)

        Returns:
            List of ConversationMessage objects
        """
        if limit is None:
            return self.history.copy()
        return self.history[-limit:] if limit > 0 else []

    def clear(self) -> None:
        """Clear conversation history."""
        self.history = []
        self.last_activity = datetime.now()

    def update_voice_settings(self, settings: Dict[str, any]) -> None:
        """Update voice settings.

        Args:
            settings: Dictionary of settings to update
        """
        self.voice_settings.update(settings)
        self.last_activity = datetime.now()

    def to_dict(self) -> Dict:
        """Convert session to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "history": [msg.to_dict() for msg in self.history],
            "voice_settings": self.voice_settings,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
        }


class SessionManager:
    """Manages multiple conversation sessions."""

    def __init__(self):
        """Initialize the session manager."""
        self.sessions: Dict[str, Session] = {}
        self._current_session_id: Optional[str] = None

    def create_session(self) -> Session:
        """Create a new session.

        Returns:
            The created Session object
        """
        session = Session()
        self.sessions[session.session_id] = session
        self._current_session_id = session.session_id
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session object or None if not found
        """
        return self.sessions.get(session_id)

    def get_or_create_session(self, session_id: Optional[str] = None) -> Session:
        """Get existing session or create a new one.

        Args:
            session_id: Optional session ID. If None, uses current or creates new.

        Returns:
            Session object
        """
        if session_id is None:
            session_id = self._current_session_id

        if session_id and session_id in self.sessions:
            return self.sessions[session_id]

        return self.create_session()

    def get_current_session(self) -> Session:
        """Get the current active session, creating one if needed.

        Returns:
            Current Session object
        """
        return self.get_or_create_session(self._current_session_id)

    def set_current_session(self, session_id: str) -> bool:
        """Set the current active session.

        Args:
            session_id: Session identifier

        Returns:
            True if session exists and was set, False otherwise
        """
        if session_id in self.sessions:
            self._current_session_id = session_id
            return True
        return False

    def delete_session(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: Session identifier

        Returns:
            True if session was deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            if self._current_session_id == session_id:
                self._current_session_id = None
            return True
        return False

    def list_sessions(self) -> List[str]:
        """List all session IDs.

        Returns:
            List of session IDs
        """
        return list(self.sessions.keys())

    def cleanup_inactive_sessions(self, max_age_hours: int = 24) -> int:
        """Remove sessions inactive for more than max_age_hours.

        Args:
            max_age_hours: Maximum age in hours

        Returns:
            Number of sessions deleted
        """
        now = datetime.now()
        to_delete = []

        for session_id, session in self.sessions.items():
            age = (now - session.last_activity).total_seconds() / 3600
            if age > max_age_hours:
                to_delete.append(session_id)

        for session_id in to_delete:
            self.delete_session(session_id)

        return len(to_delete)
