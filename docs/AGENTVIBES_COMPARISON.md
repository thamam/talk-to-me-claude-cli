# AgentVibes vs Talk-to-Me Comparison

## Executive Summary

**AgentVibes** (installed globally in `~/.claude/`) and **Talk-to-Me** (this project) are BOTH voice narration systems for Claude Code, but with fundamentally different approaches.

**Key Difference:**
- **AgentVibes**: Explicit TTS calls visible in Claude's output
- **Talk-to-Me**: Invisible background TTS via tag extraction

**Collision Risk:** **LOW** - They use different hooks and mechanisms, but both could trigger simultaneously if not configured properly.

---

## Detailed Comparison

### Architecture

| Aspect | AgentVibes | Talk-to-Me (Ours) |
|--------|------------|-------------------|
| **Hook Type** | UserPromptSubmit (injects instructions) | UserPromptSubmit (injects prompt) + Stop (extracts) |
| **TTS Trigger** | Claude calls `.claude/hooks/play-tts.sh` | Automatic extraction from `[VOICE_NARRATION]` tags |
| **Visibility** | Bash commands visible in output | Completely invisible (background) |
| **When Speaks** | Acknowledgment + Completion (2 times) | Completion only (1 time) |
| **Format** | Claude generates AND executes TTS | Claude generates tags, hook executes TTS |

### Features Comparison

| Feature | AgentVibes | Talk-to-Me |
|---------|------------|-----------|
| **TTS Providers** | ✅ ElevenLabs, Piper | ✅ ElevenLabs, OpenAI, Local (pyttsx3) |
| **STT Support** | ❌ No | ✅ Yes (OpenAI, Local Whisper, macOS) |
| **Personalities** | ✅ 19 personalities (pirate, sarcastic, etc.) | ❌ No |
| **Language Learning** | ✅ Dual-language mode | ❌ No |
| **Slash Commands** | ✅ 30+ commands (namespace: agent-vibes) | ❌ No (planned) |
| **Conversation Tracking** | ❌ No | ✅ Yes (MCP server with session history) |
| **Push-to-Talk** | ❌ No | ❌ No (planned) |
| **Voice Profiles** | ✅ Per-personality favorites | ❌ No |
| **Sentiment System** | ✅ Temporary mood override | ❌ No |
| **Verbosity Levels** | ❌ No | ✅ Yes (brief/medium/detailed) |
| **MCP Server** | ❌ No | ✅ Yes (6 tools, 3 resources) |

### How They Work

#### AgentVibes Flow
```
1. User types command
2. UserPromptSubmit hook injects TTS protocol instructions
3. Claude sees: "You MUST execute TTS at acknowledgment and completion"
4. Claude responds with Bash tool calls:

   Terminal Output:
   > I'll help you fix that bug.
   > Bash: .claude/hooks/play-tts.sh "I'll help you fix that bug"
   > [Does the work]
   > Bash: .claude/hooks/play-tts.sh "Bug fixed successfully!"

5. User sees the Bash commands in terminal
6. TTS plays audio
```

#### Talk-to-Me Flow
```
1. User types command
2. UserPromptSubmit hook injects narration prompt
3. Claude sees: "Wrap narration in [VOICE_NARRATION] tags"
4. Claude responds:

   Terminal Output:
   > Editing auth.py...
   >   + Added null check (line 45)
   >
   > [VOICE_NARRATION]
   > I fixed a bug where the API would crash if a user wasn't found.
   > [/VOICE_NARRATION]

5. Stop hook extracts "[VOICE_NARRATION]..." text
6. Background process speaks it via TTS
7. User sees tags in terminal (but could be hidden)
```

### Slash Commands

#### AgentVibes Commands (30+)
```
/agent-vibes:personality flirty
/agent-vibes:switch nova
/agent-vibes:list
/agent-vibes:preview
/agent-vibes:replay
/agent-vibes:sentiment angry
/agent-vibes:learn enable
/agent-vibes:target spanish
/agent-vibes:provider piper
... and 20+ more
```

