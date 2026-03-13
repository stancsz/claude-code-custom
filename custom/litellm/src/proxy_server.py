import copy
import json
import os
import uuid

import litellm
import uvicorn
from litellm.integrations.custom_logger import CustomLogger
from litellm.proxy.proxy_server import app


TOOL_ARGUMENT_GUARDRAIL = (
    "Tool-use rules:\n"
    "- Before every tool call, validate the tool schema and ensure all required parameters are present and non-empty.\n"
    "- Never send an empty JSON object like {} unless the tool explicitly accepts no arguments.\n"
    "- Match the tool schema exactly.\n"
    "- If a required value is unknown, ask a brief follow-up question instead of calling the tool.\n"
    "- If a tool returns InputValidationError, do not repeat the same call shape; fix the missing fields first and retry with the simplest valid single-tool invocation.\n"
    "- For Read, Edit, and Write, always provide the absolute file path.\n"
    "- Examples: Read requires file_path; Grep requires pattern; Glob requires pattern; "
    "Agent/Task tools require their documented subject/description/prompt fields."
)


def _as_plain_dict(value):
    if isinstance(value, dict):
        return dict(value)

    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        dumped = model_dump(exclude_none=True)
        if isinstance(dumped, dict):
            return dumped

    as_dict = getattr(value, "dict", None)
    if callable(as_dict):
        dumped = as_dict(exclude_none=True)
        if isinstance(dumped, dict):
            return dumped

    return None


def _json_string(value):
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=True)
    except TypeError:
        return str(value)


def _stringify_content(value):
    if value is None:
        return ""

    if isinstance(value, str):
        return value

    if isinstance(value, list):
        text_parts = []
        for item in value:
            item_dict = _as_plain_dict(item)
            if item_dict:
                item_type = item_dict.get("type")
                if item_type == "text" and isinstance(item_dict.get("text"), str):
                    text_parts.append(item_dict["text"])
                    continue

                nested_content = item_dict.get("content")
                if isinstance(nested_content, str):
                    text_parts.append(nested_content)
                    continue

                text_parts.append(_json_string(item_dict))
                continue

            text_parts.append(str(item))

        return "\n".join(part for part in text_parts if part)

    if isinstance(value, dict):
        if isinstance(value.get("text"), str):
            return value["text"]
        if isinstance(value.get("content"), str):
            return value["content"]

    return _json_string(value)


def _normalize_tool_call(tool_call):
    normalized_tool_call = _as_plain_dict(tool_call)
    if not normalized_tool_call:
        return None

    function_def = _as_plain_dict(normalized_tool_call.get("function")) or {}
    name = normalized_tool_call.get("name") or function_def.get("name")

    if not isinstance(name, str) or not name:
        return None

    arguments = normalized_tool_call.get("arguments")
    if arguments is None:
        arguments = function_def.get("arguments")
    if arguments is None:
        arguments = normalized_tool_call.get("input", {})

    normalized_function = {
        "name": name,
        "arguments": _json_string(arguments),
    }

    return {
        "id": normalized_tool_call.get("id") or f"call_{uuid.uuid4().hex}",
        "type": "function",
        "function": normalized_function,
    }


