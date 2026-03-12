#!/bin/bash
export ANTHROPIC_BASE_URL=http://localhost:4001
# Load optional env file for keys without printing them
if [ -f "$HOME/.config/claude-code-litellm.env" ]; then
  # shellcheck disable=SC1090
  set -a
  . "$HOME/.config/claude-code-litellm.env"
  set +a
fi
# Avoid CLI auth conflict; proxy handles auth via OPENAI_API_KEY
unset ANTHROPIC_API_KEY
# Prefer explicit OPENAI_API_KEY, otherwise fall back to openai_api_key
if [ -z "$OPENAI_API_KEY" ] && [ -n "$openai_api_key" ]; then
  export OPENAI_API_KEY="$openai_api_key"
fi

# Default to fully non-interactive permissions unless caller explicitly sets one.
HAS_PERMISSION_FLAG=false
for arg in "$@"; do
  case "$arg" in
    --dangerously-skip-permissions|--permission-mode|--permission-mode=*)
      HAS_PERMISSION_FLAG=true
      break
      ;;
  esac
done

if [ "$HAS_PERMISSION_FLAG" = true ]; then
  claude "$@"
else
  claude --dangerously-skip-permissions "$@"
fi
