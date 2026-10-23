# Патчи и ТЗ · Patches and specifications · 补丁与规格

Каждый патч публикуется отдельно от Dewiar и содержит собственные файлы, ТЗ, промпт, хеши и тесты. Публикация
не означает автоматическую установку. / Each patch is published separately from Dewiar with its own files,
specification, prompt, hashes, and tests. Publication is not installation. / 每个补丁都与 Dewiar 分开发布，并包含独立文件、
规格、提示词、哈希和测试；公开发布不等于自动安装。

| ID | Что делает / Purpose / 用途 | Комплект / Kit / 补丁包 |
|---|---|---|
| PATCH-012 | Безопасный выбор модели подписки / Safe subscription model selection / 安全的订阅模型选择 | [ТЗ](PATCH-012/README.md) · [prompt](PATCH-012/PROMPT.md) · [manifest](PATCH-012/manifest.json) |
| PATCH-011 | Самопроверка подписки и API/CLI/SLI / Subscription self-check and API/CLI/SLI / 订阅自检与 API/CLI/SLI | [ТЗ](PATCH-011/README.md) · [prompt](PATCH-011/PROMPT.md) · [manifest](PATCH-011/manifest.json) |
| PATCH-010 | Независимые блоки и skill агентов / Independent blocks and agent skill / 独立模块与 Agent Skill | [ТЗ](PATCH-010/README.md) · [prompt](PATCH-010/PROMPT.md) · [manifest](PATCH-010/manifest.json) |
| PATCH-009 | Локальное окно отключения / Local disconnect dialog / 本地断开对话框 | [ТЗ](PATCH-009/README.md) · [prompt](PATCH-009/PROMPT.md) · [manifest](PATCH-009/manifest.json) |
| PATCH-008 | Команды задач Windows / Windows task commands / Windows 任务命令 | [ТЗ](PATCH-008/README.md) · [prompt](PATCH-008/PROMPT.md) · [manifest](PATCH-008/manifest.json) |
| PATCH-007 | Язык ответа и голоса RU/ENG/CH / Response and voice language / 回答和语音语言 | [ТЗ](PATCH-007/README.md) · [prompt](PATCH-007/PROMPT.md) · [manifest](PATCH-007/manifest.json) |
| PATCH-005 | Human Memory, дерево Codex-задач и API/лог / Human Memory, Codex task tree and API/log / Human Memory、Codex 子任务树与 API/日志 | [ТЗ](PATCH-005/README.md) · [prompt](PATCH-005/PROMPT.md) · [manifest](PATCH-005/manifest.json) |
| PATCH-004 | Подтверждаемое продление квоты задач Codex / Confirmed Codex task quota grant / 经确认的 Codex 任务配额扩展 | [ТЗ и промпт](PATCH-004/README.md) · [manifest](PATCH-004/manifest.json) |

База PATCH-011…012: официальный Dewiar `0.40.0`, commit `0e5917abf71e6d92a67b013c6fe5031f22a8af74`.
Интегрированный кандидат MS8AT: commit `ef9f0be6df1f7f210bff827133dcb5431e393335`.

База PATCH-007…010: официальный Dewiar `0.39.8`, commit `62e7446e686dfd9d901e82dee72b5731f6d70829`.
Интегрированный кандидат MS8AT: commit `2c9343a3ffe9081219fc9d2eb8ceec66a6fc7ee5`.

База PATCH-005: официальный Dewiar `0.39.7`, commit `24a3d6c22142b623081478a121d396d7e42741c1`.
Кандидат MS8AT: merge commit `48587e55ab52cb5b596046b30ee306e3979f1ccd`.

База PATCH-004: официальный Dewiar `0.39.6`, commit `4a72b8bdbca52810c42a32a871dd8252d913036e`.
Кандидат MS8AT: commit `b117dcaa31b456a8ff5ce559434b8ba46c75cad1`.
