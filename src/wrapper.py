"""Main CLI wrapper for voice-enabled Claude Code.

This module provides the main entry point for adding voice narration
to Claude Code CLI interactions.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from .prompt import get_narration_prompt
from .extractor import split_output, extract_narration
from .voice import speak, listen


# Load environment variables
load_dotenv()


def print_banner():
    """Print welcome banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║  🎤 Talk-to-Me Claude CLI - Voice Narration Layer           ║
║                                                               ║
║  Explains WHAT was done, not what's on screen                ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def check_dependencies():
    """Check if required dependencies are available."""
    errors = []

    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        errors.append("⚠️  OPENAI_API_KEY not set. Create a .env file with your API key.")

    # Check for audio libraries
    try:
        import sounddevice
        import soundfile
    except ImportError:
        errors.append("⚠️  Audio libraries not installed. Run: pip install sounddevice soundfile")

    if errors:
        print("\n".join(errors))
        print("\nRun 'pip install -r requirements.txt' to install dependencies.")
        return False

    return True


def process_claude_output(output: str, verbosity: str = "medium", provider: Optional[str] = None) -> None:
    """Process Claude's output and handle voice narration.

    Args:
        output: Claude's response text
        verbosity: Narration verbosity level
        provider: TTS provider override (elevenlabs, openai, local)
    """
    # Split into terminal and voice components
    terminal_text, narration = split_output(output)

    # Display terminal output
    if terminal_text:
        print("\n" + "="*60)
        print(terminal_text)
        print("="*60 + "\n")

    # Speak narration if available
    if narration:
        narration_enabled = os.getenv("NARRATION_ENABLED", "true").lower() == "true"
        auto_speak = os.getenv("AUTO_SPEAK", "true").lower() == "true"

        if narration_enabled:
            print(f"🔊 Narration: {narration}\n")

            if auto_speak:
                try:
                    speak(narration, provider=provider)
                except Exception as e:
                    print(f"⚠️  TTS failed: {e}")
            else:
                print("💡 Tip: Set AUTO_SPEAK=true in .env to enable automatic voice")


def interactive_mode():
    """Run in interactive mode with voice input."""
    print_banner()
    print("\n🎤 Voice Mode Active")
    print("Press Enter to start recording, Enter again to stop\n")

    if not check_dependencies():
        sys.exit(1)

    verbosity = os.getenv("NARRATION_VERBOSITY", "medium")
    prompt_instruction = get_narration_prompt(verbosity)

    print("\n📋 System Prompt Loaded:")
    print(f"   Verbosity: {verbosity}")
    print(f"   Narration: {'enabled' if os.getenv('NARRATION_ENABLED', 'true') == 'true' else 'disabled'}")
    print()

    try:
        while True:
            print("\n" + "-"*60)
            print("Ready for voice input...")

            try:
                # Listen for voice input
                user_input = listen()

                if not user_input or user_input.strip().lower() in ["exit", "quit", "bye"]:
                    print("\n👋 Goodbye!")
                    break

                print(f"\n📝 You said: {user_input}")

                # TODO: Actually call Claude Code CLI here
                # For now, we'll simulate with a sample response
                print("\n💭 Processing with Claude Code...")
                print("\n⚠️  NOTE: This is a demo. Integration with Claude Code CLI coming soon.")
                print("   For now, this demonstrates the narration extraction and TTS flow.\n")

                # Simulate Claude's response with narration tags
                sample_response = f"""
I'll help you with that.

<voice_narration>
I've processed your request. {user_input} This is a demonstration
of how the voice narration system works. In production, this would
summarize actual code changes made by Claude.
</voice_narration>

[Detailed code changes would appear here in production]
"""

                process_claude_output(sample_response, verbosity)

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                continue

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


def text_mode(input_text: str, provider: Optional[str] = None):
    """Process text input and demonstrate narration extraction.

    Args:
        input_text: Text to process
        provider: TTS provider override
    """
    print_banner()
    print(f"\n📝 Input: {input_text}\n")

    # Simulate Claude response
    sample_response = f"""
Processing your request: {input_text}

<voice_narration>
I've completed the task. This is a simulated narration that would
normally describe the high-level changes made to your code.
</voice_narration>

[Detailed output would appear here]
"""

    process_claude_output(sample_response, provider=provider)


def show_prompt():
    """Display the narration system prompt."""
    print_banner()
    verbosity = os.getenv("NARRATION_VERBOSITY", "medium")
    prompt = get_narration_prompt(verbosity)

    print(f"\n📋 Voice Narration System Prompt (Verbosity: {verbosity})")
    print("="*60)
    print(prompt)
    print("="*60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Talk-to-Me Claude CLI - Voice narration layer for Claude Code"
    )

    parser.add_argument(
        "--voice",
        "-v",
        action="store_true",
        help="Enable voice input mode"
    )

    parser.add_argument(
        "--text",
        "-t",
        type=str,
        help="Process text input (demo mode)"
    )

    parser.add_argument(
        "--show-prompt",
        action="store_true",
        help="Display the narration system prompt"
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Check dependencies and configuration"
    )

    parser.add_argument(
        "--provider",
        "-p",
        type=str,
        choices=["elevenlabs", "openai", "local"],
        help="Override TTS provider (elevenlabs, openai, local)"
    )

    args = parser.parse_args()

    # Load environment
    load_dotenv()

    # Handle commands
    if args.check:
        print_banner()
        print("\n🔍 Checking dependencies...\n")
        if check_dependencies():
            print("✅ All dependencies satisfied")
            print(f"\n📋 Configuration:")
            provider = args.provider or os.getenv('TTS_PROVIDER', 'openai')
            print(f"   TTS Provider: {provider}")
            if provider == "elevenlabs":
                print(f"   ElevenLabs Voice: {os.getenv('ELEVENLABS_VOICE', 'adam')}")
            elif provider == "openai":
                print(f"   OpenAI Voice: {os.getenv('OPENAI_VOICE', 'nova')}")
            print(f"   STT Provider: {os.getenv('STT_PROVIDER', 'openai')}")
            print(f"   Narration: {os.getenv('NARRATION_ENABLED', 'true')}")
            print(f"   Verbosity: {os.getenv('NARRATION_VERBOSITY', 'medium')}")
        sys.exit(0)

    elif args.show_prompt:
        show_prompt()
        sys.exit(0)

    elif args.text:
        text_mode(args.text, provider=args.provider)
        sys.exit(0)

    elif args.voice:
        interactive_mode()
        sys.exit(0)

    else:
        # Default: show help
        parser.print_help()
        print("\n💡 Quick Start:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your OPENAI_API_KEY")
        print("   3. Run: talk-to-claude --voice")
        sys.exit(0)


if __name__ == "__main__":
    main()
