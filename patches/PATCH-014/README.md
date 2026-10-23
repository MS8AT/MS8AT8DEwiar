# PATCH-014 — Markdown tool-call recovery / 恢复 Markdown 工具调用

## RU

Некоторые локальные модели печатают вызов функции как Markdown вместо родного `tool_calls`. Блок принимает только
первую строгую пару `Функция/Аргументы`, только имя из списка инструментов текущего запроса и только JSON-объект
ограниченного размера. Текст после вызова отбрасывается: модель ещё не видела настоящий результат и не может его
объявлять. Сам блок ничего не выполняет, не открывает сеть и не читает пользовательские файлы.

Вход: текст ответа и список разрешённых имён. Выход: безопасный видимый префикс и один вызов либо исходный текст и
`None`. Интеграция: `core/tool_call_recovery.py`; вызов из `core/tasks.py` только при отсутствии native tool call,
после чего используется штатный `_tool` со всеми подтверждениями и защитой рабочей копии.

## EN

Some local models print a function call as Markdown instead of native `tool_calls`. This block accepts only the first
exact Function/Arguments pair, only a name offered in the current request, and only a bounded JSON object. Everything
after the call is discarded because the model has not seen the real tool result. The block performs no action, makes
no network call, and reads no user file.

Input: assistant text and allowed names. Output: safe visible prefix plus one call, or the original text plus `None`.

## 中文

某些本地模型会把函数调用打印成 Markdown，而不是返回原生 `tool_calls`。本模块只接受第一组严格的“函数/参数”，
只允许当前请求提供的工具名，并且参数必须是受大小限制的 JSON 对象。调用后的文本会被丢弃，因为模型尚未看到真实
工具结果。本模块不执行命令、不访问网络，也不读取用户文件。

输入：助手文本和允许的工具名。输出：安全的可见前缀与一个调用，或者原文本与 `None`。

## Проверка / Verification / 验证

```text
python verify.py
python tests/public_contract_test.py
```

- PASS: автономный parser contract.
- NOT_RUN: live model, installed Dewiar, user accounts, network.
- Rollback: remove the block and its two-line adapter from `core/tasks.py`.
