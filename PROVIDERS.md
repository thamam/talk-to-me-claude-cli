# 🎤 TTS Provider Comparison Guide

Complete guide to choosing and configuring Text-to-Speech providers for Talk-to-Me Claude CLI.

---

## 📊 Provider Comparison

| Feature | ElevenLabs | OpenAI TTS | Local (pyttsx3) |
|---------|------------|------------|-----------------|
| **Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Naturalness** | Extremely natural | Natural | Robotic |
| **Emotion/Expression** | ✅ High | Limited | ❌ None |
| **Voices Available** | 10+ premium | 6 standard | System default |
| **Cost (monthly)** | $0-5 | ~$1-5 | Free |
| **Free Tier** | ✅ 10K chars | ❌ No | ✅ Unlimited |
| **Offline** | ❌ No | ❌ No | ✅ Yes |
| **Speed** | Fast (cloud) | Fast (cloud) | Instant (local) |
| **Best For** | Narration, storytelling | General purpose | Testing, offline |

---

## 🎯 Recommendations by Use Case

### **For Best Quality** → ElevenLabs
**Use when:**
- Voice narration is the primary feature
- You want conversational, natural tone
- Budget allows $0-5/month

### **For Balanced Quality/Cost** → OpenAI
**Use when:**
- You need good quality but not premium
- You're already using OpenAI for other services
- You want simple, reliable TTS

### **For Testing/Offline** → Local
**Use when:**
- Developing/testing without API costs
- Need offline capability
- Voice quality is secondary

---

## 🚀 Setup Guides

### **Option 1: ElevenLabs** (Recommended)

#### **1. Get API Key**
```bash
# Sign up (free tier, no credit card)
open https://elevenlabs.io/sign-up

# Get your API key
open https://elevenlabs.io/app/settings/api-keys
```

#### **2. Configure**
```bash
# In your .env file
ELEVENLABS_API_KEY=your-key-here
TTS_PROVIDER=elevenlabs
TTS_VOICE=adam  # or: rachel, domi, bella, etc.
```

#### **3. Available Voices**
| Voice | Gender | Style | Best For |
|-------|--------|-------|----------|
| **adam** | Male | Deep, confident | Narration, explanations |
| **rachel** | Female | Calm, narrative | Documentation, guides |
| **domi** | Female | Strong, confident | Professional content |
| **bella** | Female | Soft, young | Friendly, casual |
| **antoni** | Male | Well-rounded | General purpose |
| **elli** | Female | Emotional | Expressive content |
| **josh** | Male | Young, casual | Conversational |
| **arnold** | Male | Crisp, narrative | Technical content |
| **callum** | Male | Hoarse, mature | Authoritative |
| **charlie** | Male | Casual | Informal explanations |

**For code narration, we recommend: `adam` (male) or `rachel` (female)**

#### **4. Test It**
```bash
python3 -c "
from src.voice.tts import ElevenLabsTTS
tts = ElevenLabsTTS(voice='adam')
tts.speak('I have strengthened the login system by adding email validation.')
"
```

---

### **Option 2: OpenAI TTS**

#### **1. Get API Key**
```bash
# Sign up and add credits ($5-10 recommended)
open https://platform.openai.com/signup

# Get API key
open https://platform.openai.com/api-keys
```

#### **2. Configure**
```bash
# In your .env file
OPENAI_API_KEY=your-key-here
TTS_PROVIDER=openai
TTS_VOICE=nova  # or: alloy, echo, fable, onyx, shimmer
TTS_SPEED=1.0   # 0.25 to 4.0
```

#### **3. Available Voices**
| Voice | Style | Best For |
|-------|-------|----------|
| **alloy** | Neutral | General purpose |
| **echo** | Male, clear | Professional narration |
| **fable** | Expressive | Storytelling |
| **nova** | Female, warm | Friendly explanations |
| **onyx** | Male, deep | Authoritative |
| **shimmer** | Female, soft | Gentle guidance |

**For code narration, we recommend: `nova` or `echo`**

#### **4. Test It**
```bash
python3 -c "
from src.voice.tts import OpenAITTS
tts = OpenAITTS(voice='nova')
tts.speak('I have strengthened the login system by adding email validation.')
"
```

---

### **Option 3: Local TTS** (Free, Offline)

