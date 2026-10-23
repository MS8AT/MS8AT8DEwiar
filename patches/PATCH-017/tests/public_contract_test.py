"""Synthetic budget contract, no model or network."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src/core"))
from task_budget import reserve, actions
allowed = {"project_read":["path"], "finish":["summary"], "pause":["question"]}
assert reserve() == 1
assert reserve(True, True) == 3
assert set(actions(allowed, 4, 3)) == set(allowed)
assert set(actions(allowed, 3, 3)) == {"finish", "pause"}
assert set(actions(allowed, 1, 3)) == {"finish", "pause"}
assert "project_read" in allowed
print("ALL OK: PATCH-017; model_calls=0; network=0")
