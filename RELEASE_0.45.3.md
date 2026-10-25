# Dewiar + MS8AT: комплект дополнений 0.45.3

**[RU](#ru) · [ENG](#eng) · [CH](#ch)**

## RU

Dewiar — голосовой AI-помощник с разговором, персонажами, памятью и задачами.
Этот репозиторий содержит отдельные дополнения MS8AT, промпты и проверки.
Текущий комплект ориентирован на **Dewiar 0.45.3 / Android 0.7.1**, commit `32fcd918f21fc606efc0ed37870ac8edb9d1a290`.
PC build36 и ANDROID-005 — наши кандидаты исходников, а не официальный установочный выпуск.

[Скачать полный публичный комплект](https://github.com/MS8AT/MS8AT8DEwiar/releases/tag/kit-0.45.3-pc36-android005) ·
[Промпт внедрения](prompts/DEWIAR_0453.md) · [Журнал и итог](WORK_LOG_2026-10-25.md) ·
[Точные проверки](validation/2026-10-25/CHECKS.json).

В наборе 12 блоков PATCH-020…031 и Android-конструктор. PATCH-024, 025 и 027 здесь являются
ТЗ интеграции; остальные содержат отдельные исходники и автономные проверки.
`module-files.patch` добавляет наши файлы. Подключение к существующим файлам приложения выполняется
по промпту в отдельной копии и проверяется заново. Это не установщик и не канал автообновления.
Полное дерево приложения, закрытый журнал и настройки пользователя не публикуются.

**Проверено сейчас:** 13 комплектов по хешам, 10 наборов автономного поведения, 10 патчей добавления
файлов с точной проверкой байтов и обратным применением. Ещё 3 ТЗ прошли только проверку целостности.
**Не проверено:** установка, новый APK, физический звук, настоящий ASR, аккаунты и inference.

| Блок / Block / 模块 | Назначение / Purpose / 用途 | Формат / Format / 格式 | Файлы / Files / 文件 |
|---|---|---|---|
| [PATCH-020](patches/PATCH-020/README.md) | Windows: честные результаты тестов | модули / modules / 模块 | [prompt](patches/PATCH-020/PROMPT.md) · [ZIP](dist/PATCH-020.zip) |
| [PATCH-021](patches/PATCH-021/README.md) | Управление Android | модули / modules / 模块 | [prompt](patches/PATCH-021/PROMPT.md) · [ZIP](dist/PATCH-021.zip) |
| [PATCH-022](patches/PATCH-022/README.md) | FIFO и экспериментальный выбор задач | модули / modules / 模块 | [prompt](patches/PATCH-022/PROMPT.md) · [ZIP](dist/PATCH-022.zip) |
| [PATCH-023](patches/PATCH-023/README.md) | OpenAI/Codex: промпты и Responses | модули / modules / 模块 | [prompt](patches/PATCH-023/PROMPT.md) · [ZIP](dist/PATCH-023.zip) |
| [PATCH-024](patches/PATCH-024/README.md) | Выбор голоса OpenAI TTS | ТЗ / specification / 规格 | [prompt](patches/PATCH-024/PROMPT.md) · [ZIP](dist/PATCH-024.zip) |
| [PATCH-025](patches/PATCH-025/README.md) | Индикатор слушания и распознавания | ТЗ / specification / 规格 | [prompt](patches/PATCH-025/PROMPT.md) · [ZIP](dist/PATCH-025.zip) |
| [PATCH-026](patches/PATCH-026/README.md) | Импорт WAV и проверка расшифровки | модули / modules / 模块 | [prompt](patches/PATCH-026/PROMPT.md) · [ZIP](dist/PATCH-026.zip) |
| [PATCH-027](patches/PATCH-027/README.md) | Дорожная карта аудиотракта | ТЗ / specification / 规格 | [prompt](patches/PATCH-027/PROMPT.md) · [ZIP](dist/PATCH-027.zip) |
| [PATCH-028](patches/PATCH-028/README.md) | Ограниченная очередь свежих кадров | модули / modules / 模块 | [prompt](patches/PATCH-028/PROMPT.md) · [ZIP](dist/PATCH-028.zip) |
| [PATCH-029](patches/PATCH-029/README.md) | Синтетическая волна и сравнение кодеков | модули / modules / 模块 | [prompt](patches/PATCH-029/PROMPT.md) · [ZIP](dist/PATCH-029.zip) |
| [PATCH-030](patches/PATCH-030/README.md) | Локальный звук и версии контекста | модули / modules / 模块 | [prompt](patches/PATCH-030/PROMPT.md) · [ZIP](dist/PATCH-030.zip) |
| [PATCH-031](patches/PATCH-031/README.md) | Сохранение выбранного языка RU/ENG/CH | модули / modules / 模块 | [prompt](patches/PATCH-031/PROMPT.md) · [ZIP](dist/PATCH-031.zip) |
| [ANDROID-005](android/ANDROID-005/README.md) | Android-конструктор: модели, задачи, память и языки | модули / modules / 模块 | [prompt](android/ANDROID-005/PROMPT.md) · [ZIP](dist/ANDROID-005.zip) |

### Как проверить один блок

Используйте Python 3.12; для JS — Node, для WAV/симуляции — NumPy, для PATCH-021 — зависимости его
`src/android_control/control-requirements.txt`. Проверки не устанавливают зависимости автоматически.

```text
python patches/PATCH-010/src/tools/patch_block.py inspect PATCH-030
python patches/PATCH-010/src/tools/patch_block.py test PATCH-030
python android/ANDROID-005/verify.py
python android/ANDROID-005/tests/public_contract_test.py
```

Сначала сохраните исходную копию. В новом checkout точной базы проверьте `git -c core.autocrlf=false apply --check <module-files.patch>`.
Применение и обратное применение используют ту же настройку переводов строк. Не накладывайте новые файлы
поверх изменённых старых модулей; сравните хеши и подготовьте отдельный diff. Права на upstream остаются у его автора — [NOTICE](NOTICE.md).

## ENG

Dewiar is a voice AI assistant with conversations, characters, memory and tasks. This is the independent MS8AT
source-module and prompt kit for Dewiar 0.45.3 / Android 0.7.1 at the commit above. PC build36 and ANDROID-005
are source candidates, not application installers. The table links each specification, prompt and download.

There are 12 new PATCH blocks plus the Android module bundle. PATCH-024/025/027 are specifications only.
Other blocks include authored standalone code. Additive patches do not wire existing app hooks; follow the prompt
in an isolated checkout. No complete upstream app source tree, private journal or account settings is redistributed.
Current checks: 13 manifests, 10 standalone suites, 10 byte-exact additive apply/reverse checks. Live devices,
APK build, installation, audio recognition, accounts and inference remain NOT_RUN. See [work log](WORK_LOG_2026-10-25.md).

## CH

Dewiar 是具有对话、角色、记忆和任务能力的语音 AI 助手。本仓库发布 MS8AT 独立模块、提示词与测试。
当前目标为准确版本 Dewiar 0.45.3 / Android 0.7.1。PC build36 和 ANDROID-005 是源码候选，不是安装包。
12 个新 PATCH 加一个 Android 模块包中，PATCH-024/025/027 仅含集成规格，其余含独立代码。
新增文件补丁不会自动接入现有应用接口；请在独立副本中按提示词集成并复测。
13 份清单、10 组独立行为测试及 10 组补丁字节校验与回滚通过。真实设备、APK 构建、安装、语音识别、账户和推理均未运行。
不公开完整上游应用源码、私有工作记录或账户配置。[工作日志](WORK_LOG_2026-10-25.md)。
