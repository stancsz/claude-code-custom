#!/bin/bash
set -euo pipefail

export ANTHROPIC_BASE_URL=http://localhost:4001
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load env from config folder first, then user-level fallback.
if [ -f "$ROOT_DIR/config/.env" ]; then
  # shellcheck disable=SC1090
  set -a
  . "$ROOT_DIR/config/.env"
  set +a
elif [ -f "$HOME/.config/claude-code-litellm.env" ]; then
  # shellcheck disable=SC1090
  set -a
  . "$HOME/.config/claude-code-litellm.env"
  set +a
fi

# Prefer explicit OPENAI_API_KEY, otherwise fall back to openai_api_key.
if [ -z "${OPENAI_API_KEY:-}" ] && [ -n "${openai_api_key:-}" ]; then
  OPENAI_API_KEY="$openai_api_key"
fi
export OPENAI_API_KEY

PYTHON_BIN="python3"
if [ -x "$ROOT_DIR/.venv312/bin/python3" ]; then
  PYTHON_BIN="$ROOT_DIR/.venv312/bin/python3"
elif [ -x "$ROOT_DIR/.venv/bin/python3" ]; then
  PYTHON_BIN="$ROOT_DIR/.venv/bin/python3"
fi

nohup "$PYTHON_BIN" "$ROOT_DIR/src/proxy_server.py" > "$ROOT_DIR/litellm.log" 2>&1 &
LITELLM_PID=$!

echo "LiteLLM started with PID $LITELLM_PID"
echo "$LITELLM_PID" > "$ROOT_DIR/litellm.pid"
