#!/bin/bash
export ANTHROPIC_BASE_URL=http://localhost:4000
# Load optional env file for keys without printing them
if [ -f "$HOME/.config/claude-code-litellm.env" ]; then
  # shellcheck disable=SC1090
  set -a
  . "$HOME/.config/claude-code-litellm.env"
  set +a
fi
# Prefer explicit OPENAI_API_KEY, otherwise fall back to openai_api_key
if [ -z "$OPENAI_API_KEY" ] && [ -n "$openai_api_key" ]; then
  OPENAI_API_KEY="$openai_api_key"
fi
export OPENAI_API_KEY
# Start LiteLLM on port 4000 directly
LITELLM_BIN="litellm"
if [ -x ".venv312/bin/litellm" ]; then
  LITELLM_BIN=".venv312/bin/litellm"
elif [ -x ".venv/bin/litellm" ]; then
  LITELLM_BIN=".venv/bin/litellm"
fi
nohup "$LITELLM_BIN" --config claude_litellm_config.yaml --port 4000 --telemetry False > litellm.log 2>&1 &
LITELLM_PID=$!
echo "LiteLLM started with PID $LITELLM_PID"
echo $LITELLM_PID > litellm.pid
