# Voice Conversation Guide

## Overview

The voice conversation system enables bidirectional voice communication with Claude Code:
- **Voice Input (STT)**: Speak to Claude instead of typing
- **Voice Output (TTS)**: Hear Claude's responses instead of reading

## Current Architecture

### Voice Output (TTS) - ✅ Fully Automatic

**Flow:**
1. You ask Claude to do something
2. Claude responds with both:
   - Terminal output (code, diffs, etc.)
   - `[VOICE_NARRATION]` tags with high-level summary
3. Stop hook automatically extracts narration
4. TTS speaks the narration in background

**Configuration:**
```bash
TTS_PROVIDER=local        # Options: elevenlabs, openai, local
NARRATION_ENABLED=true
AUTO_SPEAK=true
NARRATION_VERBOSITY=medium
```

**Example:**
```
User: "Fix the bug in auth.py"

Claude (Terminal):
Editing auth.py:
  + Added null check (line 45)

Claude (Voice):
[VOICE_NARRATION]
I fixed a bug where the API would crash if a user wasn't found.
[/VOICE_NARRATION]

→ You hear: "I fixed a bug where the API would crash if a user wasn't found"
```

### Voice Input (STT) - ⚠️ Manual Tool Call

**Flow:**
1. Ask Claude: "Use the listen tool"
2. Claude calls MCP `listen` tool
3. You speak into microphone
4. STT transcribes to text
5. Text is processed like typed input

**Configuration:**
```bash
STT_PROVIDER=macos        # Options: openai, local, macos
STT_MODEL=whisper-1       # Or 'base' for local Whisper
STT_LANGUAGE=en-US
```

**Example:**
```
User (typed): "Use the listen tool"

Claude: 🎤 Listening... (speak now)

User (speaks): "Add error handling to the login function"

Claude: ✓ Transcription: Add error handling to the login function

[Claude then processes this as if you typed it]
```

## Supported Use Cases

### 1. Voice-Only Workflow (Partially Supported)

**What works:**
- Say: "Use listen tool" → Speak command → Claude acts → Hears response

**What doesn't work yet:**
- Fully hands-free (need to type "use listen tool" first)
- Push-to-talk activation
- Continuous listening

### 2. Type + Hear Workflow (Fully Supported) ✅

**What works:**
- Type commands as normal
- Hear narration of what Claude does
- Best for coding while Claude explains

**Example:**
```
You type: "Refactor the database code"
You see: File edits, diffs, line numbers
You hear: "I extracted duplicate query logic into a helper function"
```

### 3. Hear + Type Workflow (Fully Supported) ✅

**What works:**
- Claude speaks narration
- You respond by typing
- Good for understanding context while coding

### 4. Multimodal (Visual + Audio) (Fully Supported) ✅

**What works:**
- Complex changes shown in terminal (visual)
- High-level summary spoken (audio)
- No duplication - narration complements terminal output

## STT Providers Comparison

| Provider | Quality | Speed | Cost | Offline | Notes |
|----------|---------|-------|------|---------|-------|
| **OpenAI** | ⭐⭐⭐⭐⭐ | Fast | $0.006/min | ❌ | Best accuracy |
| **macOS** | ⭐⭐⭐ | Fast | FREE | ✅ | CMU Sphinx (good enough) |
| **Local Whisper** | ⭐⭐⭐⭐⭐ | Slow | FREE | ✅ | GPU recommended |

## TTS Providers Comparison

| Provider | Quality | Speed | Cost | Offline | Notes |
|----------|---------|-------|------|---------|-------|
| **ElevenLabs** | ⭐⭐⭐⭐⭐ | Fast | $0.30/1K | ❌ | Most natural |
| **OpenAI** | ⭐⭐⭐⭐ | Fast | $0.015/1K | ❌ | Very good |
| **Local (pyttsx3)** | ⭐⭐ | Instant | FREE | ✅ | Robotic but works |

## MCP Tools Reference

### `listen` - Capture Voice Input

**Purpose:** Record and transcribe voice to text

**Parameters:**
- `duration` (optional): Recording time in seconds
  - If provided: Records for fixed duration
  - If omitted: Records until you press Enter

