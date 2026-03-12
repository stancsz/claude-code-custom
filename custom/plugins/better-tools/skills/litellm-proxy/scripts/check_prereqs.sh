#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "${CLAUDE_PLUGIN_ROOT}/../../.." && pwd)"
cd "$REPO_ROOT"

if [ ! -f custom/litellm/requirements.txt ]; then
  echo "Missing custom/litellm/requirements.txt"
  exit 1
fi

if [ ! -f custom/litellm/bin/start_claude_proxy.sh ]; then
  echo "Missing custom/litellm/bin/start_claude_proxy.sh"
  exit 1
fi

if [ ! -f custom/litellm/config/claude_litellm_config.yaml ]; then
  echo "Missing custom/litellm/config/claude_litellm_config.yaml"
  exit 1
fi

if [ -z "${OPENAI_API_KEY:-}" ] && [ ! -f custom/litellm/config/.env ]; then
  echo "OPENAI_API_KEY is not set and custom/litellm/config/.env is missing"
  echo "Create custom/litellm/config/.env from custom/litellm/config/.env.example"
  exit 1
fi

echo "Prereqs look good"
