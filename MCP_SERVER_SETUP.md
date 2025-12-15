# MCP Server Setup Guide

## Overview

The Talk-to-Me Claude MCP Server adds conversational capabilities to the voice narration system, enabling:
- Multi-turn conversation tracking
- Session state management
- Voice integration (TTS/STT)
- Conversation history persistence

## Requirements

- Python 3.10+ (required for MCP SDK)
- Claude Code CLI with MCP support
- OpenAI API key (for TTS/STT) or local providers

## Installation

### 1. Upgrade Python (if needed)

```bash
# Check current version
python3 --version

# If < 3.10, install Python 3.10+
# macOS (using Homebrew):
brew install python@3.10

# Or download from python.org
```

### 2. Install Dependencies

```bash
# Install all dependencies including MCP
pip3 install -r requirements.txt

# Or install MCP separately
pip3 install mcp>=0.9.0
```

### 3. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional
ELEVENLABS_API_KEY=your-key-here

# Provider Settings
TTS_PROVIDER=local              # elevenlabs, openai, or local
STT_PROVIDER=openai             # openai or local

# Narration Settings
NARRATION_ENABLED=true
AUTO_SPEAK=true
NARRATION_VERBOSITY=medium      # brief, medium, detailed
```

### 4. Configure Claude Code

Add the MCP server to Claude Code's configuration:

**Location:** `~/.config/claude-code/settings.json` (or your platform's config directory)

```json
{
  "mcpServers": {
    "talk-to-me-claude": {
      "command": "python3",
      "args": [
        "-m",
        "src.mcp_server.server"
      ],
      "cwd": "/full/path/to/talk-to-me-claude-cli",
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

Replace `/full/path/to/talk-to-me-claude-cli` with the actual path to this repository.

## Testing

### Run Unit Tests

```bash
# All unit tests
python3 -m pytest tests/unit/ -v

# Specific test file
python3 -m pytest tests/unit/test_session.py -v
```

### Run Integration Tests

Note: Integration tests require Python 3.10+ and MCP SDK installed.

```bash
# All integration tests
python3 -m pytest tests/integration/ -v

# Specific test
python3 -m pytest tests/integration/test_mcp_server.py -v
```

### Run All Tests

```bash
pytest -v
```

## Usage

### Starting the MCP Server Manually

```bash
# From project root
python3 -m src.mcp_server.server
```

The server will start with stdio transport and wait for MCP protocol messages.

### Using with Claude Code

Once configured, the MCP server will be automatically started by Claude Code when needed.

## Available Tools

The MCP server provides the following tools:

### 1. send_message
Send a message in the conversation with optional voice narration.

```json
{
  "text": "Your message here",
  "use_voice": true,
  "role": "user"
}
```

### 2. get_conversation_history
Retrieve conversation history.

```json
{
  "limit": 10  // Optional: limit to N most recent messages
}
```

### 3. clear_conversation
Clear the conversation history.

```json
{}
```

### 4. set_voice_settings
Configure voice settings.

```json
{
  "tts_provider": "openai",
  "tts_voice": "nova",
  "tts_speed": 1.2,
  "auto_speak": true,
  "narration_enabled": true,
  "verbosity": "medium"
}
```

### 5. get_voice_settings
Get current voice settings.

```json
{}
```

### 6. listen
Listen for voice input via STT.

```json
{
  "duration": 5.0  // Optional: recording duration in seconds
}
```

## Available Resources

### conversation://current
Current conversation session state (JSON).

### conversation://history
Full conversation history (JSON).

### conversation://settings
Current voice and narration settings (JSON).

### conversation://session/{session_id}
Access a specific conversation session by ID (JSON).

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Claude Code CLI                        │
│                    (MCP Client)                          │
└──────────────────────┬──────────────────────────────────┘
                       │ stdio transport
                       │
┌──────────────────────▼──────────────────────────────────┐
│        Talk-to-Me Claude MCP Server                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Session Manager                                   │ │
│  │  - Multi-session support                          │ │
│  │  - Conversation history tracking                  │ │
│  │  - Voice settings per session                     │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Voice Controller                                  │ │
│  │  - TTS integration (async, non-blocking)          │ │
│  │  - STT integration                                 │ │
│  │  - Narration extraction                           │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Troubleshooting

### MCP server not starting

1. Check Python version: `python3 --version` (must be 3.10+)
2. Verify MCP is installed: `pip3 list | grep mcp`
3. Check Claude Code logs for errors
4. Test server manually: `python3 -m src.mcp_server.server`

### Voice not working

1. Check TTS provider setting in `.env`
2. Verify API keys are set (for OpenAI/ElevenLabs)
3. Test TTS directly: `python3 -m src.voice.tts`
4. Check audio device permissions

### Tests failing

1. Install test dependencies: `pip3 install pytest pytest-asyncio`
2. Check Python version (3.9 for unit tests, 3.10+ for integration)
3. Verify imports: `python3 -c "from src.mcp_server.session import Session"`

### Session state not persisting

Sessions are currently in-memory only. They persist during the MCP server lifetime but are lost when the server restarts. Persistence layer is planned for a future release.

## Development

### Adding New Tools

1. Define tool schema in `src/mcp_server/tools.py` in `create_tools()`
2. Implement handler method in `ToolHandler` class
3. Add to routing in `handle_call_tool()`
4. Write unit tests in `tests/unit/test_tools.py`

### Adding New Resources

1. Define resource in `src/mcp_server/resources.py` in `create_resources()`
2. Implement handler method in `ResourceHandler` class
3. Add to routing in `handle_read_resource()`
4. Test with `pytest`

## Next Steps

- Add persistence layer (SQLite/JSON)
- Add conversation export functionality
- Add conversation templates
- Add multi-language support
- Add voice profile management

## Support

For issues or questions:
1. Check [CLAUDE.md](./CLAUDE.md) for development guidelines
2. Review [HOOKS.md](./HOOKS.md) for hook integration
3. Check test files for usage examples
4. Open an issue on GitHub

---

**Status:** Beta - MCP Server Implementation Complete
**Last Updated:** 2025-12-15
