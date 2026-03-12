---
name: litellm-proxy
description: This skill should be used when the user asks to "start litellm", "run claude through litellm", "route OpenAI-compatible API to Claude Code", "stop litellm proxy", "check litellm proxy status", or mentions configuring ANTHROPIC_BASE_URL for Claude Code.
version: 0.1.0
---

# LiteLLM Proxy Skill

Use this skill to run Claude Code through a local LiteLLM proxy that maps Claude requests to an OpenAI-compatible model endpoint.

## What This Skill Does

- Start a local proxy server via `custom/litellm/bin/start_claude_proxy.sh`
- Configure Claude Code invocation via `custom/litellm/bin/run_claude_with_proxy.sh`
- Stop the local proxy via `custom/litellm/bin/stop_claude_proxy.sh`
- Check proxy status via `scripts/status_proxy.sh`

## Prerequisites

- Work from repository root.
- Ensure dependencies are installed:
  - `pip install -r custom/litellm/requirements.txt`
- Ensure API key is set:
  - `OPENAI_API_KEY` environment variable, or
  - `custom/litellm/config/.env` (copy from `custom/litellm/config/.env.example`)

## Workflow

1. Validate readiness:
   - Run `bash ${CLAUDE_PLUGIN_ROOT}/skills/litellm-proxy/scripts/check_prereqs.sh`

2. Start proxy:
   - Run `bash ${CLAUDE_PLUGIN_ROOT}/skills/litellm-proxy/scripts/start_proxy.sh`

3. Verify proxy health:
   - Run `bash ${CLAUDE_PLUGIN_ROOT}/skills/litellm-proxy/scripts/status_proxy.sh`

4. Run Claude Code through proxy:
   - Run `bash custom/litellm/bin/run_claude_with_proxy.sh [claude args]`
   - Example: `bash custom/litellm/bin/run_claude_with_proxy.sh -p "hello"`

5. Stop proxy when done:
   - Run `bash ${CLAUDE_PLUGIN_ROOT}/skills/litellm-proxy/scripts/stop_proxy.sh`

## Notes

- Proxy listens on `http://localhost:4001`.
- Wrapper script sets `ANTHROPIC_BASE_URL=http://localhost:4000` for Claude compatibility.
- For troubleshooting, read `references/troubleshooting.md`.
