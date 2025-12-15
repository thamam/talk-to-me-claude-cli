---
description: Activate voice input (speak your command)
argument-hint: [duration_seconds]
---

# /talk-to-me:listen

Capture voice input and convert it to text using speech-to-text.

This command activates your microphone, records your voice, transcribes it, and passes the text to Claude as if you typed it.

## Usage

```bash
# Listen for 5 seconds (default)
/talk-to-me:listen

# Listen for custom duration
/talk-to-me:listen 10

# Listen until you press Enter (set to 0)
/talk-to-me:listen 0
```

## How It Works

1. 🎤 Microphone activates
2. You speak your command
3. 🔄 Speech-to-text transcribes
4. ✓ Text sent to Claude

## Providers

The STT provider is configured in `.env`:

- **macos** (default): Free, offline, good quality
- **openai**: Excellent quality, $0.006/minute
- **local**: Whisper model, excellent quality, offline

## Examples

### Quick Command
```bash
/talk-to-me:listen
"Add error handling to the login function"
```

### Long Explanation
```bash
/talk-to-me:listen 15
"I need you to refactor the authentication module to use JWT tokens
instead of session cookies, and update all the API endpoints to support
the new auth flow."
```

### Interactive (Press Enter to stop)
```bash
/talk-to-me:listen 0
[Speak as long as you want]
[Press Enter when done]
```

## Tips

1. **Speak clearly**: Enunciate your words
2. **Reduce noise**: Minimize background sounds
3. **Use headphones**: Prevents echo/feedback
4. **Pause briefly**: Wait 0.5s after activating before speaking

## Provider Configuration

Edit `.env` to change STT settings:

```bash
# Fast, free (macOS only)
STT_PROVIDER=macos
STT_LANGUAGE=en-US

# Best accuracy (requires API key)
STT_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Offline, excellent (requires model download)
STT_PROVIDER=local
STT_MODEL=base
```

## Keyboard Shortcut (Setup Required)

**Desired:** Shift+Space for quick voice input

**Current:** Use `/talk-to-me:listen` slash command

**To set up Shift+Space:** See `docs/QUICK_VOICE_INPUT.md` for instructions using:
- macOS Automator (built-in, free)
- BetterTouchTool (recommended if you have it)
- Karabiner-Elements (most flexible)

Or I can build a Python daemon if you prefer an integrated solution.

## Troubleshooting

### "No module named speech_recognition"
```bash
pip install SpeechRecognition pocketsphinx
```

### "Microphone not found"
Check System Preferences → Privacy → Microphone and grant access to Terminal/Python.

### "Transcription not accurate"
Try OpenAI provider for better accuracy:
```bash
# In .env
STT_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

## Implementation

!bash $CLAUDE_PROJECT_DIR/hooks/voice_input.sh ${1:-5.0}
