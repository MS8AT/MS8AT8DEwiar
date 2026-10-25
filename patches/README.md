# Патчи и ТЗ · Patches and specifications · 补丁与规格

**Актуальная поставка / Current delivery / 当前交付: [0.45.3: PATCH-020…031 + Android 005](../RELEASE_0.45.3.md).** Ниже — предыдущая база и сохранённая история.


Каждый патч публикуется отдельно от Dewiar и содержит собственные файлы, ТЗ, промпт, хеши и тесты. Публикация
не означает автоматическую установку. / Each patch is published separately from Dewiar with its own files,
specification, prompt, hashes, and tests. Publication is not installation. / 每个补丁都与 Dewiar 分开发布，并包含独立文件、
规格、提示词、哈希和测试；公开发布不等于自动安装。

Текущая база / Current base / 当前基础版本: **Dewiar 0.40.1, MS8AT build 24**,
commit `616e70afada2ca3ebe95d894cb7d836592366aed`.
[Интеграция RU/ENG/CH](../prompts/DEWIAR_0401.md) · [Проверки / Tests / 测试](../VALIDATION_2026-10-24.md).

| ID | Что делает / Purpose / 用途 | Комплект / Kit / 补丁包 |
|---|---|---|
| PATCH-019 | Human Memory stdio / 本地记忆传输 | [ТЗ](PATCH-019/README.md) · [prompt](PATCH-019/PROMPT.md) · [ZIP](../dist/PATCH-019.zip) |
| PATCH-018 | Локальные задачи / Local tasks / 本地任务 | [ТЗ](PATCH-018/README.md) · [prompt](PATCH-018/PROMPT.md) · [ZIP](../dist/PATCH-018.zip) |
| PATCH-017 | Резерв итога / Final reserve / 收尾预留 | [ТЗ](PATCH-017/README.md) · [prompt](PATCH-017/PROMPT.md) · [ZIP](../dist/PATCH-017.zip) |
| PATCH-016 | Защищённые корни / Protected roots / 受保护目录 | [ТЗ](PATCH-016/README.md) · [prompt](PATCH-016/PROMPT.md) · [ZIP](../dist/PATCH-016.zip) |
| PATCH-015 | Выбор модели / Model selection / 模型选择 | [ТЗ](PATCH-015/README.md) · [prompt](PATCH-015/PROMPT.md) · [ZIP](../dist/PATCH-015.zip) |
| PATCH-014 | Восстановление tool-call / Tool-call recovery / 工具调用恢复 | [ТЗ](PATCH-014/README.md) · [prompt](PATCH-014/PROMPT.md) · [ZIP](../dist/PATCH-014.zip) |
| PATCH-013 | AI-доктор переполнения контекста / Context overflow AI doctor / 上下文溢出 AI 医生 | [ТЗ](PATCH-013/README.md) · [prompt](PATCH-013/PROMPT.md) · [manifest](PATCH-013/manifest.json) · [ZIP](../dist/PATCH-013.zip) |
| PATCH-012 | Безопасный выбор модели подписки / Safe subscription model selection / 安全的订阅模型选择 | [ТЗ](PATCH-012/README.md) · [prompt](PATCH-012/PROMPT.md) · [manifest](PATCH-012/manifest.json) |
| PATCH-011 | Самопроверка подписки и API/CLI/SLI / Subscription self-check and API/CLI/SLI / 订阅自检与 API/CLI/SLI | [ТЗ](PATCH-011/README.md) · [prompt](PATCH-011/PROMPT.md) · [manifest](PATCH-011/manifest.json) |
| PATCH-010 | Независимые блоки и skill агентов / Independent blocks and agent skill / 独立模块与 Agent Skill | [ТЗ](PATCH-010/README.md) · [prompt](PATCH-010/PROMPT.md) · [manifest](PATCH-010/manifest.json) |
| PATCH-009 | Локальное окно отключения / Local disconnect dialog / 本地断开对话框 | [ТЗ](PATCH-009/README.md) · [prompt](PATCH-009/PROMPT.md) · [manifest](PATCH-009/manifest.json) |
| PATCH-008 | Команды задач Windows / Windows task commands / Windows 任务命令 | [ТЗ](PATCH-008/README.md) · [prompt](PATCH-008/PROMPT.md) · [manifest](PATCH-008/manifest.json) |
| PATCH-007 | Язык ответа и голоса RU/ENG/CH / Response and voice language / 回答和语音语言 | [ТЗ](PATCH-007/README.md) · [prompt](PATCH-007/PROMPT.md) · [manifest](PATCH-007/manifest.json) |
| PATCH-005 | Human Memory, дерево Codex-задач и API/лог / Human Memory, Codex task tree and API/log / Human Memory、Codex 子任务树与 API/日志 | [ТЗ](PATCH-005/README.md) · [prompt](PATCH-005/PROMPT.md) · [manifest](PATCH-005/manifest.json) |
| PATCH-004 | Подтверждаемое продление квоты задач Codex / Confirmed Codex task quota grant / 经确认的 Codex 任务配额扩展 | [ТЗ и промпт](PATCH-004/README.md) · [manifest](PATCH-004/manifest.json) |

## История баз / Base history / 历史基础版本

Следующие записи — история первых интеграций, не текущие требования установки.
Historical integration records, not current installation requirements. 以下为历史集成记录，并非当前安装要求。

База PATCH-011…013: официальный Dewiar `0.40.0`, commit `0e5917abf71e6d92a67b013c6fe5031f22a8af74`.
Интегрированный кандидат MS8AT: commit `f3204473974cb6bd0a8dc4234b5ece137c9999f6`.

База PATCH-007…010: официальный Dewiar `0.39.8`, commit `62e7446e686dfd9d901e82dee72b5731f6d70829`.
Интегрированный кандидат MS8AT: commit `2c9343a3ffe9081219fc9d2eb8ceec66a6fc7ee5`.

База PATCH-005: официальный Dewiar `0.39.7`, commit `24a3d6c22142b623081478a121d396d7e42741c1`.
Кандидат MS8AT: merge commit `48587e55ab52cb5b596046b30ee306e3979f1ccd`.

База PATCH-004: официальный Dewiar `0.39.6`, commit `4a72b8bdbca52810c42a32a871dd8252d913036e`.
Кандидат MS8AT: commit `b117dcaa31b456a8ff5ce559434b8ba46c75cad1`.
