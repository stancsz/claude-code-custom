# Claude Code with LiteLLM Integration

This folder contains custom LiteLLM integration files for Claude Code.

## Layout

- `bin/`: runnable helper scripts
- `config/`: model mapping and environment templates
- `src/`: Python proxy implementation
- `docs/`: auxiliary docs
- `templates/`: template files

## Setup

1. Create a virtual environment (optional but recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r custom/litellm/requirements.txt
   ```

3. Ensure you have `claude` (Claude Code) installed.

4. Ensure `OPENAI_API_KEY` is set in your environment.
   The proxy uses the Anthropic-compatible endpoint at `http://localhost:4001`.

## Usage

1. Start the proxy:
   ```bash
   ./custom/litellm/bin/start_claude_proxy.sh
   ```

2. Run Claude Code:
   ```bash
   ./custom/litellm/bin/run_claude_with_proxy.sh [arguments]
   ```
   Example:
   ```bash
   ./custom/litellm/bin/run_claude_with_proxy.sh -p "Hello world"
   ```

3. Stop the proxy:
   ```bash
   ./custom/litellm/bin/stop_claude_proxy.sh
   ```

## Configuration

- `config/claude_litellm_config.yaml`: maps Claude models to a target OpenAI model.
- `config/.env.example`: template for environment variables.

## Tracking

- Component registry: `custom/README.md`
- Machine-readable registry: `custom/components.yaml`
