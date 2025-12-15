# 🎤 Talk-to-Me Claude CLI

> **Voice narration layer for Claude Code CLI** - Explains WHAT was done, not what's on screen

Like a lecturer explaining concepts rather than reading slides, this tool adds intelligent voice narration to Claude Code CLI that summarizes high-level changes instead of reading code line-by-line.

---

## 🎯 The Problem

Standard text-to-speech for coding tasks is terrible:
- ❌ Reads file paths aloud
- ❌ Spells out code character by character
- ❌ Narrates tool usage ("I used the Edit tool...")
- ❌ Overwhelming for users

## ✅ The Solution

**Dual-output system:**
- **Screen** (Terminal): Shows code, diffs, file changes, errors
- **Voice** (Audio): High-level summary of what was accomplished

**Example:**

**Terminal:**
```
Editing src/auth/login.py...
  + Added email validation (lines 23-28)
  + Updated error handling (line 45)

Editing tests/test_login.py...
  + Added test_invalid_email (lines 67-72)
```

**Voice:**
> "I've strengthened the login system by adding email validation and improving
> the error messages users will see when something goes wrong. I also added
> tests to ensure the validation catches invalid email formats."

---

## 🚀 Quick Start

### One-Line Installation (Easiest)

Install from anywhere without cloning:

```bash
curl -sSL https://raw.githubusercontent.com/yourusername/talk-to-me-claude-cli/main/install-remote.sh | bash
```

Or specify custom install location:
```bash
curl -sSL https://raw.githubusercontent.com/yourusername/talk-to-me-claude-cli/main/install-remote.sh | bash -s $HOME/my-location
```

Default location: `~/.talk-to-me-claude`

### Local Installation (If You Have the Repo)

```bash
# If you already cloned the repository
cd talk-to-me-claude-cli
./install.sh

# Edit .env and add your API keys
nano .env

# Restart Claude Code
# Voice narration is now active!
```

The installer automatically:
- ✅ Checks Python 3.11+ is installed
- ✅ Installs all dependencies
- ✅ Sets up MCP server configuration
- ✅ Creates hooks for Claude Code
- ✅ Configures slash commands
- ✅ Runs tests to verify installation

### Test It

```bash
# Test voice narration
# Ask Claude to do a coding task and listen for audio

# Test voice input
/talk-to-me:listen

# Change narration mode
/talk-to-me:mode auto          # Smart mode (default)
/talk-to-me:mode coding_only   # Only narrate code changes
/talk-to-me:mode conversational # Narrate everything
```

---

## 📋 Features

### ✅ Completed (v1.0)

- [x] Custom prompts with narration tags
- [x] Multi-point narration (captures comprehensive output)
- [x] Claude Code CLI integration via hooks
- [x] MCP server with 6 tools
- [x] Session management and conversation history
- [x] Multiple TTS providers (OpenAI, ElevenLabs, local)
- [x] Multiple STT providers (OpenAI Whisper, macOS native, local)
- [x] Configurable verbosity (brief, medium, detailed)
- [x] Three narration modes (coding_only, conversational, auto)
- [x] Voice input via slash command
- [x] Background TTS (non-blocking)
- [x] Emoji/symbol cleaning for clean audio
- [x] Comprehensive test suite (61 tests)
- [x] One-command installation

### 🚧 In Backlog

- [ ] Auto-listen mode (60s VAD-triggered listening)
- [ ] Push-to-talk daemon (Shift+Space hotkey)
- [ ] Piper TTS integration (high-quality offline)
- [ ] Personality system (casual, enthusiastic, focused, etc.)
- [ ] Voice profile management (quick switching)
- [ ] Language learning mode (dual-language narration)
- [ ] Conversation export/import

### 🔮 Future Enhancements

- [ ] Voice interruption handling
- [ ] TTS caching for common phrases
- [ ] Custom vocabulary/pronunciation
- [ ] Streaming audio generation
- [ ] Performance optimization

---

## 🎛️ Configuration

Edit `.env` to customize:

