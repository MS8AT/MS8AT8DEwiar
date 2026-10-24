# PATCH-011 integration prompt · Интеграционный промпт · 集成提示词

## RU

Работай только в легально доступной точной базе Dewiar 0.40.1 commit
`616e70afada2ca3ebe95d894cb7d836592366aed`. В общей `self_check` отдели профиль
`chatgpt_subscription` от обычного API. Вызови существующую локальную проверку готовности с новым cancel-event;
не вызывай `/models`, inference, login, refresh, download или задачу. Покажи успешный текст, что Codex настроен и
тестовый запрос не отправлялся. Отображай текст только ожидаемой локальной ошибки политики; неизвестное исключение
замени общей фразой. Добавь unit-тесты: success без `list_models`, ожидаемый отказ, редактирование неизвестной ошибки.
В WebSocket-тесте жди reply по `id`, пропуская push-события. Перед установкой прогони полный offline suite, создай
SHA-план, штатно закрой Dewiar, сделай backup, установи, перезапусти и повтори живой read-only тест с контролем логов.

## EN

Integrate only into authorized exact upstream Dewiar 0.40.1 commit `616e70afada2ca3ebe95d894cb7d836592366aed`.
Route `chatgpt_subscription` through the existing local readiness
validator and never through `/models` or test inference. Preserve only expected safe policy messages; redact every
unexpected exception. Correlate WebSocket replies by `id`, run offline tests, install only after a normal exit and a
verified backup, then repeat the read-only live test and inspect only new log lines.

## 中文

仅在已获授权的 Dewiar 0.40.1 精确上游提交 `616e70afada2ca3ebe95d894cb7d836592366aed` 中集成。`chatgpt_subscription` 必须使用现有本地就绪校验，不得调用 `/models` 或
测试推理。仅允许显示预期的安全策略错误；所有未知异常都要脱敏。WebSocket reply 必须按 `id` 关联并跳过 push
事件。离线测试通过、正常退出和可验证备份完成后才能安装，重启后再次执行只读实时测试并检查新增日志。
