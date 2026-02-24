#!/bin/bash
export ANTHROPIC_BASE_URL=http://localhost:4000
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
claude "$@"
