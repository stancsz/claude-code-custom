#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "${CLAUDE_PLUGIN_ROOT}/../../.." && pwd)"
PID_FILE="$REPO_ROOT/custom/litellm/litellm.pid"
LOG_FILE="$REPO_ROOT/custom/litellm/litellm.log"

if [ ! -f "$PID_FILE" ]; then
  echo "Proxy not running (missing PID file: $PID_FILE)"
  exit 1
fi

PID="$(cat "$PID_FILE")"
if ! ps -p "$PID" > /dev/null 2>&1; then
  echo "Proxy not running (stale PID: $PID)"
  exit 1
fi

echo "Proxy process running with PID: $PID"
if curl -fsS "http://localhost:4001/health" > /dev/null 2>&1; then
  echo "Health check OK: http://localhost:4001/health"
else
  echo "Health check failed for http://localhost:4001/health"
  echo "Recent logs:"
  if [ -f "$LOG_FILE" ]; then
    tail -n 20 "$LOG_FILE"
  else
    echo "No log file found at $LOG_FILE"
  fi
  exit 1
fi
