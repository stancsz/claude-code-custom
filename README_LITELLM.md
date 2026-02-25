# Claude Code with LiteLLM Integration

This directory contains scripts to run Claude Code with LiteLLM using an OpenAI API key.

## Setup

1. Create a virtual environment (optional but recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure you have `claude` (Claude Code) installed.

4. Ensure `OPENAI_API_KEY` is set in your environment.
   The proxy uses the Anthropic-compatible endpoint at `http://localhost:4000`.

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
