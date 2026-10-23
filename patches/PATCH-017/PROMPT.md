# PATCH-017 integration prompt

## RU

Интегрируй task_budget.reserve() в расчёт завершения Codex-задачи и task_budget.actions() перед отправкой каждого шага.
Передай в prompt остаток и резерв; локально проверяй действие по сокращённому allowlist.
Сохрани счётчик попыток до отправки, подтверждение продления и отсутствие скрытых повторов.

## ENG

Use reserve() to count finalization stages and actions() before each task step.
Include the remaining budget and reserve in the prompt. Validate responses against the reduced action allowlist.
Preserve persistent attempt counting and explicit quota extension.

## CH

使用 reserve() 计算收尾请求数，每一步使用 actions() 生成允许动作。
提示词包含剩余预算和预留数量，按缩减后的白名单验证输出。
保留持久化尝试计数和明确的配额延长流程。
