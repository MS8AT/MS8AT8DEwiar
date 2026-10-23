"""Verify PATCH-011 file hashes offline. No network and no Dewiar imports."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
seen = set()
for item in manifest["files"]:
    name = item["path"]
    if (not re.fullmatch(r"[A-Za-z0-9_.\-/]+", name) or name.startswith("/") or ".." in name.split("/")
            or name.lower() in seen):
        raise SystemExit("REFUSED: invalid or duplicate path")
    seen.add(name.lower())
    path = ROOT / name
    digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    if digest != item["sha256"]:
        raise SystemExit(f"FAIL: {name}")
print(f"PASS: PATCH-011; files={len(seen)}; network=0; model_calls=0")
