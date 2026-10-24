# PATCH-013 — AI doctor for task context overflow

This is a separate MS8AT patch kit, not a redistribution of Dewiar. Integration requires an authorized exact
checkout of upstream Dewiar `0.40.1` at commit `616e70afada2ca3ebe95d894cb7d836592366aed`.

## RU — ТЗ

Dewiar — голосовой AI-помощник с персонажами, памятью и фоновыми задачами. Если история уже сокращена, но запрос
задачи всё равно не помещается в окно модели, PATCH-013 готовит один компактный повтор. Он оставляет цель, план,
блокнот и инструменты нужного типа: управление + код/веб для проекта либо управление + файлы/знания для обычной
задачи. Параметры инструментов не меняются.

Модуль — чистая подготовка данных. Он не вызывает модель и сеть, не читает пользовательские файлы, не меняет LM
Studio/Ollama и не выдаёт лечение за успех. Интегрирующий код обязан разрешить только один компактный повтор,
записать безопасные размеры до/после и остановить задачу, если контекст снова переполнен.

## EN — specification

After normal history compaction still ends in a confirmed context overflow, prepare one compact retry. Preserve the
goal, plan, notebook and task-type tools without changing parameter schemas. The standalone module has no model,
network, settings or file side effects. The adapter must allow one repair only and fail closed on a second overflow.

## 中文 — 规格

正常压缩历史后若仍确认上下文溢出，仅准备一次精简重试。保留目标、计划、任务笔记和该任务类型所需工具，
不得修改工具参数结构。独立模块不访问模型、网络、设置或用户文件；适配层只能修复一次，第二次溢出必须停止。

## Files and integration

- `src/core/task_doctor.py` — standalone pure core.
- `tests/public_contract_test.py` — zero-network contract checks.
- Integration targets: `core/tasks.py`, `tests/task_doctor_flow_test.py`, overlay manifest.

## Historical verification (Dewiar 0.40.0 / MS8AT build 15)

The following retained results describe build 15. Current Dewiar 0.40.1 acceptance is recorded separately.

- PASS: standalone contract and SHA verification.
- PASS: integrated synthetic flow: full request rejected, compact request accepted; second-overflow path stops.
- PASS: integrated suite: 231 Python + 49 Node.js checks; overlay build 15, 49 runtime files.
- PASS: installed build 15; local CLI/API/SLI/journal and feature declaration are available.
- LIVE PASS: the original failed task recovered with `14941→787` system characters and `74→22` tools. The task was
  stopped immediately after `doctor.last_result=recovered`, so completion of its project goal is not claimed.
- NOT_RUN: live Human Memory MCP and completion of the live task after treatment.

## Commands

```text
python patches/PATCH-010/src/tools/patch_block.py inspect PATCH-013
python patches/PATCH-010/src/tools/patch_block.py test PATCH-013
```
