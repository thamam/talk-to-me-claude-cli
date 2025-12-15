"""MCP Server for Conversational Voice Layer.

This module provides an MCP (Model Context Protocol) server that adds
conversational capabilities to the voice narration system.
"""

try:
    from .server import create_server
    __all__ = ["create_server"]
except ImportError:
    # MCP not installed, server functionality unavailable
    __all__ = []
