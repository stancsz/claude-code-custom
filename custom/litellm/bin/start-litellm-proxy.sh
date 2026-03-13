#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PID_FILE="$ROOT_DIR/litellm.pid"
LOG_FILE="$ROOT_DIR/litellm.log"
PORT=4001
STARTUP_TIMEOUT=20
SOURCE="${LITELLM_SOURCE:-openai}"

export ANTHROPIC_BASE_URL="http://localhost:${PORT}"

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

if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "OPENAI_API_KEY is not set. Configure custom/litellm/config/.env or export it in your shell."
  exit 1
fi

PYTHON_BIN="python3"
if [ -x "$ROOT_DIR/.venv312/bin/python3" ]; then
  PYTHON_BIN="$ROOT_DIR/.venv312/bin/python3"
elif [ -x "$ROOT_DIR/.venv/bin/python3" ]; then
  PYTHON_BIN="$ROOT_DIR/.venv/bin/python3"
fi

existing_pid=""
if command -v lsof >/dev/null 2>&1; then
  existing_pid="$(lsof -tiTCP:"$PORT" -sTCP:LISTEN -n -P 2>/dev/null | head -n 1 || true)"
fi

if [ -n "$existing_pid" ]; then
  echo "$existing_pid" > "$PID_FILE"
  echo "LiteLLM is already listening on port $PORT with PID $existing_pid"
  echo "LiteLLM source: $SOURCE"
  exit 0
fi

if [ -f "$PID_FILE" ]; then
  stale_pid="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [ -n "$stale_pid" ] && kill -0 "$stale_pid" 2>/dev/null; then
    echo "LiteLLM PID file exists and process $stale_pid is still running."
    exit 0
  fi
  rm -f "$PID_FILE"
fi

mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

START_CMD=("$PYTHON_BIN" "$ROOT_DIR/src/proxy_server.py")
if command -v setsid >/dev/null 2>&1; then
  setsid "${START_CMD[@]}" </dev/null >>"$LOG_FILE" 2>&1 &
else
  nohup "${START_CMD[@]}" </dev/null >>"$LOG_FILE" 2>&1 &
fi

LITELLM_PID=$!
echo "$LITELLM_PID" > "$PID_FILE"

for _ in $(seq 1 "$STARTUP_TIMEOUT"); do
  if command -v lsof >/dev/null 2>&1; then
    listener_pid="$(lsof -tiTCP:"$PORT" -sTCP:LISTEN -n -P 2>/dev/null | head -n 1 || true)"
    if [ -n "$listener_pid" ]; then
      echo "$listener_pid" > "$PID_FILE"
      echo "LiteLLM started on port $PORT with PID $listener_pid"
      echo "LiteLLM source: $SOURCE"
      echo "Log file: $LOG_FILE"
      if [ "$SOURCE" = "copilot" ] || [ "$SOURCE" = "github_copilot" ]; then
        echo "If this is the first Copilot run, tail the log to complete GitHub device authentication."
      fi
      exit 0
    fi
  elif kill -0 "$LITELLM_PID" 2>/dev/null; then
    echo "LiteLLM started with PID $LITELLM_PID"
    echo "Log file: $LOG_FILE"
    exit 0
  fi

  if ! kill -0 "$LITELLM_PID" 2>/dev/null; then
    break
  fi

  sleep 1
done

echo "LiteLLM failed to start on port $PORT"
if [ -s "$LOG_FILE" ]; then
  echo "Recent log output:"
  tail -n 40 "$LOG_FILE"
fi
rm -f "$PID_FILE"
exit 1
