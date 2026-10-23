"""Standalone RU/ENG/CH policy for PATCH-007. No network or model calls."""

MODES = {
    "ru": {"label": "RU", "name": "Русский", "remote": "Russian", "voices": {},
           "prompt": "Отвечай на русском языке. Имена, цитаты, код и явно запрошенный перевод сохраняй в нужном языке."},
    "en": {"label": "ENG", "name": "English", "remote": "English",
           "voices": {"female": "en_US-amy-medium", "male": "en_US-ryan-medium"},
           "prompt": "Respond in English. Preserve names, quotations, code, and explicitly requested translations in their required language."},
    "zh": {"label": "CH", "name": "简体中文", "remote": "Chinese",
           "voices": {"female": "zh_CN-huayan-medium", "male": "zh_CN-huayan-medium"},
           "prompt": "请使用简体中文回答。姓名、引文、代码以及用户明确要求的翻译应保留所需语言。"},
}


def normalize(value, strict=False):
    code = str(value or "ru").strip().lower()
    code = {"rus": "ru", "russian": "ru", "eng": "en", "english": "en",
            "ch": "zh", "cn": "zh", "zh-cn": "zh", "chinese": "zh"}.get(code, code)
    if code not in MODES:
        if strict:
            raise ValueError("language must be RU, ENG, or CH")
        return "ru"
    return code


def prompt(value):
    return MODES[normalize(value)]["prompt"]


def voice_id(value, gender="female"):
    return MODES[normalize(value)]["voices"].get("male" if gender == "male" else "female", "")


def voice_config(value, voice):
    code = normalize(value)
    out = dict(voice or {}, _language=code, _language_name=MODES[code]["remote"])
    selected = voice_id(code, out.get("_gender"))
    if selected:
        out.update(piper=selected, length_scale=1.0)
    return out
