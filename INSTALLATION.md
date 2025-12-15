# Talk-to-Me Installation Guide

Complete guide to install and configure voice narration for Claude Code.

---

## One-Line Installation (Easiest) 🚀

Install from anywhere without cloning:

```bash
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/talk-to-me-claude-cli/main/install-remote.sh | bash
```

**What this does:**
- Installs to `~/.talk-to-me-claude` (or custom location)
- Downloads latest code from GitHub
- Installs all dependencies
- Configures MCP server in `~/.claude.json`
- Sets up hooks and slash commands
- Runs tests to verify
- Ready to use immediately

**Custom install location:**
```bash
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/talk-to-me-claude-cli/main/install-remote.sh | bash -s ~/my-custom-location
```

**To update later:**
```bash
# Just run the installer again - it will update existing installation
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/talk-to-me-claude-cli/main/install-remote.sh | bash
```

---

## Local Installation (Alternative)

If you already have the repository cloned:

```bash
cd talk-to-me-claude-cli

# Run installer (Bash)
./install.sh

# OR run installer (Python)
python3 install.py
```

The installer will:
- ✅ Check Python 3.11+ is installed
- ✅ Install all dependencies
- ✅ Create necessary directories
- ✅ Set up .env configuration file
- ✅ Configure MCP server in ~/.claude.json
- ✅ Set up hooks and slash commands
- ✅ Run tests to verify installation

After installation:
1. Edit `.env` and add your API keys
2. Restart Claude Code
3. Test with: `/talk-to-me:listen`

**That's it!** Skip to [Configuration](#configuration) to customize settings.

---

## Prerequisites

- **Claude Code CLI** (latest version)
- **Python 3.11+** (required for MCP server)
- **macOS, Linux, or Windows** (WSL)
- **Git** (for cloning repository)

Optional:
- **OpenAI API Key** (for better TTS/STT quality)
- **ElevenLabs API Key** (for highest quality TTS)

---

## Manual Installation (Alternative)

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/talk-to-me-claude-cli.git
cd talk-to-me-claude-cli
```

### 2. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# For macOS STT support (offline, free)
pip install SpeechRecognition pocketsphinx
```

### 3. Configure Voice Providers

```bash
# Copy example config
cp .env.example .env

# Edit .env with your preferred settings
# Minimum config (works immediately):
TTS_PROVIDER=local          # Free, offline
STT_PROVIDER=macos          # Free, offline (macOS only)
NARRATION_ENABLED=true
AUTO_SPEAK=true
NARRATION_VERBOSITY=medium
```

### 4. Test Voice System

```bash
# Test TTS (you should hear audio)
python3 -c "from src.voice.tts import speak; speak('Testing voice output')"

# Test STT (speak into mic)
python3 -c "from src.voice.stt import listen; print(listen(duration=5))"
```

If both work, you're ready!

### 5. Add to Claude Code

The hooks are already configured in `.claude/settings.json`. Just restart Claude Code:

```bash
# Restart Claude Code CLI
claude restart  # or close and reopen
```

---

## Detailed Installation

### Option A: Project-Specific (Recommended)

Use Talk-to-Me only in this project.

**Pros:**
- No global changes
- Easy to remove
- Project-specific settings

**Steps:**
1. Follow Quick Start above
2. Hooks in `.claude/settings.json` are already configured
3. Done! Works in this project only.

### Option B: Global Installation

Use Talk-to-Me in all Claude Code projects.

**Pros:**
- Works everywhere
- Persistent across projects

**Cons:**
- Conflicts with other voice systems (AgentVibes)
- Harder to customize per-project

**Steps:**

```bash
# 1. Copy hooks to global location
cp hooks/*.py hooks/*.sh ~/.claude/hooks/

# 2. Create global settings
cat > ~/.claude/settings.json <<EOF
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/inject_narration_prompt.py"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/process_response.py"
          }
        ]
      }
    ]
  }
}
EOF

# 3. Configure .env globally
cp .env ~/.talk-to-me.env

# 4. Update hook scripts to use global .env
# (Manual step - edit hook scripts to load from ~/.talk-to-me.env)
```

---

## Configuration

### Voice Providers

