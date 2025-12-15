#!/bin/sh
# Super simple test hook - log to file to verify it's called

# Log that we were called
echo "[$(date)] UserPromptSubmit hook called" >> /tmp/claude-hook-test.log
echo "Input received:" >> /tmp/claude-hook-test.log
cat >> /tmp/claude-hook-test.log
echo "---" >> /tmp/claude-hook-test.log

# Exit successfully (don't block)
exit 0
