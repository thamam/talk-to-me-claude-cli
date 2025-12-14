#!/usr/bin/env python3
"""Basic functionality test for Talk-to-Me Claude CLI."""

import sys

def test_imports():
    """Test that all modules can be imported."""
    print("Testing module imports...")

    try:
        from src import prompt, extractor
        from src.voice import tts, stt
        print("✓ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_extractor():
    """Test narration extraction."""
    print("\nTesting narration extraction...")

    from src.extractor import split_output

    sample = """
Here's what I did:

<voice_narration>
I've added error handling to the login system and improved the user feedback.
</voice_narration>

Editing src/auth/login.py...
  + Added try/catch blocks
  + Updated error messages
"""

    terminal, narration = split_output(sample)

    if narration and "error handling" in narration:
        print(f"✓ Narration extracted: {narration[:50]}...")
        return True
    else:
        print("✗ Narration extraction failed")
        return False


def test_prompt():
    """Test prompt generation."""
    print("\nTesting prompt generation...")

    from src.prompt import get_narration_prompt

    prompt = get_narration_prompt("medium")

    if "<voice_narration>" in prompt:
        print("✓ Prompt contains narration instructions")
        return True
    else:
        print("✗ Prompt generation failed")
        return False


def main():
    """Run all basic tests."""
    print("="*60)
    print("Talk-to-Me Claude CLI - Basic Functionality Test")
    print("="*60)

    results = []

    # Run tests
    results.append(("Module Imports", test_imports()))
    results.append(("Narration Extraction", test_extractor()))
    results.append(("Prompt Generation", test_prompt()))

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n🎉 All basic tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check dependencies and configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
