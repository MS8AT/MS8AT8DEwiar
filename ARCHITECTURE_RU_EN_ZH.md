# Как развивать интеграции / Integration direction / 集成方向

[RU](#ru) | [ENG](#eng) | [CH](#ch)

Decision date: 2026-10-24. This is a development plan, not a deployment receipt.
Current compatibility: [Dewiar 0.40.1, MS8AT build 24](compatibility/dewiar-0.40.1.json).

## RU

**Выбранный путь: самостоятельные модули MS8AT, небольшой адаптер к Dewiar и
один существующий Manager для задач AI20.** Аккаунт MS8AT отвечает за публикацию;
Manager отвечает за исполнение. Это разные обязанности.

Сейчас проверены 15 patch-блоков, но полный слой интеграции затрагивает 55
runtime-файлов. Это ещё не универсальная система плагинов. Следующая цель —
постепенно уменьшать число мест, которые нужно переносить при обновлении.
Не требуется одновременно переписывать все работающие модули.

### Границы модулей

| Блок | Ответственность | Отдельная проверка |
|---|---|---|
| Модели | Выбор по назначению, контексту и проверенной работе инструментов | Синтетический каталог; явный выбор человека сохраняется |
| Codex | Собственные профили, согласия и квоты | Ошибка не запускает повтор или другой платный маршрут |
| Human Memory | Доступ к существующей памяти в рамках задачи | Без scope нет recall; данные и ключи не входят в патч |
| Задачи AI20 | Небольшой клиент существующего Manager | Отмена, устаревший маршрут, дубликат ответа, UNKNOWN |
| Наблюдение и AI-доктор | Статусы, журнал, диагностика и ограниченное восстановление | Зависание видно; завершение процесса не равно принятому результату |
| Обновление | Совместимость версии, установка и откат | Изменённый baseline запрещает запись; прерванная установка восстанавливается |

У каждого блока остаются исходники, ТЗ, prompt RU/ENG/CH, manifest, тесты и
версия. Адаптер содержит только подключение к UI/API Dewiar. Агент работает
над одним блоком в своей локальной копии; один интегратор собирает результат.

### Порядок следующих работ

1. **Паспорт совместимости и точки подключения.** Для каждого PATCH записать
   версию, проверенную базу, зависимости, конфликты, точки подключения,
   исходные/итоговые SHA и обязательные тесты. Неизвестная база, изменённый
   файл или отсутствующая зависимость запрещают запись. Составить карту 55
   файлов и постепенно отделять логику от вызовов Dewiar, начиная с одного
   адаптера. Критерий: отключение модуля не ломает обычные функции Dewiar;
   зависимые функции сообщают «недоступно» без скрытой замены модели.
2. **Добавить read-only связь с AI20.** Показать доступность Manager, свежесть
   heartbeat и реальные маршруты. Использовать существующий контракт Manager,
   не придумывать параллельную очередь. Пустой список — «недоступно», а не успех.
3. **Проверить одну локальную задачу.** Сначала ограниченный запрос без
   инструментов, затем отдельно tool-result сценарий. Автовыбор допускает
   модель только после проверки нужного контекста и инструментов. Чат и
   задачи могут использовать разные модели. Codex остаётся явным выбором.
4. **Замкнуть диагностику.** Один request ID связывает запуск, heartbeat,
   результат и журнал. При UNKNOWN сначала выясняется исход. AI-доктор
   применяет только заранее проверенные ограниченные способы восстановления;
   правка исходников проходит через отдельный патч, тесты и интеграцию.
5. **Завершить канал обновлений.** Новая версия сначала собирается и
   проверяется в отдельной копии. Готовый совместимый комплект проходит
   проверку происхождения, backup, установку при штатном выходе и post-check.
   Автоматическая установка включается после проверки подписей и репетиции
   прерывания/отката. До этого остаётся управляемый локальный установщик.

### Как проходит обновление

Новый официальный выпуск → кандидат в локальной копии → совместимые версии
модулей и адаптера → тесты и сравнение с чистым upstream → проверенный комплект
→ установка при закрытом приложении → сверка и возможность отката.

Для неизвестной версии автоматический перенос останавливается. Prompt помогает
агенту подготовить исправление, но установленное приложение не исполняет prompt
и не переписывает себя ответом модели. SHA-256 проверяет содержимое; доверие к
издателю требует отдельной проверки. Резервной копии без проверенного отката
недостаточно для автоматического обновления.

Публикуем от MS8AT самостоятельные модули, архивы, промпты и результаты тестов.
Автору Dewiar можно отдельно предлагать небольшие описания проблем; повторно
открывать закрытый большой PR для этого не требуется. В этом решении новые
issues не отправляются, runtime не меняется и модельные запросы не запускаются.

## ENG

**Chosen direction: independent MS8AT modules, a small Dewiar adapter, and the
existing Manager as the single AI20 task owner.** MS8AT is the publishing account;
Manager controls execution. The current 15 verified patch blocks still touch
55 runtime files, so this is not yet a universal plugin system. Reduce integration
points incrementally instead of rewriting the working application.

Keep six responsibilities separate: model selection; explicit Codex access;
scoped Human Memory; an AI20 Manager client; observation/limited recovery; and
versioned installation/rollback. Each block has source, a trilingual specification
and prompt, a manifest, tests and a version. One agent works on one block in a
local checkout; one integrator assembles the result.

Next: give each PATCH a compatibility record with version, exact base,
dependencies/conflicts, integration points, before/after hashes and required
tests. Refuse unknown bases or changed inputs before writing. Map existing
integration points and isolate one adapter; add read-only
Manager/route/heartbeat discovery; validate one bounded local task, then a
separate tool-result scenario; correlate diagnostics by request ID; finally
complete a trusted update channel. Explicit model choice wins. Unknown outcomes
require reconciliation. The AI doctor uses tested bounded recovery actions;
source repairs go through patches and tests.

Updates follow: official release → isolated candidate → compatible modules and
adapter → tests against upstream → verified package → stopped-app installation
→ post-check and rollback. Unknown versions stop automatic application. A prompt
guides development and is never executed by the installed application. Hashes
do not establish publisher trust; automatic installation also needs verified
signatures and interruption/rollback rehearsal. Automatic updates remain disabled
until those checks are complete.

Publish modules and evidence under MS8AT. Small upstream problem reports are
separate from the closed full PR. This document sends no issues, changes no
runtime and makes no model calls.

## CH

**选择方向：独立的 MS8AT 模块、轻量 Dewiar 适配器，以及现有 Manager 作为 AI20
任务的唯一执行负责人。** MS8AT 负责发布，Manager 负责执行。目前 15 个已验证补丁
仍涉及 55 个运行时文件，尚不是通用插件系统。应逐步减少集成点，保留现有工作成果。

分开六项职责：模型选择、明确启用的 Codex、限定范围的 Human Memory、AI20 Manager
客户端、状态观察与有限恢复、版本化安装和回滚。每块保留源码、三语规格与提示词、
manifest、测试及版本。代理各自在本地副本处理一个模块，由一个集成负责人汇总。

实施顺序：先为每个 PATCH 记录版本、精确基础版本、依赖/冲突、集成点、前后哈希和
必需测试；遇到未知基础版本或输入变化，在写入前拒绝。梳理集成点并隔离一个适配器；
只读显示 Manager、路由及心跳状态；
验证一个有限本地任务，再独立验证工具结果流程；用 request ID 关联日志；最后完成
可信更新渠道。用户明确选择优先，UNKNOWN 必须先核对实际结果。AI 医生仅使用已测试
且有边界的恢复方式；源码修复仍通过补丁、测试和集成。

更新流程：官方版本 → 隔离候选 → 兼容模块及适配器 → 对照上游测试 → 已验证安装内容
→ 关闭应用后安装 → 校验及回滚。未知版本停止自动应用。提示词用于开发，已安装应用
不执行提示词或按模型回答重写自身。哈希不能证明发布者身份；自动安装还需验证签名
并演练中断与回滚。在这些条件满足前，保持自动安装关闭。

以 MS8AT 发布模块和验证结果；上游的小范围问题反馈与已关闭的大型 PR 分开处理。
本文不发送 issue、不修改运行环境、不调用模型。
