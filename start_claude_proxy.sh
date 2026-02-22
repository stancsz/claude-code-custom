#!/bin/bash
export ANTHROPIC_BASE_URL=http://localhost:4000
export ANTHROPIC_API_KEY=sk-ant-dummy
# OPENAI_API_KEY is already in env
# Start LiteLLM on port 4001
litellm --config claude_litellm_config.yaml --port 4001 --telemetry False > litellm.log 2>&1 &
LITELLM_PID=$!
echo "LiteLLM started with PID $LITELLM_PID"
echo $LITELLM_PID > litellm.pid

# Start Shim on port 4000
python3 claude_litellm_shim.py > shim.log 2>&1 &
SHIM_PID=$!
echo "Shim started with PID $SHIM_PID"
echo $SHIM_PID > shim.pid
