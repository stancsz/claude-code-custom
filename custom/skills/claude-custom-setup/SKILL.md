---
name: claude-custom-setup
description: How to setup and use the custom Claude Code environment on Windows with DeepSeek.
---

# Claude Code Custom Setup (Windows)

This skill describes how to configure and run a custom Claude Code environment that uses DeepSeek's native Anthropic-compatible API. This setup runs within a Docker DevContainer for a consistent, secure, and isolated development environment.

## Prerequisites

1.  **Docker Desktop**: Ensure Docker is installed and running.
2.  **Node.js**: Required to run the `devcontainer` CLI.
3.  **DevContainer CLI**:
    ```powershell
    npm install -g @devcontainers/cli
    ```

## Configuration

The root directory contains a `.env` file with your DeepSeek credentials:

```bash
ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
ANTHROPIC_API_KEY=your_deepseek_api_key
ANTHROPIC_MODEL=deepseek-chat
ANTHROPIC_SMALL_FAST_MODEL=deepseek-chat
API_TIMEOUT_MS=600000
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
```

## Setup Command

To make the `claude-custom` command available globally in your PowerShell:

1.  Open your PowerShell profile:
    ```powershell
    notepad $PROFILE
    ```
2.  Add the following function:
    ```powershell
    function claude-custom { & "c:\Users\stanc\claude-code-custom\custom\scripts\claude-custom.ps1" @args }
    ```
3.  (Optional) Add the `custom\scripts` folder to your User PATH to use it from Command Prompt.

## Usage

Run the following command to start the environment:

```powershell
claude-custom
```

### Options:
*   `-Rebuild`: Force a rebuild of the DevContainer (useful if you change `.devcontainer` configuration).
*   `-Backend podman`: Use Podman instead of Docker (experimental).

## How it works

1.  **Launcher (`claude-custom.ps1`)**: Switches to the project root and invokes the DevContainer script.
2.  **DevContainer Script (`run_devcontainer_claude_code.ps1`)**: 
    *   Starts the Docker container based on `.devcontainer/Dockerfile`.
    *   Seeds `~/.claude/settings.json` inside the container to bypass theme/onboarding prompts.
    *   Loads local `.env` variables into the container session.
    *   Launches `claude` (Claude Code) directly.
3.  **Direct Integration**: Uses DeepSeek's native `https://api.deepseek.com/anthropic` endpoint to provide full Claude Code functionality with DeepSeek pricing and models.
