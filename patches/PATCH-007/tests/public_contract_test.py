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
assert language.public("ENG", False, "male") == {
    "code": "en", "label": "ENG", "name": "English", "voice_id": "en_US-ryan-medium", "voice_ready": False,
}
assert language.public("RU") == {"code": "ru", "label": "RU", "name": "Русский", "voice_id": ""}
assert language.public("CH", True)["voice_ready"] is True
assert language.status_text("en", True) == "Response language: English."
assert language.status_text("en", False) == "English selected. Preparing the local voice; text is ready now."
assert language.status_text("zh", True) == "回答和语音语言：简体中文。"
assert language.status_text("zh", False) == "已选择简体中文。正在准备本地语音，文本现在即可使用。"
assert language.status_text("ru", False) == "Язык ответа и голоса: русский."
print("ALL OK: PATCH-007 public contract; network=0; model_calls=0")
