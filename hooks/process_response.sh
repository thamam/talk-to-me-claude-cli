#!/bin/sh
# Hook: response-complete
# Extracts and speaks voice narration from Claude's response

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Read Claude's response from stdin
RESPONSE=$(cat)

# Extract and speak narration in background
(
    cd "$PROJECT_ROOT"

    # Extract narration using Python
    NARRATION=$(python3 -c "
from src.extractor import extract_narration
import sys

response = '''$RESPONSE'''
narration = extract_narration(response)
if narration:
    print(narration)
" 2>/dev/null)

    # If narration found, speak it
    if [ -n "$NARRATION" ]; then
        echo "🔊 Speaking narration..." >&2

        python3 -c "
from src.voice import speak
import sys

narration = '''$NARRATION'''
try:
    speak(narration)
except Exception as e:
    print(f'TTS error: {e}', file=sys.stderr)
" 2>/dev/null
    fi
) &

# Exit immediately, don't wait for background process
exit 0
