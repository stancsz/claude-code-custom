# Custom Components Index

This directory tracks custom additions that are not part of upstream `anthropics/claude-code`.

## Component Registry

| Name | Type | Path | Purpose |
|---|---|---|---|
| LiteLLM Bridge | integration | `custom/litellm/` | Runs a local LiteLLM proxy and wrappers to route Claude Code traffic to an OpenAI-compatible endpoint. |
| Better Tools | plugin | `custom/plugins/better-tools/` | Local plugin with utility commands and local skills. |
| LiteLLM Proxy | skill | `custom/plugins/better-tools/skills/litellm-proxy/` | Operational workflow for start/check/stop of the LiteLLM proxy and Claude wrapper usage. |

## Conventions

- Put custom integrations under `custom/<integration-name>/`.
- Put custom plugins under `custom/plugins/<plugin-name>/`.
- Put plugin skills under `<plugin-root>/skills/<skill-name>/`.
