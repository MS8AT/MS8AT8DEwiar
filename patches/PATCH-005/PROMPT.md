# PATCH-005 integration prompt · Интеграционный промпт · 集成提示词

## RU

Работай только в легально доступной копии exact upstream Dewiar 0.40.1 commit
`616e70afada2ca3ebe95d894cb7d836592366aed`. Сначала составь manifest всех runtime-файлов и SHA-256. Не читай
`Pass`, `.env`, auth/config Hermes/Codex или БД памяти напрямую. Добавь отдельные task-level галочки Human Memory и
делегирования. Вызови только allowlisted read-only MCP `human_memory_recall` с подтверждённым exact scope. Не делай
fallback, автоповтор, запись в память или модельный запрос при неполном/чужом пакете. Покажи API/лог сразу в карточке:
только хешированные ID, состояния, шаги, квоты, дети, heartbeat и allowlisted события. Не показывай цель, промпт,
ответ, аргументы, пути, аккаунт или секреты. Перед созданием частей повторно проверь cancel, профиль и родителя под
его lock. Используй уникальный task ID в каталоге. Откатывай каждый созданный незапущенный объект без `save/emit`;
если хотя бы один откат не удался, сообщи это честно. Не устанавливай до полного offline PASS и штатного закрытия
Dewiar; создай backup и проверяемый rollback.

## EN

Integrate only into authorized exact upstream Dewiar 0.40.1 commit `616e70afada2ca3ebe95d894cb7d836592366aed`.
Keep Human Memory and delegation task-scoped and opt-in. Use only
the named read-only recall tool; validate packet binding, key coverage, and quote hashes. Expose a safe immediately
visible task API/log without task content or secrets. Recheck cancellation and parent identity while holding the
parent lock, create unique task directories, and attempt rollback for every newly created child. Do not install,
log in, or call a model until offline verification passes and the user separately authorizes the live boundary.

## 中文

仅在获得授权的 Dewiar 0.40.1 精确上游提交 `616e70afada2ca3ebe95d894cb7d836592366aed` 中集成。
Human Memory 与子任务委派必须按任务单独勾选。只允许调用指定的只读
recall 工具，并校验数据包绑定、keys 覆盖和引用哈希。任务卡片应立即显示安全 API/日志，但不得暴露任务正文、
路径、账号或密钥。在父任务锁内重新检查取消状态和父任务身份；任务目录必须唯一；所有已创建但未启动的子任务
都必须尝试回滚。离线验证通过、Dewiar 正常退出且用户另行授权前，不得安装、登录或调用模型。
