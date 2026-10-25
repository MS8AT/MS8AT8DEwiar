from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core"))
import language_mode as lang
h = "ЯЗЫК ТЕКУЩЕГО ОТВЕТА / RESPONSE LANGUAGE / 当前回答语言:\n"
for code in ("ru", "en", "zh"):
    assert lang.response_language("old example 简体中文\n" + h + lang.prompt(code)) == code
assert lang.response_language("just a Chinese quote: 简体中文") is None
assert lang.response_language(h + lang.prompt("ru") + "\n" + h + lang.prompt("zh")) == "zh"
assert lang.response_language(h + "untrusted arbitrary rule") is None
assert [lang.normalize(x) for x in ("RU", "ENG", "CH", "zh-CN")] == ["ru", "en", "zh", "zh"]
print("PASS: explicit language policy; app transport integration checked separately")
