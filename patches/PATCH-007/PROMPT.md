# PATCH-007 integration prompt · Интеграционный промпт · 集成提示词

[Русский](#ru) · [English](#en) · [中文](#zh)

<a id="ru"></a>
## RU

Работай только в легально доступной копии exact upstream Dewiar 0.40.1 commit
`616e70afada2ca3ebe95d894cb7d836592366aed`. Добавь единый allowlist языков `ru/en/zh`, отдельную команду
`language_set` и кнопку `RU / ENG / CH`. Применяй последнее языковое правило к обычному системному prompt и к
изолированному Codex prompt. Не передавай произвольный settings patch из HUD. Голос выбирай по языку и полу
персонажа; скачивай Piper только после явного клика, не обходи `local_only`. Не выдавай локальный тест за проверку
реального голоса или модели. Обнови exact-SHA overlay, добавь автономные unit и browser tests и план отката.

Для Dewiar 0.40.1 сохрани CSS-адаптер узкого HUD в `ui/hud.html`: при ширине от 280 px все кнопки, включая
`RU / ENG / CH`, должны оставаться видимыми и помещаться без горизонтального переполнения. Для ширины до 320 px
используй компактные отступы и ширины кнопок. Проверь все три языка на 280, 300 и 440 px; не скрывай кнопки ради размещения.
В светлых темах контраст текста кнопки языка по скриншоту должен быть не ниже 3:1; сохрани для `#b-lang` цвет `var(--ink)`.

<a id="en"></a>
## EN

Integrate only into authorized exact upstream Dewiar 0.40.1 commit `616e70afada2ca3ebe95d894cb7d836592366aed`.
Keep one `ru/en/zh` allowlist and a dedicated `language_set`
command. Apply the same final language rule to regular chat and Codex prompts. Select Piper by language and persona
gender, download only after an explicit click, and never bypass `local_only`. Add offline unit/browser tests and
an exact-SHA overlay; do not claim live voice or inference validation.

For Dewiar 0.40.1, preserve the narrow-HUD CSS adapter in `ui/hud.html`: at widths from 280 px, every button,
including `RU / ENG / CH`, must remain visible and fit without horizontal overflow. Use compact spacing and button
widths up to 320 px. Check all three languages at 280, 300 and 440 px; do not hide buttons to make them fit.
In light themes, the language-button text contrast measured from a screenshot must be at least 3:1; keep `#b-lang` color `var(--ink)`.

<a id="zh"></a>
## 中文

仅在获得授权的 Dewiar 0.40.1 精确上游提交 `616e70afada2ca3ebe95d894cb7d836592366aed` 中集成。
使用统一的 `ru/en/zh` 白名单和独立的 `language_set` 命令，并将相同的
最终语言规则应用于普通聊天与 Codex 提示词。根据语言和角色性别选择 Piper；只有用户明确点击后才下载，
不得绕过 `local_only`。添加离线单元测试、浏览器测试和精确 SHA overlay，不得把离线测试描述为真实语音或推理验证。

对于 Dewiar 0.40.1，保留 `ui/hud.html` 中的窄屏 HUD CSS 适配：宽度从 280 px 起，所有按钮（包括
`RU / ENG / CH`）都必须可见且无水平溢出。宽度不超过 320 px 时使用紧凑间距和按钮宽度。
在 280、300 和 440 px 下检查三种语言，不得通过隐藏按钮来适配。
在浅色主题中，截图测得的语言按钮文字对比度必须至少为 3:1；保留 `#b-lang` 的 `var(--ink)` 颜色。
