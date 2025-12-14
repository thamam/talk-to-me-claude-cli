"""Text-to-Speech module with multiple provider support.

Supports:
- ElevenLabs API (highest quality, most natural)
- OpenAI TTS API (high quality)
- Local TTS engines (offline, free)
"""

import os
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import save
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

try:
    import sounddevice as sd
    import soundfile as sf
    AUDIO_PLAYBACK_AVAILABLE = True
except ImportError:
    AUDIO_PLAYBACK_AVAILABLE = False


class TTSProvider(ABC):
    """Abstract base class for TTS providers."""

    @abstractmethod
    def synthesize(self, text: str) -> Path:
        """Synthesize text to audio file.

        Args:
            text: Text to synthesize

        Returns:
            Path to generated audio file
        """
        pass

    @abstractmethod
    def speak(self, text: str) -> None:
        """Synthesize and play audio.

        Args:
            text: Text to speak
        """
        pass


class OpenAITTS(TTSProvider):
    """OpenAI TTS provider using OpenAI API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        voice: str = "nova",
        model: str = "tts-1",
        speed: float = 1.0,
    ):
        """Initialize OpenAI TTS provider.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            voice: Voice to use (alloy, echo, fable, nova, onyx, shimmer)
            model: Model to use (tts-1, tts-1-hd)
            speed: Speech speed (0.25 to 4.0)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package not installed. Run: pip install openai")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=self.api_key)
        self.voice = voice
        self.model = model
        self.speed = speed

    def synthesize(self, text: str, output_path: Optional[Path] = None) -> Path:
        """Synthesize text to audio file using OpenAI TTS.

        Args:
            text: Text to synthesize
            output_path: Optional path for output file

        Returns:
            Path to generated audio file
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Create temp file if no output path specified
        if output_path is None:
            fd, temp_path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)
            output_path = Path(temp_path)

        # Generate speech
        response = self.client.audio.speech.create(
            model=self.model,
            voice=self.voice,
            input=text,
            speed=self.speed,
        )

        # Write to file
        response.stream_to_file(str(output_path))

        return output_path

    def speak(self, text: str) -> None:
        """Synthesize and play audio.

        Args:
            text: Text to speak
        """
        if not AUDIO_PLAYBACK_AVAILABLE:
            raise ImportError(
                "Audio playback not available. Install: pip install sounddevice soundfile"
            )

        # Generate audio
        audio_path = self.synthesize(text)

        try:
            # Play audio
            data, samplerate = sf.read(str(audio_path))
            sd.play(data, samplerate)
            sd.wait()  # Wait until audio finishes playing
        finally:
            # Clean up temp file
            if audio_path.exists():
                audio_path.unlink()


class LocalTTS(TTSProvider):
    """Local TTS provider using pyttsx3 (offline, no API needed)."""

    def __init__(self, rate: int = 200, volume: float = 1.0):
        """Initialize local TTS provider.

        Args:
            rate: Speech rate (words per minute)
            volume: Volume (0.0 to 1.0)
        """
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
        except ImportError:
            raise ImportError("pyttsx3 not installed. Run: pip install pyttsx3")

    def synthesize(self, text: str, output_path: Optional[Path] = None) -> Path:
        """Synthesize text to audio file.

        Args:
            text: Text to synthesize
            output_path: Path for output file

        Returns:
            Path to generated audio file
        """
        if output_path is None:
            fd, temp_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            output_path = Path(temp_path)

        self.engine.save_to_file(text, str(output_path))
        self.engine.runAndWait()

        return output_path

    def speak(self, text: str) -> None:
        """Synthesize and play audio directly.

        Args:
            text: Text to speak
        """
        self.engine.say(text)
        self.engine.runAndWait()


class ElevenLabsTTS(TTSProvider):
    """ElevenLabs TTS provider - highest quality, most natural voices."""

    # Popular ElevenLabs voice IDs
    VOICES = {
        "adam": "pNInz6obpgDQGcFmaJgB",      # Male, deep, confident
        "rachel": "21m00Tcm4TlvDq8ikWAM",    # Female, calm, narrative
        "domi": "AZnzlk1XvdvUeBnXmlld",      # Female, strong, confident
        "bella": "EXAVITQu4vr4xnSDxMaL",     # Female, soft, young
        "antoni": "ErXwobaYiN019PkySvjV",    # Male, well-rounded
        "elli": "MF3mGyEYCl7XYWbV9V6O",      # Female, emotional
        "josh": "TxGEqnHWrfWFTfGW9XjX",      # Male, young, casual
        "arnold": "VR6AewLTigWG4xSOukaG",    # Male, crisp, narrative
        "callum": "N2lVS1w4EtoT3dr4eOWO",    # Male, hoarse, middle-aged
        "charlie": "IKne3meq5aSn9XLyUdCD",   # Male, casual, conversational
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        voice: str = "adam",
        model: str = "eleven_turbo_v2_5",
        stability: float = 0.5,
        similarity_boost: float = 0.75,
    ):
        """Initialize ElevenLabs TTS provider.

        Args:
            api_key: ElevenLabs API key (defaults to ELEVENLABS_API_KEY env var)
            voice: Voice name (adam, rachel, domi, bella, etc.) or voice ID
            model: Model to use (eleven_turbo_v2_5, eleven_multilingual_v2)
            stability: Voice stability (0.0 to 1.0) - lower = more expressive
            similarity_boost: Voice similarity (0.0 to 1.0) - higher = more consistent
        """
        if not ELEVENLABS_AVAILABLE:
            raise ImportError("elevenlabs package not installed. Run: pip install elevenlabs")

        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ElevenLabs API key required. Set ELEVENLABS_API_KEY environment variable."
            )

        self.client = ElevenLabs(api_key=self.api_key)

        # Resolve voice name to ID if needed
        if voice.lower() in self.VOICES:
            self.voice_id = self.VOICES[voice.lower()]
        else:
            self.voice_id = voice  # Assume it's already a voice ID

        self.model = model
        self.stability = stability
        self.similarity_boost = similarity_boost

    def synthesize(self, text: str, output_path: Optional[Path] = None) -> Path:
        """Synthesize text to audio file using ElevenLabs.

        Args:
            text: Text to synthesize
            output_path: Optional path for output file

        Returns:
            Path to generated audio file
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Create temp file if no output path specified
        if output_path is None:
            fd, temp_path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)
            output_path = Path(temp_path)

        # Generate speech
        audio_generator = self.client.text_to_speech.convert(
            voice_id=self.voice_id,
            text=text,
            model_id=self.model,
            voice_settings={
                "stability": self.stability,
                "similarity_boost": self.similarity_boost,
            }
        )

        # Save to file - convert generator to bytes
        with open(output_path, 'wb') as f:
            for chunk in audio_generator:
                f.write(chunk)

        return output_path

    def speak(self, text: str) -> None:
        """Synthesize and play audio.

        Args:
            text: Text to speak
        """
        if not AUDIO_PLAYBACK_AVAILABLE:
            raise ImportError(
                "Audio playback not available. Install: pip install sounddevice soundfile"
            )

        # Generate audio
        audio_path = self.synthesize(text)

        try:
            # Play audio
            data, samplerate = sf.read(str(audio_path))
            sd.play(data, samplerate)
            sd.wait()  # Wait until audio finishes playing
        finally:
            # Clean up temp file
            if audio_path.exists():
                audio_path.unlink()


