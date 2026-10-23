"""Local profile binding contract with synthetic host/task objects."""
from pathlib import Path
import sys
import threading
import types
from unittest.mock import Mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src/core"))
import local_task_mode as local
p = {"kind":"openai","base_url":"http://192.168.1.5:1234/v1","model":"synthetic"}
assert local.is_local(p)
assert local.read_limits({"context_length":8192})["local_read_chars"] == 1200
assert local.read_limits({"context_length":32768})["local_read_chars"] == 4000
assert not local.is_local({"kind":"chatgpt_subscription","base_url":"http://localhost/v1"})
assert not local.is_local({"kind":"openai","base_url":"http://192.168.1.5.evil.invalid/v1"})
host = types.SimpleNamespace(s=types.SimpleNamespace(get=lambda *keys: {"lan":p}), llm_profile=Mock())
task = types.SimpleNamespace(data={"status":"paused","subscription_binding":{"id":"old"},"subscription_attempts":5},
    control_lock=threading.RLock(), thread=None, save=Mock(), journal=Mock())
task.public=lambda: task.data
manager=types.SimpleNamespace(host=host, _emit=Mock())
local.select(manager,task,"lan")
assert task.data["previous_codex"]["subscription_attempts"] == 5
assert "subscription_binding" not in task.data
assert task.data["local_context_reset"] and task.data["local_read_only"]
assert local.task_profile(host,task)["model"] == "synthetic"
host.llm_profile.assert_not_called()
task.data["local_profile_id"]="missing"
try:
    local.task_profile(host,task)
except ValueError:
    pass
else:
    raise AssertionError("must not fall back to cloud")
print("ALL OK: PATCH-018; model_calls=0; network=0")
