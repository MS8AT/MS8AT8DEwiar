"""Проверка SHA-256 этого блока без сети и импортов Dewiar."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
for item in data["files"]:
    path = ROOT / item["path"]
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != item["sha256"]:
        raise SystemExit("REFUSED: SHA-256 не совпадает: " + item["path"])
print("PASS: " + data["id"] + "; model_calls=0; network=0")
