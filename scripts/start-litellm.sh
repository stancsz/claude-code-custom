#!/bin/bash

# Check if litellm is installed
if ! command -v litellm &> /dev/null; then
    echo "LiteLLM is not installed. Please rebuild the devcontainer (which installs it via Dockerfile)."
    exit 1
fi

echo "Starting LiteLLM proxy on port 4000..."
echo "Configured to expose Anthropic-compatible endpoint at http://localhost:4000/anthropic"
echo ""
echo "Please ensure you have set the necessary API keys as environment variables."
echo "For example:"
echo "  export OPENAI_API_KEY=sk-..."
echo "  export ANTHROPIC_API_KEY=sk-ant-..."
echo ""
echo "Usage: ./scripts/start-litellm.sh [model]"
echo "Example: ./scripts/start-litellm.sh gpt-5.1-codex"
echo ""

MODEL=${1:-gpt-5.1-codex}

echo "Proxying to model: $MODEL"
echo "You can now run 'claude' in another terminal."
echo "Press Ctrl+C to stop."

# Run litellm
# We use --drop_params to avoid issues with some providers if needed, 
# but for basic usage typically not needed.
litellm --model $MODEL --port 4000 --telemetry False
