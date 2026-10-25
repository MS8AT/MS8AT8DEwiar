# PATCH-024 — Выбор голоса OpenAI TTS / OpenAI TTS voice selection / OpenAI TTS 语音选择

**[RU](#ru) · [ENG](#eng) · [CH](#ch)**

## RU

Выбор голоса OpenAI TTS. База интеграции: Dewiar **0.45.3**, commit `32fcd918f21fc606efc0ed37870ac8edb9d1a290`.
Публичный формат: **INTEGRATION_SPEC_ONLY**. [ТЗ](SPEC.md) · [Промпт](PROMPT.md) · [Файлы и хеши](manifest.json).
В этом блоке публикуются требования и точки подключения; готового отдельного runtime-модуля здесь нет.
Файлы существующего приложения здесь не заменяются. Полный частный патч и его результаты не означают,
что этот отдельный блок уже встроен в установленный Dewiar. Подключение выполнить по PROMPT и проверить отдельно.
`python verify.py` проверяет целостность; проверки поведения перечислены в ТЗ и общем журнале, не выполняются этим verifier.
Удаление добавленных файлов допустимо только после отмены своих точек подключения и проверки хешей.
Установка, реальные модели, аккаунты, микрофон и физический Android: **NOT_RUN** в этой публикации.

## ENG

OpenAI TTS voice selection. Target: Dewiar 0.45.3 at the exact commit above. Format: **INTEGRATION_SPEC_ONLY**.
[Specification](SPEC.md), [integration prompt](PROMPT.md), [manifest](manifest.json).
Only authored standalone files are distributed. The additive patch does not wire the application hooks.
Hash verification is not an integration or installation test. Keep a clean base, review hooks, run affected tests,
and reverse only your changes. Live inference, devices and installation are **NOT_RUN**.

## CH

OpenAI TTS 语音选择。目标为上述准确提交的 Dewiar 0.45.3。格式：**INTEGRATION_SPEC_ONLY**。
[规格](SPEC.md) · [集成提示词](PROMPT.md) · [哈希清单](manifest.json)。
仅发布我们编写的独立文件；新增文件补丁不自动接入应用。哈希通过不等于集成或安装成功。
请在独立副本中接入、测试并保留回滚。真实模型、设备、账户与安装均为 **NOT_RUN**。


### Additive patch / Только новые файлы / 仅新增文件

Where `module-files.patch` exists, first inspect it, then use `git -c core.autocrlf=false apply --check module-files.patch` in a separate source copy. Apply with the same `-c core.autocrlf=false` option to preserve the LF hashes. Reverse uses `git -c core.autocrlf=false apply --reverse module-files.patch`. Existing app hooks still require the integration prompt; this is not an automatic application upgrade.
