# PATCH-011 — subscription self-check, API/CLI and SLI validation

This is a separate MS8AT patch kit, not a redistribution of Dewiar. Run `python verify.py` first. Integration
requires an authorized exact checkout of upstream Dewiar `0.40.0` at commit
`0e5917abf71e6d92a67b013c6fe5031f22a8af74`. No account, token, prompt, response, or Dewiar source tree is included.

## RU — ТЗ

Dewiar — голосовой AI-помощник с персонажами, памятью и фоновыми задачами. PATCH-011 исправляет ложный красный
статус «Мозг» в общей самопроверке, когда выбран отдельный Codex по подписке. Такой профиль нельзя проверять как
обычный OpenAI-совместимый API через `/models`: аккаунт и модель принадлежат отдельному локальному контуру.

Самопроверка должна вызвать только локальный валидатор полей, согласий и `local_only`. Она не выполняет inference,
не обновляет token, не перечисляет модели и не расходует лимит. Только сообщения явно разрешённого класса ошибки
могут попасть в UI; неизвестное исключение заменяется стабильным кодом без внутреннего текста.

Дополнительно приложен модульный план проверки CLI/API/SLI. WebSocket-клиент обязан ждать reply с собственным `id`:
push-события микрофона или состояния могут прийти раньше ответа и не являются ошибкой команды.

## EN — specification

Fix the false failed “Brain” item when the selected brain is the isolated ChatGPT-subscription route. Do not call
the generic `/models` path and do not run test inference. Validate only local profile fields, consent and policy.
Redact unexpected exceptions. Correlate WebSocket replies by request `id` because push events can arrive first.

## 中文 — 规格

修复选择独立 ChatGPT 订阅通道时“Brain”自检误报失败的问题。不得调用通用 `/models`，也不得发送测试推理；
只校验本地账号、模型、用户同意和 `local_only` 策略。未知异常必须转换为稳定错误码，不能泄露内部文本。
WebSocket 客户端必须按请求 `id` 匹配 reply，因为麦克风或状态 push 事件可能先到达。

## Files

- `src/core/subscription_self_check.py` — standalone offline contract.
- `tests/public_contract_test.py` — zero-network, redaction and routing tests.
- `PROMPT.md` — three-language integration prompt.
- `TEST_PLAN.md` — independently runnable T1–T9 plan.
- `manifest.json`, `verify.py` — offline SHA-256 verification.

## Acceptance

- `python verify.py`
- `python -B tests/public_contract_test.py`
- Integrated checkout: subscription suite, overlay verification, installed CLI `test/api/status/brains/journal/sli`,
  denied-scope checks, correlated `self_check`, and new-log inspection.
- Live inference and Human Memory MCP remain separate opt-in tests.
