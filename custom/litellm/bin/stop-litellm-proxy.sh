#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PID_FILE="$ROOT_DIR/litellm.pid"

if [ -f "$PID_FILE" ]; then
  kill "$(cat "$PID_FILE")"
  rm "$PID_FILE"
  echo "Stopped LiteLLM"
fi
