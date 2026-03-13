import os


def resolve_config_path(base_dir):
    explicit_config_path = os.getenv("LITELLM_CONFIG_PATH")
    if explicit_config_path:
        return os.path.abspath(explicit_config_path)

    config_dir = os.path.abspath(os.path.join(base_dir, "..", "config"))
    source = os.getenv("LITELLM_SOURCE", "openai").strip().lower()
    source_config_map = {
        "openai": "claude_litellm_config.yaml",
        "copilot": "claude_litellm_copilot_config.yaml",
        "github_copilot": "claude_litellm_copilot_config.yaml",
    }
    config_name = source_config_map.get(source, "claude_litellm_config.yaml")
    return os.path.join(config_dir, config_name)
