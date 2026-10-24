# API / CLI / SLI test plan · План · 测试计划

Each block is independent. T1–T8 are read-only and require zero model calls. T9 is opt-in.

| Block | RU | EN | 中文 | PASS |
|---|---|---|---|---|
| T1 | Offline `test`, `api` | Offline CLI contract | 离线 CLI | JSON schema 1; network/model calls 0 |
| T2 | Три круга `status/brains/journal/sli` | Three live read cycles | 三轮只读调用 | exit 0; journal payload unchanged |
| T3 | Неверный token и запрещённые команды | Bad token and forbidden commands | 错误 token 与禁止命令 | connection/command denied |
| T4 | Ответ только по request `id` | Correlate reply by `id` | 按 `id` 匹配 reply | push events skipped safely |
| T5 | `task_observe` | Task-card API | 任务卡 API | hashed ID; no content/secrets |
| T6 | Формула SLI и p50/p95 | SLI arithmetic | SLI 计算 | counts sum; ratio exact; p50 <= p95 |
| T7 | Подписочный `self_check` | Subscription self-check | 订阅自检 | local PASS; no `/models` or inference |
| T8 | Только новые строки логов | Inspect only new log tail | 仅检查新增日志 | no new ERROR/Traceback |
| T9 | Один live inference и Human Memory | Explicit live boundary | 明确授权的实时测试 | separate human approval required |

SLI is a retained sample, not current availability or SLA. `completed` is not result acceptance. Report every run as
PASS, PARTIAL or NOT_RUN and keep live inference separate from offline acceptance.

Historical 2026-10-23 integrated result: T1–T8 PASS on Dewiar 0.40.0 + MS8AT build 13; six CLI commands returned schema 1;
the retained SLI sample contained 25 completed, 72 failed and 3 interrupted calls (`25/97`); T9 NOT_RUN.
