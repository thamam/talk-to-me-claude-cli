#!/bin/bash
# SessionStart Hook: Announce session start via TTS
# This hook fires when Claude Code starts or resumes a session

# Read hook input (SessionStart provides session info)
INPUT=$(cat)

# Try to announce via TTS if available
PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# Check if TTS is available in this project
if [ -f "$PROJECT_DIR/src/voice/__init__.py" ]; then
    # Use project's TTS if available
    python3 -c "
import sys
sys.path.insert(0, '$PROJECT_DIR')
try:
    from src.voice import speak
    speak('Claude Code session started')
except Exception:
    pass  # Silently fail if TTS not configured
" 2>/dev/null
fi

# Always exit 0 (don't block session start)
exit 0
