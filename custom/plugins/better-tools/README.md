# Better Tools Plugin

## Overview
This plugin adds enhanced tooling capabilities to Claude Code, specifically focusing on improved search context and safer file editing.

## Features

### 1. Smart Search (Ripgrep-anchored Context)
**Command**: `/smart-search <pattern> [path]`
**Description**: Uses `ripgrep` to search for patterns with 5 lines of context (before/after) and line numbers. This helps locate code with enough context to understand the surrounding logic and identify unique anchors for editing.
**Dependencies**: Requires `ripgrep` (`rg`) to be installed and available in your PATH.

### 2. Atomic Edit (Atomic Diff Mutations)
**Command**: `/atomic-edit <file>`
**Description**: Applies changes to a file using a strict Search/Replace block format. This ensures that edits are only applied if the "Search" block exactly matches the existing file content (providing a safety mechanism against "hallucinated" locations).
**Usage**:
The command reads from Standard Input (stdin). 
Format:
```
[New content to replace with]
```

## Setup
1. Ensure `ripgrep` is installed (`choco install ripgrep` or `winget install BurntSushi.ripgrep.MSVC`).
2. This plugin is now registered in your `.claude-plugin/marketplace.json`.
3. Restart Claude Code or run `/plugin:refresh` (if available) to pick up changes.

## LiteLLM Integration
To use this with LiteLLM:
1. Configure `.env` using `.env.example` as a template.
2. Run `custom/litellm/bin/start-litellm-cli-proxy.sh`.

## LiteLLM Skill

This plugin now includes a skill at `skills/litellm-proxy/` for running Claude Code through a local LiteLLM proxy.

Typical flow:
1. `bash ${CLAUDE_PLUGIN_ROOT}/skills/litellm-proxy/scripts/check_prereqs.sh`
2. `bash custom/litellm/bin/run-claude-custom.sh [claude args]`
3. `bash ${CLAUDE_PLUGIN_ROOT}/skills/litellm-proxy/scripts/start_proxy.sh` if you want the proxy up before running Claude or want to inspect logs
4. `bash ${CLAUDE_PLUGIN_ROOT}/skills/litellm-proxy/scripts/stop_proxy.sh`
