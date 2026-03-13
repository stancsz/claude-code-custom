# LiteLLM Proxy Troubleshooting

## Proxy fails to start

- Inspect `custom/litellm/litellm.log`
- Verify Python env has `litellm` and `uvicorn`
- Verify `custom/litellm/config/claude_litellm_config.yaml` exists
- Delete a stale PID file if `custom/litellm/litellm.pid` exists but no process is listening on port `4001`

## Claude cannot connect

- Ensure proxy is up: `bash ${CLAUDE_PLUGIN_ROOT}/skills/litellm-proxy/scripts/status_proxy.sh`
- Ensure wrapper script is used: `bash custom/litellm/bin/run-claude-custom.sh`
- The wrapper now auto-starts the proxy if port `4001` is not already listening
- Confirm `ANTHROPIC_BASE_URL` points to local proxy endpoint expected by your wrapper

## Authentication errors

- Set `OPENAI_API_KEY` in environment, or provide `custom/litellm/config/.env`
- Validate that mapped model in `custom/litellm/config/claude_litellm_config.yaml` exists for your provider
- For GitHub Copilot, check `custom/litellm/litellm.log` for the GitHub device-login code and confirm the token cache under `~/.config/litellm/github_copilot/`
