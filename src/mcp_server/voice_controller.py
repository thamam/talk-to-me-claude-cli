"""Voice controller for MCP server.

Integrates TTS/STT functionality with session management.
"""

import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

from ..extractor import extract_narration
from ..voice.tts import get_tts_provider
from ..voice.stt import get_stt_provider
from .session import Session


class VoiceController:
    """Controls voice input/output for a conversation session."""

    def __init__(self, session: Session):
        """Initialize voice controller for a session.

        Args:
            session: The conversation session to control
        """
        self.session = session
        self._tts_provider = None
        self._stt_provider = None

    def _get_tts_provider(self):
        """Get or create TTS provider based on session settings."""
        provider_name = self.session.voice_settings.get("tts_provider", "local")
        voice = self.session.voice_settings.get("tts_voice", "default")
        speed = self.session.voice_settings.get("tts_speed", 1.0)

        # Cache provider if settings haven't changed
        if self._tts_provider is None:
            self._tts_provider = get_tts_provider(
                provider=provider_name,
                voice=voice if voice != "default" else None,
                speed=speed
            )

        return self._tts_provider

    def _get_stt_provider(self):
        """Get or create STT provider based on session settings."""
        provider_name = self.session.voice_settings.get("stt_provider", "openai")

        # Cache provider if settings haven't changed
        if self._stt_provider is None:
            self._stt_provider = get_stt_provider(provider=provider_name)

        return self._stt_provider

    def extract_and_speak_narration(self, text: str) -> Optional[str]:
        """Extract narration from text and speak it if enabled.

        Args:
            text: Text potentially containing narration tags

        Returns:
            Extracted narration text or None
        """
        narration = extract_narration(text)

        if narration and self.session.voice_settings.get("narration_enabled", True):
            auto_speak = self.session.voice_settings.get("auto_speak", True)

            if auto_speak:
                # Speak in background (non-blocking)
                self.speak_async(narration)

        return narration

    def speak_async(self, text: str) -> None:
        """Speak text asynchronously (non-blocking).

        Uses the background TTS script to avoid blocking the main process.

        Args:
            text: Text to speak
        """
        try:
            # Use the existing background TTS script
            project_dir = Path(__file__).parent.parent.parent
            speak_script = project_dir / "hooks" / "speak_narration_bg.py"

            if speak_script.exists():
                # Launch in background
                subprocess.Popen(
                    [sys.executable, str(speak_script), text],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                # Fallback: use TTS directly but in a fire-and-forget manner
                # This is synchronous but we're not waiting for it
                provider = self._get_tts_provider()
                provider.speak(text)

        except Exception as e:
            # Log error but don't raise - voice failure shouldn't break conversation
            import logging
            logging.error(f"TTS error: {e}")

    def speak_sync(self, text: str) -> None:
        """Speak text synchronously (blocking).

        Args:
            text: Text to speak
        """
        try:
            provider = self._get_tts_provider()
            provider.speak(text)
        except Exception as e:
            import logging
            logging.error(f"TTS error: {e}")

    def listen(self, duration: Optional[float] = None) -> str:
        """Listen for voice input and transcribe.

        Args:
            duration: Recording duration in seconds (None = press Enter to stop)

        Returns:
            Transcribed text
        """
        try:
            provider = self._get_stt_provider()
            return provider.listen(duration=duration)
        except Exception as e:
            import logging
            logging.error(f"STT error: {e}")
            raise

    def update_settings(self, **settings) -> None:
        """Update voice settings.

        Args:
            **settings: Voice settings to update
        """
        self.session.update_voice_settings(settings)

        # Invalidate cached providers if relevant settings changed
        if any(key in settings for key in ["tts_provider", "tts_voice", "tts_speed"]):
            self._tts_provider = None

        if "stt_provider" in settings:
            self._stt_provider = None

    async def process_message_async(self, text: str, extract_voice: bool = True) -> Tuple[str, Optional[str]]:
        """Process a message asynchronously, extracting and speaking narration if enabled.

        Args:
            text: Message text
            extract_voice: Whether to extract and speak narration

        Returns:
            Tuple of (text, narration)
        """
        narration = None

        if extract_voice and self.session.voice_settings.get("narration_enabled", True):
            narration = self.extract_and_speak_narration(text)

        return text, narration

    def process_message_sync(self, text: str, extract_voice: bool = True) -> Tuple[str, Optional[str]]:
        """Process a message synchronously, extracting and speaking narration if enabled.

        Args:
            text: Message text
            extract_voice: Whether to extract and speak narration

        Returns:
            Tuple of (text, narration)
        """
        narration = None

        if extract_voice and self.session.voice_settings.get("narration_enabled", True):
            narration = self.extract_and_speak_narration(text)

        return text, narration
