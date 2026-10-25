"""Small OpenAI Responses adapter for the existing Chat Completions event contract."""
import json
from urllib.parse import urlsplit


def eligible(profile, model, tools):
    """Use Responses only for official OpenAI GPT-6 tool calls; keep every other route unchanged."""
    if not tools or profile.get("kind") != "openai":
        return False
    try:
        url = urlsplit(str(profile.get("base_url") or ""))
    except ValueError:
        return False
    return (url.scheme == "https" and url.hostname == "api.openai.com"
            and (url.path or "").rstrip("/") in ("", "/v1")
            and str(model or "").lower().startswith("gpt-6"))


def _content(value):
    if isinstance(value, str):
        return [{"type": "input_text", "text": value}]
    if not isinstance(value, list):
        return [{"type": "input_text", "text": str(value or "")}]
    out = []
    for part in value:
        if not isinstance(part, dict):
            continue
        if part.get("type") == "text":
            out.append({"type": "input_text", "text": str(part.get("text") or "")})
        elif part.get("type") == "image_url":
            image = part.get("image_url") or {}
            if isinstance(image, dict) and image.get("url"):
                out.append({"type": "input_image", "image_url": image["url"]})
    return out


def request_body(model, system, messages, tools, max_tokens):
    """Translate the app's messages and function schemas to Responses API input."""
    input_items = []
    instructions = [str(system or "")]
    for message in messages or []:
        role = message.get("role")
        if role in ("system", "developer"):
            instructions.append(str(message.get("content") or ""))
        elif role == "tool":
            input_items.append({"type": "function_call_output", "call_id": str(message.get("tool_call_id") or ""),
                                "output": str(message.get("content") or "")})
        elif role == "assistant" and message.get("tool_calls"):
            if message.get("content"):
                input_items.append({"role": "assistant", "content": _content(message["content"])})
            for call in message["tool_calls"]:
                function = call.get("function") or {}
                args = function.get("arguments") or "{}"
                input_items.append({"type": "function_call", "call_id": str(call.get("id") or ""),
                                    "name": str(function.get("name") or ""),
                                    "arguments": args if isinstance(args, str) else json.dumps(args, ensure_ascii=False)})
        elif role in ("user", "assistant"):
            input_items.append({"role": role, "content": _content(message.get("content"))})
    body = {"model": model, "instructions": "\n\n".join(x for x in instructions if x),
            "input": input_items, "stream": True, "store": False,
            "max_output_tokens": int(max_tokens)}
    if tools:
        body["tools"] = [{"type": "function", "name": str(tool.get("name") or ""),
                          "description": str(tool.get("description") or ""),
                          "parameters": tool.get("parameters") or {"type": "object", "properties": {}},
                          "strict": False} for tool in tools]
        body["tool_choice"] = "auto"
    return body


class EventAdapter:
    """Normalize Responses SSE events for the existing OpenAI stream collector."""
    def __init__(self):
        self.calls = {}

    def feed_line(self, line):
        text = line.decode("utf-8", "replace") if isinstance(line, bytes) else str(line)
        text = text.strip()
        if not text.startswith("data:"):
            return None
        payload = text[5:].strip()
        if not payload or payload == "[DONE]":
            return None
        event = json.loads(payload)
        kind = event.get("type")
        if kind == "error" or kind == "response.failed":
            error = event.get("error") or (event.get("response") or {}).get("error") or {}
            raise ValueError(str(error.get("message") if isinstance(error, dict) else error or "Responses API failed"))
        if kind == "response.output_text.delta":
            return {"choices": [{"delta": {"content": str(event.get("delta") or "")}, "finish_reason": None}]}
        if kind == "response.output_item.added":
            item = event.get("item") or {}
            if item.get("type") != "function_call":
                return None
            index = event.get("output_index", 0)
            call_id = item.get("call_id") or item.get("id") or ""
            self.calls[index] = {"id": call_id, "arguments_seen": False}
            return {"choices": [{"delta": {"tool_calls": [{"index": index, "id": call_id, "type": "function",
                        "function": {"name": item.get("name") or "", "arguments": ""}}]}, "finish_reason": None}]}
        if kind == "response.function_call_arguments.delta":
            index = event.get("output_index", 0)
            call = self.calls.setdefault(index, {"id": event.get("call_id") or "", "arguments_seen": False})
            call["arguments_seen"] = True
            return {"choices": [{"delta": {"tool_calls": [{"index": index, "id": call["id"], "type": "function",
                        "function": {"arguments": str(event.get("delta") or "")}}]}, "finish_reason": None}]}
        if kind == "response.function_call_arguments.done":
            return None
        if kind == "response.completed":
            has_calls = any((item or {}).get("type") == "function_call"
                            for item in ((event.get("response") or {}).get("output") or []))
            return {"choices": [{"delta": {}, "finish_reason": "tool_calls" if has_calls else "stop"}]}
        return None
