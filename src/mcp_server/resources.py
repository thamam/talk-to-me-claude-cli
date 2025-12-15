"""MCP resources implementation.

Defines the resources exposed by the MCP server for conversation access.
"""

import json
from typing import List

from mcp.types import Resource, TextContent, ResourceTemplate

from .session import SessionManager


def create_resources() -> List[Resource]:
    """Create the list of MCP resources.

    Returns:
        List of Resource objects
    """
    return [
        Resource(
            uri="conversation://current",
            name="Current Conversation",
            description="The current conversation session state",
            mimeType="application/json"
        ),
        Resource(
            uri="conversation://history",
            name="Conversation History",
            description="Full conversation history in the current session",
            mimeType="application/json"
        ),
        Resource(
            uri="conversation://settings",
            name="Voice Settings",
            description="Current voice and narration settings",
            mimeType="application/json"
        )
    ]


def create_resource_templates() -> List[ResourceTemplate]:
    """Create resource templates for dynamic resources.

    Returns:
        List of ResourceTemplate objects
    """
    return [
        ResourceTemplate(
            uriTemplate="conversation://session/{session_id}",
            name="Conversation Session",
            description="Access a specific conversation session by ID",
            mimeType="application/json"
        )
    ]


class ResourceHandler:
    """Handles reading of MCP resources."""

    def __init__(self, session_manager: SessionManager):
        """Initialize resource handler.

        Args:
            session_manager: The session manager instance
        """
        self.session_manager = session_manager

    async def read_current_conversation(self) -> str:
        """Read the current conversation resource.

        Returns:
            JSON string of current session
        """
        session = self.session_manager.get_current_session()
        return json.dumps(session.to_dict(), indent=2)

    async def read_conversation_history(self) -> str:
        """Read the conversation history resource.

        Returns:
            JSON string of conversation history
        """
        session = self.session_manager.get_current_session()
        history_data = {
            "session_id": session.session_id,
            "message_count": len(session.history),
            "messages": [msg.to_dict() for msg in session.history]
        }
        return json.dumps(history_data, indent=2)

    async def read_voice_settings(self) -> str:
        """Read the voice settings resource.

        Returns:
            JSON string of voice settings
        """
        session = self.session_manager.get_current_session()
        return json.dumps(session.voice_settings, indent=2)

    async def read_session(self, session_id: str) -> str:
        """Read a specific session resource.

        Args:
            session_id: Session identifier

        Returns:
            JSON string of session data

        Raises:
            ValueError: If session not found
        """
        session = self.session_manager.get_session(session_id)
        if session is None:
            raise ValueError(f"Session not found: {session_id}")

        return json.dumps(session.to_dict(), indent=2)

    async def handle_read_resource(self, uri: str) -> List[TextContent]:
        """Route resource reads to the appropriate handler.

        Args:
            uri: Resource URI

        Returns:
            List of TextContent responses
        """
        try:
            if uri == "conversation://current":
                content = await self.read_current_conversation()
            elif uri == "conversation://history":
                content = await self.read_conversation_history()
            elif uri == "conversation://settings":
                content = await self.read_voice_settings()
            elif uri.startswith("conversation://session/"):
                session_id = uri.split("/")[-1]
                content = await self.read_session(session_id)
            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown resource: {uri}"
                )]

            return [TextContent(
                type="text",
                text=content
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error reading resource {uri}: {str(e)}"
            )]
