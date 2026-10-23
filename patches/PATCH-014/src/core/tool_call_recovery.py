"""Восстановить один строгий Markdown-вызов без сети и побочных действий."""

import json
import re

MAX_RESPONSE_CHARS = 24000
MAX_ARGUMENT_CHARS = 8000

_NAME = re.compile(
    r"(?mi)^\s*\*\*(?:Функция|Function|函数):\*\*\s*([A-Za-z_][\w.-]*)\s*$"
)
_ARGS = re.compile(r"(?mi)^\s*\*\*(?:Аргументы|Arguments|参数):\*\*\s*")
_HEADING = re.compile(
    r"(?mi)^\s*#{1,6}\s*(?:Функция|Function|函数):\s*[A-Za-z_][\w.-]*\s*$\n?"
)


def recover_one(text, allowed_names):
    """Вернуть ``(видимый_текст, вызов)`` или ``(исходный_текст, None)``."""
    source = str(text or "")
    allowed = {str(name) for name in (allowed_names or ())}
    if not source or len(source) > MAX_RESPONSE_CHARS or not allowed:
        return source, None

    match = _NAME.search(source)
    if not match or match.group(1) not in allowed:
        return source, None
    args_label = _ARGS.search(source, match.end())
    if not args_label or source[match.end():args_label.start()].strip():
        return source, None
    tail = source[args_label.end():].lstrip()
    if not tail.startswith("{"):
        return source, None
    try:
        args, end = json.JSONDecoder().raw_decode(tail)
    except ValueError:
        return source, None
    if not isinstance(args, dict) or end > MAX_ARGUMENT_CHARS:
        return source, None

    prefix = source[:match.start()]
    if _NAME.search(prefix) or _ARGS.search(prefix):
        return source, None
    return _HEADING.sub("", prefix).rstrip(), {"name": match.group(1), "args": args}
