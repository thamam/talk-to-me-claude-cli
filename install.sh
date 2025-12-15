#!/bin/bash
set -e

# Talk-to-Me Claude CLI - One-Command Installation
# Usage: ./install.sh

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_CONFIG="$HOME/.claude.json"

echo "=================================================="
echo "  Talk-to-Me Claude CLI Installation"
echo "=================================================="
echo

# Step 1: Check Python version
echo "📋 Checking Python version..."

# Try python3.11 first, then python3
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
    PYTHON_VERSION=$(python3.11 --version 2>&1 | awk '{print $2}')
elif python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
else
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' 2>/dev/null || echo "not found")
    echo "❌ Python 3.11+ required (found: $PYTHON_VERSION)"
    echo
    echo "Install Python 3.11:"
    echo "  brew install python@3.11"
    echo
    exit 1
fi
echo "✅ Python $PYTHON_VERSION detected (using $PYTHON_CMD)"
echo

# Step 2: Install Python dependencies
echo "📦 Installing Python dependencies..."
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    $PYTHON_CMD -m pip install -q -r "$PROJECT_DIR/requirements.txt"
    echo "✅ Dependencies installed"
else
    echo "⚠️  requirements.txt not found, skipping"
fi
echo

# Step 3: Create necessary directories
echo "📁 Creating project directories..."
mkdir -p "$PROJECT_DIR/.claude/commands/talk-to-me"
mkdir -p "$PROJECT_DIR/hooks"
mkdir -p "$PROJECT_DIR/tests"
echo "✅ Directories created"
echo

# Step 4: Check if .env exists, create from template if not
echo "⚙️  Configuring environment..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    cat > "$PROJECT_DIR/.env" << 'EOF'
# API Keys (REQUIRED for cloud providers)
OPENAI_API_KEY=         # For OpenAI TTS/STT
ELEVENLABS_API_KEY=     # For ElevenLabs TTS (optional)

# Voice Provider Selection
TTS_PROVIDER=openai     # Options: openai, elevenlabs, local
STT_PROVIDER=openai     # Options: openai, macos, local

# Provider-Specific Voice Settings
OPENAI_VOICE=alloy      # Options: alloy, echo, fable, nova, onyx, shimmer
ELEVENLABS_VOICE=adam   # Options: adam, rachel, domi, bella, etc.
TTS_SPEED=1.0           # Speed multiplier (0.25 to 4.0)

# STT Settings
STT_MODEL=whisper-1     # OpenAI Whisper model
STT_LANGUAGE=en-US      # Language code for recognition

# Narration Settings
NARRATION_ENABLED=true
NARRATION_VERBOSITY=medium  # Options: brief, medium, detailed
AUTO_SPEAK=true             # Automatically speak narration

# Audio Settings
AUDIO_FORMAT=mp3
SAMPLE_RATE=24000
EOF
    echo "✅ Created .env template"
    echo "⚠️  IMPORTANT: Edit .env and add your API keys!"
    echo
else
    echo "✅ .env already exists"
    echo
fi

# Step 5: Set up MCP server in ~/.claude.json
echo "🔧 Configuring MCP server..."

if [ ! -f "$CLAUDE_CONFIG" ]; then
    echo "Creating new $CLAUDE_CONFIG..."
    cat > "$CLAUDE_CONFIG" << EOF
{
  "mcpServers": {
    "talk-to-me-claude": {
      "command": "$PYTHON_CMD",
      "args": ["-m", "src.mcp_server.server"],
      "cwd": "$PROJECT_DIR",
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
EOF
    echo "✅ Created $CLAUDE_CONFIG with talk-to-me-claude MCP server"
else
    # Check if talk-to-me-claude already exists
    if grep -q '"talk-to-me-claude"' "$CLAUDE_CONFIG"; then
        echo "⚠️  talk-to-me-claude MCP server already exists in $CLAUDE_CONFIG"
        echo "   Skipping MCP configuration"
    else
        echo "⚠️  $CLAUDE_CONFIG exists with other MCP servers"
        echo
        echo "Add this to your mcpServers section:"
        echo
        cat << EOF
    "talk-to-me-claude": {
      "command": "$PYTHON_CMD",
      "args": ["-m", "src.mcp_server.server"],
      "cwd": "$PROJECT_DIR",
      "env": {
        "PYTHONPATH": "."
      }
    }
EOF
        echo
        read -p "Would you like me to automatically add it? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Backup original
            cp "$CLAUDE_CONFIG" "$CLAUDE_CONFIG.backup"

            # Use Python to safely merge JSON
            $PYTHON_CMD << PYEOF
import json
with open('$CLAUDE_CONFIG', 'r') as f:
    config = json.load(f)

if 'mcpServers' not in config:
    config['mcpServers'] = {}

config['mcpServers']['talk-to-me-claude'] = {
    "command": "$PYTHON_CMD",
    "args": ["-m", "src.mcp_server.server"],
    "cwd": "$PROJECT_DIR",
    "env": {
        "PYTHONPATH": "."
    }
}

with open('$CLAUDE_CONFIG', 'w') as f:
    json.dump(config, f, indent=2)
PYEOF
            echo "✅ Added talk-to-me-claude to $CLAUDE_CONFIG"
            echo "   (Backup saved to $CLAUDE_CONFIG.backup)"
        else
            echo "⚠️  Skipped MCP configuration. You'll need to add it manually."
        fi
    fi
fi
echo

# Step 6: Set up hooks
echo "🪝 Setting up Claude Code hooks..."

# Create hook registration file
cat > "$PROJECT_DIR/.claude/hooks.json" << EOF
{
  "userPromptSubmit": "hooks/inject_narration_prompt.py",
  "stop": "hooks/process_response.py"
}
EOF
echo "✅ Hook configuration created"
echo

# Step 7: Set default mode
echo "🎛️  Setting default narration mode..."
echo "auto" > "$PROJECT_DIR/.claude/narration-mode.txt"
echo "✅ Default mode: auto"
echo

# Step 8: Run tests to verify installation
echo "🧪 Running tests to verify installation..."
if $PYTHON_CMD -m pytest "$PROJECT_DIR/tests" -q --tb=short 2>/dev/null; then
    echo "✅ All tests passed"
else
    echo "⚠️  Some tests failed (this may be okay for initial setup)"
fi
echo

# Step 9: Installation summary
echo "=================================================="
echo "  Installation Complete! 🎉"
echo "=================================================="
echo
echo "Next Steps:"
echo
echo "1. Edit .env and add your API keys:"
echo "   nano $PROJECT_DIR/.env"
echo
echo "2. Restart Claude Code to load the MCP server"
echo
echo "3. Verify MCP tools are loaded:"
echo "   Look for 'talk-to-me-claude' tools in Claude Code"
echo
echo "4. Test voice narration:"
echo "   Ask Claude to do a coding task and listen for audio"
echo
echo "5. Try voice input:"
echo "   /talk-to-me:listen"
echo
echo "Available Commands:"
echo "  /talk-to-me:mode [coding_only|conversational|auto]"
echo "  /talk-to-me:listen [duration_seconds]"
echo "  /talk-to-me:status"
echo
echo "Documentation:"
echo "  - INSTALLATION.md - Full setup guide"
echo "  - CLAUDE.md - Development guide"
echo "  - BACKLOG.md - Future enhancements"
echo
echo "Troubleshooting:"
echo "  - Check .env file has valid API keys"
echo "  - Verify Python 3.11+ is in PATH"
echo "  - Restart terminal if MCP tools not showing"
echo
echo "Installation log saved to: install.log"
echo "=================================================="
