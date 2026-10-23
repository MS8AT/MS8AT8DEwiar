"""Автономный контракт PATCH-015: без сети, моделей и пользовательских файлов."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "core"))
from model_purpose import choose  # noqa: E402

models = ["openai/gpt-oss-20b", "wb-node21-qwen3.5-9b", "qwen2.5-1.5b-instruct",
          "qwen3.5-9b", "qwen/qwen3.8-27b", "qwen/qwen3.6-35b-a3b", "nomic-embed"]
assert choose(models, "chat") == "qwen2.5-1.5b-instruct"
assert choose(models, "tasks") == "wb-node21-qwen3.5-9b"
assert choose(["qwen2.5-1.5b-instruct", "qwen3.5-9b"], "tasks") == "qwen3.5-9b"
assert choose(["qwen3.5-9b", "wb-node21-qwen3.5-9b"], "tasks") == "wb-node21-qwen3.5-9b"
assert "embed" not in choose(models, "tasks")
print("ALL OK: PATCH-015; chat=light; tasks=tool-family-9b; model_calls=0; network=0")