def _normalize_function_tool(tool):
    normalized_tool = _as_plain_dict(tool)
    if not normalized_tool:
        return None

    function_def = _as_plain_dict(normalized_tool.get("function"))
    input_schema = normalized_tool.get("input_schema")
    name = normalized_tool.get("name")
    description = normalized_tool.get("description")
    strict = normalized_tool.get("strict")

    if function_def:
        for field in ("name", "description", "parameters", "strict"):
            if field not in normalized_tool and function_def.get(field) is not None:
                normalized_tool[field] = function_def[field]

    name = normalized_tool.get("name", name)
    description = normalized_tool.get("description", description)
    strict = normalized_tool.get("strict", strict)

    # Anthropic-style tools use input_schema; downstream OpenAI-compatible calls need parameters.
    if "parameters" not in normalized_tool and isinstance(input_schema, dict):
        normalized_tool["parameters"] = input_schema

    should_be_function = (
        normalized_tool.get("type") == "function"
        or bool(function_def)
        or (
            isinstance(normalized_tool.get("name"), str)
            and isinstance(normalized_tool.get("parameters"), dict)
        )
    )

    if should_be_function:
        parameters = normalized_tool.get("parameters")
        if not isinstance(parameters, dict):
            parameters = {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            }
        normalized_function = {
            "name": name,
            "parameters": parameters,
        }
        if isinstance(description, str) and description:
            normalized_function["description"] = description
        if strict is not None:
            normalized_function["strict"] = strict

        normalized_tool = {
            "type": "function",
            "function": normalized_function,
        }

    normalized_function = _as_plain_dict(normalized_tool.get("function"))
    if normalized_function and isinstance(normalized_function.get("name"), str):
        return normalized_tool

    return None


def _normalize_tool_choice(tool_choice):
    normalized_choice = _as_plain_dict(tool_choice)
    if not normalized_choice:
        return tool_choice

    choice_type = normalized_choice.get("type")
    name = normalized_choice.get("name")

    if choice_type == "tool" and isinstance(name, str):
        return {"type": "function", "function": {"name": name}}

    if choice_type == "auto":
        return "auto"

    if choice_type == "any":
        return "required"

    function_def = _as_plain_dict(normalized_choice.get("function"))
    if choice_type == "function" and function_def:
        normalized_choice.pop("function", None)
        if not isinstance(name, str) and isinstance(function_def.get("name"), str):
            name = function_def["name"]

    if choice_type == "function" and isinstance(name, str):
        return {"type": "function", "function": {"name": name}}

    return normalized_choice


def _normalize_messages(messages):
    if not isinstance(messages, list):
        return messages

    normalized_messages = []

    for message in messages:
        message_dict = _as_plain_dict(message)
        if not message_dict:
            normalized_messages.append(message)
            continue

        role = message_dict.get("role")
        content = message_dict.get("content")

        if isinstance(message_dict.get("tool_calls"), list):
            normalized_tool_calls = []
            for tool_call in message_dict["tool_calls"]:
                normalized_tool_call = _normalize_tool_call(tool_call)
                if normalized_tool_call:
                    normalized_tool_calls.append(normalized_tool_call)
            message_dict["tool_calls"] = normalized_tool_calls

        if not isinstance(content, list):
            if not isinstance(content, str):
                message_dict["content"] = _stringify_content(content)
            normalized_messages.append(message_dict)
            continue

        if role == "assistant":
            text_parts = []
            tool_calls = list(message_dict.get("tool_calls") or [])

            for block in content:
                block_dict = _as_plain_dict(block)
                if not block_dict:
                    text_parts.append(str(block))
                    continue

                block_type = block_dict.get("type")
                if block_type == "text":
                    text = block_dict.get("text")
                    if isinstance(text, str) and text:
                        text_parts.append(text)
                    continue

                if block_type == "tool_use":
                    normalized_tool_call = _normalize_tool_call(block_dict)
                    if normalized_tool_call:
                        tool_calls.append(normalized_tool_call)
                    continue

                fallback_text = _stringify_content(block_dict)
                if fallback_text:
                    text_parts.append(fallback_text)

            message_dict["content"] = "\n".join(text_parts) if text_parts else None
            if tool_calls:
                message_dict["tool_calls"] = tool_calls
            normalized_messages.append(message_dict)
            continue

        if role == "user":
            pending_text_parts = []

            def flush_user_text():
                if not pending_text_parts:
                    return
                normalized_messages.append(
                    {
                        "role": "user",
                        "content": "\n".join(part for part in pending_text_parts if part),
                    }
                )
                pending_text_parts.clear()

            for block in content:
                block_dict = _as_plain_dict(block)
                if not block_dict:
                    pending_text_parts.append(str(block))
                    continue

                block_type = block_dict.get("type")
                if block_type == "text":
                    text = block_dict.get("text")
                    if isinstance(text, str) and text:
                        pending_text_parts.append(text)
                    continue

                if block_type == "tool_result":
                    flush_user_text()
                    normalized_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": block_dict.get("tool_use_id")
                            or block_dict.get("id")
                            or f"call_{uuid.uuid4().hex}",
                            "content": _stringify_content(block_dict.get("content")),
                        }
                    )
                    continue

                fallback_text = _stringify_content(block_dict)
                if fallback_text:
                    pending_text_parts.append(fallback_text)

            flush_user_text()
            continue

        message_dict["content"] = _stringify_content(content)
        normalized_messages.append(message_dict)

    return normalized_messages


