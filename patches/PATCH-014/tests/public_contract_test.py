"""Автономный контракт PATCH-014: без сети, модели и пользовательских файлов."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "core"))
from tool_call_recovery import recover_one  # noqa: E402


text = ("Проверю проект.\n\n### Функция: code_list\n\n"
        "**Функция:** code_list\n**Аргументы:** {\"pattern\": \"*.py\"}\n\n"
        "**Ответ от функции:** выдумка\n"
        "**Функция:** code_delete\n**Аргументы:** {\"path\": \"project\"}")
visible, call = recover_one(text, {"code_list", "code_delete"})
assert visible == "Проверю проект."
assert call == {"name": "code_list", "args": {"pattern": "*.py"}}

for sample in ('**Function:** finish\n**Arguments:** {"summary":"ok"}',
               '**函数:** finish\n**参数:** {"summary":"好"}'):
    assert recover_one(sample, {"finish"})[1]["name"] == "finish"

bad = [
    '**Функция:** code_delete\n**Аргументы:** {"path":"x"}',
    '**Функция:** code_list\n**Аргументы:** {broken}',
    '**Функция:** code_list\n**Аргументы:** ["*.py"]',
    '> **Функция:** code_list\n> **Аргументы:** {"pattern":""}',
]
for sample in bad:
    assert recover_one(sample, {"code_list"}) == (sample, None)

huge = "x" * 24001 + '\n**Функция:** code_list\n**Аргументы:** {}'
assert recover_one(huge, {"code_list"}) == (huge, None)
print("ALL OK: PATCH-014; calls=1; fictional_results=0; model_calls=0; network=0")
