---
description: Show current voice settings and configuration
---

# /talk-to-me:status

Display current voice narration settings and provider configuration.

## What It Shows

- 🎤 STT Provider (speech-to-text)
- 🔊 TTS Provider (text-to-speech)
- 📢 Narration Mode (coding_only/conversational/auto)
- 📏 Verbosity Level (brief/medium/detailed)
- ✅ Enabled/Disabled Status
- 🎯 Auto-speak Setting

## Usage

```bash
/talk-to-me:status
```

## Example Output

```
🎙️  Talk-to-Me Voice Settings
═══════════════════════════════════

📢 Narration Mode:    auto
📏 Verbosity:         medium
✅ Narration Enabled: true
🔊 Auto-speak:        true

🗣️  Text-to-Speech (TTS)
─────────────────────────
  Provider:     local (pyttsx3)
  Voice:        Albert
  Speed:        1.0x

🎤 Speech-to-Text (STT)
─────────────────────────
  Provider:     macos (CMU Sphinx)
  Language:     en-US
  Model:        whisper-1

💡 Tips:
  • Change mode:      /talk-to-me:mode coding_only
  • Change verbosity: /talk-to-me:verbosity brief
  • Test TTS:         /talk-to-me:test
  • Voice input:      /talk-to-me:listen
```

## Implementation

!bash cat $CLAUDE_PROJECT_DIR/.env | grep -E "(TTS_|STT_|NARRATION_)" | sed 's/=/ = /' && echo "" && echo "Mode: $(cat $CLAUDE_PROJECT_DIR/.claude/narration-mode.txt 2>/dev/null || echo 'auto')"