#### Talk-to-Me Commands (Planned)
```
/talk-to-me:mode auto           # coding_only/conversational/auto
/talk-to-me:verbosity brief     # brief/medium/detailed
/talk-to-me:provider openai     # TTS/STT provider
/talk-to-me:listen              # Push-to-talk shortcut
... (to be implemented)
```

### Configuration

#### AgentVibes Config
```bash
# Location: ~/.claude/tts-*.txt files

# Personality
~/.claude/tts-personality.txt → "sarcastic"

# Sentiment (overrides personality)
~/.claude/tts-sentiment.txt → "angry"

# Provider
~/.claude/tts-provider.txt → "piper" or "elevenlabs"

# Voice
~/.claude/tts-voice.txt → "nova" (provider-specific)
```

#### Talk-to-Me Config
```bash
# Location: .env file in project root

# TTS
TTS_PROVIDER=local              # elevenlabs, openai, local
TTS_VOICE=nova                  # Provider-specific voice
TTS_SPEED=1.0

# STT
STT_PROVIDER=macos              # openai, local, macos
STT_MODEL=whisper-1
STT_LANGUAGE=en-US

# Narration
NARRATION_ENABLED=true
NARRATION_VERBOSITY=medium      # brief, medium, detailed
AUTO_SPEAK=true
```

### Pros & Cons

#### AgentVibes Pros
✅ Mature, feature-rich (19 personalities!)
✅ Excellent Piper TTS integration (high quality, offline)
✅ Language learning mode (dual-language)
✅ Extensive slash commands
✅ Active community (GitHub: paulpreibisch/AgentVibes)
✅ Voice profile management
✅ Sentiment system for temporary mood

#### AgentVibes Cons
❌ Visible Bash commands clutter output
❌ No STT (voice input)
❌ No conversation tracking
❌ No MCP integration
❌ Speaks TWICE per task (acknowledgment + completion)
❌ No verbosity control

#### Talk-to-Me Pros
✅ Invisible TTS (cleaner output)
✅ STT support (3 providers: OpenAI, Local, macOS)
✅ Full conversation tracking (MCP server)
✅ Session management with history
✅ Verbosity levels (brief/medium/detailed)
✅ Speaks ONCE per task (completion only)
✅ MCP tools for programmatic control
✅ OpenAI TTS support

#### Talk-to-Me Cons
❌ No personalities
❌ No language learning
❌ Fewer slash commands
❌ Less mature (new project)
❌ No Piper integration yet
❌ No sentiment system

---

## Collision Analysis

### Do They Conflict?

**Potential Conflicts:**

1. **Hook Collision**: BOTH use `UserPromptSubmit` hook
   - AgentVibes: `~/.claude/hooks/user-prompt-submit.sh` (global)
   - Talk-to-Me: `.claude/settings.json` (project-specific)
   - **Result**: Project hooks override global hooks → AgentVibes disabled in Talk-to-Me projects

2. **Double Narration**: If both active, user hears:
   - AgentVibes: Acknowledgment
   - AgentVibes: Completion
   - Talk-to-Me: Completion
   - **Total**: 3 audio messages per task! 😱

3. **Visual Clutter**: If both active, terminal shows:
   - Bash commands from AgentVibes
   - [VOICE_NARRATION] tags from Talk-to-Me
   - Very messy output

**Current Status in This Project:**
- ✅ Talk-to-Me hooks configured (`.claude/settings.json`)
- ✅ AgentVibes hooks exist globally (`~/.claude/hooks/`)
- ✅ **No collision**: Project hooks take precedence
- ✅ AgentVibes is NOT active in this project

### How to Check for Collisions

