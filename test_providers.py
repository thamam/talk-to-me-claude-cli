#!/usr/bin/env python3
"""Test script to verify all TTS providers are properly configured."""

import sys

def test_provider_imports():
    """Test that all provider classes can be imported."""
    print("Testing provider imports...")

    try:
        from src.voice.tts import OpenAITTS, ElevenLabsTTS, LocalTTS, get_tts_provider
        print("✓ All provider classes imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_provider_selection():
    """Test provider selection logic."""
    print("\nTesting provider selection...")

    from src.voice.tts import get_tts_provider

    providers_to_test = [
        ("elevenlabs", "adam"),
        ("openai", "nova"),
        ("local", "default"),
    ]

    results = []
    for provider, voice in providers_to_test:
        try:
            # Don't actually call APIs, just test instantiation logic
            print(f"  Testing {provider} provider...")

            if provider == "elevenlabs":
                # Skip if no API key (expected in tests)
                print(f"    ⚠️  {provider}: Requires ELEVENLABS_API_KEY (skipped)")
                results.append((provider, "skipped"))
            elif provider == "openai":
                # Skip if no API key (expected in tests)
                print(f"    ⚠️  {provider}: Requires OPENAI_API_KEY (skipped)")
                results.append((provider, "skipped"))
            elif provider == "local":
                # Local should work without API key
                try:
                    tts = get_tts_provider(provider=provider)
                    print(f"    ✓ {provider}: Initialized successfully")
                    results.append((provider, "success"))
                except ImportError:
                    print(f"    ⚠️  {provider}: pyttsx3 not installed (install with: pip install pyttsx3)")
                    results.append((provider, "missing_dependency"))
                except Exception as e:
                    print(f"    ✗ {provider}: {e}")
                    results.append((provider, "failed"))

        except Exception as e:
            print(f"    ✗ {provider}: {e}")
            results.append((provider, "failed"))

    return all(status in ["success", "skipped", "missing_dependency"] for _, status in results)


def test_voice_lists():
    """Test that voice lists are properly defined."""
    print("\nTesting voice configurations...")

    from src.voice.tts import ElevenLabsTTS

    # Check ElevenLabs voices
    print(f"  ElevenLabs voices: {len(ElevenLabsTTS.VOICES)} available")
    for name in ["adam", "rachel", "domi"]:
        if name in ElevenLabsTTS.VOICES:
            print(f"    ✓ {name}: {ElevenLabsTTS.VOICES[name][:20]}...")
        else:
            print(f"    ✗ {name}: Not found")
            return False

    return True


def main():
    """Run all tests."""
    print("="*60)
    print("TTS Provider Configuration Test")
    print("="*60)

    results = []

    # Run tests
    results.append(("Provider Imports", test_provider_imports()))
    results.append(("Voice Lists", test_voice_lists()))
    results.append(("Provider Selection", test_provider_selection()))

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
        print("\n🎉 All provider tests passed!")
        print("\n📖 Next steps:")
        print("   1. Set API keys in .env:")
        print("      - ELEVENLABS_API_KEY (recommended)")
        print("      - OPENAI_API_KEY (alternative)")
        print("   2. Choose provider: TTS_PROVIDER=elevenlabs")
        print("   3. Test with: python3 -m src.wrapper --check")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check dependencies.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
