# Проверки / Validation / 验证 — 2026-10-23

[RU](#ru) | [ENG](#eng) | [CH](#ch)

## RU

- PASS: PATCH-016…019 прошли inspect и автономные тесты; ZIP собраны из manifest.
- PASS: интеграционный subscription_suite — ALL OK, Python и 49 JS-проверок.
- PASS: Dewiar 0.40.0, overlay build 23, 55 runtime-файлов; полный установочный
  план проверил 313 файлов с резервной копией и повторной сверкой.
- PASS: installed CLI test/status/brains/sli; API различает локального исполнителя,
  прежний расход Codex и Human Memory connector/scope.
- LIVE PASS: Qwen 14B, Qwen 3.5 9B и GPT-OSS 20B прошли короткий двухходовый
  tool-result тест. Этот probe не является приёмкой долгих задач.
- LIVE FINDING: GPT-OSS в настоящей многошаговой задаче дал ошибку LM Studio
  peg-native, а текстовый формат инструментов дал пустой final. Для задач
  выбран Qwen 14B 8K с ограниченными чтением/историей; Qwen 3.5 9B 32K
  оставлен для длинного контекста чата. Новые веса не скачивались.
- LIVE PASS: реальная локальная задача прочитала три источника, закрыла план
  4/4, доработала обзор после самопроверки и сохранила итог. Это ограниченное
  изучение фрагментов, не полный аудит и не гарантия точности каждого вывода.
- LIVE PASS: Human Memory stdio handshake/tools/health, SQLite integrity=ok,
  исходный snapshot не изменился по SHA. Ключи, база и цитаты не публикуются.
- NOT_RUN: новый платный Codex inference, пользовательский recall без точного
  scope, физический Android и полная ручная проверка всех UI-кнопок.
- PARTIAL: SLI содержит исторические сбои и не является availability/SLA или
  приёмкой новой сборки. Полный upstream quick-suite остаётся отдельной проверкой.
- PARTIAL: в рабочем UI остались предупреждения доступа Windows к сейфу
  (`close_state`) и сохранения PDF (`ws_export`); их исправление не заявляется.

## ENG

All four standalone blocks and the focused integration suite passed. Build 23
was installed with a backup and a verified 313-file plan; its overlay contains
55 runtime files. CLI and API checks passed. Short tool probes passed for three
local models, but GPT-OSS later failed in a real multi-step task. Qwen 14B 8K
is selected for tasks and short background work with bounded reads/history;
Qwen 3.5 9B 32K is used for longer chat context. No new weights were downloaded.
A real task read three sources, completed its four-item plan and saved an
initial report after review feedback. This is not a full project audit or a
guarantee of every model claim. Windows vault access and PDF export warnings
remain separate unresolved UI limitations.

Human Memory handshake and health passed; SQLite integrity and hash checks
confirmed the existing snapshot was unchanged. A task still needs an explicit
scope before recall. No new paid Codex inference or physical Android/UI-complete
acceptance was performed. Historical SLI is not release acceptance.

## CH

四个独立模块及重点集成测试通过。build 23 使用备份和 313 文件校验计划安装，
overlay 包含 55 个运行时文件。CLI/API 检查通过。三个本地模型通过短工具测试，
但 GPT-OSS 在真实多步任务中失败。任务及短后台工作选择 Qwen 14B 8K，限制读取片段与历史长度；
较长聊天上下文选择 Qwen 3.5 9B 32K，未下载新权重。真实任务读取三个来源、完成四项计划，
按复查反馈改进后保存初步报告。这不是完整项目审计，也不保证模型每项结论准确。
Windows 保险库访问和 PDF 导出警告仍是独立的未解决界面限制。

Human Memory 握手和 health 通过，SQLite 完整性及哈希检查确认现有快照未改变。
recall 仍需要明确的任务范围。未新增付费 Codex 推理，未完成物理 Android 或全部界面按钮验收。
历史 SLI 不等于版本验收。
