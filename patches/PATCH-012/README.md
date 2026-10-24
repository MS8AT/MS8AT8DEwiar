# PATCH-012 — safe model selection for the subscription brain

This is a separate MS8AT patch kit, not a redistribution of Dewiar. Integration requires an authorized exact
checkout of upstream Dewiar `0.40.1` at commit `616e70afada2ca3ebe95d894cb7d836592366aed`.

## RU — ТЗ

Dewiar — голосовой AI-помощник с персонажами, памятью и фоновыми задачами. Когда отдельный Codex по подписке
выбран основным мозгом, общая фоновая проверка tools не должна проверять его как обычный OpenAI-совместимый API.
Подписочный маршрут принимает текст отдельно и намеренно не предоставляет общие tools.

PATCH-012 добавляет один ранний guard: для `kind=chatgpt_subscription` поток `probe-tools` не создаётся. Список
моделей остаётся доступен только по явной кнопке «Получить модели аккаунта». Выбор модели сохраняется обычным
интерфейсом, но не вызывает проверку tools, inference, задачу или автоматическую смену аккаунта.

Вход автономного модуля — словарь безопасных метаданных профиля. Выход — только `true/false`. Сеть, аккаунт,
настройки, журнал и модель не вызываются. Пустое или неверное значение закрывается безопасно (`false`).

## EN — specification

When an isolated ChatGPT-subscription profile is the active brain, never run the generic background tools probe.
That route is text-only by design. Model discovery remains an explicit user action through the account-model button.
The guard is a pure predicate over safe profile metadata and has no network, account, inference or settings effects.

## 中文 — 规格

当独立的 ChatGPT 订阅配置被选为主模型时，不得运行通用后台 tools 探测。该通道按设计仅处理文本。
模型列表只能由用户明确点击“获取账号模型”按钮后读取。守卫函数只检查安全的配置元数据，不访问网络、
账号、模型或设置；无效输入必须安全返回 `false`。

## Files and integration

- `src/core/subscription_model_probe_guard.py` — standalone pure contract.
- `tests/public_contract_test.py` — zero-network unit tests.
- `PROMPT.md` — three-language integration prompt.
- `manifest.json`, `verify.py` — offline SHA-256 verification.
- Integration target: early return in `core/engine_answer.py::probe_tools_bg` immediately after `active_llm()`.

## Acceptance

- `python patches/PATCH-010/src/tools/patch_block.py inspect PATCH-012`
- `python patches/PATCH-010/src/tools/patch_block.py test PATCH-012`
- Integrated checkout: full subscription suite and overlay verification.
- Historical verification on Dewiar 0.40.0 + MS8AT build 14: account model list returned seven models, the saved model was present, `model_calls=0`, and the
  fresh startup log had no generic tools-probe error for the subscription profile.
- Live inference and Human Memory MCP are `NOT_RUN` for this patch.
