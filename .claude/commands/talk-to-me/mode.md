---
description: Set narration mode (coding_only/conversational/auto)
argument-hint: [coding_only|conversational|auto|list]
---

# /talk-to-me:mode

Set the narration mode to control when Claude provides voice narration.

## Modes

### `coding_only` - Coding Tasks Only
Narrate **only** when performing coding tasks:
- File edits, bug fixes, refactoring
- Adding features, tests, documentation
- Error fixes and optimizations

**Skip narration** for:
- Questions and answers
- Explanations and discussions
- General conversation

### `conversational` - All Responses
Narrate **all** responses, including:
- Q&A and explanations
- Discussions and recommendations
- Everything Claude says

### `auto` - Smart Mode (Default)
Let Claude decide based on context. Claude narrates:
- Completed work (edits, fixes, refactors)
- Complex explanations where audio helps
- Important findings or insights

Claude skips narration for:
- Simple yes/no answers
- Quick clarifications
- When user is reading code on screen

## Usage

```bash
# Set mode
/talk-to-me:mode coding_only
/talk-to-me:mode conversational
/talk-to-me:mode auto

# List available modes
/talk-to-me:mode list

# Show current mode
/talk-to-me:mode
```

## Examples

### Scenario 1: Deep coding session
```bash
/talk-to-me:mode coding_only
```
Now Claude only speaks when completing actual coding work, not for every question.

### Scenario 2: Learning/tutoring
```bash
/talk-to-me:mode conversational
```
Now Claude narrates all explanations, making it easier to learn while not looking at screen.

### Scenario 3: General workflow
```bash
/talk-to-me:mode auto
```
Let Claude decide - best for most use cases.

## Implementation

!bash $CLAUDE_PROJECT_DIR/hooks/mode_manager.sh ${1:-list}
