#!/usr/bin/env bash
#
# Mode Manager for Talk-to-Me
# Handles narration mode selection: coding_only, conversational, auto
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env"
MODE_FILE="$PROJECT_ROOT/.claude/narration-mode.txt"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Parse command
COMMAND="${1:-get}"

# Ensure .claude directory exists
mkdir -p "$(dirname "$MODE_FILE")"

get_mode() {
    if [ -f "$MODE_FILE" ]; then
        cat "$MODE_FILE"
    else
        echo "auto"
    fi
}

set_mode() {
    local mode="$1"

    case "$mode" in
        coding_only|conversational|auto)
            echo "$mode" > "$MODE_FILE"
            echo -e "${GREEN}✓${NC} Narration mode set to: ${CYAN}$mode${NC}"

            # Show mode description
            case "$mode" in
                coding_only)
                    echo "  → Narrate only when doing coding tasks (file edits, bug fixes, etc.)"
                    ;;
                conversational)
                    echo "  → Narrate all responses, including Q&A and explanations"
                    ;;
                auto)
                    echo "  → Let Claude decide based on context (default)"
                    ;;
            esac
            ;;
        *)
            echo -e "${YELLOW}✗${NC} Invalid mode: $mode"
            echo "  Valid modes: coding_only, conversational, auto"
            exit 1
            ;;
    esac
}

show_help() {
    echo "Usage: mode_manager.sh [get|set MODE|list]"
    echo ""
    echo "Modes:"
    echo "  coding_only     - Narrate only file edits, bug fixes, refactoring"
    echo "  conversational  - Narrate all responses (Q&A, explanations, etc.)"
    echo "  auto            - Claude decides based on context (default)"
    echo ""
    echo "Examples:"
    echo "  mode_manager.sh get"
    echo "  mode_manager.sh set coding_only"
    echo "  mode_manager.sh list"
}

list_modes() {
    local current=$(get_mode)

    echo "Available narration modes:"
    echo ""

    if [ "$current" = "coding_only" ]; then
        echo -e "  ${GREEN}●${NC} coding_only     - Narrate only coding tasks"
    else
        echo -e "    coding_only     - Narrate only coding tasks"
    fi

    if [ "$current" = "conversational" ]; then
        echo -e "  ${GREEN}●${NC} conversational  - Narrate all responses"
    else
        echo -e "    conversational  - Narrate all responses"
    fi

    if [ "$current" = "auto" ]; then
        echo -e "  ${GREEN}●${NC} auto            - Claude decides (default)"
    else
        echo -e "    auto            - Claude decides (default)"
    fi
}

# Main command router
case "$COMMAND" in
    get)
        get_mode
        ;;
    set)
        if [ -z "$2" ]; then
            echo "Error: MODE required"
            show_help
            exit 1
        fi
        set_mode "$2"
        ;;
    list)
        list_modes
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac
