"""Public PATCH-008 contract. Offline; no subprocess is launched."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/core"))
from windows_task_commands import powershell_command, repair_drive_path_json

raw = r'{"tool_name":"write_file","arguments":{"path":"C:\Users\MMS\task\outputs\a.html","content":"ok"}}'
fixed = repair_drive_path_json(raw)
obj = json.loads(fixed)
assert obj["arguments"]["path"] == r"C:\Users\MMS\task\outputs\a.html"
valid = r'{"path":"C:\\Users\\MMS\\ok.txt","text":"line\nnext"}'
assert repair_drive_path_json(valid) == valid
script = powershell_command("python3 test_calc.py", r"C:\Dewiar\python.exe", r"C:\Task [abc]\work")
assert '& "C:\\Dewiar\\python.exe" test_calc.py' in script
assert "Set-Location -LiteralPath 'C:\\Task [abc]\\work'" in script
assert "python3" not in script
plain = powershell_command("git status", r"C:\Dewiar\python.exe", r"C:\Task\work")
assert plain.endswith("git status")
print("ALL OK: PATCH-008 public contract; commands_executed=0; model_calls=0")
