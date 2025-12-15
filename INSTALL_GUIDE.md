# Installation Guide - Quick Reference

Three ways to install Talk-to-Me Claude CLI. Choose what works best for you.

---

## Method 1: One-Line Remote Install (Recommended) ⭐

**Best for:** First-time users, quick testing, production use

**Command:**
```bash
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/talk-to-me-claude-cli/main/install-remote.sh | bash
```

**What it does:**
- Downloads code to `~/.talk-to-me-claude`
- Installs all dependencies
- Configures MCP server globally
- Runs tests
- Ready to use in ANY Claude Code project

**Pros:**
- ✅ No need to clone repo
- ✅ Works from any directory
- ✅ Updates easily (just run again)
- ✅ Clean separation from your projects
- ✅ Global installation (works everywhere)

**Cons:**
- ⚠️ Requires internet connection
- ⚠️ Less control over install location (default: `~/.talk-to-me-claude`)

**Custom location:**
```bash
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/talk-to-me-claude-cli/main/install-remote.sh | bash -s ~/my-location
```

---

## Method 2: Local Install (Development)

**Best for:** Developers, contributors, those who want to modify code

**Commands:**
```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/talk-to-me-claude-cli.git
cd talk-to-me-claude-cli

# 2. Run installer
./install.sh
# OR: python3 install.py
```

**What it does:**
- Uses your cloned repository
- Installs dependencies locally
- Configures MCP server to point to your clone
- Runs tests

**Pros:**
- ✅ Full control over code
- ✅ Can modify and contribute
- ✅ Can switch branches
- ✅ Works offline (after initial clone)

**Cons:**
- ⚠️ Requires manual git clone
- ⚠️ MCP points to specific directory (less portable)

---

## Method 3: Manual Installation (Advanced)

**Best for:** Understanding the system, custom setups, troubleshooting

See [INSTALLATION.md](INSTALLATION.md) for detailed manual steps.

---

## Comparison Table

| Feature | One-Line Remote | Local Install | Manual |
|---------|----------------|---------------|---------|
| **Time to install** | 2 min | 3 min | 15 min |
| **Commands** | 1 | 2 | 20+ |
| **Internet required** | Yes | Clone only | Clone only |
| **Install location** | `~/.talk-to-me-claude` | Repo dir | Anywhere |
| **Easy updates** | Yes (rerun) | Yes (git pull) | Manual |
| **Modify code** | No | Yes | Yes |
| **Global use** | Yes | Yes | Optional |
| **Best for** | Production | Development | Learning |

---

## After Installation (All Methods)

### 1. Add API Keys

```bash
# Edit config file
nano ~/.talk-to-me-claude/.env  # For Method 1
# OR
nano <repo-dir>/.env             # For Method 2

# Add your keys:
OPENAI_API_KEY=sk-your-key-here
```

### 2. Restart Claude Code

```bash
# Close and reopen Claude Code CLI
# Or restart terminal
```

### 3. Test It

Ask Claude to do a coding task:
```
"Add a comment to any file"
```

You should:
1. See code changes in terminal
2. Hear voice narration

### 4. Try Voice Input

```
/talk-to-me:listen
```

Speak your command and it will be transcribed.

---

## Choosing the Right Method

### Use One-Line Remote Install if:
- ✅ You just want it to work
- ✅ You don't need to modify the code
- ✅ You want global installation
- ✅ You want easy updates

### Use Local Install if:
- ✅ You're contributing to the project
- ✅ You want to modify the code
- ✅ You're testing features
- ✅ You prefer git-based updates

### Use Manual Install if:
- ✅ You're learning how it works
- ✅ You have custom requirements
- ✅ You're troubleshooting issues
- ✅ You need fine-grained control

---

## Updating

### Method 1 (One-Line Remote)
```bash
# Just run the installer again
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/talk-to-me-claude-cli/main/install-remote.sh | bash
```

### Method 2 (Local Install)
```bash
cd talk-to-me-claude-cli
git pull origin main
./install.sh
```

### Method 3 (Manual)
Follow manual update steps in INSTALLATION.md

---

## Uninstalling

### Method 1 (One-Line Remote)
```bash
# 1. Remove installation directory
rm -rf ~/.talk-to-me-claude

# 2. Remove from MCP config
nano ~/.claude.json
# Delete the "talk-to-me-claude" entry from mcpServers

# 3. Restart Claude Code
```

### Method 2 (Local Install)
```bash
# 1. Remove from MCP config
nano ~/.claude.json
# Delete the "talk-to-me-claude" entry

# 2. Delete cloned repo
rm -rf talk-to-me-claude-cli

# 3. Restart Claude Code
```

---

## Troubleshooting

### "curl: command not found"
```bash
# macOS
brew install curl

# Or use wget
wget -qO- https://raw.githubusercontent.com/YOUR_USERNAME/talk-to-me-claude-cli/main/install-remote.sh | bash
```

### "Python 3.11+ required"
```bash
brew install python@3.11
```

### "git: command not found"
```bash
brew install git
```

### "Installation failed"
1. Check internet connection
2. Verify Python version: `python3.11 --version`
3. Try local install method instead
4. Check logs for errors

### "MCP server not showing"
1. Check `~/.claude.json` has `talk-to-me-claude` entry
2. Restart Claude Code completely
3. Verify install location in MCP config matches actual location
4. Run: `python3.11 -m src.mcp_server.server` manually to test

---

## Quick Command Reference

```bash
# Install (Method 1)
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/talk-to-me-claude-cli/main/install-remote.sh | bash

# Install (Method 2)
git clone <repo> && cd talk-to-me-claude-cli && ./install.sh

# Update (Method 1)
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/talk-to-me-claude-cli/main/install-remote.sh | bash

# Update (Method 2)
cd talk-to-me-claude-cli && git pull && ./install.sh

# Test installation
python3.11 -m pytest ~/.talk-to-me-claude/tests -v

# Check MCP config
cat ~/.claude.json | grep -A 8 "talk-to-me-claude"

# Edit settings
nano ~/.talk-to-me-claude/.env

# Uninstall
rm -rf ~/.talk-to-me-claude && nano ~/.claude.json
```

---

## Need Help?

- **Issues:** https://github.com/YOUR_USERNAME/talk-to-me-claude-cli/issues
- **Discussions:** https://github.com/YOUR_USERNAME/talk-to-me-claude-cli/discussions
- **Documentation:** [README.md](README.md) • [INSTALLATION.md](INSTALLATION.md) • [CLAUDE.md](CLAUDE.md)

---

**Recommendation:** Start with Method 1 (One-Line Remote Install). It's the fastest and easiest. You can always switch to Method 2 later if you want to contribute or modify code.
