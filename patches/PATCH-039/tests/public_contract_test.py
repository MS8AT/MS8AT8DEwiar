"""Synthetic MCP contract: no network, model, real catalog or Manager writes."""
from pathlib import Path
import hashlib
import json
import socket
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "core"))
import workbook_contour_mcp as mcp


class Catalog:
    def __init__(self):
        self.rows = [{"id": f"c_module_{i}", "owner": f"owner_{i}",
                      "source_present": True, "execution_allowed": False,
                      "purpose": "Synthetic module " + "x" * 200,
                      "documents": ["README.md"], "cwd": f"Source/c_module_{i}",
                      "runtime": "not_checked"} for i in range(19)]
        self.lines = ["line " + str(i) + "\n" for i in range(1, 91)]

    def list_modules(self):
        return {"count": len(self.rows), "registry_sha256": "a" * 64, "modules": self.rows}

    def get_module(self, module_id):
        row = next((r for r in self.rows if r["id"] == module_id), None)
        return {"found": bool(row), "module": row} if row else {"found": False}

    def read_document(self, module_id, document, offset, limit):
        if module_id != self.rows[0]["id"] or document != "README.md":
            raise ValueError("document not allowed")
        return {"module_id": module_id, "document": document, "offset": offset,
                "total_lines": len(self.lines), "text": "".join(self.lines[offset - 1:offset - 1 + limit])}


