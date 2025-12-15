#!/bin/sh
# Hook: user-prompt-submit
# Injects voice narration system prompt into user's message

# Debug: log that hook was called
echo "[HOOK] inject_narration_prompt.sh called" >> /tmp/claude-hook-debug.log
date >> /tmp/claude-hook-debug.log

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Read user message from stdin
USER_MESSAGE=$(cat)

# Get the narration prompt using Python
NARRATION_PROMPT=$(cd "$PROJECT_ROOT" && python3 -c "
from src.prompt import get_narration_prompt
import os
print(get_narration_prompt(os.getenv('NARRATION_VERBOSITY', 'medium')))
" 2>&1)

# Check if we got a valid prompt (not an error)
if echo "$NARRATION_PROMPT" | grep -q "Voice Narration Mode"; then
    # Combine prompt with user message
    printf "%s\n\n---\n\n%s\n" "$NARRATION_PROMPT" "$USER_MESSAGE"
else
    # If prompt failed, just pass through user message
    printf "%s\n" "$USER_MESSAGE"
fi
