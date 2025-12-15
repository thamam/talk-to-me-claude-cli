#!/usr/bin/env python3
"""
Background TTS Script
====================
Speaks narration text using configured TTS provider.
Runs independently in background, logs errors but doesn't block.
"""

import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    narration_text = sys.argv[1]

    try:
        # Get project directory and load environment
        project_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(project_dir))

        # Load .env file to get TTS_PROVIDER and API keys
        from dotenv import load_dotenv
        load_dotenv(project_dir / ".env")

        from src.voice import speak

        # Speak the narration
        speak(narration_text)

    except Exception as e:
        # Log error to a file (can't use stderr in background process)
        error_log = Path("/tmp/claude-tts-error.log")
        with open(error_log, "a") as f:
            f.write(f"TTS Error: {e}\n")

if __name__ == "__main__":
    main()