def _looks_like_anthropic_request(data):
    tools = data.get("tools")
    if isinstance(tools, list):
        for tool in tools:
            tool_dict = _as_plain_dict(tool)
            if not tool_dict:
                continue
            if "input_schema" in tool_dict and "function" not in tool_dict:
                return True

    messages = data.get("messages")
    if isinstance(messages, list):
        for message in messages:
            message_dict = _as_plain_dict(message)
            if not message_dict:
                continue

            content = message_dict.get("content")
            if not isinstance(content, list):
                continue

            for block in content:
                block_dict = _as_plain_dict(block)
                if not block_dict:
                    continue
                if block_dict.get("type") in {"text", "tool_use", "tool_result", "image"}:
                    return True

    return False


def _inject_tool_argument_guardrail(messages):
    if not isinstance(messages, list):
        return messages

    guardrail_message = {"role": "system", "content": TOOL_ARGUMENT_GUARDRAIL}
    new_messages = list(messages)

    for index, message in enumerate(new_messages):
        message_dict = _as_plain_dict(message)
        if not message_dict or message_dict.get("role") != "system":
            continue

        content = message_dict.get("content")
        if isinstance(content, str):
            if TOOL_ARGUMENT_GUARDRAIL in content:
                return new_messages
            updated_message = dict(message_dict)
            updated_message["content"] = f"{content.rstrip()}\n\n{TOOL_ARGUMENT_GUARDRAIL}"
            new_messages[index] = updated_message
            return new_messages

    new_messages.insert(0, guardrail_message)
    return new_messages


class FixOpenAIRequests(CustomLogger):
    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        data = copy.deepcopy(data)
        is_anthropic_request = _looks_like_anthropic_request(data)

        # Clamp output token values to avoid API rejections.
        if "max_tokens" in data and isinstance(data["max_tokens"], int) and data["max_tokens"] < 16:
            data["max_tokens"] = 16

        if (
            "max_output_tokens" in data
            and isinstance(data["max_output_tokens"], int)
            and data["max_output_tokens"] < 16
        ):
            data["max_output_tokens"] = 16

        # OpenAI responses API rejects long user identifiers.
        if "user" in data and isinstance(data["user"], str) and len(data["user"]) > 64:
            data["user"] = data["user"][:64]

        if is_anthropic_request:
            return data

        if "messages" in data:
            data["messages"] = _normalize_messages(data["messages"])

        # Normalize Anthropic-style tools and messages into OpenAI chat-compatible payloads.
        if "tools" in data and isinstance(data["tools"], list):
            normalized_tools = []

            for tool in data["tools"]:
                normalized_tool = _normalize_function_tool(tool)
                if normalized_tool:
                    normalized_tools.append(normalized_tool)

            data["tools"] = normalized_tools

        if "system" in data:
            data["system"] = _stringify_content(data["system"])

        if "instructions" in data:
            data["instructions"] = _stringify_content(data["instructions"])

        if "tool_choice" in data:
            data["tool_choice"] = _normalize_tool_choice(data["tool_choice"])

        if data.get("tools"):
            data["messages"] = _inject_tool_argument_guardrail(data.get("messages"))

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
