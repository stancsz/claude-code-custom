#!/bin/bash
export ANTHROPIC_BASE_URL=http://localhost:4001
export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1
export CLAUDE_CODE_ATTRIBUTION_HEADER=false
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
export CLAUDE_CODE_DISABLE_CRON=1
export DISABLE_TELEMETRY=1
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

# Forward all original args to claude, only normalizing the legacy permission alias.
HAS_PERMISSION_FLAG=false
CLAUDE_ARGS=()
for arg in "$@"; do
  case "$arg" in
    --allow-dangerously-skip-permissions)
      HAS_PERMISSION_FLAG=true
      CLAUDE_ARGS+=(--dangerously-skip-permissions)
      ;;
    --dangerously-skip-permissions|--permission-mode|--permission-mode=*)
      HAS_PERMISSION_FLAG=true
      CLAUDE_ARGS+=("$arg")
      ;;
    *)
      CLAUDE_ARGS+=("$arg")
      ;;
  esac
done

if [ "$HAS_PERMISSION_FLAG" = false ]; then
  if [ ${#CLAUDE_ARGS[@]} -gt 0 ]; then
    CLAUDE_ARGS=(--dangerously-skip-permissions "${CLAUDE_ARGS[@]}")
  else
    CLAUDE_ARGS=(--dangerously-skip-permissions)
  fi
fi

exec claude "${CLAUDE_ARGS[@]}"
