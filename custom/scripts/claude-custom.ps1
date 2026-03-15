<#
.SYNOPSIS
    Launcher for Claude Code with LiteLLM proxy (DeepSeek) support.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('docker','podman')]
    [string]$Backend = 'docker',
    
    [Parameter(Mandatory=$false)]
    [switch]$Rebuild
)

$ScriptFolder = Split-Path -Parent $MyInvocation.MyCommand.Definition
$customDir = Split-Path -Parent $ScriptFolder
$ProjectRoot = Split-Path -Parent $customDir

# Check if .env exists in project root
$envFile = Join-Path $ProjectRoot ".env"
if (Test-Path $envFile) {
    Write-Host "Loading environment from $envFile"
    # Note: We don't necessarily need to load it into the host PS session
    # because the container will load it from /workspace/.env
} else {
    Write-Warning "No .env file found at $ProjectRoot. DeepSeek configuration might be missing."
}

# Run the devcontainer script with a modified command to use the wrapper
Write-Host "Starting DevContainer via run_devcontainer_claude_code.ps1..."

# We need to temporarily modify the command executed in the container
# or create a version of the script that accepts a command.
# Switch to project root to ensure devcontainer finds the config
Write-Host "Switching to project root: $ProjectRoot"
Set-Location $ProjectRoot

$params = @{ Backend = $Backend }
if ($Rebuild) { $params["Rebuild"] = $true }

& "$ScriptFolder\run_devcontainer_claude_code.ps1" @params
