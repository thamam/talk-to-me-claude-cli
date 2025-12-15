# Quick Voice Input Setup

## Current: Slash Command

Right now, voice input works via slash command:
```bash
/talk-to-me:listen
```

## macOS Keyboard Shortcut (DIY)

You can set up Shift+Space to trigger voice input using macOS native tools:

### Using macOS Services + Automator

1. Open **Automator**
2. Create new **Quick Action**
3. Set "Workflow receives" to **no input**
4. Add action: **Run Shell Script**
   ```bash
   /usr/bin/osascript -e 'tell application "System Events" to keystroke "/talk-to-me:listen"'
   /usr/bin/osascript -e 'tell application "System Events" to keystroke return'
   ```
5. Save as "Talk-to-Me Listen"
6. Go to **System Settings → Keyboard → Keyboard Shortcuts → Services**
7. Find "Talk-to-Me Listen" and assign **Shift+Space**

### Using BetterTouchTool (Recommended)

If you have BetterTouchTool:

1. Create new keyboard shortcut: **Shift+Space**
2. Action: **Execute Terminal Command**
   ```bash
   /usr/bin/osascript -e 'tell application "Terminal" to activate'
   /usr/bin/osascript -e 'tell application "System Events" to keystroke "/talk-to-me:listen"'
   /usr/bin/osascript -e 'tell application "System Events" to keystroke return'
   ```

### Using Karabiner-Elements

1. Install Karabiner-Elements
2. Add complex modification:
   ```json
   {
     "description": "Talk-to-Me Voice Input (Shift+Space)",
     "manipulators": [{
       "type": "basic",
       "from": {"key_code": "spacebar", "modifiers": {"mandatory": ["shift"]}},
       "to": [
         {"shell_command": "echo '/talk-to-me:listen' | pbcopy"},
         {"key_code": "v", "modifiers": ["command"]}
       ]
     }]
   }
   ```

## Option: Background Daemon (Future)

For a true system-wide hotkey without third-party tools, we'd need a Python daemon using `pynput` or similar.

Would you like me to implement that?
