# PATCH-015 — Purpose-aware model selection / 按用途选择模型

## RU

Одна ответственность: выбрать имя модели из уже полученного списка по назначению контура. Обычный чат сохраняет
лёгкий instruct-выбор. Фоновые задачи предпочитают tool-friendly семейство 7–14B вместо 1–2B или тяжёлой модели по
умолчанию. Embedding, speech, rerank и moderation исключаются. Явно выбранную человеком модель меняет не этот блок,
а адаптер обязан пропустить её без вызова `choose`.

Вход: список имён и `purpose`. Выход: одно имя или пустая строка. Сеть, inference, настройки и файлы пользователя не
затрагиваются. Интеграция: `core/llm.py`, только ветка автоматического выбора; кэш — по endpoint и purpose.

## EN

One responsibility: select a model name from an already available list for a given purpose. Chat keeps the lightweight
instruct choice. Background tasks prefer a tool-friendly 7–14B family instead of a 1–2B model or a heavy default.
Non-chat models are excluded. The adapter must bypass this module when the user selected a model explicitly.

## 中文

单一职责：从已有模型列表中按用途选择名称。普通聊天保留轻量 instruct 模型；后台任务优先选择支持工具的 7–14B
系列，而不是 1–2B 小模型或默认使用重型模型。排除非聊天模型。用户明确选择模型时，适配器不得调用本模块覆盖它。

## Проверка / Verification / 验证

```text
python verify.py
python tests/public_contract_test.py
```

- PASS: pure selection contract.
- NOT_RUN: live model, installed Dewiar, network, accounts.
- Rollback: remove this block and restore the previous `pick_model/resolve_model` adapter.
