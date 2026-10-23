"""Проверить публичный PATCH-004 по manifest.json; без сети и исходников Dewiar."""
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
if manifest.get("schema") != 1 or manifest.get("id") != "PATCH-004":
    raise SystemExit("REFUSED: invalid manifest")
for item in manifest.get("files", []):
    relative = Path(item.get("path", ""))
    if relative.is_absolute() or ".." in relative.parts:
        raise SystemExit("REFUSED: unsafe path")
    path = ROOT / relative
    actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    if actual != item.get("sha256"):
        raise SystemExit("REFUSED: SHA-256 mismatch: " + relative.as_posix())
print(f"PASS: {len(manifest['files'])} PATCH-004 files; network=0; model_calls=0")
