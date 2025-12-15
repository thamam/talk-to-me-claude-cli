#!/usr/bin/env python3
"""
UserPromptSubmit Hook: Inject Voice Narration System Prompt
============================================================
Adds narration instructions to user prompts before Claude processes them.

This hook:
1. Reads user prompt from stdin (JSON format)
2. Loads narration system prompt
3. Outputs narration prompt to stdout (prepended to user's prompt)
"""

import json
import sys
from pathlib import Path

def main():
    # Debug logging
    with open("/tmp/claude-hook-inject-debug.log", "a") as f:
        f.write(f"[{Path(__file__).name}] Hook called at {__import__('datetime').datetime.now()}\n")

    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)

        # Check if narration is enabled (from environment or default to true)
        import os
        narration_enabled = os.getenv("NARRATION_ENABLED", "true").lower() == "true"

        if not narration_enabled:
            # Narration disabled - just exit, Claude will receive original prompt
            sys.exit(0)

        # Get project directory and import narration prompt
        project_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(project_dir))

        from src.prompt import get_narration_prompt

        # Get verbosity level
        verbosity = os.getenv("NARRATION_VERBOSITY", "medium")

        # Get narration mode
        mode_file = project_dir / ".claude" / "narration-mode.txt"
        if mode_file.exists():
            mode = mode_file.read_text().strip()
        else:
            mode = "auto"

        # Get the narration system prompt
        narration_prompt = get_narration_prompt(verbosity, mode)

        # Output to stdout - this will be prepended to user's prompt
        print(narration_prompt)
        print("\n---\n")

        sys.exit(0)

    except Exception as e:
        # Log error to stderr but don't block
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(0)  # Exit 0 so prompt still goes through

if __name__ == "__main__":
    main()
