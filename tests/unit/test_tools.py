"""Unit tests for MCP tools."""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from mcp.types import TextContent

from src.mcp_server.session import SessionManager
from src.mcp_server.tools import ToolHandler, create_tools


class TestCreateTools:
    """Tests for create_tools function."""

    def test_create_tools_returns_list(self):
        """Test that create_tools returns a list."""
        tools = create_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0

    def test_all_tools_have_required_fields(self):
        """Test that all tools have required fields."""
        tools = create_tools()

        for tool in tools:
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'inputSchema')

    def test_expected_tools_present(self):
        """Test that expected tools are present."""
        tools = create_tools()
        tool_names = [tool.name for tool in tools]

        assert "send_message" in tool_names
        assert "get_conversation_history" in tool_names
        assert "clear_conversation" in tool_names
        assert "set_voice_settings" in tool_names
        assert "get_voice_settings" in tool_names
        assert "listen" in tool_names


class TestToolHandler:
    """Tests for ToolHandler class."""

    def test_create_handler(self):
        """Test creating a tool handler."""
        manager = SessionManager()
        handler = ToolHandler(manager)

        assert handler.session_manager is manager

    @pytest.mark.asyncio
    async def test_send_message(self):
        """Test send_message tool."""
        manager = SessionManager()
        handler = ToolHandler(manager)

        arguments = {
            "text": "Hello, world!",
            "use_voice": False,
            "role": "user"
        }

        result = await handler.send_message(arguments)

        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], TextContent)

        # Check message was added to session
        session = manager.get_current_session()
        assert len(session.history) == 1
        assert session.history[0].content == "Hello, world!"
        assert session.history[0].role == "user"

    @pytest.mark.asyncio
    async def test_send_message_with_voice(self):
        """Test send_message with voice enabled."""
        manager = SessionManager()
        handler = ToolHandler(manager)

        arguments = {
            "text": "[VOICE_NARRATION]Summary[/VOICE_NARRATION]Full message",
            "use_voice": True,
            "role": "assistant"
        }

        with patch('src.mcp_server.voice_controller.subprocess.Popen'):
            result = await handler.send_message(arguments)

        assert isinstance(result, list)

        # Check message was added with narration
        session = manager.get_current_session()
        assert len(session.history) == 1
        assert session.history[0].narration is not None
        assert "Summary" in session.history[0].narration

    @pytest.mark.asyncio
    async def test_get_conversation_history_empty(self):
        """Test getting history from empty conversation."""
        manager = SessionManager()
        handler = ToolHandler(manager)

        result = await handler.get_conversation_history({})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "No conversation history" in result[0].text

    @pytest.mark.asyncio
    async def test_get_conversation_history(self):
        """Test getting conversation history."""
        manager = SessionManager()
        handler = ToolHandler(manager)

        # Add some messages
        session = manager.get_current_session()
        session.add_message("user", "Message 1")
        session.add_message("assistant", "Response 1")
        session.add_message("user", "Message 2")

        result = await handler.get_conversation_history({})

        assert isinstance(result, list)
        assert len(result) > 0
        text = result[0].text
        assert "3 messages" in text
        assert "Message 1" in text
        assert "Response 1" in text
        assert "Message 2" in text

    @pytest.mark.asyncio
    async def test_get_conversation_history_with_limit(self):
        """Test getting limited conversation history."""
        manager = SessionManager()
        handler = ToolHandler(manager)

        # Add some messages
        session = manager.get_current_session()
        session.add_message("user", "Message 1")
        session.add_message("assistant", "Response 1")
        session.add_message("user", "Message 2")

        result = await handler.get_conversation_history({"limit": 2})

        text = result[0].text
        assert "2 messages" in text
        assert "Message 1" not in text  # Oldest should be excluded
        assert "Response 1" in text
        assert "Message 2" in text

    @pytest.mark.asyncio
    async def test_clear_conversation(self):
        """Test clearing conversation."""
        manager = SessionManager()
        handler = ToolHandler(manager)

        # Add some messages
        session = manager.get_current_session()
        session.add_message("user", "Message 1")
        session.add_message("user", "Message 2")

        result = await handler.clear_conversation({})

        assert isinstance(result, list)
        assert "2 messages removed" in result[0].text

        # Verify history is cleared
        assert len(session.history) == 0

    @pytest.mark.asyncio
    async def test_set_voice_settings(self):
        """Test setting voice settings."""
        manager = SessionManager()
        handler = ToolHandler(manager)

        arguments = {
            "tts_provider": "openai",
            "tts_voice": "nova",
            "auto_speak": False,
            "verbosity": "detailed"
        }

        result = await handler.set_voice_settings(arguments)

        assert isinstance(result, list)
        text = result[0].text
        assert "Voice settings updated" in text
        assert "tts_provider" in text
        assert "openai" in text

        # Verify settings were updated
        session = manager.get_current_session()
        assert session.voice_settings["tts_provider"] == "openai"
        assert session.voice_settings["tts_voice"] == "nova"
        assert session.voice_settings["auto_speak"] is False
        assert session.voice_settings["verbosity"] == "detailed"

    @pytest.mark.asyncio
    async def test_get_voice_settings(self):
        """Test getting voice settings."""
        manager = SessionManager()
        handler = ToolHandler(manager)

        result = await handler.get_voice_settings({})

        assert isinstance(result, list)
        text = result[0].text
        assert "Current voice settings" in text
        assert "tts_provider" in text
        assert "auto_speak" in text

    @pytest.mark.asyncio
    async def test_handle_call_tool_routing(self):
        """Test that handle_call_tool routes to correct handler."""
        manager = SessionManager()
        handler = ToolHandler(manager)

        # Test routing to clear_conversation
        result = await handler.handle_call_tool("clear_conversation", {})
        assert isinstance(result, list)

        # Test unknown tool
        result = await handler.handle_call_tool("unknown_tool", {})
        assert "Unknown tool" in result[0].text

    @pytest.mark.asyncio
    async def test_send_message_defaults(self):
        """Test send_message with default values."""
        manager = SessionManager()
        handler = ToolHandler(manager)

        # Only provide required text argument
        arguments = {"text": "Test message"}

        result = await handler.send_message(arguments)

        session = manager.get_current_session()
        assert len(session.history) == 1
        assert session.history[0].role == "user"  # Default role
        assert session.history[0].narration is None  # use_voice=False by default
