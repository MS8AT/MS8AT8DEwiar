"""Run from the matching full candidate; this is not a standalone test."""
import re
from pathlib import Path
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--root", type=Path, required=True)
ROOT = parser.parse_args().root.resolve()
commands = (ROOT / "core" / "engine_commands.py").read_text(encoding="utf-8")
handler = re.search(r'if cmd == "audio_file_transcribe":(.*?)(?=\n        if cmd == )', commands, re.S)
assert handler and "transcribe_wav(self, data)" in handler.group(1)
assert "self.ask(" not in handler.group(1) and "self.handle_text(" not in handler.group(1)
hud = (ROOT / "ui" / "hud.html").read_text(encoding="utf-8")
assert "Передать выбранную WAV-запись" in hud and 'core.call("audio_file_transcribe"' in hud
assert '$("askin").value = text' in hud and "нажмите «Отправить»" in hud
print("PASS: UI requests consent and leaves transcript editable; no automatic command execution")
