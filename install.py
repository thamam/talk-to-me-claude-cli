#!/usr/bin/env python3
"""
Talk-to-Me Claude CLI - Python Installation Script
Usage: python3 install.py
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def print_step(text):
    print(f"\n{text}")


def print_success(text):
    print(f"✅ {text}")


def print_warning(text):
    print(f"⚠️  {text}")


def print_error(text):
    print(f"❌ {text}")


def check_python_version():
    """Check if Python 3.11+ is available."""
    print_step("📋 Checking Python version...")

    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print_error(f"Python 3.11+ required (found: {version.major}.{version.minor})")
        print("\nInstall Python 3.11:")
        print("  brew install python@3.11")
        return False

    print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def install_dependencies(project_dir):
    """Install Python dependencies from requirements.txt."""
    print_step("📦 Installing Python dependencies...")

    requirements_file = project_dir / "requirements.txt"
    if not requirements_file.exists():
        print_warning("requirements.txt not found, skipping")
        return

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "-r", str(requirements_file)],
            check=True,
            capture_output=True
        )
        print_success("Dependencies installed")
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        sys.exit(1)


def create_directories(project_dir):
    """Create necessary project directories."""
    print_step("📁 Creating project directories...")

    directories = [
        project_dir / ".claude" / "commands" / "talk-to-me",
        project_dir / "hooks",
        project_dir / "tests",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    print_success("Directories created")


def setup_env_file(project_dir):
    """Create .env file if it doesn't exist."""
    print_step("⚙️  Configuring environment...")

    env_file = project_dir / ".env"

    if env_file.exists():
        print_success(".env already exists")
        return

    env_template = '''# API Keys (REQUIRED for cloud providers)
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
'''

    env_file.write_text(env_template)
    print_success("Created .env template")
    print_warning("IMPORTANT: Edit .env and add your API keys!")


def setup_mcp_server(project_dir):
    """Configure MCP server in ~/.claude.json."""
    print_step("🔧 Configuring MCP server...")

    claude_config = Path.home() / ".claude.json"

    mcp_config = {
        "command": "python3",
        "args": ["-m", "src.mcp_server.server"],
        "cwd": str(project_dir),
        "env": {
            "PYTHONPATH": "."
        }
    }

    if not claude_config.exists():
        # Create new config
        config = {
            "mcpServers": {
                "talk-to-me-claude": mcp_config
            }
        }
        claude_config.write_text(json.dumps(config, indent=2))
        print_success(f"Created {claude_config} with talk-to-me-claude MCP server")
        return

    # Load existing config
    try:
        with open(claude_config, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError:
        print_error(f"Failed to parse {claude_config} (invalid JSON)")
        return

    # Check if already configured
    if 'mcpServers' in config and 'talk-to-me-claude' in config['mcpServers']:
        print_warning("talk-to-me-claude MCP server already exists in config")
        return

    # Add to existing config
    print_warning(f"{claude_config} exists with other MCP servers")
    print("\nAdd this to your mcpServers section:")
    print(json.dumps({"talk-to-me-claude": mcp_config}, indent=2))

    response = input("\nWould you like me to automatically add it? (y/N): ").strip().lower()

    if response == 'y':
        # Backup original
        backup_file = Path(str(claude_config) + ".backup")
        backup_file.write_text(claude_config.read_text())

        # Add MCP server
        if 'mcpServers' not in config:
            config['mcpServers'] = {}

        config['mcpServers']['talk-to-me-claude'] = mcp_config

        # Write back
        with open(claude_config, 'w') as f:
            json.dump(config, f, indent=2)

        print_success(f"Added talk-to-me-claude to {claude_config}")
        print_success(f"Backup saved to {backup_file}")
    else:
        print_warning("Skipped MCP configuration. You'll need to add it manually.")


def setup_hooks(project_dir):
    """Set up Claude Code hooks."""
    print_step("🪝 Setting up Claude Code hooks...")

    hooks_config = project_dir / ".claude" / "hooks.json"

    config = {
        "userPromptSubmit": "hooks/inject_narration_prompt.py",
        "stop": "hooks/process_response.py"
    }

    with open(hooks_config, 'w') as f:
        json.dump(config, f, indent=2)

    print_success("Hook configuration created")


def set_default_mode(project_dir):
    """Set default narration mode."""
    print_step("🎛️  Setting default narration mode...")

    mode_file = project_dir / ".claude" / "narration-mode.txt"
    mode_file.write_text("auto")

    print_success("Default mode: auto")


def run_tests(project_dir):
    """Run tests to verify installation."""
    print_step("🧪 Running tests to verify installation...")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(project_dir / "tests"), "-q", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print_success("All tests passed")
        else:
            print_warning("Some tests failed (this may be okay for initial setup)")
            if result.stdout:
                print(result.stdout)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        print_warning("Could not run tests (pytest may not be installed yet)")


def print_summary(project_dir):
    """Print installation summary."""
    print_header("Installation Complete! 🎉")

    print("Next Steps:\n")
    print("1. Edit .env and add your API keys:")
    print(f"   nano {project_dir / '.env'}\n")
    print("2. Restart Claude Code to load the MCP server\n")
    print("3. Verify MCP tools are loaded:")
    print("   Look for 'talk-to-me-claude' tools in Claude Code\n")
    print("4. Test voice narration:")
    print("   Ask Claude to do a coding task and listen for audio\n")
    print("5. Try voice input:")
    print("   /talk-to-me:listen\n")

    print("Available Commands:")
    print("  /talk-to-me:mode [coding_only|conversational|auto]")
    print("  /talk-to-me:listen [duration_seconds]")
    print("  /talk-to-me:status\n")

    print("Documentation:")
    print("  - INSTALLATION.md - Full setup guide")
    print("  - CLAUDE.md - Development guide")
    print("  - BACKLOG.md - Future enhancements\n")

    print("Troubleshooting:")
    print("  - Check .env file has valid API keys")
    print("  - Verify Python 3.11+ is in PATH")
    print("  - Restart terminal if MCP tools not showing\n")


def main():
    """Main installation flow."""
    project_dir = Path(__file__).parent.resolve()

    print_header("Talk-to-Me Claude CLI Installation")

    # Run installation steps
    if not check_python_version():
        sys.exit(1)

    install_dependencies(project_dir)
    create_directories(project_dir)
    setup_env_file(project_dir)
    setup_mcp_server(project_dir)
    setup_hooks(project_dir)
    set_default_mode(project_dir)
    run_tests(project_dir)

    # Print summary
    print_summary(project_dir)

    print("=" * 60)


if __name__ == "__main__":
    main()
