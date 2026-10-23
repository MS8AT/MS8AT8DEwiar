# PATCH-005 — Human Memory, Codex task tree, API/log

This is a separate MS8AT patch kit, not a redistribution of Dewiar. Run `python verify.py` first. Full integration
requires an authorized exact checkout of upstream Dewiar `0.39.7` at commit
`24a3d6c22142b623081478a121d396d7e42741c1`. Publication is not installation and does not grant access to accounts,
memory, models, networks, or paid requests.

## RU — ТЗ

Dewiar — голосовой AI-помощник с персонажами, памятью и фоновыми задачами. Патч добавляет три независимых контура:

1. Human Memory через единственный read-only MCP `human_memory_recall`, только при отдельной галочке задачи и точном
   scope: `session_id`, `object_key`, `keys`, `since`, `as_of`.
2. Одноуровневое дерево Codex-задач: 1–4 части за запуск, максимум 16, тот же профиль, отдельная квота и отдельное
   подтверждение человека.
3. Локальный read-only API/лог карточки задачи: состояние, квота, heartbeat, прямые дети и безопасные события без
   промптов, ответов, путей, имён аккаунтов и секретов.

Ответ памяти принимается только при совпадении task/revision/scope/object/as_of, полном покрытии keys и реальном
SHA-256 каждой целой цитаты. Одинаковые названия задач не должны делить каталог; stop/delete родителя проверяется
под блокировкой до создания и запуска частей. Откат новых незапущенных задач не должен зависеть от `save/emit`.
API сначала фильтрует события и детей выбранной задачи, затем применяет лимит 100.

## EN — specification

Add three opt-in contours: exact-scope read-only Human Memory MCP retrieval, one-level confirmed Codex task
delegation with separate quotas, and an immediately visible local read-only task API/log. Bind every memory packet
to task, revision, scope, object, timestamp, requested-key coverage, and the actual SHA-256 of each full quote.
Profile permission is capability only; a task without its own Human Memory checkbox must follow the normal Codex
path. Serialize child creation/launch with parent stop/delete, use unique task directories, and provide truthful
rollback status without leaking internal errors.

## 中文 — 规格

增加三个默认关闭、可独立选择的模块：精确作用域的只读 Human Memory MCP、经人工确认的一层 Codex 子任务树，
以及在任务卡片中立即可见的本地只读 API/日志。内存数据包必须绑定 task、revision、scope、object、as_of、
完整 keys 覆盖范围，并校验每条完整引用文本的真实 SHA-256。配置文件权限只表示“允许使用”；任务未勾选
Human Memory 时必须走普通 Codex 路径。子任务创建与首次启动必须和父任务 stop/delete 串行化，任务目录必须
唯一，回滚失败必须如实显示且不得泄露内部错误。

## Files and integration targets

- Standalone MS8AT modules: `src/core/human_memory_contour.py`, `src/core/task_observability.py`.
- Integration prompt: `PROMPT.md`.
- Offline public contract test: `tests/public_contract_test.py`.
- Dewiar integration targets: `core/subscription_context.py`, `core/engine_commands.py`, `core/tasks.py`,
  `core/brain_watch.py`, `core/diagnostics.py`, `ui/settings.html`, `ui/studio/subscription.js`,
  `ui/studio/tasks.js`.

## Acceptance

- `python verify.py`
- `python -B tests/public_contract_test.py`
- In an authorized integrated checkout: full `subscription_suite_test.py`, `task_parts_test.py`, Python AST check,
  JavaScript syntax check, and exact-upstream overlay verification.
- Offline acceptance requires zero model calls. Live Human Memory and paid inference remain separate, explicit tests.

The two project illustrations remain in [`../../assets`](../../assets/README.md).
