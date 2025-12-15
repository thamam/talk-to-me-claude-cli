# Talk-to-Me Development Backlog

## AgentVibes Integration Ideas (Future Enhancement)

**Status:** Research Complete, Implementation Deferred
**Priority:** Medium
**Estimated Effort:** 2-3 days

### Summary

AgentVibes is a mature voice narration system already installed globally on this system. We've analyzed its architecture and identified features worth adopting while maintaining our cleaner "invisible narration" approach.

**Full Analysis:** See `docs/AGENTVIBES_COMPARISON.md`

### Key Findings

**What AgentVibes Does Better:**
- 19 personality modes (pirate, sarcastic, professional, etc.)
- Piper TTS integration (high-quality offline neural TTS)
- Language learning mode (dual-language narration)
- Voice profile management (favorites per personality)
- Sentiment system (temporary mood override)
- Extensive slash commands (30+ commands)

**What We Do Better:**
- Invisible narration (no visible Bash commands cluttering output)
- STT support (voice input via 3 providers)
- MCP server with conversation tracking
- Single narration per task (vs AgentVibes' 2x: acknowledgment + completion)
- Verbosity control (brief/medium/detailed)

**No Collision:** Project hooks override global hooks, so both systems can coexist.

---

## Features to Potentially Adopt

### 1. Piper TTS Provider (High Priority)

**Why:** High-quality neural TTS, offline, fast, free
**Current:** We use local pyttsx3 (robotic) or cloud (costs money)
**Effort:** 1-2 days

**Implementation Notes:**
- Piper scripts already exist in `~/.claude/hooks/`
- Can reuse AgentVibes' integration
- Would add as 4th TTS provider: `TTS_PROVIDER=piper`

**Files to Create:**
```python
# src/voice/providers/piper_tts.py
class PiperTTS(TTSProvider):
    """Piper TTS provider - high-quality offline neural TTS."""

    def __init__(self, model="en_US-libritts-high", voice="p225"):
        # Use Piper CLI: ~/.local/share/piper/piper
        # Models in: ~/.local/share/piper/models/
        pass
```

**Config Changes:**
```bash
# .env
TTS_PROVIDER=piper
PIPER_MODEL=en_US-libritts-high  # or en_US-lessac-medium
PIPER_VOICE=p225                # Speaker ID (multi-speaker models)
PIPER_SPEED=1.0
```

**Testing:**
```bash
# Test Piper directly
echo "Testing Piper TTS" | ~/.local/share/piper/piper \
  --model ~/.local/share/piper/models/en_US-libritts-high.onnx \
  --output_file /tmp/test.wav
afplay /tmp/test.wav
```

---

### 2. Simple Personality System (Medium Priority)

**Why:** Adds character to narration without AgentVibes' visible Bash calls
**Current:** Professional tone only
**Effort:** 1 day

**Design:**
- Store personalities as markdown files in `.claude/personalities/`
- Each personality modifies narration prompt (not TTS calls)
- Slash command: `/talk-to-me:personality [name]`

**Example Personalities:**
1. **professional** (default) - Standard technical narration
2. **casual** - Relaxed, conversational
3. **enthusiastic** - Energetic, encouraging
4. **focused** - Minimal words, direct
5. **teaching** - Educational, explains concepts

**Implementation:**
```python
# src/personality.py
def get_personality_prompt(personality: str) -> str:
    """Get personality modifier for narration."""
    prompts = {
        "casual": "Use casual, relaxed language. Like chatting with a colleague.",
        "enthusiastic": "Be energetic and encouraging! Show excitement about progress.",
        "focused": "Be concise and direct. Minimal words, maximum clarity.",
        "teaching": "Explain concepts clearly, as if teaching a student.",
    }
    return prompts.get(personality, "")
```

**Personality Files:**
```markdown
# .claude/personalities/enthusiastic.md
---
name: enthusiastic
description: Energetic and encouraging narration
---

## Style Guidelines
- Use exclamation points (but not excessively)
- Celebrate accomplishments
- Positive, uplifting tone
- Show excitement about progress

## Example Narrations
- "Great! I've fixed that authentication bug that was causing issues."
- "Excellent progress! The new feature is working perfectly now."
```

---

### 3. Voice Profile Management (Low Priority)

**Why:** Easy switching between voices for different contexts
**Current:** Manual .env editing
**Effort:** 0.5 days

**Design:**
- Pre-configured voice profiles
- Quick switching via slash command
- Per-mode voice preferences

**Example Profiles:**
```bash
/talk-to-me:profile work        # Professional voice (OpenAI Onyx)
/talk-to-me:profile casual      # Friendly voice (OpenAI Nova)
/talk-to-me:profile presentation # High-quality (ElevenLabs Adam)
/talk-to-me:profile dev         # Fast/free (Piper or local)
```

**Config:**
```json
// .claude/voice-profiles.json
{
  "profiles": {
    "work": {
      "tts_provider": "openai",
      "tts_voice": "onyx",
      "tts_speed": 1.0,
      "verbosity": "medium"
    },
    "casual": {
      "tts_provider": "openai",
      "tts_voice": "nova",
      "tts_speed": 1.1,
      "verbosity": "brief"
    },
    "presentation": {
      "tts_provider": "elevenlabs",
      "tts_voice": "adam",
      "verbosity": "detailed"
    },
    "dev": {
      "tts_provider": "piper",
      "piper_model": "en_US-lessac-medium",
      "verbosity": "brief"
    }
  }
}
```

---

### 4. Language Learning Mode (Low Priority)

**Why:** Support for learning/practicing foreign languages
**Current:** English only
**Effort:** 1-2 days

**Design:**
- Dual-language narration (native + target language)
- Separate voices for each language
- Configurable order (native first vs target first)

**Usage:**
```bash
/talk-to-me:language native en-US
/talk-to-me:language target es-ES
/talk-to-me:learn enable
```

**Narration Output:**
```
[English Voice]: "I fixed the authentication bug"
[Spanish Voice]: "Arreglé el error de autenticación"
```

**Implementation Notes:**
- Requires bilingual narration generation
- Two TTS calls per narration
- Adds ~2s latency per response
- Probably better as separate mode than default

---

## Other Backlog Items

### Auto-Listen Mode (High Priority) ⭐ USER REQUESTED

**Status:** Design phase
**Priority:** High (user's preferred workflow)
**Effort:** 2-3 days

**User Request (2025-12-15):**
> "After Claude responds, automatically listen for ~60 seconds. If I speak during that window (and terminal has focus), capture and transcribe my voice, then submit it as my next prompt."

**Current State:**
- ✅ Slash command works: `/talk-to-me:listen`
- ❌ Shift+Space not implemented
- ❌ Auto-listen mode not implemented

**Desired Flow:**
```
1. Claude finishes response
2. Auto-listen window opens (60s)
3. Voice Activity Detection (VAD) triggers on speech
4. Transcribe speech to text
5. Auto-submit as next prompt
6. Repeat after next response
```

**Implementation Plan:**

```python
# hooks/auto_listen_daemon.py
"""
Auto-listen mode: Automatically capture voice input after responses.

Triggered by Stop hook, listens for ~60 seconds after each response.
Uses VAD to detect when user starts speaking.
"""

import time
import threading
from pathlib import Path

class AutoListenMode:
    def __init__(self):
        self.listening = False
        self.window_duration = 60  # seconds
        self.vad_threshold = 0.5   # Voice activity threshold

    def start_listen_window(self):
        """Start listening window after Claude response."""
        if self.listening:
            return  # Already listening

        self.listening = True
        thread = threading.Thread(target=self._listen_with_timeout)
        thread.daemon = True
        thread.start()

    def _listen_with_timeout(self):
        """Listen for voice input with timeout."""
        from src.voice.stt import listen
        import webrtcvad  # Voice Activity Detection

        # Start listening with VAD
        start_time = time.time()

        while time.time() - start_time < self.window_duration:
            # Check if terminal has focus
            if not self._is_terminal_focused():
                time.sleep(0.5)
                continue

            # Listen with VAD
            try:
                text = listen(duration=None, use_vad=True)
                if text and len(text.strip()) > 0:
                    # Got speech! Submit to Claude
                    self._submit_to_claude(text)
                    break
            except TimeoutError:
                # No speech detected in window
                pass
            except KeyboardInterrupt:
                # User typed instead
                break

        self.listening = False

    def _is_terminal_focused(self):
        """Check if terminal/Claude Code has focus."""
        import AppKit
        app = AppKit.NSWorkspace.sharedWorkspace().activeApplication()
        return 'Terminal' in app['NSApplicationName'] or \
               'iTerm' in app['NSApplicationName']

    def _submit_to_claude(self, text):
        """Submit transcribed text to Claude Code."""
        # Write to stdin or use AppleScript to inject
        # This is the tricky part - needs integration with Claude Code
        pass
```

**Integration with Stop Hook:**

```python
# hooks/process_response.py (add at end)

# After TTS launches, start auto-listen window
if os.getenv("AUTO_LISTEN_MODE", "false").lower() == "true":
    from auto_listen_daemon import AutoListenMode
    listener = AutoListenMode()
    listener.start_listen_window()
```

**Configuration:**
```bash
# .env
AUTO_LISTEN_MODE=true          # Enable auto-listen after responses
AUTO_LISTEN_DURATION=60        # Listening window in seconds
AUTO_LISTEN_VAD_THRESHOLD=0.5  # Voice activity detection sensitivity
```

**Challenges:**

1. **Terminal Focus Detection**
   - Need to check if terminal has focus
   - User might switch to browser/other app
   - Solution: Use macOS AppKit to check active app

2. **Input Injection**
   - Need to inject transcribed text into Claude Code
   - Options:
     - AppleScript keystroke simulation
     - Clipboard + paste
     - Write to pseudo-TTY (complex)
   - Recommended: AppleScript

3. **Voice Activity Detection (VAD)**
   - Distinguish speech from silence
   - Prevent false triggers from background noise
   - Library: `webrtcvad` or `py-webrtcvad`

4. **Interruption Handling**
   - User types instead of speaking
   - Need to cancel listen window
   - Solution: Monitor keyboard input

**Dependencies:**
```bash
pip install webrtcvad       # Voice Activity Detection
pip install pyobjc-framework-Cocoa  # macOS app detection
```

**Pros:**
- Hands-free workflow
- Natural conversation flow
- No need to remember slash command or hotkey

**Cons:**
- Always listening (privacy concern?)
- May trigger on background conversations
- More complex than push-to-talk
- Drains more battery (mic always on)

**Alternative: Simpler Push-to-Talk First**

Before implementing full auto-listen, consider simpler approach:

1. **Phase 1:** Shift+Space push-to-talk daemon (0.5 days)
2. **Phase 2:** Auto-listen mode (2-3 days)

This lets user test voice workflow before committing to complex auto-listen.

---

### Push-to-Talk Daemon (Medium Priority)

**Status:** Partially implemented (slash command works)
**What's Missing:** Global Shift+Space hotkey
**Effort:** 0.5 days

**Simpler Alternative to Auto-Listen:**
- User presses Shift+Space when ready to speak
- More control, less complexity
- No false triggers from background noise

**Implementation:**
```python
# hooks/push_to_talk_daemon.py
import pynput
from pynput import keyboard

def on_activate():
    """Triggered when Shift+Space is pressed."""
    from src.voice.stt import listen

    # 1. Show notification
    os.system('osascript -e \'display notification "Listening..." with title "Talk-to-Me"\'')

    # 2. Capture audio via STT
    text = listen(duration=5)

    # 3. Inject into Claude Code input
    import subprocess
    subprocess.run([
        'osascript', '-e',
        f'tell application "System Events" to keystroke "{text}"'
    ])

with keyboard.GlobalHotKeys({'<shift>+<space>': on_activate}):
    keyboard.wait()
```

**Requirements:**
- `pip install pynput`
- macOS accessibility permissions
- Launch daemon on startup

**Startup Script:**
```bash
# hooks/start_push_to_talk.sh
#!/bin/bash
cd "$(dirname "$0")/.."
python3 hooks/push_to_talk_daemon.py &
echo $! > /tmp/talk-to-me-daemon.pid
echo "Push-to-talk daemon started (PID: $!)"
```

---

### Narration Tag Removal from Display (Medium Priority)

**Issue:** `[VOICE_NARRATION]` tags currently visible in terminal
**Goal:** Show only spoken content, hide tags
**Effort:** 0.25 days

**Current:**
```
I fixed the bug.

[VOICE_NARRATION]
I fixed the authentication bug.
[/VOICE_NARRATION]
```

**Desired:**
```
I fixed the bug.

🔊 (Narration spoken in background)
```

**Implementation:**
- Add post-processing hook that strips tags from terminal display
- Or use ANSI escape codes to hide tags
- Or modify Claude Code's rendering (not possible from hooks)

---

### Conversation Export/Import (Low Priority)

**Goal:** Save and restore conversation sessions
**Use Case:** Continue conversation later, share with others
**Effort:** 0.5 days

**Features:**
- Export session to JSON file
- Import previous session
- Replay narrations from history

---

### Performance Optimization (Low Priority)

**Current Issues:**
- Background TTS subprocess adds 0.1s latency
- Multi-point narration concatenates with string operations
- No TTS caching for repeated phrases

**Optimizations:**
- Cache common narrations (e.g., "Done!", "Tests passing")
- Pre-generate audio for frequent phrases
- Use audio streaming instead of file-based playback
- Parallel TTS generation for multi-point narration

---

## Decision Log

### Why Keep Talk-to-Me Instead of Switching to AgentVibes?

**Date:** 2025-12-15

**Decision:** Keep Talk-to-Me as primary system, selectively adopt AgentVibes features

**Reasons:**
1. **STT Support:** AgentVibes has no voice input, we do (3 providers)
2. **Cleaner Output:** Our invisible tags vs their visible Bash commands
3. **MCP Infrastructure:** Conversation tracking, session management, programmatic control
4. **Flexibility:** Can cherry-pick AgentVibes features without switching

**Trade-offs Accepted:**
- Less mature than AgentVibes (fewer features)
- No personalities (yet)
- No Piper integration (yet)
- Smaller community

---

## How to Pick Up This Work Later

1. **Read Full Analysis:** `docs/AGENTVIBES_COMPARISON.md`
2. **Check AgentVibes Scripts:** `~/.claude/hooks/` (especially Piper integration)
3. **Priority Order:**
   - Piper TTS (high value, reuses existing code)
   - Personality system (user requested, differentiator)
   - Voice profiles (quality of life)
   - Language learning (niche, defer)

4. **Testing Strategy:**
   - Test with AgentVibes disabled globally
   - Ensure no conflicts if both active
   - Verify performance impact

---

## Notes

- AgentVibes uses **explicit TTS calls** (visible): `Bash: .claude/hooks/play-tts.sh "text"`
- We use **implicit extraction** (invisible): `[VOICE_NARRATION]text[/VOICE_NARRATION]`
- Both approaches work, ours is cleaner but theirs is more debuggable
- Consider hybrid: explicit for complex scenarios, implicit for simplicity

**Last Updated:** 2025-12-15
**Next Review:** When implementing Piper TTS or personality system