```bash
# Voice Providers
TTS_PROVIDER=openai        # openai or local
TTS_VOICE=nova            # alloy, echo, fable, nova, onyx, shimmer
TTS_SPEED=1.0             # 0.25 to 4.0

STT_PROVIDER=openai        # openai or local
STT_MODEL=whisper-1

# Narration Settings
NARRATION_ENABLED=true
NARRATION_VERBOSITY=medium  # brief, medium, detailed
AUTO_SPEAK=true            # Auto-play narration
```

---

## 💡 How It Works

### Architecture

```
User (voice) → STT → Claude Code (with custom prompt)
                            ↓
                 Output with <voice_narration> tags
                            ↓
                    ┌───────┴────────┐
                    ↓                ↓
               Terminal          TTS (speak summary)
              (code/details)
```

### Narration Prompt

Claude receives a special system prompt instructing it to wrap summaries in `<voice_narration>` tags:

```xml
<voice_narration>
High-level summary of what was accomplished...
</voice_narration>

[Regular detailed output continues...]
```

The wrapper:
1. Extracts narration from tags
2. Displays regular output in terminal
3. Speaks the narration via TTS

---

## 📖 Usage Examples

### Voice Mode

```bash
python -m src.wrapper --voice
```

Press Enter to record → Speak your command → Press Enter to stop → Claude processes and narrates

### Text Mode (Demo)

```bash
python -m src.wrapper --text "Add error handling to the API"
```

### Show Narration Prompt

```bash
python -m src.wrapper --show-prompt
```

### Check Configuration

```bash
python -m src.wrapper --check
```

---

## 🔧 Development

### Project Structure

```
talk-to-me-claude-cli/
├── src/
│   ├── wrapper.py       # Main CLI entry point
│   ├── prompt.py        # Narration system prompts
│   ├── extractor.py     # Extract <voice_narration> tags
│   └── voice/
│       ├── tts.py       # Text-to-Speech providers
│       └── stt.py       # Speech-to-Text providers
├── .env.example         # Configuration template
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Package configuration
└── README.md
```

### Running Tests

```bash
# Test narration extraction
python -m src.extractor

# Test TTS
python -m src.voice.tts

# Test STT
python -m src.voice.stt
```

---

## 🤝 Contributing

Contributions welcome! Areas that need help:

- [ ] Claude Code CLI integration
- [ ] MCP server implementation
- [ ] Local Whisper support
- [ ] Better VAD (Voice Activity Detection)
- [ ] Documentation improvements

---

## 📚 Technical Background

This project was built based on research into:

- **Bumba-Voice** - MCP voice integration pattern
- **LiveWhisper** - Real-time STT with VAD
- **ALTS** - Local voice assistant architecture
- **SuperClaude** - Code summarization patterns

See [RESEARCH.md](.octocode/research/voice-integration/research.md) for full research findings.

---

## 🎓 Design Philosophy

**Key Principle:** Like a lecturer explaining slides, not reading them.

❌ **Bad (Reading Output):**
> "Editing source slash auth slash login dot pie why... line twenty-three... added email at rate..."

✅ **Good (Explaining Concepts):**
> "I've strengthened the login system by adding email validation and improving error messages."

---

## 🐛 Troubleshooting

### No Audio Output

```bash
# Install audio libraries
pip install sounddevice soundfile numpy

# Test audio
python -c "import sounddevice as sd; sd.play([0.1]*10000, 44100); sd.wait()"
```

### OpenAI API Errors

```bash
# Check API key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY')[:10])"

# Test OpenAI connection
python -m src.voice.tts
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- **Bumba-Voice** - MCP integration patterns
- **OpenAI** - Whisper and TTS APIs
- **Claude Code CLI** - The amazing tool we're enhancing

---

## 🔗 Links

- [Report Issues](https://github.com/yourusername/talk-to-me-claude-cli/issues)
- [Research Documentation](.octocode/research/voice-integration/research.md)
- [Claude Code](https://claude.ai/code)

---

**Built with ❤️ for better developer experience**
