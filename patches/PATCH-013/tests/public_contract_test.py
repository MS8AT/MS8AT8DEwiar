"""Автономный контракт PATCH-013: без сети и моделей."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "core"))
import task_doctor

def spec(name):
    return {"name": name, "description": "длинное описание " * 30,
            "parameters": {"type": "object", "properties": {"path": {"type": "string"}}}}


source = [spec(n) for n in ("finish", "code_read", "code_run", "web_search", "write_file", "power")]
compact = task_doctor.compact_specs(source, project=True)
assert {item["name"] for item in compact} == {"finish", "code_read", "code_run", "web_search"}
assert all(len(item["description"]) <= 220 for item in compact)
assert compact[0]["parameters"] == source[0]["parameters"]

prompt = task_doctor.compact_system(persona="Агент", title="Изучи", goal="G" * 5000,
                                    notebook="N" * 5000, plan="START\n" + "P" * 5000 + "\nEND",
                                    project=r"Z:\Source", task_dir=r"C:\Task", now="23.10.2026 20:00")
assert len(prompt) < 5000 and "START" in prompt and "END" in prompt
assert "сокращена AI-доктором" in prompt

safe = task_doctor.report("private prompt", [spec("finish")], "short", [spec("finish")])
assert safe["mode"] == "context_compact" and "private prompt" not in str(safe)
print("ALL OK: PATCH-013; model_calls=0; network=0")
