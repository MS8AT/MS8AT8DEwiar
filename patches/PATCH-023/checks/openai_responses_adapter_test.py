import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "core"))
from subscription_runtime.openai_responses import EventAdapter, eligible, request_body


class ResponsesAdapterTest(unittest.TestCase):
    def test_routes_only_official_openai_gpt6_tool_requests(self):
        official = {"kind": "openai", "base_url": "https://api.openai.com/v1"}
        self.assertTrue(eligible(official, "gpt-6.1-sol", [{"name": "read"}]))
        self.assertFalse(eligible(official, "gpt-6.1-sol", []))
        self.assertFalse(eligible({"kind": "openai", "base_url": "https://proxy.example/v1"}, "gpt-6.1-sol", [{"name": "read"}]))
        self.assertFalse(eligible(official, "gpt-5.6-sol", [{"name": "read"}]))

    def test_builds_responses_input_and_tool_schema(self):
        body = request_body("gpt-6.1-sol", "follow policy", [
            {"role": "user", "content": "read file"},
            {"role": "assistant", "tool_calls": [{"id": "call-1", "function": {"name": "read", "arguments": "{}"}}]},
            {"role": "tool", "tool_call_id": "call-1", "content": "done"},
        ], [{"name": "read", "description": "read only", "parameters": {"type": "object", "properties": {}}}], 512)
        self.assertEqual(body["instructions"], "follow policy")
        self.assertEqual(body["input"][0]["content"][0]["text"], "read file")
        self.assertEqual(body["input"][1]["type"], "function_call")
        self.assertEqual(body["input"][2]["type"], "function_call_output")
        self.assertEqual(body["tools"][0]["type"], "function")
        self.assertEqual(body["max_output_tokens"], 512)
        self.assertFalse(body["store"])

    def test_converts_text_and_tool_stream_events(self):
        adapter = EventAdapter()
        text = adapter.feed_line('data: {"type":"response.output_text.delta","delta":"OK"}')
        self.assertEqual(text["choices"][0]["delta"]["content"], "OK")
        added = adapter.feed_line('data: {"type":"response.output_item.added","output_index":2,"item":{"type":"function_call","call_id":"call-2","name":"read"}}')
        self.assertEqual(added["choices"][0]["delta"]["tool_calls"][0]["function"]["name"], "read")
        args = adapter.feed_line('data: {"type":"response.function_call_arguments.delta","output_index":2,"call_id":"call-2","delta":"{}"}')
        self.assertEqual(args["choices"][0]["delta"]["tool_calls"][0]["function"]["arguments"], "{}")
        completed = adapter.feed_line('data: {"type":"response.completed","response":{"output":[{"type":"function_call"}]}}')
        self.assertEqual(completed["choices"][0]["finish_reason"], "tool_calls")

    def test_ignores_non_data_lines_and_fails_on_error_event(self):
        adapter = EventAdapter()
        self.assertIsNone(adapter.feed_line("event: response.created"))
        with self.assertRaises(ValueError):
            adapter.feed_line('data: {"type":"error","error":{"message":"mock failure"}}')


if __name__ == "__main__":
    unittest.main()