**Returns:** `"Transcribed: {text}"`

**Example:**
```json
{
  "tool": "listen",
  "arguments": {
    "duration": 5.0
  }
}
```

### `send_message` - Add to Conversation

**Purpose:** Send message with optional voice narration

**Parameters:**
- `text` (required): Message content
- `use_voice` (optional): Extract and speak narration (default: false)
- `role` (optional): "user" or "assistant" (default: "user")

**Example:**
```json
{
  "tool": "send_message",
  "arguments": {
    "text": "Fix the authentication bug",
    "role": "user",
    "use_voice": false
  }
}
```

### `get_conversation_history` - View History

**Purpose:** Retrieve conversation messages

**Parameters:**
- `limit` (optional): Number of recent messages

**Returns:** Formatted conversation history

### `set_voice_settings` - Configure Voice

**Purpose:** Change TTS/STT providers and settings

**Parameters:**
- `tts_provider`: "elevenlabs", "openai", or "local"
- `stt_provider`: "openai", "local", or "macos"
- `tts_voice`: Voice name (provider-specific)
- `tts_speed`: 0.25 to 4.0
- `auto_speak`: true/false
- `narration_enabled`: true/false
- `verbosity`: "brief", "medium", or "detailed"

**Example:**
```json
{
  "tool": "set_voice_settings",
  "arguments": {
    "stt_provider": "macos",
    "tts_provider": "local",
    "auto_speak": true,
    "verbosity": "medium"
  }
}
```

## Future Enhancements (Not Yet Implemented)

### Push-to-Talk (Planned)

**Concept:** Press keyboard shortcut to activate voice input

**How it would work:**
1. Press Ctrl+Space (or configurable key)
2. Microphone activates
3. Speak your command
4. Release key or auto-detect silence
5. Text sent to Claude

**Implementation needed:**
- Keyboard hook to capture shortcut
- Integration with Claude Code input system

### Continuous Listening (Planned)

**Concept:** Always-on voice activation with wake word

**How it would work:**
1. Background process listens continuously
2. Detects wake word ("Hey Claude")
3. Activates full STT
4. Processes command
5. Returns to listening mode

**Challenges:**
- Resource intensive
- Privacy concerns
- Wake word detection accuracy

### Voice-First Mode (Planned)

**Concept:** Optimize entire workflow for voice

**Features:**
- Shorter, more conversational responses
- Confirmations before destructive operations
- Voice-friendly error messages
- "Read that again" command

## Testing

Run the example:
```bash
python3 examples/voice_conversation_example.py
```

Test STT directly:
```bash
# macOS provider (free, offline)
STT_PROVIDER=macos python3 -c "from src.voice.stt import listen; print(listen())"

# OpenAI provider (requires API key)
STT_PROVIDER=openai python3 -c "from src.voice.stt import listen; print(listen())"
```

Test TTS directly:
```bash
# Local provider (free, offline)
TTS_PROVIDER=local python3 -c "from src.voice.tts import speak; speak('Testing voice output')"

# OpenAI provider (requires API key)
TTS_PROVIDER=openai python3 -c "from src.voice.tts import speak; speak('Testing voice output')"
```

## Troubleshooting

### "No module named speech_recognition"
```bash
pip install SpeechRecognition pocketsphinx
```

### "Microphone not found"
- Check system preferences → Privacy → Microphone
- Grant terminal/Python access

### "STT not transcribing correctly"
- Speak clearly and slowly
- Reduce background noise
- Consider using OpenAI provider for better accuracy

### "No audio playback"
- Check system volume
- Try different TTS provider
- Check TTS error log: `/tmp/claude-tts-error.log`

## Cost Analysis

**Heavy Usage Example (1000 interactions):**
- Typing → Claude responds with voice: $4.50 (tokens) + $15 (OpenAI TTS) = **$19.50**
- Voice → Claude responds with voice: $4.50 (tokens) + $6 (STT) + $15 (TTS) = **$25.50**
- Using free local providers: **$4.50** (tokens only)

**Recommendations:**
- Development: Use local/macos (free)
- Production: Use OpenAI or ElevenLabs (better quality)
- Hybrid: Local for routine tasks, cloud for important presentations
