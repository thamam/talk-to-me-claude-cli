"""Speech-to-Text module with multiple provider support.

Supports:
- OpenAI Whisper API (primary)
- Local Whisper models (fallback)
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
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
    AUDIO_RECORDING_AVAILABLE = True
except ImportError:
    AUDIO_RECORDING_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False


class STTProvider(ABC):
    """Abstract base class for STT providers."""

    @abstractmethod
    def transcribe(self, audio_path: Path) -> str:
        """Transcribe audio file to text.

        Args:
            audio_path: Path to audio file

        Returns:
            Transcribed text
        """
        pass

    @abstractmethod
    def listen(self, duration: Optional[float] = None) -> str:
        """Record audio and transcribe to text.

        Args:
            duration: Recording duration in seconds (None = press Enter to stop)

        Returns:
            Transcribed text
        """
        pass


class OpenAIWhisper(STTProvider):
    """OpenAI Whisper STT provider using OpenAI API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "whisper-1",
        language: Optional[str] = None,
    ):
        """Initialize OpenAI Whisper STT provider.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Whisper model to use
            language: Language code (e.g., 'en', 'es') or None for auto-detect
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package not installed. Run: pip install openai")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.language = language

    def transcribe(self, audio_path: Path) -> str:
        """Transcribe audio file using OpenAI Whisper.

        Args:
            audio_path: Path to audio file

        Returns:
            Transcribed text
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        with open(audio_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                language=self.language,
            )

        return transcript.text

    def listen(self, duration: Optional[float] = None) -> str:
        """Record audio and transcribe.

        Args:
            duration: Recording duration in seconds (None = press Enter to stop)

        Returns:
            Transcribed text
        """
        if not AUDIO_RECORDING_AVAILABLE:
            raise ImportError(
                "Audio recording not available. Install: pip install sounddevice soundfile numpy"
            )

        # Recording parameters
        sample_rate = 16000  # Whisper expects 16kHz
        channels = 1  # Mono

        print("🎤 Recording... ", end="", flush=True)

        if duration:
            # Fixed duration recording
            print(f"({duration}s)")
            audio_data = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=channels,
                dtype=np.float32
            )
            sd.wait()
        else:
            # Press Enter to stop
            print("(Press Enter to stop)")
            recording = []

            def callback(indata, frames, time, status):
                recording.append(indata.copy())

            with sd.InputStream(
                samplerate=sample_rate,
                channels=channels,
                callback=callback,
                dtype=np.float32
            ):
                input()  # Wait for Enter key

            audio_data = np.concatenate(recording, axis=0)

        print("✓ Recording complete")

        # Save to temp file
        fd, temp_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        temp_file = Path(temp_path)

        try:
            sf.write(str(temp_file), audio_data, sample_rate)

            print("🔄 Transcribing...")
            text = self.transcribe(temp_file)
            print(f"✓ Transcription: {text}")

            return text
        finally:
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()


class LocalWhisper(STTProvider):
    """Local Whisper STT provider using openai-whisper."""

    def __init__(self, model_name: str = "base"):
        """Initialize local Whisper STT provider.

        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
        """
        try:
            import whisper
            self.model = whisper.load_model(model_name)
        except ImportError:
            raise ImportError("whisper not installed. Run: pip install openai-whisper")

    def transcribe(self, audio_path: Path) -> str:
        """Transcribe audio file using local Whisper.

        Args:
            audio_path: Path to audio file

        Returns:
            Transcribed text
        """
        result = self.model.transcribe(str(audio_path), fp16=False)
        return result["text"]

    def listen(self, duration: Optional[float] = None) -> str:
        """Record audio and transcribe.

        Args:
            duration: Recording duration in seconds (None = press Enter to stop)

        Returns:
            Transcribed text
        """
        # Use same recording logic as OpenAI provider
        # (Implementation similar to OpenAIWhisper.listen())
        raise NotImplementedError("Local Whisper listen() not yet implemented")


class MacOSSTT(STTProvider):
    """macOS native STT provider using built-in speech recognition."""

    def __init__(self, language: str = "en-US"):
        """Initialize macOS STT provider.

        Args:
            language: Language code (e.g., 'en-US', 'es-ES')
        """
        if not SPEECH_RECOGNITION_AVAILABLE:
            raise ImportError("speech_recognition not installed. Run: pip install SpeechRecognition")

        self.recognizer = sr.Recognizer()
        self.language = language

    def transcribe(self, audio_path: Path) -> str:
        """Transcribe audio file using macOS speech recognition.

        Args:
            audio_path: Path to audio file

        Returns:
            Transcribed text
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        with sr.AudioFile(str(audio_path)) as source:
            audio = self.recognizer.record(source)
            try:
                # Use macOS built-in recognition (offline, free)
                text = self.recognizer.recognize_sphinx(audio)
                return text
            except sr.UnknownValueError:
                raise ValueError("Could not understand audio")
            except sr.RequestError as e:
                raise RuntimeError(f"Speech recognition error: {e}")

    def listen(self, duration: Optional[float] = None) -> str:
        """Record audio and transcribe using macOS microphone.

        Args:
            duration: Recording duration in seconds (None = auto-detect silence)

        Returns:
            Transcribed text
        """
        print("🎤 Listening... ", end="", flush=True)

        with sr.Microphone() as source:
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

            if duration:
                print(f"({duration}s)")
                audio = self.recognizer.record(source, duration=duration)
            else:
                print("(speak now)")
                audio = self.recognizer.listen(source)

        print("✓ Processing...")

        try:
            # Use macOS built-in recognition (offline, free)
            text = self.recognizer.recognize_sphinx(audio)
            print(f"✓ Transcription: {text}")
            return text
        except sr.UnknownValueError:
            raise ValueError("Could not understand audio")
        except sr.RequestError as e:
            raise RuntimeError(f"Speech recognition error: {e}")


def get_stt_provider(
    provider: str = "openai",
    model: str = "whisper-1",
    language: Optional[str] = None,
) -> STTProvider:
    """Get STT provider instance.

    Args:
        provider: Provider name (openai, local, macos)
        model: Model to use
        language: Language code or None for auto-detect

    Returns:
        STTProvider instance
    """
    provider = provider.lower()

    if provider == "openai":
        return OpenAIWhisper(model=model, language=language)
    elif provider == "local":
        return LocalWhisper(model_name=model)
    elif provider == "macos":
        lang = language or "en-US"
        return MacOSSTT(language=lang)
    else:
        raise ValueError(f"Unknown STT provider: {provider}. Choose: openai, local, or macos")


def listen(
    duration: Optional[float] = None,
    provider: Optional[str] = None,
) -> str:
    """Convenience function to record and transcribe using configured provider.

    Args:
        duration: Recording duration in seconds (None = press Enter to stop)
        provider: Provider name (defaults to STT_PROVIDER env var or 'openai')

    Returns:
        Transcribed text
    """
    provider = provider or os.getenv("STT_PROVIDER", "openai")
    model = os.getenv("STT_MODEL", "whisper-1")

    stt = get_stt_provider(provider=provider, model=model)
    return stt.listen(duration=duration)


# Example usage
if __name__ == "__main__":
    print("Testing STT...")

    try:
        text = listen()
        print(f"\n✓ You said: {text}")
    except Exception as e:
        print(f"\n✗ STT test failed: {e}")
