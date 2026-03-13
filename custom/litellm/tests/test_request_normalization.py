import os
import sys
import unittest


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(TESTS_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from request_normalization import (  # noqa: E402
    TOOL_ARGUMENT_GUARDRAIL,
    inject_tool_argument_guardrail,
    looks_like_anthropic_request,
    normalize_function_tool,
    normalize_messages,
    normalize_tool_choice,
    stringify_content,
)


class RequestNormalizationTests(unittest.TestCase):
    def test_normalize_function_tool_from_input_schema(self):
        tool = {
            "name": "Read",
            "description": "Read a file",
            "input_schema": {
                "type": "object",
                "properties": {"file_path": {"type": "string"}},
                "required": ["file_path"],
            },
        }

        normalized = normalize_function_tool(tool)

        self.assertEqual(normalized["type"], "function")
        self.assertEqual(normalized["function"]["name"], "Read")
        self.assertEqual(normalized["function"]["description"], "Read a file")
        self.assertEqual(normalized["function"]["parameters"]["required"], ["file_path"])

    def test_normalize_tool_choice_from_anthropic_shape(self):
        choice = {"type": "tool", "name": "Read"}
        self.assertEqual(
            normalize_tool_choice(choice),
            {"type": "function", "function": {"name": "Read"}},
        )

    def test_normalize_messages_converts_tool_loop(self):
        messages = [
            {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "Inspecting."},
                    {
                        "type": "tool_use",
                        "id": "toolu_1",
                        "name": "Read",
                        "input": {"file_path": "/tmp/demo.txt"},
                    },
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "toolu_1",
                        "content": [{"type": "text", "text": "file contents"}],
                    },
                    {"type": "text", "text": "Continue."},
                ],
            },
        ]

        normalized = normalize_messages(messages)

        self.assertEqual(normalized[0]["role"], "assistant")
        self.assertEqual(normalized[0]["content"], "Inspecting.")
        self.assertEqual(normalized[0]["tool_calls"][0]["function"]["name"], "Read")
        self.assertEqual(normalized[1]["role"], "tool")
        self.assertEqual(normalized[1]["tool_call_id"], "toolu_1")
        self.assertEqual(normalized[1]["content"], "file contents")
        self.assertEqual(normalized[2], {"role": "user", "content": "Continue."})

    def test_stringify_content_handles_dict_and_list(self):
        self.assertEqual(stringify_content({"type": "text", "text": "hello"}), "hello")
        self.assertEqual(
            stringify_content(
                [{"type": "text", "text": "one"}, {"type": "text", "text": "two"}]
            ),
            "one\ntwo",
        )

    def test_detects_anthropic_request(self):
        data = {
            "tools": [{"name": "Read", "input_schema": {"type": "object"}}],
            "messages": [{"role": "user", "content": [{"type": "text", "text": "hi"}]}],
        }
        self.assertTrue(looks_like_anthropic_request(data))

    def test_guardrail_is_injected_once(self):
        messages = [{"role": "user", "content": "hello"}]

        guarded = inject_tool_argument_guardrail(messages)
        guarded_again = inject_tool_argument_guardrail(guarded)

        self.assertEqual(guarded[0]["role"], "system")
        self.assertIn(TOOL_ARGUMENT_GUARDRAIL, guarded[0]["content"])
        self.assertEqual(guarded, guarded_again)


if __name__ == "__main__":
    unittest.main()
