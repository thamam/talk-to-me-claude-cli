"""Unit tests for voice controller."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.mcp_server.session import Session
from src.mcp_server.voice_controller import VoiceController


class TestVoiceController:
    """Tests for VoiceController class."""

    def test_create_controller(self):
        """Test creating a voice controller."""
        session = Session()
        controller = VoiceController(session)

        assert controller.session is session
        assert controller._tts_provider is None
        assert controller._stt_provider is None

    def test_extract_narration_no_tags(self):
        """Test extracting narration when no tags present."""
        session = Session()
        controller = VoiceController(session)

        text = "Regular text without narration tags"
        narration = controller.extract_and_speak_narration(text)

        assert narration is None

    def test_extract_narration_with_tags(self):
        """Test extracting narration from text with tags."""
        session = Session()
        controller = VoiceController(session)

        text = """
        Some output here.

        [VOICE_NARRATION]
        This is the narration to be spoken.
        [/VOICE_NARRATION]

        More output.
        """

        with patch.object(controller, 'speak_async'):
            narration = controller.extract_and_speak_narration(text)

        assert narration is not None
        assert "This is the narration to be spoken" in narration

    def test_extract_narration_disabled(self):
        """Test narration extraction when disabled."""
        session = Session()
        session.voice_settings["narration_enabled"] = False
        controller = VoiceController(session)

        text = "[VOICE_NARRATION]Test[/VOICE_NARRATION]"

        with patch.object(controller, 'speak_async') as mock_speak:
            narration = controller.extract_and_speak_narration(text)

        # Should still extract but not speak
        assert narration is not None
        mock_speak.assert_not_called()

    def test_extract_narration_auto_speak_disabled(self):
        """Test narration with auto_speak disabled."""
        session = Session()
        session.voice_settings["auto_speak"] = False
        controller = VoiceController(session)

        text = "[VOICE_NARRATION]Test[/VOICE_NARRATION]"

        with patch.object(controller, 'speak_async') as mock_speak:
            narration = controller.extract_and_speak_narration(text)

        assert narration is not None
        mock_speak.assert_not_called()

    @patch('src.mcp_server.voice_controller.subprocess.Popen')
    def test_speak_async(self, mock_popen):
        """Test asynchronous speech."""
        session = Session()
        controller = VoiceController(session)

        controller.speak_async("Test text")

        mock_popen.assert_called_once()

    def test_update_settings(self):
        """Test updating voice settings."""
        session = Session()
        controller = VoiceController(session)

        # Initial provider should be None
        assert controller._tts_provider is None

        # Update settings
        controller.update_settings(
            tts_provider="openai",
            tts_voice="nova",
            auto_speak=False
        )

        # Check settings were updated
        assert session.voice_settings["tts_provider"] == "openai"
        assert session.voice_settings["tts_voice"] == "nova"
        assert session.voice_settings["auto_speak"] is False

    def test_update_settings_invalidates_provider(self):
        """Test that updating settings invalidates cached providers."""
        session = Session()
        controller = VoiceController(session)

        # Set a mock provider
        controller._tts_provider = Mock()

        # Update TTS settings
        controller.update_settings(tts_provider="openai")

        # Provider should be invalidated
        assert controller._tts_provider is None

    def test_process_message_sync(self):
        """Test synchronous message processing."""
        session = Session()
        controller = VoiceController(session)

        text = "[VOICE_NARRATION]Summary[/VOICE_NARRATION]Full text"

        with patch.object(controller, 'speak_async'):
            result_text, narration = controller.process_message_sync(text)

        assert result_text == text
        assert "Summary" in narration

    def test_process_message_sync_no_extraction(self):
        """Test message processing without extraction."""
        session = Session()
        controller = VoiceController(session)

        text = "[VOICE_NARRATION]Summary[/VOICE_NARRATION]Full text"

        with patch.object(controller, 'extract_and_speak_narration') as mock_extract:
            result_text, narration = controller.process_message_sync(text, extract_voice=False)

        assert result_text == text
        assert narration is None
        mock_extract.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_message_async(self):
        """Test asynchronous message processing."""
        session = Session()
        controller = VoiceController(session)

        text = "[VOICE_NARRATION]Summary[/VOICE_NARRATION]Full text"

        with patch.object(controller, 'speak_async'):
            result_text, narration = await controller.process_message_async(text)

        assert result_text == text
        assert "Summary" in narration
