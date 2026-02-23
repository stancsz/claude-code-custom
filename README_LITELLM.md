# Claude Code with LiteLLM Integration

This directory contains scripts to run Claude Code with LiteLLM using an OpenAI API key.

## Setup

1. Ensure you have `litellm` installed:
   ```bash
   pip install 'litellm[proxy]'
   ```

2. Ensure you have `claude` (Claude Code) installed.

3. Ensure `OPENAI_API_KEY` is set in your environment.

## Usage

1. Start the proxy:
   ```bash
   ./start_claude_proxy.sh
   ```
   This starts LiteLLM on port 4000 to handle API compatibility.
   By default, it uses the `gpt-5.2-codex` model.

2. Run Claude Code:
   ```bash
   ./run_claude_with_proxy.sh [arguments]
   ```
   Example:
   ```bash
   ./run_claude_with_proxy.sh -p "Hello world"
   ```

3. Stop the proxy:
   ```bash
   ./stop_claude_proxy.sh
   ```

## Configuration

- `claude_litellm_config.yaml`: Maps Claude models to the target OpenAI model (`gpt-5.2-codex`).
