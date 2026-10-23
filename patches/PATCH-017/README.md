# PATCH-017 — Резерв итога / Final request reserve / 最终请求预留

[RU](#ru) | [ENG](#eng) | [CH](#ch)

## RU

Одна ответственность: оставить в подтверждённом бюджете запросы на итог, включённую самопроверку и урок.
Вход: флаги этапов, разрешённые действия и остаток. Выход: число зарезервированных запросов и допустимые действия.
Когда остаётся только резерв, доступны finish/pause. Квота не увеличивается, сеть и модель не вызываются.
Лимит 5 с самопроверкой и уроком даёт два рабочих запроса и три завершающих.

## ENG

Reserve the final answer plus enabled review and learning requests inside the existing budget.
Inputs are stage flags, allowed actions and remaining requests. Outputs are the reserve and allowed action map.
When only the reserve remains, allow finish/pause. No quota extension, network, models or file changes.

## CH

在已有预算内预留最终回答、复查和学习所需的请求。
输入为阶段开关、允许动作和剩余请求，输出为预留数量及允许动作。
只剩预留请求时，仅允许 finish/pause。不增加配额，不调用网络或模型。

Standalone tests use synthetic dictionaries. The full application test covers two reads, finish, review and lesson within five requests.
Rollback: restore the previous verified overlay.
