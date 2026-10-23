# Проверки / Validation / 验证 — 2026-10-23

[RU](#ru) | [ENG](#eng) | [CH](#ch)

## RU

- PASS: PATCH-016…019 прошли inspect и автономные тесты; ZIP собраны из manifest.
- PASS: интеграционный subscription_suite — ALL OK, Python и 49 JS-проверок.
- PASS: Dewiar 0.40.0, overlay build 22, 55 runtime-файлов; полный установочный
  план проверил 313 файлов с резервной копией и повторной сверкой.
- PASS: installed CLI test/status/brains/sli; API различает локального исполнителя,
  прежний расход Codex и Human Memory connector/scope.
- LIVE PASS: Qwen 14B, Qwen 3.5 9B и GPT-OSS 20B прошли короткий двухходовый
  tool-result тест. Этот probe не является приёмкой долгих задач.
- LIVE FINDING: GPT-OSS в настоящей многошаговой задаче дал ошибку LM Studio
  peg-native, а текстовый формат инструментов дал пустой final. Для задач
  выбран Qwen 3.5 9B; Qwen 14B назначен коротким фоновым контурам.
- LIVE PASS: Human Memory stdio handshake/tools/health, SQLite integrity=ok,
  исходный snapshot не изменился по SHA. Ключи, база и цитаты не публикуются.
- NOT_RUN: новый платный Codex inference, пользовательский recall без точного
  scope, физический Android и полная ручная проверка всех UI-кнопок.
- PARTIAL: SLI содержит исторические сбои и не является availability/SLA или
  приёмкой новой сборки. Полный upstream quick-suite остаётся отдельной проверкой.

## ENG

All four standalone blocks and the focused integration suite passed. Build 22
was installed with a backup and a verified 313-file plan; its overlay contains
55 runtime files. CLI and API checks passed. Short tool probes passed for three
local models, but GPT-OSS later failed in a real multi-step task, so Qwen 3.5 9B
was selected for tasks and Qwen 14B for short background work.

Human Memory handshake and health passed; SQLite integrity and hash checks
confirmed the existing snapshot was unchanged. A task still needs an explicit
scope before recall. No new paid Codex inference or physical Android/UI-complete
acceptance was performed. Historical SLI is not release acceptance.

## CH

四个独立模块及重点集成测试通过。build 22 使用备份和 313 文件校验计划安装，
overlay 包含 55 个运行时文件。CLI/API 检查通过。三个本地模型通过短工具测试，
但 GPT-OSS 在真实多步任务中失败，因此任务选择 Qwen 3.5 9B，短后台工作选择 Qwen 14B。

Human Memory 握手和 health 通过，SQLite 完整性及哈希检查确认现有快照未改变。
recall 仍需要明确的任务范围。未新增付费 Codex 推理，未完成物理 Android 或全部界面按钮验收。
历史 SLI 不等于版本验收。
