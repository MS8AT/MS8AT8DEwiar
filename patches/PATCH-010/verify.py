"""Проверяет PATCH-010 по manifest без сети и импортов Dewiar."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
seen = set()
for item in data["files"]:
    relative = item["path"]
    if relative in seen or Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise SystemExit("REFUSED: небезопасный или повторный путь")
    seen.add(relative)
    path = ROOT / relative
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != item["sha256"]:
        raise SystemExit("REFUSED: SHA-256 не совпадает: " + relative)
print(f"PASS: PATCH-010; files={len(seen)}; network=0; model_calls=0; publish=0")
