#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "${CLAUDE_PLUGIN_ROOT}/../../.." && pwd)"
cd "$REPO_ROOT"

bash custom/litellm/bin/stop-litellm-proxy.sh
