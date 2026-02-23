#!/bin/bash
export ANTHROPIC_BASE_URL=http://localhost:4000
export ANTHROPIC_API_KEY=sk-ant-dummy
# OPENAI_API_KEY is already in env
# Start LiteLLM on port 4000 directly
litellm --config claude_litellm_config.yaml --port 4000 --telemetry False > litellm.log 2>&1 &
LITELLM_PID=$!
echo "LiteLLM started with PID $LITELLM_PID"
echo $LITELLM_PID > litellm.pid
