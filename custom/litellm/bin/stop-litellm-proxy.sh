#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PID_FILE="$ROOT_DIR/litellm.pid"
PORT=4001
stopped=false

if [ -f "$PID_FILE" ]; then
  pid="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    kill "$pid"
    stopped=true
  fi
  rm "$PID_FILE"
fi

if command -v lsof >/dev/null 2>&1; then
  listener_pid="$(lsof -tiTCP:"$PORT" -sTCP:LISTEN -n -P 2>/dev/null | head -n 1 || true)"
  if [ -n "$listener_pid" ]; then
    kill "$listener_pid"
    stopped=true
  fi
fi

if [ "$stopped" = true ]; then
  echo "Stopped LiteLLM"
else
  echo "LiteLLM is not running"
fi
