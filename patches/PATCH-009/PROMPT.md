# PATCH-009 integration prompt · Интеграционный промпт · 集成提示词

[Русский](#ru) · [English](#en) · [中文](#zh)

<a id="ru"></a>
## RU

Интегрируй только в авторизованный exact upstream. В async-обработчике отключения замени системный `confirm` на
`await ask(...)`. Не вызывай disconnect при false/reject. Сохрани отдельный понятный текст Codex: выбранный локальный
профиль отключается, основной Codex и Hermes не меняются. Проверь статически отсутствие `confirm/prompt/alert` во
всех studio JS и браузерно — Escape, Enter, щелчок мимо и отсутствие native dialog. Не выполнять реальный вход или выход.

<a id="en"></a>
## EN

Integrate into the authorized exact upstream only. Replace native `confirm` with `await ask(...)` in the async
disconnect handler and never call disconnect after a false/rejected answer. Preserve the explicit Codex/Hermes
scope message. Verify static absence of native dialogs and browser Cancel/Escape/Enter/outside-click behavior,
without a live account operation.

<a id="zh"></a>
## 中文

仅在获得授权的精确上游中集成。在异步断开处理器中用 `await ask(...)` 替换系统 `confirm`，如果回答为 false
或被拒绝，绝不能调用断开命令。保留明确的 Codex/Hermes 作用域说明。通过静态检查和浏览器中的取消、Escape、
Enter、点击外部行为验证，不执行真实账户操作。
