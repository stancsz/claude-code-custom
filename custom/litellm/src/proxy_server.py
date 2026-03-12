import os

import litellm
import uvicorn
from litellm.integrations.custom_logger import CustomLogger
from litellm.proxy.proxy_server import app


class FixOpenAIRequests(CustomLogger):
    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        # Clamp output token values to avoid API rejections.
        if "max_tokens" in data and isinstance(data["max_tokens"], int) and data["max_tokens"] < 16:
            data["max_tokens"] = 16

        if (
            "max_output_tokens" in data
            and isinstance(data["max_output_tokens"], int)
            and data["max_output_tokens"] < 16
        ):
            data["max_output_tokens"] = 16

        # Keep only tool messages with a matching assistant tool_call id.
        if "messages" in data:
            messages = data["messages"]
            new_messages = []
            valid_tool_call_ids = set()

            for msg in messages:
                role = msg.get("role")
                if role == "assistant":
                    if "tool_calls" in msg:
                        for tc in msg["tool_calls"]:
                            valid_tool_call_ids.add(tc["id"])
                    new_messages.append(msg)
                elif role == "tool":
                    tc_id = msg.get("tool_call_id")
                    if tc_id and tc_id in valid_tool_call_ids:
                        new_messages.append(msg)
                else:
                    new_messages.append(msg)

            data["messages"] = new_messages

        return data


litellm.callbacks = [c for c in litellm.callbacks if not isinstance(c, FixOpenAIRequests)]
litellm.callbacks.append(FixOpenAIRequests())

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(BASE_DIR, "..", "config", "claude_litellm_config.yaml")
os.environ["CONFIG_FILE_PATH"] = os.path.abspath(config_path)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4001)
