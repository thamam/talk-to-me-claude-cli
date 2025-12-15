#!/usr/bin/env python3
"""
Stop Hook: Extract and Speak Voice Narration
=============================================
Extracts <voice_narration> tags from Claude's response and speaks them via TTS.

This hook:
1. Reads session info from stdin
2. Parses transcript to get Claude's latest response
3. Extracts narration from <voice_narration> tags
4. Speaks narration using configured TTS provider (runs in background)
"""

import json
import sys
import subprocess
from pathlib import Path

def extract_last_assistant_message(transcript_path):
    """Extract the last assistant message from transcript."""
    try:
        with open(transcript_path, 'r') as f:
            lines = f.readlines()

        # Transcript is JSONL format - each line is a message
        assistant_messages = []
        for line in lines:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                # Check if this is an assistant message (role is nested in message object)
                msg = entry.get("message", {})
                if msg.get("role") == "assistant":
                    content = msg.get("content", "")
                    if isinstance(content, list):
                        # Content is array of content blocks
                        text_parts = [
                            block.get("text", "")
                            for block in content
                            if block.get("type") == "text"
                        ]
                        assistant_messages.append("\n".join(text_parts))
                    elif isinstance(content, str):
                        assistant_messages.append(content)
            except json.JSONDecodeError:
                continue

        # Return the last assistant message
        return assistant_messages[-1] if assistant_messages else None

    except Exception as e:
        print(f"Error reading transcript: {e}", file=sys.stderr)
        return None

def main():
    # Debug logging
    debug_log = Path("/tmp/claude-hook-stop-debug.log")

    try:
        import os

        with open(debug_log, "a") as f:
            f.write(f"[process_response.py] Hook called at {__import__('datetime').datetime.now()}\n")

        # Check if narration and auto-speak are enabled
        narration_enabled = os.getenv("NARRATION_ENABLED", "true").lower() == "true"
        auto_speak = os.getenv("AUTO_SPEAK", "true").lower() == "true"

        if not narration_enabled or not auto_speak:
            with open(debug_log, "a") as f:
                f.write(f"  Narration disabled: enabled={narration_enabled}, auto_speak={auto_speak}\n")
            sys.exit(0)

        # Read hook input from stdin
        input_data = json.load(sys.stdin)

        # Get transcript path
        transcript_path = input_data.get("transcript_path")
        with open(debug_log, "a") as f:
            f.write(f"  Transcript path: {transcript_path}\n")

        if not transcript_path or not Path(transcript_path).exists():
            with open(debug_log, "a") as f:
                f.write(f"  Transcript not found\n")
            sys.exit(0)

        # Extract last assistant message
        response = extract_last_assistant_message(transcript_path)
        with open(debug_log, "a") as f:
            f.write(f"  Response length: {len(response) if response else 0}\n")

        if not response:
            with open(debug_log, "a") as f:
                f.write(f"  No assistant response found\n")
            sys.exit(0)

        # Get project directory and import extractor
        project_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(project_dir))

        from src.extractor import extract_narration

        # Extract narration
        narration = extract_narration(response)
        with open(debug_log, "a") as f:
            f.write(f"  Narration extracted: {narration[:50] if narration else 'None'}...\n")

        if not narration:
            # No narration tags found
            with open(debug_log, "a") as f:
                f.write(f"  No narration tags found\n")
            sys.exit(0)

        # Speak narration in background (don't block)
        speak_script = project_dir / "hooks" / "speak_narration_bg.py"
        with open(debug_log, "a") as f:
            f.write(f"  Launching TTS: {speak_script}\n")

        subprocess.Popen(
            [sys.executable, str(speak_script), narration],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        with open(debug_log, "a") as f:
            f.write(f"  TTS launched successfully\n")

        # Exit immediately (don't wait for TTS)
        sys.exit(0)

    except Exception as e:
        # Log error to stderr but don't block
        with open(debug_log, "a") as f:
            f.write(f"  ERROR: {e}\n")
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    main()