#### **1. Install**
```bash
pip install pyttsx3
```

#### **2. Configure**
```bash
# In your .env file
TTS_PROVIDER=local
# No API key needed!
```

#### **3. Test It**
```bash
python3 -c "
from src.voice.tts import LocalTTS
tts = LocalTTS()
tts.speak('I have strengthened the login system by adding email validation.')
"
```

**Note:** Quality will be noticeably lower (robotic), but it works offline and is free.

---

## 💰 Cost Breakdown

### **ElevenLabs Pricing**
| Plan | Cost | Characters | Narrations* |
|------|------|------------|-------------|
| Free | $0/mo | 10,000/mo | ~15-20 |
| Starter | $5/mo | 30,000/mo | ~50-60 |
| Creator | $22/mo | 100,000/mo | ~150-200 |

*Assuming ~500-600 characters per narration

**Free tier is usually enough for development and light usage!**

### **OpenAI Pricing**
- **TTS**: $0.015 per 1K characters
- ~500 character narration = $0.0075
- 100 narrations = ~$0.75
- **No free tier**, but very affordable

### **Local Pricing**
- **Free forever**
- No API costs
- Uses your CPU

---

## 🔄 Switching Providers

You can easily switch between providers by changing one line in `.env`:

```bash
# Use ElevenLabs (best quality)
TTS_PROVIDER=elevenlabs

# Use OpenAI (good quality, simple)
TTS_PROVIDER=openai

# Use Local (free, offline)
TTS_PROVIDER=local
```

**Or test them all:**
```bash
# Test ElevenLabs
TTS_PROVIDER=elevenlabs python3 -m src.voice.tts

# Test OpenAI
TTS_PROVIDER=openai python3 -m src.voice.tts

# Test Local
TTS_PROVIDER=local python3 -m src.voice.tts
```

---

## 🎛️ Advanced Configuration

### **ElevenLabs Fine-Tuning**
```python
# In code (for custom needs)
from src.voice.tts import ElevenLabsTTS

tts = ElevenLabsTTS(
    voice="adam",
    stability=0.5,          # 0-1: Lower = more expressive
    similarity_boost=0.75,  # 0-1: Higher = more consistent
)
```

### **OpenAI Speed Control**
```bash
# In .env
TTS_SPEED=1.2  # 20% faster
TTS_SPEED=0.8  # 20% slower
```

### **Local Voice Selection**
```python
# List available system voices
import pyttsx3
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    print(voice.name)
```

---

## 🎓 Voice Selection Tips

### **For Code Narration:**
1. **Choose conversational over dramatic**
   - ✅ Adam, Rachel, Nova
   - ❌ Overly expressive voices

2. **Consider your audience**
   - Technical: Arnold, Echo (crisp, clear)
   - General: Adam, Nova (friendly, approachable)
   - Professional: Rachel, Antoni (calm, authoritative)

3. **Test with actual narration**
```bash
python3 -m src.wrapper --text "Add error handling to the authentication system"
```

Listen to how it sounds with real code narration, not just test phrases.

---

## 🐛 Troubleshooting

### **ElevenLabs: "API key invalid"**
```bash
# Verify your key is set correctly
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('ELEVENLABS_API_KEY')[:10])"
```

### **OpenAI: "Insufficient credits"**
Add credits at: https://platform.openai.com/account/billing

### **Local: "No module named 'pyttsx3'"**
```bash
pip install pyttsx3
```

### **All Providers: No audio output**
```bash
# Test audio system
python3 -c "import sounddevice as sd; sd.play([0.1]*10000, 44100); sd.wait()"
```

---

## 📈 Performance Comparison

**Average latency for ~500 character narration:**

| Provider | Generation | Total Time |
|----------|-----------|------------|
| ElevenLabs | ~2-3s | ~3-4s |
| OpenAI | ~1-2s | ~2-3s |
| Local | <0.5s | <1s |

**Total time includes generation + playback start**

---

## 🔗 Resources

- **ElevenLabs Dashboard**: https://elevenlabs.io/app
- **OpenAI Platform**: https://platform.openai.com
- **pyttsx3 Docs**: https://pyttsx3.readthedocs.io

---

**Ready to choose? Start with ElevenLabs free tier for best quality, or use Local for instant testing!**
