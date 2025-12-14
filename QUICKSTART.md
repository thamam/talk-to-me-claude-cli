# 🚀 Quick Start Guide

Get up and running with Talk-to-Me Claude CLI in 5 minutes!

---

## Step 1: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Or install the package in development mode
pip install -e .
```

**System Requirements:**
- Python 3.10+
- FFmpeg (for audio processing)
- OpenAI API key

**Install FFmpeg:**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows (using Chocolatey)
choco install ffmpeg
```

---

## Step 2: Configure Environment

```bash
# Copy the environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env  # or use your favorite editor
```

**Minimum configuration:**
```bash
OPENAI_API_KEY=sk-your-api-key-here
```

---

## Step 3: Test Your Setup

```bash
# Check if everything is configured correctly
python -m src.wrapper --check
```

You should see:
```
✅ All dependencies satisfied

📋 Configuration:
   TTS Provider: openai
   TTS Voice: nova
   STT Provider: openai
   Narration: true
   Verbosity: medium
```

---

## Step 4: Try the Demo

### Option A: Text Mode (No Voice Input)

```bash
python -m src.wrapper --text "Fix the login bug"
```

This will:
1. Show a simulated Claude response
2. Extract and display the narration
3. Speak it using TTS

### Option B: Voice Mode (Full Experience)

```bash
python -m src.wrapper --voice
```

This will:
1. Show the welcome banner
2. Wait for you to press Enter
3. Record your voice command
4. Transcribe it using Whisper
5. Process with Claude (simulated)
6. Speak the narration

---

## Step 5: Understand the Output

When you run the demo, you'll see:

### Terminal Output
```
╔═══════════════════════════════════════════════════════════════╗
║  🎤 Talk-to-Me Claude CLI - Voice Narration Layer           ║
║                                                               ║
║  Explains WHAT was done, not what's on screen                ║
╚═══════════════════════════════════════════════════════════════╝

🎤 Voice Mode Active
Press Enter to start recording, Enter again to stop

------------------------------------------------------------
Ready for voice input...

🎤 Recording... (Press Enter to stop)
✓ Recording complete
🔄 Transcribing...
✓ Transcription: Add error handling to the authentication system

📝 You said: Add error handling to the authentication system

💭 Processing with Claude Code...

============================================================
I'll help you with that.

[Detailed code changes would appear here in production]
============================================================

🔊 Narration: I've processed your request. Add error handling
to the authentication system. This is a demonstration of how
the voice narration system works.
```

### Audio Output
You'll hear a voice speaking the narration.

---

## 🎯 Next Steps

### Customize Your Voice

Edit `.env` to change the voice:

```bash
TTS_VOICE=alloy    # Try: alloy, echo, fable, nova, onyx, shimmer
TTS_SPEED=1.2      # Speak 20% faster
```

### Adjust Verbosity

```bash
NARRATION_VERBOSITY=brief    # Options: brief, medium, detailed
```

**Brief:**
> "I fixed the login bug."

**Medium:**
> "I fixed the login bug by adding null checks and improving error handling."

**Detailed:**
> "I fixed the login bug by adding null checks to prevent crashes when users aren't found. I also improved the error messages to give clearer feedback and added tests to ensure the fix works correctly."

---

## 🔍 View the Narration Prompt

Want to see the exact instructions Claude receives?

```bash
python -m src.wrapper --show-prompt
```

This displays the full system prompt that tells Claude how to generate narrations.

---

## 🧪 Test Individual Components

### Test TTS Only

```bash
python -m src.voice.tts
```

### Test STT Only

```bash
python -m src.voice.stt
```

### Test Narration Extraction

```bash
python -m src.extractor
```

---

## ⚙️ Advanced Configuration

### Use Local TTS (Offline, Free)

```bash
# Install pyttsx3
pip install pyttsx3

# Update .env
TTS_PROVIDER=local
```

### Use Different STT Model

```bash
STT_MODEL=whisper-1    # OpenAI (default)
# or
STT_MODEL=base         # Local Whisper (when implemented)
```

---

## 🐛 Common Issues

### "No audio devices found"

**Fix:**
```bash
# Test if audio devices are accessible
python -c "import sounddevice as sd; print(sd.query_devices())"
```

### "OpenAI API error: Unauthorized"

**Fix:**
```bash
# Verify your API key is set correctly
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('OPENAI_API_KEY')[:10] + '...')"
```

### "Module not found" errors

**Fix:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Or install in editable mode
pip install -e .
```

---

## 📚 Learn More

- [Full README](README.md) - Complete documentation
- [Architecture](README.md#-how-it-works) - How it works under the hood
- [Contributing](README.md#-contributing) - Help improve the project

---

## 🎉 You're Ready!

You now have a working voice narration system. The current demo mode simulates Claude's responses, but Phase 2 will integrate with the actual Claude Code CLI.

**Happy coding with voice! 🎤✨**
