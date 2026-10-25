"""Verify this package without network, model, account or application imports."""
from pathlib import Path
import hashlib
import json
root = Path(__file__).resolve().parent
data = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
for item in data["files"]:
    path = root / item["path"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
        raise SystemExit("HASH MISMATCH: " + item["path"])
print("PASS: " + data["id"] + "; package hashes; model_calls=0")
