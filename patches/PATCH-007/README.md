# PATCH-007 — RU / ENG / CH response and voice mode

[Русский](#ru) · [English](#en) · [中文](#zh)

This is a separate MS8AT patch kit, not a redistribution of Dewiar. Run `python verify.py` first. Integration
targets the authorized exact upstream Dewiar `0.40.1` commit `616e70afada2ca3ebe95d894cb7d836592366aed`.
Publication does not install voices, call a model, or grant account access.

<a id="ru"></a>
## RU — ТЗ

Добавить в HUD кнопку `RU / ENG / CH`. Выбор сохраняется и задаёт язык ответа как обычному чату, так и отдельному
Codex-контуру. Английские локальные голоса Piper: `en_US-amy-medium` и `en_US-ryan-medium`; китайский:
`zh_CN-huayan-medium`. Голос загружается только после явного выбора. `local_only` блокирует загрузку, а текстовый
язык переключается сразу. Патч не переводит весь интерфейс и не меняет язык распознавания голосовых команд.

В Dewiar 0.40.1 CSS-адаптер `ui/hud.html` должен сохранять все кнопки вместе с переключателем языка видимыми
без горизонтального переполнения при ширине от 280 px. До 320 px нужны компактные отступы и ширины кнопок.
Приёмка: RU, ENG и CH на ширинах 280, 300 и 440 px; ни одна кнопка не скрывается ради размещения.

<a id="en"></a>
## EN — specification

Add a persisted `RU / ENG / CH` HUD control shared by the regular chat and isolated Codex routes. Use local Piper
voices `en_US-amy-medium` / `en_US-ryan-medium` for English and `zh_CN-huayan-medium` for Simplified Chinese.
Download a voice only after an explicit user selection and honor `local_only`. This is response-language and
speech-synthesis scope, not full UI localization or command-recognition localization.

For Dewiar 0.40.1, the `ui/hud.html` CSS adapter must keep every button and the language control visible without
horizontal overflow at widths from 280 px. Use compact spacing and button widths up to 320 px.
Acceptance: RU, ENG and CH at 280, 300 and 440 px; no button is hidden to make the row fit.

<a id="zh"></a>
## 中文 — 规格

在 HUD 中增加可保存的 `RU / ENG / CH` 控件，并同时应用于普通聊天路径和隔离的 Codex 路径。英语使用
`en_US-amy-medium` / `en_US-ryan-medium`，简体中文使用 `zh_CN-huayan-medium`。只有用户明确选择语言后
才下载语音，并且必须遵守 `local_only`。该补丁只控制回答语言和语音合成，不是完整界面或语音命令本地化。

对于 Dewiar 0.40.1，`ui/hud.html` 的 CSS 适配必须在宽度从 280 px 起保持所有按钮和语言切换控件可见，
且无水平溢出。宽度不超过 320 px 时使用紧凑间距和按钮宽度。
验收：在 280、300 和 440 px 下检查 RU、ENG、CH，不得通过隐藏按钮来适配。

## Files and acceptance

- Standalone module: `src/core/language_mode.py`.
- Integration prompt: `PROMPT.md`.
- Offline test: `tests/public_contract_test.py`.
- Dewiar targets: settings, normal chat system prompt, subscription context, voice selection, remote TTS, and HUD.
- Integrated acceptance: `language_mode_test.py`, `hud_language_test.py`, subscription suite, HUD regression, overlay SHA.
- Offline tests require `model_calls=0`; live voice download and inference remain NOT_RUN until separately authorized.
