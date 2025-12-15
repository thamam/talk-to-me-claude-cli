"""MCP tools implementation.

Defines the tools exposed by the MCP server for conversation management.
"""

from typing import Any, Dict, List, Optional

from mcp.types import Tool, TextContent

from .session import SessionManager
from .voice_controller import VoiceController


def create_tools() -> List[Tool]:
    """Create the list of MCP tools.

    Returns:
        List of Tool objects
    """
    return [
        Tool(
            name="send_message",
            description="Send a message in the conversation with optional voice narration",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The message text to send"
                    },
                    "use_voice": {
                        "type": "boolean",
                        "description": "Whether to enable voice narration for this message",
                        "default": False
                    },
                    "role": {
                        "type": "string",
                        "description": "Message role (user or assistant)",
                        "enum": ["user", "assistant"],
                        "default": "user"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="get_conversation_history",
            description="Get the conversation history",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of recent messages to return (omit for all)",
                        "minimum": 1
                    }
                }
            }
        ),
        Tool(
            name="clear_conversation",
            description="Clear the conversation history",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="set_voice_settings",
            description="Configure voice settings for TTS and STT",
            inputSchema={
                "type": "object",
                "properties": {
                    "tts_provider": {
                        "type": "string",
                        "description": "TTS provider to use",
                        "enum": ["elevenlabs", "openai", "local"]
                    },
                    "stt_provider": {
                        "type": "string",
                        "description": "STT provider to use",
                        "enum": ["openai", "local", "macos"]
                    },
                    "tts_voice": {
                        "type": "string",
                        "description": "Voice to use for TTS"
                    },
                    "tts_speed": {
                        "type": "number",
                        "description": "Speech speed (0.25 to 4.0)",
                        "minimum": 0.25,
                        "maximum": 4.0
                    },
                    "auto_speak": {
                        "type": "boolean",
                        "description": "Automatically speak narration"
                    },
                    "narration_enabled": {
                        "type": "boolean",
                        "description": "Enable narration extraction"
                    },
                    "verbosity": {
                        "type": "string",
                        "description": "Narration verbosity level",
                        "enum": ["brief", "medium", "detailed"]
                    }
                }
            }
        ),
        Tool(
            name="get_voice_settings",
            description="Get current voice settings",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="listen",
            description="Listen for voice input and transcribe to text",
            inputSchema={
                "type": "object",
                "properties": {
                    "duration": {
                        "type": "number",
                        "description": "Recording duration in seconds (omit to use Enter key to stop)",
                        "minimum": 0.1
                    }
                }
            }
        )
    ]


class ToolHandler:
    """Handles execution of MCP tools."""

    def __init__(self, session_manager: SessionManager):
        """Initialize tool handler.

        Args:
            session_manager: The session manager instance
        """
        self.session_manager = session_manager

    async def send_message(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle send_message tool.

        Args:
            arguments: Tool arguments

        Returns:
            List of TextContent responses
        """
        text = arguments["text"]
        use_voice = arguments.get("use_voice", False)
        role = arguments.get("role", "user")

        session = self.session_manager.get_current_session()
        voice_controller = VoiceController(session)

        # Process message with voice if requested
        if use_voice:
            _, narration = voice_controller.process_message_sync(text, extract_voice=True)
        else:
            narration = None

        # Add to conversation history
        message = session.add_message(role=role, content=text, narration=narration)

        result = {
            "status": "sent",
            "message_role": message.role,
            "message_content": message.content,
            "narration": message.narration,
            "timestamp": message.timestamp.isoformat()
        }

        return [TextContent(
            type="text",
            text=f"Message sent:\n{text}\n\nNarration: {narration or 'none'}"
        )]

    async def get_conversation_history(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_conversation_history tool.

        Args:
            arguments: Tool arguments

        Returns:
            List of TextContent responses
        """
        limit = arguments.get("limit")

        session = self.session_manager.get_current_session()
        history = session.get_history(limit=limit)

        if not history:
            return [TextContent(
                type="text",
                text="No conversation history"
            )]

        # Format history as text
        lines = [f"Conversation history ({len(history)} messages):"]
        lines.append("")

        for i, msg in enumerate(history, 1):
            lines.append(f"{i}. [{msg.role}] ({msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')})")
            lines.append(f"   {msg.content}")
            if msg.narration:
                lines.append(f"   [Narration: {msg.narration}]")
            lines.append("")

        return [TextContent(
            type="text",
            text="\n".join(lines)
        )]

    async def clear_conversation(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle clear_conversation tool.

        Args:
            arguments: Tool arguments

        Returns:
            List of TextContent responses
        """
        session = self.session_manager.get_current_session()
        message_count = len(session.history)
        session.clear()

        return [TextContent(
            type="text",
            text=f"Conversation cleared ({message_count} messages removed)"
        )]

    async def set_voice_settings(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle set_voice_settings tool.

        Args:
            arguments: Tool arguments

        Returns:
            List of TextContent responses
        """
        session = self.session_manager.get_current_session()
        voice_controller = VoiceController(session)

        # Update settings
        voice_controller.update_settings(**arguments)

        # Format updated settings
        lines = ["Voice settings updated:"]
        for key, value in arguments.items():
            lines.append(f"  {key}: {value}")

        return [TextContent(
            type="text",
            text="\n".join(lines)
        )]

    async def get_voice_settings(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_voice_settings tool.

        Args:
            arguments: Tool arguments

        Returns:
            List of TextContent responses
        """
        session = self.session_manager.get_current_session()

        lines = ["Current voice settings:"]
        for key, value in session.voice_settings.items():
            lines.append(f"  {key}: {value}")

        return [TextContent(
            type="text",
            text="\n".join(lines)
        )]

    async def listen(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle listen tool.

        Args:
            arguments: Tool arguments

        Returns:
            List of TextContent responses
        """
        duration = arguments.get("duration")

        session = self.session_manager.get_current_session()
        voice_controller = VoiceController(session)

        try:
            text = voice_controller.listen(duration=duration)
            return [TextContent(
                type="text",
                text=f"Transcribed: {text}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error during voice input: {str(e)}"
            )]

    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Route tool calls to the appropriate handler.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            List of TextContent responses
        """
        handlers = {
            "send_message": self.send_message,
            "get_conversation_history": self.get_conversation_history,
            "clear_conversation": self.clear_conversation,
            "set_voice_settings": self.set_voice_settings,
            "get_voice_settings": self.get_voice_settings,
            "listen": self.listen,
        }

        handler = handlers.get(name)
        if handler is None:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]

        return await handler(arguments)
