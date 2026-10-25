"""Run the declared standalone checks in a new temporary source tree."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
root = Path(__file__).resolve().parents[1]
plan = json.loads((root / "checks.json").read_text(encoding="utf-8"))
with tempfile.TemporaryDirectory(prefix="ms8at-block-") as temp:
    work = Path(temp)
    shutil.copytree(root / "src", work, dirs_exist_ok=True)
    shutil.copytree(root / "checks", work / "tests", dirs_exist_ok=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
    for check in plan:
        command = [sys.executable, "-B"] if check.endswith(".py") else ["node"]
        subprocess.run(command + [str(work / "tests" / check)], cwd=work, env=env, check=True, timeout=90)
print("PASS: standalone checks; real models/devices/accounts NOT_RUN")
