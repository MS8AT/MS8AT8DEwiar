# Dewiar 0.45.3 integration prompt

**[RU](#ru) · [ENG](#eng) · [CH](#ch)**

## RU

Работай над одним выбранным блоком из [каталога](../RELEASE_0.45.3.md) в отдельной локальной копии
Dewiar commit `32fcd918f21fc606efc0ed37870ac8edb9d1a290`. Сначала прочитай ТЗ и manifest, проверь SHA-256 и standalone-тесты.
Сохрани стиль автора и текущие настройки. Добавляй новые файлы отдельно; существующие хуки изменяй минимальным diff.
Явный выбор человека важнее маршрутизации. Codex app-server, официальный OpenAI API и локальный совместимый
сервер — разные типы подключения. Каталог моделей и capabilities получай от выбранного сервиса только при
разрешённом подключении; тестовые model ID не превращай в обязательный список. Для каждой задачи выбирай
короткий профиль: chat, plan, task, review, summary или memory из [профилей](../patches/PATCH-023/src/integrations/ms8at/openai_prompt_profiles.json).
Экономь токены ограничением релевантного контекста и размера ответа, не удалением правил и подтверждений.
Не переключай на платный сервис и не копируй токены между провайдерами. Новые языки должны сохраняться в
ответе, ASR и TTS; русская эвристика не должна отменять ENG/CH.
Для звука сначала используй синтетику и локальный WAV. Предварительный контекст — версия и срок действия,
не предсказанный факт и не команда. Поправленная фраза отменяет устаревший recall; до final нельзя исполнять действие.
Android не должен показывать Codex/MCP/vector как подключённые без реализации и проверяемого соединения.
По завершении сохрани diff, результаты отдельных и интеграционных проверок, способ отката и NOT_RUN.
Не устанавливай приложение и не публикуй изменения автоматически.

## ENG

Integrate one selected block into an isolated checkout at the exact commit above. Read its specification and
manifest; verify hashes and standalone tests first. Keep upstream style, existing settings and a minimal hook diff.
Explicit user model choices win. Codex app-server, official OpenAI API and local compatible servers are separate
connection types; test model IDs are not a required catalog. Use the short chat/plan/task/review/summary/memory
profile matching capabilities. Save tokens by bounding relevant context and output, not by removing permission
checks. Never silently switch to a paid provider or copy account tokens. Preserve selected RU/ENG/CH across
response, ASR and TTS. Audio tests start with synthetic/local WAV. Prepared context is revision-bound and expires;
revised speech cancels stale recall and no action runs from a partial transcript. Android must report unavailable
Codex/MCP/vector integrations honestly. Return diff, tests, rollback and NOT_RUN; do not auto-install or publish.

## CH

在上述准确提交的独立副本中仅集成一个模块。先读规格与清单，验证哈希并运行独立测试。
保留原作者风格、用户设置和最小接口差异。用户显式选择优先；Codex app-server、官方 OpenAI API
和本地兼容服务是不同连接类型，测试模型名不是固定目录。按能力和任务选择简短的聊天、计划、
执行、审查、摘要或记忆提示词。通过限制相关上下文与输出节省 token，不删除权限检查。
不得自动转到收费服务或复制账户 token。回答、ASR 和 TTS 均应保留 RU/ENG/CH 选择。
音频先用合成信号和本地 WAV；预备上下文绑定版本并过期，改口取消旧召回，partial 文本不能触发动作。
Android 对未连接的 Codex/MCP/向量记忆必须如实显示。交付差异、测试、回滚与 NOT_RUN，不自动安装或发布。
