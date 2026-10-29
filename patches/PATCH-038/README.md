# PATCH-038 — Прозрачная смысловая обработка расшифровки

## RU

Добавочный модуль для Dewiar **0.67.0**, commit
`80f1870074dbde643855b2b0ff1c40d7496dcb4c`. Контракт решения — revision 2.
`raw_transcript` всегда содержит точную исходную строку, включая пробелы и
переводы строк. `normalized_transcript` хранит отдельное предложение адаптера.

Любая изменённая фраза получает notice: «Мне кажется, вы сказали: … Я могу
ошибаться: это предположение по смыслу сообщения». Флаг модели
`meaning_inferred=false` не может скрыть факт правки.

Автоматически разрешены только регистр/пробелы при высокой уверенности,
явном safety-флаге и отсутствии известных защищённых токенов. Любая замена
слов требует уточнения: регулярное выражение не умеет надёжно находить
неизвестные имена. Числа, пути, URL, ID, версии, команды, секреты, платежи и
удаление не нормализуются автоматически. Самооценка модели не даёт
полномочий на действие.

При уточнении или ошибочном candidate возвращаются `can_dispatch=false` и
`effective_transcript=null`. Адаптер обязан проверить этот запрет перед
любым вызовом инструмента, созданием задачи или модельным запросом.
Исходная фраза сохраняется для человека, но не используется как запасная
команда. Пустой ввод также не отправляется. Обычный непустой raw без
адаптера остаётся прежним путём обработки, с отдельными gates приложения.

Модуль не вызывает модель, сеть, микрофон и не хранит аудио.
[PROMPT.md](PROMPT.md) описывает подключение. Проверка:
`python verify.py`, затем `python tests/public_contract_test.py`.
Реальные модель, микрофон, UI и установка — **NOT_RUN**.

## ENG

The additive module targets the exact Dewiar 0.67.0 commit above. Decision
contract revision 2 preserves the raw string exactly. Every changed proposal
has an uncertainty notice regardless of model flags. Only high-confidence
case/whitespace changes without protected tokens may dispatch. Any lexical
substitution requires clarification because regex cannot identify arbitrary
names. A blocked or malformed decision has `can_dispatch=false` and
`effective_transcript=null`; do not fall back to raw as a command.
No network, model, microphone or audio storage operation is performed.

## 中文

本模块适用于上述精确的 Dewiar 0.67.0 提交。决策协议 revision 2 完整保留
原始字符串。每次修改都显示不确定性提示。只允许不含受保护标记的高置信度
大小写/空格调整；词语替换须澄清，因为正则表达式不能识别任意姓名。
被阻止或格式无效的结果返回 `can_dispatch=false` 和
`effective_transcript=null`，不得退回原文执行命令。模块不调用网络、模型或麦克风。
