# PATCH-007 integration prompt · Интеграционный промпт · 集成提示词

[Русский](#ru) · [English](#en) · [中文](#zh)

<a id="ru"></a>
## RU

Работай только в легально доступной копии exact upstream Dewiar 0.39.8 commit
`62e7446e686dfd9d901e82dee72b5731f6d70829`. Добавь единый allowlist языков `ru/en/zh`, отдельную команду
`language_set` и кнопку `RU / ENG / CH`. Применяй последнее языковое правило к обычному системному prompt и к
изолированному Codex prompt. Не передавай произвольный settings patch из HUD. Голос выбирай по языку и полу
персонажа; скачивай Piper только после явного клика, не обходи `local_only`. Не выдавай локальный тест за проверку
реального голоса или модели. Обнови exact-SHA overlay, добавь автономные unit и browser tests и план отката.

<a id="en"></a>
## EN

Integrate only into the authorized exact upstream. Keep one `ru/en/zh` allowlist and a dedicated `language_set`
command. Apply the same final language rule to regular chat and Codex prompts. Select Piper by language and persona
gender, download only after an explicit click, and never bypass `local_only`. Add offline unit/browser tests and
an exact-SHA overlay; do not claim live voice or inference validation.

<a id="zh"></a>
## 中文

仅在获得授权的精确上游代码中集成。使用统一的 `ru/en/zh` 白名单和独立的 `language_set` 命令，并将相同的
最终语言规则应用于普通聊天与 Codex 提示词。根据语言和角色性别选择 Piper；只有用户明确点击后才下载，
不得绕过 `local_only`。添加离线单元测试、浏览器测试和精确 SHA overlay，不得把离线测试描述为真实语音或推理验证。
