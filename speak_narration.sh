#!/bin/bash
# Quick script to extract and speak narration from clipboard

cd "$(dirname "$0")"

# Get text from clipboard
TEXT=$(pbpaste)

# Extract and speak narration
python3 -c "
from src.extractor import extract_narration
from src.voice import speak
import sys

text = '''$TEXT'''

narration = extract_narration(text)
if narration:
    print('🔊 Speaking:', narration)
    speak(narration)
else:
    print('⚠️  No <voice_narration> tags found in clipboard')
    sys.exit(1)
"