class Manager:
    def __init__(self):
        self.task = {"id": 11, "revision": "rev-a", "state": "running",
                     "task_control": "running", "dispatch_block": None}
        self.calls, self.writes, self.receipts = [], [], {}
        self.rows = [{"task_id": i, "state": "queued", "revision": f"r{i}",
                      "source": {"title": f"Task {i}"}} for i in range(1, 13)]

    def call(self, command, *args):
        self.calls.append((command, args))
        if command == "status":
            return {"mode": "test", "maintenance_fence": True, "tasks": [dict(self.task)]}
        if command == "view":
            after = int(args[1])
            return [dict(r) for r in self.rows if r["task_id"] > after]
        if command not in ("task-pause", "task-stop", "task-resume"):
            raise AssertionError("unexpected backend call: " + command)
        key = (command, *args)
        if key not in self.receipts:
            self.writes.append(key)
            self.receipts[key] = {"ok": True, "task_id": args[0], "request_id": args[1],
                                  "state": "stopping" if command == "task-stop" else command[5:]}
        return dict(self.receipts[key])

    def apply_control(self, args, authorize):
        authorize(args, dict(self.task))
        return self.call("task-" + args["action"], args["task_id"], args["request_id"])


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        # /tmp may itself be a symlink on the test host. Canonicalize only the
        # synthetic fixture root; production link refusal remains unchanged.
        fixture_root = Path(self.tmp.name).resolve()
        self.root = fixture_root / "Source"
        self.root.mkdir()
        self.approvals = fixture_root / "operator-approvals"
        self.approvals.mkdir()
        self.catalog, self.manager = Catalog(), Manager()
        self.host = socket.gethostname()
        self.bridge = mcp.Bridge(self.catalog, self.manager, self.host, self.root, self.approvals)
        # These synthetic approvals test bindings only. Privilege separation has
        # its own tests; the local test process never receives operator rights.
        self.permissions = patch.object(self.bridge, "_approval_permissions", return_value=None, create=True)
        self.permissions.start()
        self.clock = patch.object(mcp.time, "time", return_value=1000)
        self.clock.start()

    def tearDown(self):
        self.clock.stop()
        self.permissions.stop()
        self.tmp.cleanup()

    def request(self, **changes):
        args = {"task_id": 11, "action": "stop", "request_id": "request-1",
                "revision": "rev-a", "approval_id": "approval-1"}
        args.update(changes)
        return args

    def grant(self, args=None, **changes):
        args = self.request() if args is None else args
        data = {"approval_id": args["approval_id"], "host": self.host,
                "source_root": self.bridge.source_root, "task_id": args["task_id"],
                "action": args["action"], "request_id": args["request_id"],
                "revision": args["revision"], "approved": True, "expires_at": 1100}
        data.update(changes)
        path = self.approvals / (args["approval_id"] + ".json")
        path.write_text(json.dumps(data), encoding="utf-8")
        path.chmod(0o600)
        return path

    def call_rpc(self, name, args):
        return mcp.rpc(self.bridge, {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
                                    "params": {"name": name, "arguments": args}})["result"]

    def test_module_pagination_complete_and_bounded(self):
        offset, ids = 0, []
        while offset is not None:
            result = self.call_rpc("workbook_modules", {"offset": offset, "limit": 8})
            self.assertFalse(result["isError"])
            self.assertLess(len(result["content"][0]["text"]), mcp.MAX_RESULT)
            page = json.loads(result["content"][0]["text"])
            ids.extend(row["id"] for row in page["modules"])
            self.assertTrue(all(not row["execution_allowed"] for row in page["modules"]))
            offset = page["next_offset"]
        self.assertEqual(ids, [r["id"] for r in self.catalog.rows])
        self.assertEqual(self.manager.writes, [])

    def test_document_pages_resume_at_next_unread_line(self):
        first = self.bridge.call("workbook_document", {"module_id": "c_module_0", "document": "README.md", "limit": 40})
        self.assertEqual(first["next_offset"], 41)
        second = self.bridge.call("workbook_document", {"module_id": "c_module_0", "document": "README.md",
                                                       "offset": first["next_offset"], "limit": 40})
        third = self.bridge.call("workbook_document", {"module_id": "c_module_0", "document": "README.md",
                                                      "offset": second["next_offset"], "limit": 40})
        self.assertEqual(first["text"] + second["text"] + third["text"], "".join(self.catalog.lines))
        self.assertIsNone(third["next_offset"])
        self.catalog.lines = ["x" * 2000 + "\n"] * 10
        trimmed = self.bridge.call("workbook_document", {"module_id": "c_module_0", "document": "README.md", "limit": 40})
        self.assertEqual(trimmed["next_offset"], 3)
        self.assertEqual(len(trimmed["text"].splitlines()), 2)

    def test_oversized_document_line_returns_explicit_refusal(self):
        self.catalog.lines = ["x" * 4501 + "\n"]
        result = self.call_rpc("workbook_document", {"module_id": "c_module_0", "document": "README.md"})
        self.assertTrue(result["isError"])
        self.assertEqual(self.manager.writes, [])

    def test_read_tools_and_preview_have_zero_writes(self):
        self.bridge.call("workbook_status", {})
        self.bridge.call("workbook_module", {"module_id": "c_module_0"})
        self.bridge.call("workbook_modules", {})
        self.bridge.call("workbook_document", {"module_id": "c_module_0", "document": "README.md"})
        page = self.bridge.call("workbook_tasks", {})
        self.assertEqual(len(page["tasks"]), 8)
        self.assertEqual(page["next_after"], 8)
        page2 = self.bridge.call("workbook_tasks", {"after": page["next_after"]})
        self.assertEqual([r["task_id"] for r in page2["tasks"]], [9, 10, 11, 12])
        preview = self.bridge.call("workbook_control_preview",
                                   {"task_id": 11, "action": "pause", "request_id": "request-2"})
        self.assertFalse(preview["approved"])
        self.assertFalse(preview["control_allowed"])
        self.assertEqual(preview["writes"], 0)
        self.assertEqual(preview["revision"], "rev-a")
        self.assertEqual(self.manager.writes, [])

    def test_strict_unknown_missing_and_integer_validation(self):
        cases = [
            ("workbook_modules", {"unknown": 1}),
            ("workbook_modules", {"offset": True}),
            ("workbook_modules", {"offset": 0.0}),
            ("workbook_modules", {"limit": 0}),
            ("workbook_modules", {"limit": 9}),
            ("workbook_tasks", {"after": -1}),
            ("workbook_document", {"module_id": "c_module_0", "document": "README.md", "offset": 0}),
            ("workbook_module", {"module_id": 1}),
            ("workbook_control_preview", {"task_id": True, "action": "stop", "request_id": "r"}),
            ("workbook_control_preview", {"task_id": 11.0, "action": "stop", "request_id": "r"}),
            ("workbook_control_preview", {"task_id": 11, "action": "shell", "request_id": "r"}),
            ("workbook_control_preview", {"task_id": 11, "action": "stop", "request_id": "../x"}),
            ("workbook_control_preview", {"task_id": 11, "action": "stop"}),
        ]
        for name, args in cases:
            with self.subTest(name=name, args=args):
                self.assertTrue(self.call_rpc(name, args)["isError"])
        self.assertEqual(self.manager.writes, [])

    def test_host_mismatch_refuses_before_backend_call(self):
        self.bridge.host = self.host + "-wrong"
        self.assertTrue(self.call_rpc("workbook_status", {})["isError"])
        self.assertEqual(self.manager.calls, [])
        self.assertEqual(self.manager.writes, [])

    def test_operator_approval_missing_or_absent_file_refused(self):
        self.assertTrue(self.call_rpc("workbook_control_apply", self.request())["isError"])
        self.bridge.approval_dir = None
        self.assertTrue(self.call_rpc("workbook_control_apply", self.request())["isError"])
        self.assertEqual(self.manager.writes, [])

    def test_operator_approval_expired_long_lived_and_invalid_timestamp_refused(self):
        for expires in (999, 1000, 1901, True, "1100", None, float("inf"), float("nan")):
            with self.subTest(expires=expires):
                self.grant(expires_at=expires)
                self.assertTrue(self.call_rpc("workbook_control_apply", self.request())["isError"])
        self.assertEqual(self.manager.writes, [])

    def test_operator_approval_every_binding_is_exact(self):
        changes = [{"host": self.host + "-wrong"}, {"source_root": "elsewhere"}, {"task_id": 12},
                   {"action": "pause"}, {"request_id": "request-other"}, {"revision": "rev-old"},
                   {"approval_id": "approval-other"}, {"approved": False}, {"approved": 1}]
        for change in changes:
            with self.subTest(change=change):
                self.grant(**change)
                self.assertTrue(self.call_rpc("workbook_control_apply", self.request())["isError"])
        self.assertEqual(self.manager.writes, [])

    def test_task_revision_change_refuses_stale_approval(self):
        self.grant()
        self.manager.task["revision"] = "rev-b"
        self.assertTrue(self.call_rpc("workbook_control_apply", self.request())["isError"])
        self.assertEqual(self.manager.writes, [])

    def test_valid_stop_preserves_stopping_receipt(self):
        self.grant()
        result = self.bridge.call("workbook_control_apply", self.request())
        self.assertEqual(self.manager.writes, [("task-stop", 11, "request-1")])
        self.assertEqual(result["manager_receipt"]["state"], "stopping")
        self.assertEqual(result["dispatch"], "not_requested")
        self.assertEqual(result["model_calls"], 0)

    def test_valid_pause_uses_native_manager_command(self):
        args = self.request(action="pause")
        self.grant(args)
        result = self.bridge.call("workbook_control_apply", args)
        self.assertEqual(self.manager.writes, [("task-pause", 11, "request-1")])
        self.assertEqual(result["manager_receipt"]["state"], "pause")

    def test_blocked_resume_never_dispatches(self):
        args = self.request(action="resume")
        self.grant(args)
        self.manager.task["dispatch_block"] = "stale-binding"
        self.assertTrue(self.call_rpc("workbook_control_apply", args)["isError"])
        self.assertEqual(self.manager.writes, [])
        self.assertTrue(all(command in ("status", "view") for command, _ in self.manager.calls))

    def test_replay_request_uses_backend_idempotency_receipt(self):
        self.grant()
        first = self.bridge.call("workbook_control_apply", self.request())
        second = self.bridge.call("workbook_control_apply", self.request())
        self.assertEqual(first["manager_receipt"], second["manager_receipt"])
        self.assertEqual(len(self.manager.writes), 1)

    def test_rpc_methods_and_annotations(self):
        init = mcp.rpc(self.bridge, {"id": 1, "method": "initialize"})["result"]
        self.assertEqual(init["protocolVersion"], "2025-06-18")
        self.assertEqual(mcp.rpc(self.bridge, {"id": 2, "method": "ping"})["result"], {})
        listing = mcp.rpc(self.bridge, {"id": 3, "method": "tools/list"})["result"]["tools"]
        self.assertEqual(len(listing), 7)
        for tool in listing:
            self.assertFalse(tool["inputSchema"]["additionalProperties"])
            self.assertFalse(tool["annotations"]["openWorldHint"])
            mutates = tool["name"] == "workbook_control_apply"
            self.assertEqual(tool["annotations"]["readOnlyHint"], not mutates)
            self.assertEqual(tool["annotations"]["destructiveHint"], mutates)
        self.assertIsNone(mcp.rpc(self.bridge, {"method": "notifications/initialized"}))
        self.assertEqual(mcp.rpc(self.bridge, {"id": 4, "method": "unknown"})["error"]["code"], -32601)
        self.assertTrue(self.call_rpc("arbitrary_shell", {})["isError"])
        self.assertEqual(self.manager.writes, [])

    def test_oversized_tool_result_is_error_not_silent_truncation(self):
        self.catalog.rows[0]["purpose"] = "x" * 9000
        result = self.call_rpc("workbook_module", {"module_id": "c_module_0"})
        self.assertTrue(result["isError"])
        self.assertEqual(self.manager.writes, [])

    def test_missing_task_refused_without_write(self):
        args = self.request(task_id=99)
        self.grant(args)
        self.assertTrue(self.call_rpc("workbook_control_apply", args)["isError"])
        self.assertEqual(self.manager.writes, [])

    def test_approval_permissions_require_independent_root_owned_path(self):
        def node(uid=0, mode=0o644, parents=()):
            return SimpleNamespace(stat=lambda: SimpleNamespace(st_uid=uid, st_mode=mode), parents=parents)

        protected = node(parents=(node(mode=0o755), node(mode=0o755)))
        check = mcp.Bridge._approval_permissions
        with patch.object(mcp, "os", SimpleNamespace(name="posix", getuid=lambda: 1000)):
            check(self.bridge, protected)
            with self.assertRaises(ValueError):
                check(self.bridge, node(uid=1000))
            with self.assertRaises(ValueError):
                check(self.bridge, node(mode=0o666))
            with self.assertRaises(ValueError):
                check(self.bridge, node(parents=(node(mode=0o777),)))
        for platform, uid in (("nt", 1000), ("posix", 0)):
            with self.subTest(platform=platform, uid=uid):
                with patch.object(mcp, "os", SimpleNamespace(name=platform, getuid=lambda: uid)):
                    with self.assertRaises(ValueError):
                        check(self.bridge, protected)
        self.assertEqual(self.manager.writes, [])

    def native_fixture(self, revision="rev-a"):
        folder = self.root / "c_AI_TASK_MANAGER"
        folder.mkdir()
        cli = folder / "cli.py"
        cli.write_text("# synthetic read-only CLI\n", encoding="utf-8")
        source = '''from pathlib import Path
from contextlib import contextmanager
import json
EVENTS = Path(__file__).with_name("events.json")
def event(name):
    rows = json.loads(EVENTS.read_text()) if EVENTS.exists() else []
    EVENTS.write_text(json.dumps(rows + [name]))
class Manager:
    def __init__(self, root):
        self.locked = False
    @contextmanager
    def transaction(self):
        event("begin")
        self.locked = True
        try:
            yield self
        except BaseException:
            event("rollback")
            raise
        else:
            event("commit")
        finally:
            self.locked = False
    def work(self, task_id):
        event("work")
        return {"id": task_id, "revision": REVISION, "locked": self.locked}
    def task_control(self, task_id, action, request_id):
        assert self.locked
        event("task_control")
        return {"state": "stopping", "request_id": request_id, "locked": self.locked}
'''.replace("REVISION", repr(revision))
        core = folder / "manager.py"
        core.write_text(source, encoding="utf-8")
        native = mcp.NativeManager(self.root, hashlib.sha256(cli.read_bytes()).hexdigest(),
                                   hashlib.sha256(core.read_bytes()).hexdigest())
        return native, folder / "events.json"

    def test_native_approval_runs_under_lock_and_returns_after_commit(self):
        native, events = self.native_fixture()
        original_path = list(sys.path)
        def authorize(args, task):
            self.assertTrue(task["locked"])
            self.assertEqual(json.loads(events.read_text()), ["begin", "work"])
            self.assertEqual(task["revision"], args["revision"])
        result = native.apply_control(self.request(), authorize)
        self.assertEqual(result["state"], "stopping")
        self.assertEqual(json.loads(events.read_text()), ["begin", "work", "task_control", "commit"])
        self.assertEqual(sys.path, original_path)

    def test_revision_race_after_preview_is_refused_under_native_lock(self):
        self.grant()
        native, events = self.native_fixture("rev-b")
        self.bridge.manager = native
        # Preview/status still sees rev-a; locked work has already advanced.
        with patch.object(native, "call", return_value={"tasks": [{"id": 11, "revision": "rev-a"}]}):
            result = self.call_rpc("workbook_control_apply", self.request())
        self.assertTrue(result["isError"])
        self.assertEqual(json.loads(events.read_text()), ["begin", "work", "rollback"])

    def test_native_manager_hash_change_is_refused_before_transaction(self):
        native, events = self.native_fixture()
        native.core_path.write_text("# changed after integration\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            native.apply_control(self.request(), lambda *_: None)
        self.assertFalse(events.exists())


if __name__ == "__main__":
    unittest.main()
