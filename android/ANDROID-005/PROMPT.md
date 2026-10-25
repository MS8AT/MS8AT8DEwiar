# ANDROID-005 — integration task

**[RU](#ru) · [ENG](#eng) · [CH](#ch)**

## RU

Внедри только «Android-конструктор: модели, задачи, память и языки» в отдельную копию Dewiar 0.45.3 (`32fcd918f21fc606efc0ed37870ac8edb9d1a290`).
Прочитай SPEC.md и manifest.json; проверь SHA-256. Сохрани стиль исходника: небольшие функции,
явные аргументы и plain Python/JavaScript/Java. Точки подключения: android/assets/www/app.js, android/assets/www/index.html, Bridge.java, Speech.java.
Сначала проверь отдельный модуль, затем затронутые контракты приложения. Не меняй соседние модули,
права пользователя, модель, лимиты, секреты или канал обновления. Не скачивай модели и не вызывай inference.
Промпты выбирай по провайдеру, возможностям и назначению, а не по догадке о названии модели.
Сохрани diff, команды проверки и PASS/PARTIAL/NOT_RUN; отдельным списком — то, что пока не подключено.
Проверяй обратное применение в копии. Не устанавливай и не публикуй автоматически.

## ENG

Integrate only "Android constructor: routing, tasks, memory and languages" into an isolated exact-base checkout. Read SPEC.md and the manifest;
verify hashes before execution. Use small plain functions and explicit dependencies in the upstream style.
Targets: android/assets/www/app.js, android/assets/www/index.html, Bridge.java, Speech.java. Test the standalone module, then affected app contracts.
Preserve explicit model choices, permissions, quotas, secrets and update trust. No model downloads or inference.
Return the diff, commands, rollback evidence and honest PASS/PARTIAL/NOT_RUN. Do not auto-install or publish.

## CH

仅在准确基础版本的独立副本中集成“Android 构建模块：模型、任务、记忆与语言”。先阅读 SPEC.md 和清单并验证哈希。
沿用原作者的小函数、显式依赖风格。连接位置：android/assets/www/app.js, android/assets/www/index.html, Bridge.java, Speech.java。
先测独立模块，再测应用接口；保留用户模型选择、权限、额度和更新信任链。
不得下载模型或调用推理。交付差异、测试命令、回滚证据及 PASS/PARTIAL/NOT_RUN；不得自动安装或发布。
