# PATCH-010 — simple independent blocks for Dewiar

[Русский](#ru) · [English](#en) · [中文](#zh)

Source-only developer tool. It does not modify the Dewiar runtime, call a model, use the network, install, or publish.

<a id="ru"></a>
## RU — коротко

Один блок — одна папка `PATCH-NNN`, одна ответственность и один автономный тест. Инструмент даёт четыре понятные команды:

```text
python patches/PATCH-010/src/tools/patch_block.py inspect PATCH-007
python patches/PATCH-010/src/tools/patch_block.py test PATCH-007
python patches/PATCH-010/src/tools/patch_block.py pack PATCH-007
python patches/PATCH-010/src/tools/patch_block.py new PATCH-011 task_router
```

- `inspect` проверяет состав и SHA-256, но не запускает код.
- `test` запускает только тесты выбранного блока.
- `pack` сначала тестирует, затем создаёт воспроизводимый ZIP.
- `new` создаёт маленькую заготовку, не перезаписывая существующий каталог.

В комплект входит skill `dewiar-block-worker`: агент меняет один блок, не трогает соседние, не публикует и не устанавливает без отдельного разрешения.

[Короткая карта функциональных блоков и параллельной работы агентов](ARCHITECTURE.md)

Стиль сохранён близким к Dewiar: стандартная библиотека, небольшие функции, явные словари, ранняя проверка входа, честные состояния `unknown/NOT_RUN`, автономные `unittest` или прямые assertions.

<a id="en"></a>
## EN — summary

One block is one `PATCH-NNN` folder, one responsibility, and one standalone test. `inspect` is static, `test` runs only the selected block, `pack` tests before creating a deterministic ZIP, and `new` creates a minimal non-overwriting scaffold. The bundled agent skill forbids silent cross-block edits and automatic publication.

<a id="zh"></a>
## 中文 — 摘要

一个模块对应一个 `PATCH-NNN` 目录、一个职责和一组独立测试。`inspect` 只做静态检查，`test` 只运行所选模块，`pack` 在测试后生成可重复的 ZIP，`new` 创建最小模板且不会覆盖现有目录。附带的 Agent Skill 禁止无声修改其他模块，也不会自动发布。

## Boundary

This tool organizes and verifies patch-kit files. Integrating a patch into upstream Dewiar remains a separate reviewed task and is subject to the upstream license.
