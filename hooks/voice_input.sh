#!/usr/bin/env bash
#
# Voice Input Handler for Talk-to-Me
# Captures voice input via STT and returns transcribed text
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Load .env to get STT settings
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
fi

# Default to macOS STT if not set
STT_PROVIDER="${STT_PROVIDER:-macos}"
DURATION="${1:-5.0}"

echo -e "${CYAN}🎤 Voice Input${NC}" >&2
echo -e "   Provider: ${STT_PROVIDER}" >&2
echo -e "   Duration: ${DURATION}s" >&2
echo "" >&2

# Run STT via Python
TRANSCRIPTION=$(python3 -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT')

from dotenv import load_dotenv
load_dotenv('$PROJECT_ROOT/.env')

from src.voice.stt import listen

try:
    text = listen(duration=${DURATION})
    print(text)
except Exception as e:
    print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
" 2>&1)

EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo -e "${YELLOW}✗${NC} Transcription failed" >&2
    echo "$TRANSCRIPTION" >&2
    exit 1
fi

# Output transcription to stdout (for Claude to receive)
echo -e "\n${GREEN}✓${NC} Transcribed: ${CYAN}${TRANSCRIPTION}${NC}\n" >&2
echo "User said via voice: \"$TRANSCRIPTION\""
