from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core"))
from task_scheduler import Candidate, choose_next, CONTROLLED_CONTEXT
c = (Candidate("short", 1), Candidate("long", 10))
assert choose_next(c, ["short", "long"]).task_id == "short"
assert choose_next(c, ["short", "long"], "c_good").fallback
assert choose_next(c, ["short", "long"], "c_good", CONTROLLED_CONTEXT).task_id == "long"
assert choose_next(c, ["short"], "c_good", CONTROLLED_CONTEXT).task_id == "short"
assert choose_next(c, ["unknown"]).task_id is None
assert choose_next(c, ["long"], "other").reason_code == "unknown_strategy_fallback"
cycle = (Candidate("a", 1, dependencies=("b",)), Candidate("b", 2, dependencies=("a",)))
assert choose_next(cycle, ["a"], "c_good", CONTROLLED_CONTEXT).fallback
print("PASS: 7 scheduler contracts; no Manager dispatch")