#### TTS (Text-to-Speech)

**Local (pyttsx3)** - FREE, Offline
```bash
TTS_PROVIDER=local
# Uses macOS system voices (Albert, Alice, etc.)
# Quality: Basic/Robotic
# Cost: FREE
```

**OpenAI** - High Quality
```bash
TTS_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_VOICE=nova              # Options: alloy, echo, fable, nova, onyx, shimmer
TTS_SPEED=1.0                  # 0.25 to 4.0
# Quality: Very Good
# Cost: $15/1M characters (~$0.015 per narration)
```

**ElevenLabs** - Highest Quality
```bash
TTS_PROVIDER=elevenlabs
ELEVENLABS_API_KEY=your-key-here
ELEVENLABS_VOICE=adam          # Options: adam, rachel, domi, etc.
# Quality: Excellent/Natural
# Cost: $0.30/1K characters (20x OpenAI)
```

#### STT (Speech-to-Text)

**macOS Native** - FREE, Offline (macOS only)
```bash
STT_PROVIDER=macos
STT_LANGUAGE=en-US
# Quality: Good
# Cost: FREE
```

**OpenAI Whisper API** - Best Quality
```bash
STT_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
STT_MODEL=whisper-1
# Quality: Excellent
# Cost: $0.006/minute
```

**Local Whisper** - Excellent, Offline
```bash
STT_PROVIDER=local
STT_MODEL=base                 # Options: tiny, base, small, medium, large
# Quality: Excellent
# Cost: FREE (but slow, GPU recommended)
# Note: Requires 'pip install openai-whisper'
```

### Narration Settings

```bash
# Enable/disable narration
NARRATION_ENABLED=true

# When to narrate (set via /talk-to-me:mode)
# coding_only, conversational, auto (default)

# How much detail (set via /talk-to-me:verbosity)
NARRATION_VERBOSITY=medium     # Options: brief, medium, detailed

# Auto-speak vs manual
AUTO_SPEAK=true                # false = narration extracted but not spoken
```

---

## Slash Commands

After installation, these commands are available:

```bash
# Set narration mode
/talk-to-me:mode coding_only    # Only narrate when coding
/talk-to-me:mode conversational # Narrate everything
/talk-to-me:mode auto           # Claude decides (default)

# Voice input
/talk-to-me:listen              # Record 5 seconds
/talk-to-me:listen 10           # Record 10 seconds

# Check settings
/talk-to-me:status              # Show current configuration

# Test TTS
/talk-to-me:test                # Play sample audio
```

---

## Verification

### 1. Check Hooks Are Active

```bash
# Should see both hooks configured
cat .claude/settings.json | grep -A 5 "hooks"
```

Expected output:
```json
{
  "hooks": {
    "UserPromptSubmit": [...],
    "Stop": [...]
  }
}
```

### 2. Test Narration Injection

```bash
# Should output narration prompt
python3 hooks/inject_narration_prompt.py <<< '{"prompt":"test"}'
```

Expected: Long prompt about [VOICE_NARRATION] tags

### 3. Test Narration Extraction

```bash
# Check recent hook execution
tail -20 /tmp/claude-hook-stop-debug.log
```

Expected: Recent timestamps with "Narration extracted" logs

### 4. Test TTS

```bash
# Should hear audio
python3 hooks/speak_narration_bg.py "Testing talk-to-me voice system"
```

### 5. Test Complete Flow

1. Ask Claude to do a coding task (e.g., "Add a comment to src/prompt.py")
2. Look for `[VOICE_NARRATION]` tags in response
3. Listen for audio playback
4. Check logs: `tail -20 /tmp/claude-hook-stop-debug.log`

---

## Troubleshooting

### "No voice narration playing"

**Check:**
1. Is `NARRATION_ENABLED=true` in `.env`?
2. Is `AUTO_SPEAK=true` in `.env`?
3. Check TTS error log: `cat /tmp/claude-tts-error.log`
4. Test TTS directly: `python3 -c "from src.voice.tts import speak; speak('test')"`

**Fix:**
```bash
# Reload .env
source .env

# Test TTS
TTS_PROVIDER=local python3 -c "from src.voice.tts import speak; speak('testing')"
```

