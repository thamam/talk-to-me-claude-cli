"""MCP Server implementation for conversational voice layer.

Provides an MCP server that manages conversation sessions with voice integration.
"""

import asyncio
import logging
from typing import Any, Dict

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent

from .session import SessionManager
from .tools import ToolHandler, create_tools
from .resources import ResourceHandler, create_resources, create_resource_templates


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_server() -> Server:
    """Create and configure the MCP server.

    Returns:
        Configured Server instance
    """
    # Create server
    server = Server("talk-to-me-claude")

    # Create session manager
    session_manager = SessionManager()

    # Create handlers
    tool_handler = ToolHandler(session_manager)
    resource_handler = ResourceHandler(session_manager)

    # Register capabilities
    @server.list_tools()
    async def list_tools() -> list:
        """List available tools."""
        tools = create_tools()
        logger.info(f"Listed {len(tools)} tools")
        return tools

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
        """Execute a tool."""
        logger.info(f"Tool called: {name} with args: {arguments}")
        try:
            result = await tool_handler.handle_call_tool(name, arguments)
            logger.info(f"Tool {name} executed successfully")
            return result
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}", exc_info=True)
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]

    @server.list_resources()
    async def list_resources() -> list:
        """List available resources."""
        resources = create_resources()
        logger.info(f"Listed {len(resources)} resources")
        return resources

    @server.list_resource_templates()
    async def list_resource_templates() -> list:
        """List available resource templates."""
        templates = create_resource_templates()
        logger.info(f"Listed {len(templates)} resource templates")
        return templates

    @server.read_resource()
    async def read_resource(uri: str) -> list[TextContent]:
        """Read a resource."""
        logger.info(f"Resource read: {uri}")
        try:
            result = await resource_handler.handle_read_resource(uri)
            logger.info(f"Resource {uri} read successfully")
            return result
        except Exception as e:
            logger.error(f"Error reading resource {uri}: {e}", exc_info=True)
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]

    return server


async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting Talk-to-Me Claude MCP Server")

    # Create server
    server = create_server()

    # Run with stdio transport
    logger.info("Using stdio transport")
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Server started successfully")
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def run():
    """Synchronous entry point for running the server."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    run()
