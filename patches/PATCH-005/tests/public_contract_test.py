"""Offline public checks for MS8AT-owned PATCH-005 modules; no network/model/user data."""
import hashlib
import json
from pathlib import Path
import sys
import threading
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "core"))
import human_memory_contour as memory

brain = types.ModuleType("brain_watch")
brain.STATES = {"queued", "running", "waiting", "paused", "sleeping", "stopped", "done", "failed", "blocked"}
brain.TASK_ACTIONS = {"plan", "finish", "human_memory_recall"}
brain.ACTION_STATES = {"accepted", "blocked", "done", "failed"}
brain.tag = lambda value: hashlib.sha256(str(value).encode()).hexdigest()[:16]
brain.status = lambda host: {"observed_at": 1, "journal": True, "storage_error": False, "events": []}
sys.modules["brain_watch"] = brain
import task_observability as observe


class MCP:
    def __init__(self, value): self.value = value
    def has(self, name): return name == memory.TOOL
    def call(self, name, args): return json.dumps(self.value, ensure_ascii=False)


class PublicContractTests(unittest.TestCase):
    def scope(self):
        return {"session_id": "session-1", "object_key": "person/main", "keys": ["criteria"],
                "since": "2026-10-01T00:00:00+03:00", "as_of": "2026-10-23T00:00:00+03:00"}

    def test_memory_is_task_opt_in_and_bound_to_quote(self):
        task = types.SimpleNamespace(id="task-1", data={})
        memory.configure(task, self.scope())
        self.assertTrue(task.data["human_memory_enabled"])
        request = {"task_id": task.id, "revision": task.data["human_memory_revision"],
                   **task.data["human_memory_scope"], "budget_bytes": 4500, "recent_days": 7,
                   "max_rounds": 2, "page_size": 16, "include_unknown_dates": False, "cursors": {}}
        quote = "Synthetic evidence"
        packet = {"packet": {"schema": memory.MEMORY_SCHEMA, "task_id": task.id,
                  "revision": request["revision"], "scope": memory._scope_hash(request),
                  "object": request["object_key"], "as_of": memory._utc(request["as_of"]),
                  "status": "ready", "covered": ["criteria"], "missing": [],
                  "items": [{"id": "evidence:1", "quote": quote,
                             "quote_sha256": hashlib.sha256(quote.encode()).hexdigest()}]}}
        out = memory.recall(types.SimpleNamespace(mcp=MCP(packet)), task, threading.Event())
        self.assertEqual("evidence:1", out["items"][0]["id"])
        packet["packet"]["revision"] = "foreign"
        with self.assertRaises(memory.HumanMemoryError):
            memory.recall(types.SimpleNamespace(mcp=MCP(packet)), task, threading.Event())

    def test_observability_filters_before_limit_and_hides_ids(self):
        parent = types.SimpleNamespace(id="private-parent", status="running",
                                       data={"id": "private-parent", "status": "running", "steps": 1})
        tasks = {f"noise-{i}": types.SimpleNamespace(id=f"noise-{i}", status="running",
                 data={"id": f"noise-{i}", "status": "running", "steps": 0}) for i in range(120)}
        child = types.SimpleNamespace(id="private-child", status="paused",
                                      data={"id": "private-child", "status": "paused", "steps": 0,
                                            "parent": parent.id})
        tasks.update({parent.id: parent, child.id: child})
        host = types.SimpleNamespace(tasks=types.SimpleNamespace(tasks=tasks), mcp=None)
        with patch.object(brain, "status", return_value={"observed_at": 1, "journal": True,
                          "storage_error": False, "events": []}):
            out = observe.view(host, parent)
        encoded = json.dumps(out)
        self.assertEqual(1, len(out["children"]))
        self.assertNotIn(parent.id, encoded); self.assertNotIn(child.id, encoded)
        self.assertTrue(out["read_only"])

    def test_local_profile_projection_is_hashed_and_read_only_is_strict(self):
        profile_id = "private-local-profile"
        task = types.SimpleNamespace(id="task-local", status="paused", data={
            "steps": 0, "local_profile_id": profile_id, "local_read_only": True,
        })
        host = types.SimpleNamespace(tasks=types.SimpleNamespace(tasks={task.id: task}), mcp=None)
        out = observe.view(host, task)
        self.assertEqual(out["local"], {
            "enabled": True, "profile_ref": brain.tag(profile_id), "read_only": True,
        })
        self.assertNotIn(profile_id, json.dumps(out))
        task.data["local_read_only"] = "true"
        self.assertFalse(observe.view(host, task)["local"]["read_only"])
        task.data.clear()
        self.assertEqual(observe.view(host, task)["local"], {
            "enabled": False, "profile_ref": None, "read_only": False,
        })


if __name__ == "__main__":
    unittest.main()
