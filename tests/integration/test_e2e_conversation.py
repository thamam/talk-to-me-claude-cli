"""End-to-end tests for conversation flow with voice."""

import pytest
from unittest.mock import patch, Mock

from src.mcp_server.session import SessionManager
from src.mcp_server.voice_controller import VoiceController
from src.mcp_server.tools import ToolHandler


class TestE2EConversation:
    """End-to-end conversation flow tests."""

    @pytest.mark.asyncio
    async def test_multi_turn_conversation(self):
        """Test multi-turn conversation with context persistence."""
        manager = SessionManager()
        handler = ToolHandler(manager)

        # Turn 1: User asks a question
        await handler.send_message({
            "text": "Can you help me with authentication?",
            "role": "user"
        })

        # Turn 2: Assistant responds
        await handler.send_message({
            "text": "Yes, I can help with authentication.",
            "role": "assistant"
        })

        # Turn 3: User asks follow-up
        await handler.send_message({
            "text": "How do I implement JWT?",
            "role": "user"
        })

        # Turn 4: Assistant responds
        await handler.send_message({
            "text": "Here's how to implement JWT...",
            "role": "assistant"
        })

        # Verify all messages are in history
        session = manager.get_current_session()
        assert len(session.history) == 4

        # Verify conversation order
        assert session.history[0].content == "Can you help me with authentication?"
        assert session.history[1].content == "Yes, I can help with authentication."
        assert session.history[2].content == "How do I implement JWT?"
        assert session.history[3].content == "Here's how to implement JWT..."

        # Verify roles
        assert session.history[0].role == "user"
        assert session.history[1].role == "assistant"
        assert session.history[2].role == "user"
        assert session.history[3].role == "assistant"

    @pytest.mark.asyncio
    @patch('src.mcp_server.voice_controller.subprocess.Popen')
    async def test_conversation_with_voice_narration(self, mock_popen):
        """Test conversation with voice narration extraction and TTS."""
        manager = SessionManager()
        handler = ToolHandler(manager)

        # Send message with narration
        await handler.send_message({
            "text": """
            I've added error handling to the login function.

            [VOICE_NARRATION]
            I strengthened the authentication by adding comprehensive error
            handling that catches invalid credentials and network failures.
            [/VOICE_NARRATION]

            The changes include:
            - Added try-catch blocks
            - Improved error messages
            """,
            "role": "assistant",
            "use_voice": True
        })

        # Verify message was stored
        session = manager.get_current_session()
        assert len(session.history) == 1

        # Verify narration was extracted
        message = session.history[0]
        assert message.narration is not None
        assert "strengthened the authentication" in message.narration

        # Verify TTS was called (background process)
        mock_popen.assert_called_once()

    @pytest.mark.asyncio
    async def test_voice_settings_change_mid_conversation(self):
        """Test changing voice settings during conversation."""
        manager = SessionManager()
        handler = ToolHandler(manager)

        # Start conversation with default settings
        session = manager.get_current_session()
        assert session.voice_settings["tts_provider"] == "local"

        # Send first message
        await handler.send_message({
            "text": "First message",
            "role": "user"
        })

        # Change voice settings
        await handler.set_voice_settings({
            "tts_provider": "openai",
            "tts_voice": "nova",
            "auto_speak": False
        })

        # Send second message
        await handler.send_message({
            "text": "Second message",
            "role": "user"
        })

        # Verify settings were updated
        assert session.voice_settings["tts_provider"] == "openai"
        assert session.voice_settings["tts_voice"] == "nova"
        assert session.voice_settings["auto_speak"] is False

        # Verify both messages are in history
        assert len(session.history) == 2

    @pytest.mark.asyncio
    async def test_conversation_history_retrieval_at_different_points(self):
        """Test retrieving history at different conversation points."""
        manager = SessionManager()
        handler = ToolHandler(manager)

        # Initially empty
        result = await handler.get_conversation_history({})
        assert "No conversation history" in result[0].text

        # After 1 message
        await handler.send_message({"text": "Message 1", "role": "user"})
        result = await handler.get_conversation_history({})
        assert "1 messages" in result[0].text

        # After 3 messages
        await handler.send_message({"text": "Message 2", "role": "assistant"})
        await handler.send_message({"text": "Message 3", "role": "user"})
        result = await handler.get_conversation_history({})
        assert "3 messages" in result[0].text

        # Get limited history (last 2)
        result = await handler.get_conversation_history({"limit": 2})
        text = result[0].text
        assert "2 messages" in text
        assert "Message 1" not in text  # Oldest excluded
        assert "Message 2" in text
        assert "Message 3" in text

    @pytest.mark.asyncio
    async def test_clear_and_restart_conversation(self):
        """Test clearing conversation and starting fresh."""
        manager = SessionManager()
        handler = ToolHandler(manager)

        # First conversation
        await handler.send_message({"text": "First conversation, message 1"})
        await handler.send_message({"text": "First conversation, message 2"})

        session = manager.get_current_session()
        first_session_id = session.session_id
        assert len(session.history) == 2

        # Clear conversation
        await handler.clear_conversation({})
        assert len(session.history) == 0

        # Start new conversation (same session)
        await handler.send_message({"text": "Second conversation, message 1"})

        assert len(session.history) == 1
        assert session.history[0].content == "Second conversation, message 1"
        assert session.session_id == first_session_id  # Same session

    @pytest.mark.asyncio
    @patch('src.mcp_server.voice_controller.subprocess.Popen')
    async def test_narration_verbosity_affects_output(self, mock_popen):
        """Test that verbosity setting affects narration."""
        manager = SessionManager()
        handler = ToolHandler(manager)

        # Set to brief
        await handler.set_voice_settings({"verbosity": "brief"})

        session = manager.get_current_session()
        assert session.voice_settings["verbosity"] == "brief"

        # Set to detailed
        await handler.set_voice_settings({"verbosity": "detailed"})
        assert session.voice_settings["verbosity"] == "detailed"

    @pytest.mark.asyncio
    async def test_session_persistence_across_operations(self):
        """Test that session persists across different operations."""
        manager = SessionManager()
        handler = ToolHandler(manager)

        # Get initial session
        initial_session = manager.get_current_session()
        initial_id = initial_session.session_id

        # Perform various operations
        await handler.send_message({"text": "Message 1"})
        await handler.set_voice_settings({"auto_speak": False})
        await handler.send_message({"text": "Message 2"})
        await handler.get_conversation_history({})

        # Verify session is still the same
        current_session = manager.get_current_session()
        assert current_session.session_id == initial_id
        assert len(current_session.history) == 2
        assert current_session.voice_settings["auto_speak"] is False

    @pytest.mark.asyncio
    @patch('src.mcp_server.voice_controller.subprocess.Popen')
    async def test_voice_controller_integration(self, mock_popen):
        """Test VoiceController integration with session."""
        session = SessionManager().get_current_session()
        controller = VoiceController(session)

        # Test message processing with narration
        text = "[VOICE_NARRATION]Summary[/VOICE_NARRATION]Full content"

        processed_text, narration = controller.process_message_sync(text, extract_voice=True)

        assert processed_text == text
        assert "Summary" in narration

        # Verify TTS was triggered
        mock_popen.assert_called_once()

    @pytest.mark.asyncio
    async def test_empty_message_handling(self):
        """Test handling of edge cases like empty messages."""
        manager = SessionManager()
        handler = ToolHandler(manager)

        # Send empty-like messages
        await handler.send_message({"text": "", "role": "user"})
        await handler.send_message({"text": "   ", "role": "user"})

        session = manager.get_current_session()
        assert len(session.history) == 2

        # Both should be stored
        assert session.history[0].content == ""
        assert session.history[1].content == "   "

    @pytest.mark.asyncio
    @patch('src.mcp_server.voice_controller.subprocess.Popen')
    async def test_narration_extraction_with_multiple_tags(self, mock_popen):
        """Test narration extraction when multiple tags present."""
        manager = SessionManager()
        handler = ToolHandler(manager)

        # Message with multiple narration tags (only first should be used)
        text = """
        [VOICE_NARRATION]First narration[/VOICE_NARRATION]
        Some content
        [VOICE_NARRATION]Second narration[/VOICE_NARRATION]
        """

        await handler.send_message({
            "text": text,
            "role": "assistant",
            "use_voice": True
        })

        session = manager.get_current_session()
        message = session.history[0]

        # Should extract first narration
        assert message.narration is not None
        assert "First narration" in message.narration
