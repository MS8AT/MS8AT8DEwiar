"""Public PATCH-007 contract. Offline and independent of Dewiar."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/core"))
import language_mode as language

assert [language.normalize(x) for x in ("RU", "ENG", "CH", "zh-CN")] == ["ru", "en", "zh", "zh"]
assert [language.MODES[x]["label"] for x in ("ru", "en", "zh")] == ["RU", "ENG", "CH"]
assert language.voice_id("en", "female") == "en_US-amy-medium"
assert language.voice_id("en", "male") == "en_US-ryan-medium"
assert language.voice_id("zh", "female") == "zh_CN-huayan-medium"
assert language.voice_id("ru") == ""
assert "Respond in English" in language.prompt("en") and "简体中文" in language.prompt("zh")
source = {"piper": "ru_RU-denis-medium", "_gender": "male"}
configured = language.voice_config("zh", source)
assert configured["piper"] == "zh_CN-huayan-medium" and configured["_language_name"] == "Chinese"
assert source["piper"] == "ru_RU-denis-medium"
try:
    language.normalize("unknown", strict=True)
    raise AssertionError("unknown language accepted")
except ValueError:
    pass
print("ALL OK: PATCH-007 public contract; network=0; model_calls=0")
