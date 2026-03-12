# CLAUDE.md

This repository contains upstream Claude Code plus local custom components under `custom/`.

## Primary Rule

When the user asks to set up, install, or validate local custom components, install from `custom/` into this repo and report progress after each phase.

## Scope

- Repo root: `claude-code-litellm/`
- Custom integration: `custom/litellm/`
- Custom plugin: `custom/plugins/better-tools/`
- Component index: `custom/components.yaml`

## Install Workflow (Custom -> Repo)

Execute in order from repo root:

1. Validate component inventory
- Read `custom/components.yaml` and confirm expected paths exist.

2. Register local plugin
- Ensure `.claude-plugin/marketplace.json` includes plugin entry:
  - `name`: `better-tools`
  - `source`: `./custom/plugins/better-tools`
- If missing, add it.

3. Prepare LiteLLM integration
- Ensure env/config files exist:
  - `custom/litellm/config/claude_litellm_config.yaml`
  - `custom/litellm/config/.env.example`
- If `custom/litellm/config/.env` is missing, create it from `.env.example` and request user to fill secrets.

4. Install Python dependencies
- Install from `custom/litellm/requirements.txt` into active environment.

5. Validate runtime scripts
- Verify executable scripts:
  - `custom/litellm/bin/start-litellm-proxy.sh`
  - `custom/litellm/bin/run-claude-custom.sh`
  - `custom/litellm/bin/stop-litellm-proxy.sh`
- Run shell syntax checks (`bash -n`) for all scripts in `custom/litellm/bin/`.

6. Validate skill presence
- Ensure skill exists:
  - `custom/plugins/better-tools/skills/litellm-proxy/SKILL.md`
- Ensure helper scripts exist under:
  - `custom/plugins/better-tools/skills/litellm-proxy/scripts/`

7. Optional smoke test (only if user requests start/test)
- Start proxy: `custom/litellm/bin/start-litellm-proxy.sh`
- Check status using skill script.
- Stop proxy when done.

## Runtime Setup (OPENAI key + start proxy + run Claude)

Use these exact steps when the user asks to run Claude Code through the custom LiteLLM setup.

### 1) Set `OPENAI_API_KEY`

Preferred options (do not print secret values):

- Shell env (current session):
  - `export OPENAI_API_KEY='<your_key>'`
- Project env file:
  - Create `custom/litellm/config/.env` from `custom/litellm/config/.env.example`
  - Add: `OPENAI_API_KEY=<your_key>`
- User-level fallback:
  - `~/.config/claude-code-litellm.env` with `OPENAI_API_KEY=<your_key>`

### 2) Start LiteLLM (choose one mode)

- Mode A: custom Python proxy on port `4001`
  - `bash custom/litellm/bin/start-litellm-proxy.sh`
  - Runs `custom/litellm/src/proxy_server.py`

- Mode B: LiteLLM CLI proxy on port `4000` (wrapper-compatible)
  - `bash custom/litellm/bin/start-litellm-cli-proxy.sh [model]`
  - Example: `bash custom/litellm/bin/start-litellm-cli-proxy.sh gpt-5.3-codex`

### 3) Start Claude Code with proxy

- If using Mode B (port `4000`), use wrapper:
  - `bash custom/litellm/bin/run-claude-custom.sh [claude args]`

- If using Mode A (port `4001`), run Claude directly:
  - `ANTHROPIC_BASE_URL=http://localhost:4001 claude [args]`

### 4) Stop proxy

- For Mode A:
  - `bash custom/litellm/bin/stop-litellm-proxy.sh`
- For Mode B:
  - Stop the foreground `start-litellm-cli-proxy.sh` process with `Ctrl+C`

## Optional Launcher: `claude-custom`

Strongly recommend this launcher whenever the user asks to run Claude Code with LiteLLM, even if they did not explicitly ask for an alias.

Suggested wording:
- `Strongly recommended: add a claude-custom launcher so future runs are one command and auto-wire LiteLLM + OPENAI_API_KEY.`
- `I can set this up now in ~/.local/bin and PATH.`

If the user agrees, set up a PATH launcher script (preferred over shell alias-only).

### Setup steps

1. Create `~/.local/bin/claude-custom` (or `~/bin/claude-custom`) with executable permissions.
2. Ensure that directory is on `PATH` in shell profile (`~/.zshrc` or `~/.bashrc`).
3. Launcher behavior must:
   - Use `OPENAI_API_KEY` from current environment if set.
   - Otherwise load `custom/litellm/config/.env` from this repo.
   - Start LiteLLM proxy if not already listening on port `4001`.
   - Run Claude with `ANTHROPIC_BASE_URL=http://localhost:4001`.

### Launcher template

```bash
#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/absolute/path/to/claude-code-litellm"
CALLER_DIR="$PWD"

if [ -z "${OPENAI_API_KEY:-}" ] && [ -f "$REPO_ROOT/custom/litellm/config/.env" ]; then
  set -a
  . "$REPO_ROOT/custom/litellm/config/.env"
  set +a
fi

if ! lsof -iTCP:4001 -sTCP:LISTEN -n -P >/dev/null 2>&1; then
  (cd "$REPO_ROOT" && bash custom/litellm/bin/start-litellm-proxy.sh)
  sleep 5
fi

cd "$CALLER_DIR"
ANTHROPIC_BASE_URL=http://localhost:4001 claude "$@"
```

### PATH snippet example

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Required Progress/Status Reporting

Provide user-facing updates at each phase:

- `Phase 1/7: <name> - in progress`
- `Phase 1/7: <name> - done`

If blocked, report:

- `Phase X/7: <name> - blocked`
- Include exact blocker, file/path, and next action needed from user.

## Final Response Format

Always end with:

1. `Completed`: bullet list of completed phases.
2. `Changed Files`: bullet list of modified files (absolute or repo-relative paths).
3. `Pending`: remaining tasks or explicit `None`.
4. `Run Commands`: key commands executed.

## Safety

- Do not print secret values from `.env` files.
- If credentials are missing, stop at configuration phase and ask user to provide them.
- Prefer non-destructive edits; do not remove upstream files unless asked.
