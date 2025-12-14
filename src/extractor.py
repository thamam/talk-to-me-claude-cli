"""Extract voice narration from Claude's output.

This module parses Claude's responses to find and extract <voice_narration>
tags, cleaning the text for optimal TTS output.
"""

import re
from typing import Optional, Tuple


def extract_narration(text: str) -> Optional[str]:
    """Extract voice narration from Claude's output.

    Args:
        text: Claude's response text

    Returns:
        Extracted narration text, or None if no narration found
    """
    # Match <voice_narration>...</voice_narration> tags
    pattern = r'<voice_narration>(.*?)</voice_narration>'
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

    if not match:
        return None

    narration = match.group(1)
    return clean_narration(narration)


def clean_narration(narration: str) -> str:
    """Clean narration text for optimal TTS output.

    Removes:
    - Leading/trailing whitespace
    - Excessive newlines
    - Markdown formatting that sounds bad when spoken
    - Code blocks
    - Special characters that TTS might mispronounce

    Args:
        narration: Raw narration text

    Returns:
        Cleaned narration text ready for TTS
    """
    # Remove leading/trailing whitespace
    cleaned = narration.strip()

    # Replace multiple newlines with single space
    cleaned = re.sub(r'\n+', ' ', cleaned)

    # Remove markdown code blocks (```...```)
    cleaned = re.sub(r'```[\s\S]*?```', '', cleaned)

    # Remove inline code markers (`)
    cleaned = cleaned.replace('`', '')

    # Remove markdown headers (#)
    cleaned = re.sub(r'#+\s*', '', cleaned)

    # Remove markdown bold/italic (**text** or *text*)
    cleaned = re.sub(r'\*\*?(.*?)\*\*?', r'\1', cleaned)

    # Remove markdown links ([text](url))
    cleaned = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', cleaned)

    # Replace multiple spaces with single space
    cleaned = re.sub(r'\s+', ' ', cleaned)

    # Remove URLs (they sound terrible when spoken)
    cleaned = re.sub(r'https?://\S+', '', cleaned)

    return cleaned.strip()


def remove_narration_tags(text: str) -> str:
    """Remove narration tags from text for terminal display.

    This ensures the narration doesn't appear in the terminal output.

    Args:
        text: Claude's full response

    Returns:
        Text with narration tags removed
    """
    pattern = r'<voice_narration>.*?</voice_narration>'
    return re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE).strip()


def split_output(text: str) -> Tuple[str, Optional[str]]:
    """Split Claude's output into terminal and voice components.

    Args:
        text: Claude's full response

    Returns:
        Tuple of (terminal_text, narration_text)
    """
    narration = extract_narration(text)
    terminal_text = remove_narration_tags(text)

    return terminal_text, narration


# Example usage and testing
if __name__ == "__main__":
    # Test case
    sample_output = """
I've completed the authentication refactoring. Here are the changes:

Editing src/auth/login.py...
  + Added email validation (lines 23-28)
  + Updated error handling (line 45)

Editing tests/test_login.py...
  + Added test_invalid_email (lines 67-72)

<voice_narration>
I've strengthened the login system by adding email validation and improving
the error messages users will see when something goes wrong. I also added
tests to ensure the validation catches invalid email formats.
</voice_narration>

All tests passing ✓
"""

    terminal, narration = split_output(sample_output)

    print("=== TERMINAL OUTPUT ===")
    print(terminal)
    print("\n=== VOICE NARRATION ===")
    print(narration)
