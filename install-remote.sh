#!/bin/bash
set -e

# Talk-to-Me Claude CLI - Remote Installation
# Usage: curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/talk-to-me-claude-cli/main/install-remote.sh | bash
# Or: bash <(curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/talk-to-me-claude-cli/main/install-remote.sh)

REPO_URL="https://github.com/YOUR_USERNAME/talk-to-me-claude-cli.git"
INSTALL_DIR="${1:-$HOME/.talk-to-me-claude}"
CLAUDE_CONFIG="$HOME/.claude.json"

echo "=================================================="
echo "  Talk-to-Me Claude CLI - Remote Installation"
echo "=================================================="
echo
echo "Installing to: $INSTALL_DIR"
echo

# Step 1: Check Python version
echo "📋 Checking Python version..."

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

# Step 2: Check if git is available
echo "📋 Checking for git..."
if ! command -v git &> /dev/null; then
    echo "❌ git is required but not installed"
    echo
    echo "Install git:"
    echo "  brew install git"
    echo
    exit 1
fi
echo "✅ git found"
echo

# Step 3: Clone or update repository
if [ -d "$INSTALL_DIR" ]; then
    echo "📦 Updating existing installation..."
    cd "$INSTALL_DIR"
    git pull origin main 2>&1 || echo "⚠️  Could not update (may be modified locally)"
else
    echo "📦 Cloning repository..."
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi
echo "✅ Repository ready"
echo

# Step 4: Install dependencies
echo "📦 Installing Python dependencies..."
$PYTHON_CMD -m pip install -q -r requirements.txt
echo "✅ Dependencies installed"
echo

# Step 5: Create necessary directories
echo "📁 Creating project directories..."
mkdir -p "$INSTALL_DIR/.claude/commands/talk-to-me"
mkdir -p "$INSTALL_DIR/hooks"
echo "✅ Directories created"
echo

# Step 6: Set up .env if not exists
echo "⚙️  Configuring environment..."
if [ ! -f "$INSTALL_DIR/.env" ]; then
    cat > "$INSTALL_DIR/.env" << 'EOF'
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
    echo "⚠️  IMPORTANT: Edit $INSTALL_DIR/.env and add your API keys!"
else
    echo "✅ .env already exists"
fi
echo

# Step 7: Configure MCP server
echo "🔧 Configuring MCP server..."

if [ ! -f "$CLAUDE_CONFIG" ]; then
    cat > "$CLAUDE_CONFIG" << EOF
{
  "mcpServers": {
    "talk-to-me-claude": {
      "command": "$PYTHON_CMD",
      "args": ["-m", "src.mcp_server.server"],
      "cwd": "$INSTALL_DIR",
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
EOF
    echo "✅ Created $CLAUDE_CONFIG with talk-to-me-claude MCP server"
else
    if grep -q '"talk-to-me-claude"' "$CLAUDE_CONFIG"; then
        echo "⚠️  talk-to-me-claude MCP server already configured"
        echo "   Updating configuration..."

        # Backup and update
        cp "$CLAUDE_CONFIG" "$CLAUDE_CONFIG.backup"

        $PYTHON_CMD << PYEOF
import json
with open('$CLAUDE_CONFIG', 'r') as f:
    config = json.load(f)

if 'mcpServers' not in config:
    config['mcpServers'] = {}

config['mcpServers']['talk-to-me-claude'] = {
    "command": "$PYTHON_CMD",
    "args": ["-m", "src.mcp_server.server"],
    "cwd": "$INSTALL_DIR",
    "env": {
        "PYTHONPATH": "."
    }
}

with open('$CLAUDE_CONFIG', 'w') as f:
    json.dump(config, f, indent=2)
PYEOF
        echo "✅ Updated MCP server configuration"
    else
        echo "⚠️  $CLAUDE_CONFIG exists with other MCP servers"
        echo
        read -p "Add talk-to-me-claude to config? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cp "$CLAUDE_CONFIG" "$CLAUDE_CONFIG.backup"

            $PYTHON_CMD << PYEOF
import json
with open('$CLAUDE_CONFIG', 'r') as f:
    config = json.load(f)

if 'mcpServers' not in config:
    config['mcpServers'] = {}

config['mcpServers']['talk-to-me-claude'] = {
    "command": "$PYTHON_CMD",
    "args": ["-m", "src.mcp_server.server"],
    "cwd": "$INSTALL_DIR",
    "env": {
        "PYTHONPATH": "."
    }
}

with open('$CLAUDE_CONFIG', 'w') as f:
    json.dump(config, f, indent=2)
PYEOF
            echo "✅ Added talk-to-me-claude to $CLAUDE_CONFIG"
        else
            echo "⚠️  Skipped. You'll need to add manually."
        fi
    fi
fi
echo

# Step 8: Set up hooks
echo "🪝 Setting up hooks..."
cat > "$INSTALL_DIR/.claude/hooks.json" << EOF
{
  "userPromptSubmit": "hooks/inject_narration_prompt.py",
  "stop": "hooks/process_response.py"
}
EOF
echo "✅ Hooks configured"
echo

# Step 9: Set default mode
echo "🎛️  Setting default narration mode..."
echo "auto" > "$INSTALL_DIR/.claude/narration-mode.txt"
echo "✅ Default mode: auto"
echo

# Step 10: Run tests
echo "🧪 Running tests..."
if $PYTHON_CMD -m pytest "$INSTALL_DIR/tests" -q --tb=short 2>/dev/null; then
    echo "✅ All tests passed"
else
    echo "⚠️  Some tests failed (this may be okay)"
fi
echo

# Installation complete
echo "=================================================="
echo "  Installation Complete! 🎉"
echo "=================================================="
echo
echo "Installed to: $INSTALL_DIR"
echo
echo "Next Steps:"
echo
echo "1. Add API keys to configuration:"
echo "   nano $INSTALL_DIR/.env"
echo
echo "2. Restart Claude Code to load MCP server"
echo
echo "3. Test voice narration:"
echo "   Ask Claude to do a coding task and listen"
echo
echo "4. Try voice input:"
echo "   /talk-to-me:listen"
echo
echo "Available Commands:"
echo "  /talk-to-me:mode [coding_only|conversational|auto]"
echo "  /talk-to-me:listen [duration_seconds]"
echo "  /talk-to-me:status"
echo
echo "Configuration file: $INSTALL_DIR/.env"
echo "MCP server config: $CLAUDE_CONFIG"
echo
echo "To uninstall:"
echo "  rm -rf $INSTALL_DIR"
echo "  # And remove 'talk-to-me-claude' from $CLAUDE_CONFIG"
echo
echo "=================================================="