```bash
# Check if AgentVibes is active globally
cat ~/.claude/hooks/user-prompt-submit.sh | head -5

# Check if Talk-to-Me is active in project
cat .claude/settings.json

# Test which is active
echo "Test prompt" | ~/.claude/hooks/user-prompt-submit.sh 2>&1 | head -20
```

---

## Can We Learn From AgentVibes?

### What to Adopt

1. **✅ Slash Command Structure**
   - Namespace: `talk-to-me` (like `agent-vibes`)
   - `commands.json` manifest
   - Markdown command files with `!bash` directives

2. **✅ Piper TTS Integration**
   - High-quality neural TTS
   - Offline, fast
   - Already in AgentVibes hooks (reusable)

3. **✅ Voice Profile System**
   - Map voices to providers
   - Favorites per personality
   - Seamless switching

4. **❓ Personality System** (Optional)
   - Could add simple personalities
   - But conflicts with "invisible" design philosophy
   - Maybe as opt-in feature?

5. **❓ Language Learning** (Optional)
   - Dual-language narration
   - Great for learning
   - But niche use case

### What NOT to Adopt

1. **❌ Explicit Bash Calls**
   - Clutters terminal output
   - Our invisible approach is cleaner

2. **❌ Acknowledgment + Completion**
   - Too much audio (2x per task)
   - Our single narration is sufficient

3. **❌ Global Config in ~/.claude/**
   - Project-specific .env is better
   - Allows per-project settings

---

## Should We Switch to AgentVibes?

### Consider Switching If:
- ✅ You want 19 personalities (pirate mode!)
- ✅ You need language learning features
- ✅ You don't mind visible Bash commands
- ✅ You don't need STT or conversation tracking

### Stick with Talk-to-Me If:
- ✅ You want clean, invisible TTS
- ✅ You need STT (voice input)
- ✅ You want conversation history tracking
- ✅ You prefer MCP integration
- ✅ You want verbosity control
- ✅ You need programmatic access via MCP tools

### Best of Both Worlds (Hybrid Approach):

**Option 1: Use Both (Different Projects)**
- AgentVibes: Global default for all projects
- Talk-to-Me: Specific projects needing STT/tracking
- Project hooks override global hooks automatically

**Option 2: Integrate Features**
- Keep Talk-to-Me architecture
- Add Piper TTS provider
- Add simple personality system
- Add AgentVibes-style slash commands
- **Result**: Best of both!

**Option 3: Contribute to AgentVibes**
- Add invisible narration mode to AgentVibes
- Add STT support
- Add MCP server
- Merge projects

---

## Implementation Plan

### Phase 1: Learn from AgentVibes ✅ (Current)
- [x] Analyze AgentVibes architecture
- [x] Document differences
- [x] Identify reusable components

### Phase 2: Add Compatible Features (Next)
- [ ] Implement slash commands (Talk-to-Me namespace)
- [ ] Add Piper TTS provider
- [ ] Add simple personality system (optional)
- [ ] Mode selection (coding_only/conversational/auto)

### Phase 3: Integration (Future)
- [ ] Make systems mutually exclusive (detect + disable other)
- [ ] Migration tool (AgentVibes → Talk-to-Me)
- [ ] Unified config format

---

## Recommendation

**Keep Talk-to-Me, Add AgentVibes Features**

Why:
1. Talk-to-Me has unique features (STT, MCP, conversation tracking)
2. Invisible narration is cleaner for coding
3. Can selectively adopt AgentVibes features (Piper, slash commands)
4. No need to reinvent what Talk-to-Me does well

**Next Steps:**
1. Implement slash commands (like AgentVibes format)
2. Add Piper TTS provider (reuse AgentVibes scripts)
3. Add mode selection (coding_only/conversational/auto)
4. Add push-to-talk (Ctrl+Space)
5. Consider simple personality system later

**Don't Switch Because:**
- Losing STT would be a step backward
- MCP server provides valuable infrastructure
- Invisible narration is better for focus
- Can cherry-pick AgentVibes features without switching
