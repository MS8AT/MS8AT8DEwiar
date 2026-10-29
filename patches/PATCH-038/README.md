# PATCH-038 — Прозрачная смысловая обработка голосовой расшифровки

**[RU](#ru) · [ENG](#eng) · [中文](#中文)**

## RU

Независимый добавочный модуль для Dewiar **0.67.0**, commit
`80f1870074dbde643855b2b0ff1c40d7496dcb4c`. Он хранит исходную
расшифровку в `raw_transcript` всегда. Явно подключённый смысловой адаптер
может предложить `normalized_transcript` по контексту разговора, но этот
модуль не вызывает модель, сеть, микрофон и не сохраняет аудио.

При принятой смысловой правке пользователь видит исходный и нормализованный
варианты, а также сообщение: «Мне кажется, вы сказали: … Я могу ошибаться:
это предположение по смыслу сообщения». Имена, числа, адреса, секреты,
команды, платежи и удаление не исправляются автоматически: сохраняется raw и
запрашивается уточнение. Адаптер обязан явно пометить предложение безопасным
для автоприменения; без такой отметки, как и при низкой уверенности, действует
то же правило.

`src/` содержит только наш новый файл. [PROMPT.md](PROMPT.md) описывает
отдельное подключение к чистой копии upstream; публикация не означает
установку. Запуск: `python verify.py`, затем
`python tests/public_contract_test.py`. Проверены только автономные тесты;
реальные модель, микрофон, UI и установка — **NOT_RUN**.

## ENG

An additive module for Dewiar **0.67.0** at the exact commit above. It always
keeps `raw_transcript`. An explicitly wired semantic adapter may suggest a
context-aware `normalized_transcript`; this module itself performs no model,
network, microphone, or audio-storage operation. Meaning-based changes are
shown with a notice. Names, numbers, addresses, secrets, commands, payments,
and deletion requests require clarification and remain raw. Publication is not
installation; only standalone offline checks are verified.

## 中文

这是适用于上述精确 Dewiar 0.67.0 基线的独立附加模块。它始终保留
`raw_transcript`。只有明确接入的语义适配器才能按对话上下文提出
`normalized_transcript`；模块本身不调用模型、网络或麦克风，也不保存音频。
基于语义的修改会向用户说明。姓名、数字、地址、密钥、命令、支付和删除请求
不会自动改写，而是保留原文并请求澄清。发布不代表安装；仅验证离线独立测试。
