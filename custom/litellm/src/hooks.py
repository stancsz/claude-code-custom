import copy

from litellm.integrations.custom_logger import CustomLogger

from request_normalization import (
    inject_tool_argument_guardrail,
    looks_like_anthropic_request,
    normalize_function_tool,
    normalize_messages,
    normalize_tool_choice,
    stringify_content,
)


class FixOpenAIRequests(CustomLogger):
    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        data = copy.deepcopy(data)
        is_anthropic_request = looks_like_anthropic_request(data)

        if "max_tokens" in data and isinstance(data["max_tokens"], int) and data["max_tokens"] < 16:
            data["max_tokens"] = 16

        if (
            "max_output_tokens" in data
            and isinstance(data["max_output_tokens"], int)
            and data["max_output_tokens"] < 16
        ):
            data["max_output_tokens"] = 16

        if "user" in data and isinstance(data["user"], str) and len(data["user"]) > 64:
            data["user"] = data["user"][:64]

        if is_anthropic_request:
            return data

        if "messages" in data:
            data["messages"] = normalize_messages(data["messages"])

        if "tools" in data and isinstance(data["tools"], list):
            normalized_tools = []

            for tool in data["tools"]:
                normalized_tool = normalize_function_tool(tool)
                if normalized_tool:
                    normalized_tools.append(normalized_tool)

            data["tools"] = normalized_tools

        if "system" in data:
            data["system"] = stringify_content(data["system"])

        if "instructions" in data:
            data["instructions"] = stringify_content(data["instructions"])

        if "tool_choice" in data:
            data["tool_choice"] = normalize_tool_choice(data["tool_choice"])

        if data.get("tools"):
            data["messages"] = inject_tool_argument_guardrail(data.get("messages"))

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