### "ModuleNotFoundError"

**Problem:** Missing Python packages

**Fix:**
```bash
pip install -r requirements.txt
pip install SpeechRecognition pocketsphinx  # For macOS STT
```

### "Hooks not running"

**Problem:** Claude Code not detecting hooks

**Fix:**
```bash
# Verify hooks file exists
cat .claude/settings.json

# Restart Claude Code completely
claude restart

# Check hook execution
tail -f /tmp/claude-hook-inject-debug.log
tail -f /tmp/claude-hook-stop-debug.log
```

### "Voice input not working"

**Problem:** Microphone access or STT issues

**Fix:**
```bash
# 1. Grant microphone access
# System Preferences → Privacy → Microphone → Enable for Terminal

# 2. Test STT
python3 -c "from src.voice.stt import listen; print(listen(duration=5))"

# 3. Try different provider
# Edit .env:
STT_PROVIDER=openai  # Requires OPENAI_API_KEY
```

### "TTS audio quality poor"

**Problem:** Using local pyttsx3 (robotic)

**Solution:** Use cloud providers

```bash
# Option 1: OpenAI (very good, affordable)
TTS_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Option 2: ElevenLabs (excellent, expensive)
TTS_PROVIDER=elevenlabs
ELEVENLABS_API_KEY=...
```

### "Python version too old"

**Problem:** MCP server requires Python 3.10+

**Fix:**
```bash
# macOS (Homebrew)
brew install python@3.11
python3.11 -m pip install -r requirements.txt

# Update shebang in hooks
sed -i '' 's/python3/python3.11/g' hooks/*.py
```

### "Conflicts with AgentVibes"

**Problem:** Both voice systems active

**Fix:**

Option A: Disable AgentVibes globally
```bash
# Backup AgentVibes hooks
mv ~/.claude/hooks/user-prompt-submit.sh ~/.claude/hooks/user-prompt-submit.sh.disabled
```

Option B: Use Talk-to-Me project-specific
```bash
# Project hooks override global
# Just use Talk-to-Me in specific projects
# AgentVibes works everywhere else
```

---

## Cost Estimation

### Free Setup (Local)
```
TTS: local (pyttsx3)
STT: macos (CMU Sphinx)
Cost: $0
Quality: Good for development
```

### Budget Setup (OpenAI)
```
TTS: openai ($15/1M chars)
STT: macos (free)
Cost: ~$15/month (1000 narrations)
Quality: Very good
```

### Premium Setup (ElevenLabs + OpenAI)
```
TTS: elevenlabs ($0.30/1K chars)
STT: openai ($0.006/min)
Cost: ~$300/month (1000 narrations with voice input)
Quality: Excellent
```

---

## Uninstallation

### Project-Specific

```bash
# 1. Remove hooks configuration
rm .claude/settings.json

# 2. (Optional) Remove files
rm -rf hooks/
rm -rf src/voice/
rm -rf src/mcp_server/
rm .env
```

### Global Installation

```bash
# Remove global hooks
rm ~/.claude/hooks/inject_narration_prompt.py
rm ~/.claude/hooks/process_response.py
rm ~/.claude/hooks/speak_narration_bg.py

# Remove global config
rm ~/.claude/settings.json
rm ~/.talk-to-me.env
```

---

## Next Steps

1. ✅ **Test the system**: Try a coding task and verify narration works
2. ✅ **Customize settings**: Adjust mode and verbosity via slash commands
3. ✅ **Try voice input**: Use `/talk-to-me:listen` for voice commands
4. ✅ **Read documentation**: Check `docs/` for advanced features
5. ✅ **Join community**: Share feedback and get help

---

## Support

- **Issues**: https://github.com/YOUR_USERNAME/talk-to-me-claude-cli/issues
- **Discussions**: https://github.com/YOUR_USERNAME/talk-to-me-claude-cli/discussions
- **Documentation**: `/docs` directory in repo

---

## Credits

- **Inspired by**: AgentVibes (https://agentvibes.org)
- **Built with**: Claude Code, Python, OpenAI, ElevenLabs
- **License**: MIT (see LICENSE file)
