# PATCH-008 — reliable Windows task commands

[Русский](#ru) · [English](#en) · [中文](#zh)

Separate MS8AT patch kit for authorized Dewiar `0.39.8` commit
`62e7446e686dfd9d901e82dee72b5731f6d70829`. It does not redistribute upstream code or execute commands.

<a id="ru"></a>
## RU — ТЗ

Исправить два сбоя фоновых задач Windows. Если модель прислала tool JSON с полным путём `C:\...`, но не удвоила
обратные слеши, восстанавливать только строку, явно похожую на путь с буквой диска. Другой JSON не менять. Команду,
начинающуюся с `python3` или `python`, запускать текущим проверенным интерпретатором Dewiar. Перед выполнением
PowerShell обязан перейти в изолированную рабочую копию через `Set-Location -LiteralPath`. Guard и подтверждение
человека проверяют исходную команду до нормализации; результат и код возврата пишутся в журнал.

<a id="en"></a>
## EN — specification

Narrowly repair unescaped backslashes only in JSON strings that clearly start with a Windows drive path. Map a
leading `python3`/`python` to Dewiar's current verified interpreter and explicitly enter the isolated worktree with
PowerShell `Set-Location -LiteralPath`. Preserve command guards, human confirmation, journaling, and manual accept.

<a id="zh"></a>
## 中文 — 规格

只修复明显以 Windows 盘符路径开头的 JSON 字符串中未转义的反斜杠。将开头的 `python3`/`python` 映射到
Dewiar 当前经过验证的解释器，并通过 PowerShell `Set-Location -LiteralPath` 明确进入隔离工作树。保留命令
保护、人工确认、日志记录和手动接受流程。

## Files and acceptance

- Standalone helpers: `src/core/windows_task_commands.py`.
- Integration prompt: `PROMPT.md`.
- Offline test: `tests/public_contract_test.py`.
- Dewiar targets: `core/llm.py`, `core/codework.py`.
- Integrated acceptance: `bare_calls_test.py`, `tasks_test.py`, overlay SHA, `model_calls=0`.
