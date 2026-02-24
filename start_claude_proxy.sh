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
PYTHON_BIN="python3"
if [ -x ".venv312/bin/python3" ]; then
  PYTHON_BIN=".venv312/bin/python3"
elif [ -x ".venv/bin/python3" ]; then
  PYTHON_BIN=".venv/bin/python3"
fi
nohup "$PYTHON_BIN" proxy_server.py > litellm.log 2>&1 &
LITELLM_PID=$!
echo "LiteLLM started with PID $LITELLM_PID"
echo $LITELLM_PID > litellm.pid
