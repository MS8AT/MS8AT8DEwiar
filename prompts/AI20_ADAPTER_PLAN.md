# AI20 adapter: next stage / следующий этап / 下一阶段

[RU](#ru) | [ENG](#eng) | [CH](#ch)

Status: **PLAN, not deployed**. This document does not start services or model calls.

## RU

Один адаптер соединяет Dewiar с существующим Manager. Новый диспетчер задач,
своя очередь и второй каталог моделей не нужны. Dewiar передаёт цель, назначение
модели и разрешённый scope; Manager остаётся владельцем исполнения. Маршрут:
Manager → Router → точный MS8AT Node → локальный LM Studio.

Небольшие блоки внедрения:

1. **Discovery.** Read-only status: версия протокола, свежесть heartbeat,
   доступные маршруты, состояние Manager. Пустой каталог — `unavailable`.
2. **Selection.** Явный выбор человека важнее автоматического. Автовыбор
   учитывает инструменты, размер контекста, память узла, занятость и свежую
   квалификацию модели. Не переходить на Codex/платный API скрыто.
3. **Task binding.** Запрос содержит task ID/revision, scope, purpose,
   лимиты и idempotency key; ответ — принятый route/model/exact instance,
   request ID и статус. Ответ модели не расширяет полномочия.
4. **Execution.** Сначала один ограниченный запрос `tools=[]`. Затем отдельная
   реализация исполнителя инструментов и отдельные тесты его разрешений.
5. **Observation.** Heartbeat, отмена, итог и обезличенный журнал связаны с
   тем же request ID. `UNKNOWN` требует reconciliation, не повторной отправки.
6. **Memory.** Human Memory подключается с task scope и существующим reader;
   доступность коннектора не разрешает чтение всей памяти.

Тестировать каждый блок на fake Manager отдельно: пустой каталог, устаревший
heartbeat, несовпадение instance/revision, отмена, timeout/UNKNOWN, повторный
ответ, превышение контекста и отказ инструментов. После этого — один live
canary на разрешённом маршруте. Разделять SOURCE_READY, LOCAL_TESTED,
LIVE_DEPLOYED, MODEL_TESTED и OPERATOR_ACCEPTED.

В build 24 этот маршрут не активирован. Сначала закрывается существующая
связка Manager↔Router; после её приёмки добавляется тонкий адаптер Dewiar.

## ENG

Use one thin Dewiar adapter to the existing Manager; do not add another queue,
scheduler or model registry. Route through Manager → Router → exact MS8AT Node
→ local LM Studio. Implement separate blocks: read-only discovery; capability,
context and fresh-health based selection; explicit task/scope/limits binding;
one bounded `tools=[]` canary; observation/cancellation/reconciliation; scoped
Human Memory. Explicit human model choices take precedence. Never silently
fallback to Codex or paid APIs. Model output grants no new permissions.

Each block needs fake-Manager tests for stale health, empty routes, identity
mismatch, cancellation, UNKNOWN, duplicate replies, context limits and denied
tools. UNKNOWN requires reconciliation before any retry. Keep source, local,
live, model and operator acceptance separate. Build 24 does not activate this
route; first finish and accept the existing Manager↔Router connection.

## CH

仅添加连接现有 Manager 的轻量 Dewiar 适配器，不新建队列、调度器或模型目录。
路径为 Manager → Router → 精确的 MS8AT Node → 本地 LM Studio。
按模块实现只读发现、按工具/上下文/实时状态选模、明确任务权限与限额绑定、
单次有限 `tools=[]` 验证、状态观察/取消/核对，以及限定范围的 Human Memory。
用户明确选择优先，禁止隐式切换 Codex 或付费 API；模型输出不能授予新权限。

每块独立测试空路由、过期心跳、实例不匹配、取消、UNKNOWN、重复响应、上下文超限
和工具拒绝。UNKNOWN 必须先核对再决定是否重试。源码、本地、部署、模型和人工验收
状态分开记录。build 24 尚未启用该路径；先完成并验收现有 Manager↔Router。
