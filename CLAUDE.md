# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**talk-to-me-claude-cli** is a voice narration layer for Claude Code CLI that provides intelligent audio summaries of coding tasks. Like a lecturer explaining concepts rather than reading slides, it extracts high-level narration from Claude's responses and speaks them via TTS while showing detailed code changes on screen.

## Architecture

### Core Components

The system uses a **dual-output architecture**:

1. **Hooks Layer** (`hooks/`)
   - `inject_narration_prompt.py`: UserPromptSubmit hook that injects narration instructions into user prompts
   - `process_response.py`: Stop hook that extracts narration from responses and triggers TTS
   - `speak_narration_bg.py`: Background TTS process to avoid blocking CLI

2. **Narration System** (`src/`)
   - `prompt.py`: System prompts that instruct Claude to generate narration in `[VOICE_NARRATION]` tags
   - `extractor.py`: Pattern matching and tag extraction from Claude's responses
   - Uses regex to find `[VOICE_NARRATION]...[/VOICE_NARRATION]` blocks

3. **Voice Layer** (`src/voice/`)
   - `tts.py`: Multi-provider TTS system (ElevenLabs, OpenAI, Local/pyttsx3)
   - `stt.py`: Speech-to-text for voice input (OpenAI Whisper)
   - Provider pattern with abstract base class

### Data Flow

```
User Prompt → UserPromptSubmit Hook → Inject Narration Prompt
                                             ↓
                                  Claude processes with prompt
                                             ↓
                                    Response with tags
                                             ↓
                                      Stop Hook
                                             ↓
                             Extract [VOICE_NARRATION] tags
                                             ↓
                            Background TTS (non-blocking)
                                             ↓
                                    Terminal + Audio
```

## Development Commands

### Testing

```bash
# Test narration extraction
python -m src.extractor

# Test TTS (uses configured provider from .env)
python -m src.voice.tts

# Test STT (voice input)
python -m src.voice.stt

# Test basic functionality
python test_basic.py
python test_providers.py
```

### Running

```bash
# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Test TTS providers
python -m src.voice.tts

# Check hook configuration
cat .claude/settings.json
```

### Hooks Testing

```bash
# Test inject hook manually
echo '{"type": "user_prompt", "message": "test"}' | python3 hooks/inject_narration_prompt.py

# Test process hook manually (requires transcript file)
python3 hooks/process_response.py

# View hook debug logs
tail -f /tmp/claude-hook-inject-debug.log
tail -f /tmp/claude-hook-stop-debug.log
```

## Key Implementation Details

### Narration Tag Format

Claude's responses must include narration in this format:

```
[Regular terminal output here...]

[VOICE_NARRATION]
High-level summary of what was accomplished (2-3 sentences).
[/VOICE_NARRATION]

[More terminal output...]
```

### Extraction Process

The extractor (`src/extractor.py`) uses regex with `re.DOTALL | re.IGNORECASE` flags:
- Pattern: `\[VOICE_NARRATION\](.*?)\[/VOICE_NARRATION\]`
- Cleans markdown, URLs, code blocks for better TTS
- Normalizes whitespace and newlines

### Hook Integration

Hooks are configured in `.claude/settings.json`:
- **UserPromptSubmit**: Runs before Claude sees user message
- **Stop**: Runs after Claude completes response
- Both hooks check `NARRATION_ENABLED` env var
- Exit 0 on error to avoid blocking Claude CLI

### TTS Provider Selection

The `get_tts_provider()` function in `src/voice/tts.py`:
1. Reads `TTS_PROVIDER` from environment (elevenlabs, openai, local)
2. Auto-selects voice based on provider (ELEVENLABS_VOICE, OPENAI_VOICE)
3. Falls back to defaults: "adam" for ElevenLabs, "nova" for OpenAI
4. Returns provider instance implementing `TTSProvider` interface

## Environment Variables

Required in `.env`:

```bash
# Voice Providers (at least one TTS provider API key needed)
OPENAI_API_KEY=sk-...              # For OpenAI TTS/Whisper
ELEVENLABS_API_KEY=...             # For ElevenLabs (optional)

# Provider Selection
TTS_PROVIDER=local                 # elevenlabs, openai, or local
STT_PROVIDER=openai                # openai, local, or macos

# Narration Settings
NARRATION_ENABLED=true             # Enable/disable narration
NARRATION_VERBOSITY=medium         # brief, medium, detailed
AUTO_SPEAK=true                    # Auto-play narration after extraction

# Voice Settings (provider-specific)
OPENAI_VOICE=nova                  # alloy, echo, fable, nova, onyx, shimmer
ELEVENLABS_VOICE=adam              # adam, rachel, domi, bella, etc.
TTS_SPEED=1.0                      # 0.25 to 4.0 (OpenAI), affects local too
```

## Important Patterns

### When Adding New TTS Providers

1. Create class extending `TTSProvider` in `src/voice/tts.py`
2. Implement `synthesize()` and `speak()` methods
3. Add to `get_tts_provider()` factory function
4. Update PROVIDERS.md documentation

### When Modifying Narration Prompts

1. Edit `NARRATION_SYSTEM_PROMPT` in `src/prompt.py`
2. Ensure verbosity levels (brief/medium/detailed) are documented
3. Test with `hooks/inject_narration_prompt.py` directly
4. Update examples in prompt to match new format

### When Debugging Hooks

Hooks write to `/tmp/claude-hook-*-debug.log`:
- Check these logs if narration isn't working
- Hooks exit 0 on error to avoid blocking CLI
- Errors are logged to stderr but won't stop Claude

## Voice Narration Mode

When completing coding tasks in this project, you MUST provide TWO types of output:

1. **Standard Output** (for terminal): Code, file paths, diffs, error messages, etc.
2. **Voice Narration** (for audio): High-level summary of what you accomplished

### Voice Narration Guidelines

Wrap your voice narration in [VOICE_NARRATION] tags. This will be spoken aloud to the user via TTS.

#### DO (Good Narration):
- Explain WHAT you accomplished and WHY
- Use conversational, natural language
- Mention high-level concepts and purpose
- Keep it brief (2-4 sentences)
- Speak like a lecturer explaining concepts

#### DON'T (Bad Narration):
- List file names or paths
- Read code line-by-line
- Describe tool usage ("I used the Edit tool...")
- Mention internal processes
- Include technical details better shown visually
- Use emojis or symbols (✅, ❌, 🎉, →, etc.) - they sound weird when spoken

#### Example

**Terminal Output:**
```
Editing src/auth/login.py...
  + Added email validation (lines 23-28)
```

**Voice Narration:**
```
[VOICE_NARRATION]
I've strengthened the login system by adding email validation to catch invalid email formats before they reach the database.
[/VOICE_NARRATION]
```

### IMPORTANT

- ALWAYS include [VOICE_NARRATION] tags when completing tasks
- Keep narration concise - users can see details on screen
- Focus on the USER BENEFIT, not implementation details
