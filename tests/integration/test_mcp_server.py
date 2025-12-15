"""Integration tests for MCP server.

Note: These tests verify the MCP server can be created and configured correctly.
Direct testing of MCP protocol requires a running server instance, which is
tested via the E2E tests and manual testing.
"""

import pytest

from src.mcp_server.server import create_server
from src.mcp_server.session import SessionManager
from src.mcp_server.tools import ToolHandler, create_tools
from src.mcp_server.resources import ResourceHandler, create_resources


class TestMCPServerSetup:
    """Integration tests for MCP server setup and configuration."""

    def test_create_server(self):
        """Test creating an MCP server."""
        server = create_server()
        assert server is not None
        assert server.name == "talk-to-me-claude"

    def test_tools_created(self):
        """Test that all expected tools are created."""
        tools = create_tools()

        assert isinstance(tools, list)
        assert len(tools) == 6  # We defined 6 tools

        tool_names = [tool.name for tool in tools]
        assert "send_message" in tool_names
        assert "get_conversation_history" in tool_names
        assert "clear_conversation" in tool_names
        assert "set_voice_settings" in tool_names
        assert "get_voice_settings" in tool_names
        assert "listen" in tool_names

    def test_resources_created(self):
        """Test that all expected resources are created."""
        resources = create_resources()

        assert isinstance(resources, list)
        assert len(resources) == 3  # We defined 3 static resources

        resource_uris = [str(resource.uri) for resource in resources]
        assert "conversation://current" in resource_uris
        assert "conversation://history" in resource_uris
        assert "conversation://settings" in resource_uris

    @pytest.mark.asyncio
    async def test_tool_handler_integration(self):
        """Test ToolHandler with SessionManager integration."""
        manager = SessionManager()
        handler = ToolHandler(manager)

        # Send a message
        result = await handler.send_message({
            "text": "Integration test message",
            "use_voice": False
        })

        assert isinstance(result, list)
        assert len(result) > 0

        # Verify it was added to session
        session = manager.get_current_session()
        assert len(session.history) == 1
        assert session.history[0].content == "Integration test message"

    @pytest.mark.asyncio
    async def test_resource_handler_integration(self):
        """Test ResourceHandler with SessionManager integration."""
        manager = SessionManager()
        handler = ResourceHandler(manager)

        # Add a message to session
        session = manager.get_current_session()
        session.add_message("user", "Test message")

        # Read current conversation
        result = await handler.read_current_conversation()

        assert isinstance(result, str)
        assert "session_id" in result
        assert "Test message" in result

    @pytest.mark.asyncio
    async def test_full_conversation_integration(self):
        """Test a complete conversation flow through handlers."""
        manager = SessionManager()
        tool_handler = ToolHandler(manager)
        resource_handler = ResourceHandler(manager)

        # 1. Send user message
        await tool_handler.send_message({
            "text": "Hello, world!",
            "role": "user"
        })

        # 2. Send assistant response
        await tool_handler.send_message({
            "text": "Hi there!",
            "role": "assistant"
        })

        # 3. Verify via resource
        history_json = await resource_handler.read_conversation_history()
        assert "Hello, world!" in history_json
        assert "Hi there!" in history_json
        assert "2" in history_json  # message_count: 2

        # 4. Get history via tool
        history_result = await tool_handler.get_conversation_history({})
        history_text = history_result[0].text
        assert "2 messages" in history_text

        # 5. Clear conversation
        clear_result = await tool_handler.clear_conversation({})
        assert "2 messages removed" in clear_result[0].text

        # 6. Verify cleared
        session = manager.get_current_session()
        assert len(session.history) == 0

    @pytest.mark.asyncio
    async def test_voice_settings_integration(self):
        """Test voice settings through handlers."""
        manager = SessionManager()
        tool_handler = ToolHandler(manager)
        resource_handler = ResourceHandler(manager)

        # Set voice settings via tool
        await tool_handler.set_voice_settings({
            "tts_provider": "openai",
            "tts_voice": "nova",
            "auto_speak": False
        })

        # Read via resource
        settings_json = await resource_handler.read_voice_settings()
        assert "openai" in settings_json
        assert "nova" in settings_json
        assert "false" in settings_json.lower()  # auto_speak: false

        # Verify via tool
        get_result = await tool_handler.get_voice_settings({})
        settings_text = get_result[0].text
        assert "openai" in settings_text
        assert "nova" in settings_text

    @pytest.mark.asyncio
    async def test_session_manager_cleanup_integration(self):
        """Test session cleanup functionality."""
        manager = SessionManager()

        # Create multiple sessions
        session1 = manager.create_session()
        session2 = manager.create_session()
        session3 = manager.create_session()

        assert len(manager.list_sessions()) == 3

        # Delete one
        manager.delete_session(session2.session_id)
        assert len(manager.list_sessions()) == 2

        # Cleanup (no old sessions to clean)
        deleted = manager.cleanup_inactive_sessions(max_age_hours=24)
        assert deleted == 0  # All sessions are recent
