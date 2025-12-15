# 🎣 Claude Code Hooks Integration

This guide shows how to integrate voice narration with Claude Code using hooks.

---

## 🚀 Quick Setup

### 1. Configure Claude Code Hooks

Add these hooks to your Claude Code settings file:

**Location:** `~/.config/claude-code/settings.json` (or your platform's config directory)

```json
{
  "hooks": {
    "user-prompt-submit": "/Users/tomerhamam/personal/repos/talk-to-me-claude-cli/hooks/inject_narration_prompt.sh",
    "response-complete": "/Users/tomerhamam/personal/repos/talk-to-me-claude-cli/hooks/process_response.sh"
  }
}
```

**Note:** Update the paths to match your actual installation directory!

### 2. Verify Hooks Are Loaded

Restart Claude Code and run:

```bash
claude --version
```

You should see the hooks being loaded in the startup messages (if verbose mode is enabled).

---

## 🔧 How It Works

### Hook 1: `user-prompt-submit` (inject_narration_prompt.sh)

**Triggers:** When you submit a message to Claude

**Action:** Injects the voice narration system prompt before your message

**Example:**
```
Your message: "Add error handling to login"

Becomes: "[Narration System Prompt]

---

Add error handling to login"
```

### Hook 2: `response-complete` (process_response.sh)

**Triggers:** After Claude generates a response

**Action:**
1. Extracts `<voice_narration>` tags from response
2. Speaks the narration using configured TTS provider
3. Runs in background so CLI doesn't block

---

## ⚙️ Configuration

Edit `.env` to customize behavior:

```bash
# Enable/disable narration
NARRATION_ENABLED=true

# Auto-speak narration (false = extract only, don't speak)
AUTO_SPEAK=true

# Verbosity level
NARRATION_VERBOSITY=medium  # brief, medium, detailed

# TTS Provider
TTS_PROVIDER=local  # elevenlabs, openai, local
```

---

## 🧪 Testing Hooks Manually

### Test the inject hook:
```bash
echo "Add error handling" | ./hooks/inject_narration_prompt.sh
```

**Expected:** Should output your message with the narration prompt prepended.

### Test the process hook:
```bash
cat <<'EOF' | ./hooks/process_response.sh
I've updated the code.

<voice_narration>
I added error handling to the login function.
</voice_narration>

[Code changes here...]
EOF
```

**Expected:** Should extract and speak "I added error handling to the login function."

---

## 🐛 Troubleshooting

### Hook not running?

1. **Check paths are absolute:**
   ```bash
   # Get full path
   realpath hooks/inject_narration_prompt.sh
   ```

2. **Check hooks are executable:**
   ```bash
   ls -la hooks/*.sh
   # Should show: -rwxr-xr-x
   ```

3. **Check hook output:**
   ```bash
   # Test manually
   echo "test" | ./hooks/inject_narration_prompt.sh
   ```

### Narration not speaking?

1. **Check environment variables:**
   ```bash
   python3 -c "
   from dotenv import load_dotenv
   import os
   load_dotenv()
   print('NARRATION_ENABLED:', os.getenv('NARRATION_ENABLED'))
   print('AUTO_SPEAK:', os.getenv('AUTO_SPEAK'))
   print('TTS_PROVIDER:', os.getenv('TTS_PROVIDER'))
   "
   ```

2. **Test TTS directly:**
   ```bash
   python3 -m src.wrapper --text "Test narration"
   ```

3. **Check for errors in hook:**
   ```bash
   # The hook logs to stderr
   # Look for "⚠️  TTS failed" messages
   ```

### Python module not found?

The hooks add the project root to Python path:
```bash
sys.path.insert(0, '$PROJECT_ROOT')
```

If this fails, check:
```bash
# Make sure you're in the project directory
pwd
# Should show: .../talk-to-me-claude-cli

# Verify Python can find modules
python3 -c "from src.voice import speak; print('OK')"
```

---

## 📝 Hook Environment Variables

Both hooks have access to:

- `PROJECT_ROOT` - Full path to talk-to-me-claude-cli
- `NARRATION_ENABLED` - Enable/disable narration
- `NARRATION_VERBOSITY` - Verbosity level
- `AUTO_SPEAK` - Auto-speak narration
- `TTS_PROVIDER` - TTS provider to use
- All other `.env` variables

---

## 🔄 Disabling Hooks Temporarily

### Option 1: Disable in settings
```json
{
  "hooks": {
    // Comment out or remove hooks
  }
}
```

### Option 2: Use environment variable
```bash
NARRATION_ENABLED=false claude "your message"
```

### Option 3: Edit .env
```bash
# In .env
NARRATION_ENABLED=false
```

---

## 🎯 Advanced: Conditional Narration

You can modify the hooks to enable narration only for certain commands:

```bash
# In inject_narration_prompt.sh
# Only add narration prompt if user message contains "explain" or "summarize"
if echo "$USER_MESSAGE" | grep -qE "(explain|summarize)"; then
    # Add narration prompt
else
    # Skip narration
fi
```

---

## 📚 Next Steps

Once hooks are working:

1. **Test with real Claude Code commands**
2. **Adjust verbosity** to your preference
3. **Try different TTS providers** (elevenlabs, openai, local)
4. **Customize the narration prompt** in `src/prompt.py`

---

## 🔗 Resources

- [Claude Code Documentation](https://claude.ai/code)
- [Hook Configuration Reference](https://github.com/anthropics/claude-code/docs/hooks.md)
- [TTS Provider Guide](PROVIDERS.md)

---

**Ready to test! Ask Claude to do something and listen for the voice narration.**
