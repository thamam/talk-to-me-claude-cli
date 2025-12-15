"""Extract voice narration from Claude's output.

This module parses Claude's responses to find and extract [VOICE_NARRATION]
tags, cleaning the text for optimal TTS output.
"""

import re
from typing import Optional, Tuple


def extract_narration(text: str, multi_point: bool = True) -> Optional[str]:
    """Extract voice narration from Claude's output.

    Args:
        text: Claude's response text
        multi_point: If True, extract and combine ALL narration blocks.
                     If False, extract only the first block (legacy behavior).

    Returns:
        Extracted narration text, or None if no narration found
    """
    # Match [VOICE_NARRATION]...[/VOICE_NARRATION] tags
    pattern = r'\[VOICE_NARRATION\](.*?)\[/VOICE_NARRATION\]'

    if multi_point:
        # Find ALL narration blocks
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

        if not matches:
            return None

        # Clean each block and join with pauses
        cleaned_blocks = [clean_narration(block) for block in matches]

        # Join multiple blocks with pause indicators
        # TTS will naturally pause at periods
        return ". ".join(cleaned_blocks)
    else:
        # Legacy: Only extract first block
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
    - Emojis and special symbols
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

    # Remove checkmarks and other symbols that sound weird
    cleaned = cleaned.replace('✅', '')
    cleaned = cleaned.replace('✓', '')
    cleaned = cleaned.replace('❌', '')
    cleaned = cleaned.replace('✗', '')
    cleaned = cleaned.replace('⚠️', '')
    cleaned = cleaned.replace('🎉', '')
    cleaned = cleaned.replace('🎤', '')
    cleaned = cleaned.replace('🔊', '')
    cleaned = cleaned.replace('📢', '')
    cleaned = cleaned.replace('→', '')
    cleaned = cleaned.replace('•', '')
    cleaned = cleaned.replace('—', '-')
    cleaned = cleaned.replace('–', '-')

    # Remove emoji ranges (comprehensive)
    # This covers most emoji characters
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642"
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
        "]+", flags=re.UNICODE)
    cleaned = emoji_pattern.sub(r'', cleaned)

    # Replace multiple spaces with single space
    cleaned = re.sub(r'\s+', ' ', cleaned)

    # Remove URLs (they sound terrible when spoken)
    cleaned = re.sub(r'https?://\S+', '', cleaned)

    # Remove standalone symbols and punctuation that might remain
    cleaned = re.sub(r'\s+[^\w\s,.!?-]+\s+', ' ', cleaned)

    return cleaned.strip()


def remove_narration_tags(text: str) -> str:
    """Remove narration tags from text for terminal display.

    This ensures the narration doesn't appear in the terminal output.

    Args:
        text: Claude's full response

    Returns:
        Text with narration tags removed
    """
    pattern = r'\[VOICE_NARRATION\].*?\[/VOICE_NARRATION\]'
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

[VOICE_NARRATION]
I've strengthened the login system by adding email validation and improving
the error messages users will see when something goes wrong. I also added
tests to ensure the validation catches invalid email formats.
[/VOICE_NARRATION]

All tests passing ✓
"""

    terminal, narration = split_output(sample_output)

    print("=== TERMINAL OUTPUT ===")
    print(terminal)
    print("\n=== VOICE NARRATION ===")
    print(narration)