def get_tts_provider(
    provider: str = "openai",
    voice: Optional[str] = None,
    speed: float = 1.0,
) -> TTSProvider:
    """Get TTS provider instance.

    Args:
        provider: Provider name (elevenlabs, openai, local)
        voice: Voice to use (provider-specific, defaults to env var)
        speed: Speech speed (OpenAI only)

    Returns:
        TTSProvider instance
    """
    provider = provider.lower()

    # Get provider-specific voice from env if not specified
    if voice is None:
        if provider == "elevenlabs":
            voice = os.getenv("ELEVENLABS_VOICE", "adam")
        elif provider == "openai":
            voice = os.getenv("OPENAI_VOICE", "nova")
        else:
            voice = "default"

    if provider == "elevenlabs":
        return ElevenLabsTTS(voice=voice)
    elif provider == "openai":
        return OpenAITTS(voice=voice, speed=speed)
    elif provider == "local":
        return LocalTTS(rate=int(speed * 200))
    else:
        raise ValueError(f"Unknown TTS provider: {provider}. Choose: elevenlabs, openai, or local")


def speak(text: str, provider: Optional[str] = None) -> None:
    """Convenience function to speak text using configured provider.

    Args:
        text: Text to speak
        provider: Provider name (defaults to TTS_PROVIDER env var or 'openai')
    """
    if not text or not text.strip():
        return

    provider = provider or os.getenv("TTS_PROVIDER", "openai")
    speed = float(os.getenv("TTS_SPEED", "1.0"))

    # Voice is auto-selected based on provider in get_tts_provider()
    tts = get_tts_provider(provider=provider, speed=speed)
    tts.speak(text)


# Example usage
if __name__ == "__main__":
    sample_text = """
    I've strengthened the login system by adding email validation and improving
    the error messages users will see when something goes wrong.
    """

    print("Testing TTS...")
    print(f"Text: {sample_text}")

    try:
        speak(sample_text.strip())
        print("✓ TTS test completed")
    except Exception as e:
        print(f"✗ TTS test failed: {e}")
