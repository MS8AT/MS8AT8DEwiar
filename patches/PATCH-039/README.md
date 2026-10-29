# PATCH-039 — Dewiar ↔ WorkBook: карта, инструкции и типизированное управление

Мост использует существующий каталог `tools/workbook_modules.py` и штатный
`c_AI_TASK_MANAGER/cli.py`. Он запускается на закреплённом host и читает
существующий runtime этого host. Новый Manager, БД, очередь и сетевой сервер
не создаются. `SKILL.md` устанавливается как пользовательский навык Dewiar:
инструкции из MCP initialize клиент Dewiar не загружает.

Семь tools: статус, страница модулей, точный модуль, страница документа,
задачи, preview и apply pause/stop/resume. Документы и ответы ограничены с
учётом лимита Dewiar 8000 символов. Только входные документы из каталога
разрешены; обнаруженный путь не является правом на выполнение.

Apply требует отдельный файл разрешения с точными host, source_root,
task_id, revision, action, request_id, approval_id, approved=true и expires_at
(Unix UTC, не больше 15 минут). Файл создаёт root вне MCP в защищённом
root-owned каталоге, например `/var/lib/dewiar-workbook/approvals`; все
родительские каталоги также root-owned, без group/world write. Сам мост
работает непривилегированным пользователем. Это защищает разрешение даже
при наличии у модели файловых tools того же пользователя. Повтор использует
тот же request_id и штатную идемпотентность
Manager. Разрешение и revision повторно проверяются в той же транзакции
Manager, которая вызывает штатный `task_control`. При потере квитанции
ответ UNKNOWN требует сверки с тем же ID.
`stopping` не считается `stopped`; resume не делает dispatch.

Запуск: `python src/core/workbook_contour_mcp.py --source-root <Source>
--expected-host <HOST> --catalog-sha256 <SHA256> --manager-sha256 <SHA256>
--manager-core-sha256 <SHA256>
--approval-dir <private-local-directory>`. Хеши получают из текущего
проверенного исходника. Заменившиеся зависимости требуют повторной проверки.
Настройка MCP: command=проверенный Python, args=путь к скрипту и перечисленные
аргументы, enabled=true, trust=false. Для write-tool сохранять подтверждение
Dewiar. Live-команды для настоящих задач при тестах не выполняются.

EN: Native-host MCP bridge to the existing WorkBook catalog and Manager.
Bounded discovery/document pages, exact revision approvals, fixed commands,
and no general shell or dispatch. An installed custom skill teaches the AI
the workflow. Connection, model tool use and real task execution are separate
acceptance checks.

中文：通过固定主机上的 MCP 连接既有目录与任务管理器，分页读取模块和指令。
暂停、停止、继续必须具有绑定准确任务及修订的独立操作员授权；不提供任意命令或调度。

Run `python verify.py`, then `python tests/public_contract_test.py`.
The verification receipt records offline and live-read-only results separately.
