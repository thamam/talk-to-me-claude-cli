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

### 1. Install

```bash
# Clone the repository
git clone https://github.com/yourusername/talk-to-me-claude-cli.git
cd talk-to-me-claude-cli

# Install dependencies
pip install -r requirements.txt

# Or using the package
pip install -e .
```

### 2. Configure

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your-key-here
```

### 3. Run

```bash
# Check configuration
python -m src.wrapper --check

# Run in voice mode (demo)
python -m src.wrapper --voice

# Or use the installed command
talk-to-claude --voice
```

---

## 📋 Features

### ✅ Phase 1 (Current - MVP)

- [x] Custom prompts with narration tags
- [x] Narration extraction from Claude's output
- [x] OpenAI TTS for voice output
- [x] OpenAI Whisper for voice input
- [x] Configurable verbosity (brief, medium, detailed)
- [x] Local TTS fallback (pyttsx3)

### 🚧 Phase 2 (Coming Soon)

- [ ] Actual Claude Code CLI integration
- [ ] MCP server implementation
- [ ] Provider fallback chain
- [ ] PTT (Push-to-Talk) support
- [ ] Session summaries

### 🔮 Phase 3 (Future)

- [ ] Multiple voice profiles
- [ ] Voice interruption handling
- [ ] Local Whisper support
- [ ] Custom vocabulary/pronunciation
- [ ] Multi-language support

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
