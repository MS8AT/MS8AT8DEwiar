"""Protected roots contract: synthetic files, no network or models."""
from pathlib import Path
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src/core"))
from project_scope import protected, walk

assert all(protected(name) for name in ("Pass/a", "PRIVATE/a", "Runtime/x", "pass\\a"))
assert not protected("Source/runtime.py")
with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    for rel in ("Pass/key.txt", "Private/a.txt", "Runtime/a.txt", "Source/main.py"):
        file = root / rel
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text("synthetic", encoding="utf-8")
    assert [str(x) for x in walk(root)] == ["Source/main.py"]
    assert len(walk(root, limit=1)) == 1
print("ALL OK: PATCH-016; model_calls=0; network=0")
