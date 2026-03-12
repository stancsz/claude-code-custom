# LiteLLM Proxy Troubleshooting

## Proxy fails to start

- Inspect `custom/litellm/litellm.log`
- Verify Python env has `litellm` and `uvicorn`
- Verify `custom/litellm/config/claude_litellm_config.yaml` exists

## Claude cannot connect

- Ensure proxy is up: `bash ${CLAUDE_PLUGIN_ROOT}/skills/litellm-proxy/scripts/status_proxy.sh`
- Ensure wrapper script is used: `bash custom/litellm/bin/run-claude-custom.sh`
- Confirm `ANTHROPIC_BASE_URL` points to local proxy endpoint expected by your wrapper

## Authentication errors

- Set `OPENAI_API_KEY` in environment, or provide `custom/litellm/config/.env`
- Validate that mapped model in `custom/litellm/config/claude_litellm_config.yaml` exists for your provider
