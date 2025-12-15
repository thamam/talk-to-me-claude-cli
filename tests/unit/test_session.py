"""Unit tests for session management."""

import pytest
from datetime import datetime, timedelta

from src.mcp_server.session import ConversationMessage, Session, SessionManager


class TestConversationMessage:
    """Tests for ConversationMessage class."""

    def test_create_message(self):
        """Test creating a conversation message."""
        msg = ConversationMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.narration is None
        assert isinstance(msg.timestamp, datetime)

    def test_create_message_with_narration(self):
        """Test creating a message with narration."""
        msg = ConversationMessage(
            role="assistant",
            content="Response text",
            narration="High-level summary"
        )
        assert msg.role == "assistant"
        assert msg.content == "Response text"
        assert msg.narration == "High-level summary"

    def test_to_dict(self):
        """Test serializing message to dict."""
        msg = ConversationMessage(
            role="user",
            content="Test",
            narration="Summary"
        )
        data = msg.to_dict()

        assert data["role"] == "user"
        assert data["content"] == "Test"
        assert data["narration"] == "Summary"
        assert "timestamp" in data


class TestSession:
    """Tests for Session class."""

    def test_create_session(self):
        """Test creating a session."""
        session = Session()
        assert session.session_id
        assert len(session.history) == 0
        assert isinstance(session.voice_settings, dict)
        assert session.voice_settings["tts_provider"] == "local"

    def test_add_message(self):
        """Test adding messages to session."""
        session = Session()

        msg1 = session.add_message("user", "Hello")
        assert len(session.history) == 1
        assert msg1.role == "user"
        assert msg1.content == "Hello"

        msg2 = session.add_message("assistant", "Hi there", "Greeting response")
        assert len(session.history) == 2
        assert msg2.role == "assistant"
        assert msg2.narration == "Greeting response"

    def test_get_history(self):
        """Test getting conversation history."""
        session = Session()

        session.add_message("user", "Message 1")
        session.add_message("assistant", "Response 1")
        session.add_message("user", "Message 2")

        # Get all history
        all_history = session.get_history()
        assert len(all_history) == 3

        # Get limited history
        recent = session.get_history(limit=2)
        assert len(recent) == 2
        assert recent[0].content == "Response 1"
        assert recent[1].content == "Message 2"

    def test_clear_history(self):
        """Test clearing conversation history."""
        session = Session()

        session.add_message("user", "Message 1")
        session.add_message("user", "Message 2")
        assert len(session.history) == 2

        session.clear()
        assert len(session.history) == 0

    def test_update_voice_settings(self):
        """Test updating voice settings."""
        session = Session()

        session.update_voice_settings({
            "tts_provider": "openai",
            "tts_voice": "nova",
            "auto_speak": False
        })

        assert session.voice_settings["tts_provider"] == "openai"
        assert session.voice_settings["tts_voice"] == "nova"
        assert session.voice_settings["auto_speak"] is False

    def test_to_dict(self):
        """Test serializing session to dict."""
        session = Session()
        session.add_message("user", "Test message")

        data = session.to_dict()

        assert data["session_id"] == session.session_id
        assert len(data["history"]) == 1
        assert data["voice_settings"] == session.voice_settings
        assert "created_at" in data
        assert "last_activity" in data


class TestSessionManager:
    """Tests for SessionManager class."""

    def test_create_session(self):
        """Test creating a new session."""
        manager = SessionManager()

        session = manager.create_session()
        assert session.session_id
        assert session.session_id in manager.sessions

    def test_get_session(self):
        """Test getting a session by ID."""
        manager = SessionManager()

        session = manager.create_session()
        retrieved = manager.get_session(session.session_id)

        assert retrieved is session
        assert retrieved.session_id == session.session_id

    def test_get_session_not_found(self):
        """Test getting non-existent session."""
        manager = SessionManager()

        result = manager.get_session("nonexistent")
        assert result is None

    def test_get_or_create_session(self):
        """Test get or create session logic."""
        manager = SessionManager()

        # Create first session
        session1 = manager.get_or_create_session()
        assert session1.session_id

        # Get same session
        session2 = manager.get_or_create_session(session1.session_id)
        assert session2 is session1

        # Create new session when ID not found
        session3 = manager.get_or_create_session("nonexistent")
        assert session3.session_id != session1.session_id

    def test_get_current_session(self):
        """Test getting current active session."""
        manager = SessionManager()

        # First call creates a session
        session1 = manager.get_current_session()
        assert session1.session_id

        # Second call returns same session
        session2 = manager.get_current_session()
        assert session2 is session1

    def test_set_current_session(self):
        """Test setting current session."""
        manager = SessionManager()

        session1 = manager.create_session()
        session2 = manager.create_session()

        # Set current to session2
        result = manager.set_current_session(session2.session_id)
        assert result is True
        assert manager.get_current_session() is session2

        # Try to set to non-existent session
        result = manager.set_current_session("nonexistent")
        assert result is False

    def test_delete_session(self):
        """Test deleting a session."""
        manager = SessionManager()

        session = manager.create_session()
        session_id = session.session_id

        # Delete the session
        result = manager.delete_session(session_id)
        assert result is True
        assert session_id not in manager.sessions

        # Try to delete again
        result = manager.delete_session(session_id)
        assert result is False

    def test_list_sessions(self):
        """Test listing all sessions."""
        manager = SessionManager()

        session1 = manager.create_session()
        session2 = manager.create_session()

        session_ids = manager.list_sessions()
        assert len(session_ids) == 2
        assert session1.session_id in session_ids
        assert session2.session_id in session_ids

    def test_cleanup_inactive_sessions(self):
        """Test cleaning up inactive sessions."""
        manager = SessionManager()

        # Create sessions with different activity times
        old_session = Session()
        old_session.last_activity = datetime.now() - timedelta(hours=25)
        manager.sessions[old_session.session_id] = old_session

        recent_session = manager.create_session()

        # Cleanup sessions older than 24 hours
        deleted_count = manager.cleanup_inactive_sessions(max_age_hours=24)

        assert deleted_count == 1
        assert old_session.session_id not in manager.sessions
        assert recent_session.session_id in manager.sessions
