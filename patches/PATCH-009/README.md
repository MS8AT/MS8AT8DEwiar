# PATCH-009 — local disconnect confirmation dialog

[Русский](#ru) · [English](#en) · [中文](#zh)

Separate patch kit for authorized Dewiar `0.40.1` commit `616e70afada2ca3ebe95d894cb7d836592366aed`.
It contains no account token and does not disconnect anything during verification.

<a id="ru"></a>
## RU — ТЗ

Кнопка отключения Codex/аккаунта не должна открывать системный JavaScript `confirm`, который может показать
технический URL и локальный токен связи. Использовать штатное локальное окно Dewiar `ask`: явные действия
«Отмена»/«Выйти», Escape и щелчок мимо означают отказ. Текст для отдельного Codex-профиля обязан пояснять, что
основной Codex и Hermes не изменяются. Команда отключения вызывается только после положительного ответа.

<a id="en"></a>
## EN — specification

Replace native JavaScript `confirm` in the Codex/account disconnect action with Dewiar's local `ask` dialog so a
technical page URL and local connection token are not exposed. Cancel, Escape, or outside click must decline. The
separate Codex-profile text must explicitly say that the main Codex and Hermes remain unchanged. Call disconnect
only after a positive local answer.

<a id="zh"></a>
## 中文 — 规格

将 Codex/账户断开操作中的系统 JavaScript `confirm` 替换为 Dewiar 本地 `ask` 对话框，避免暴露技术页面地址
和本地连接令牌。取消、Escape 或点击对话框外部都必须表示拒绝。独立 Codex 配置的文本必须明确说明主 Codex
和 Hermes 不会改变。只有本地明确同意后才能调用断开命令。

## Files and acceptance

- Standalone UI helper: `src/ui/subscription_disconnect.mjs`.
- Integration prompt: `PROMPT.md`.
- Offline Node.js test: `tests/public_contract.test.mjs`.
- Dewiar target: `ui/studio/subscription.js`; regression: `dialogs1021_test.py`.
- Verification performs no login, account call, network request, or model call.
