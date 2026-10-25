# PATCH-022 — сменные стратегии планирования задач

**Статус: EXPERIMENTAL_API.** В build28 добавлен `core/task_scheduler.py` и
ограниченный hook для выбора частей задачи. Обычный запуск остаётся FIFO.
`c_good` допускается только при явном контексте
`controlled_offline_integration`; это не настройка live-диспетчеризации и не
подтверждение общего выигрыша.

## RU — ТЗ

**Цель.** Дать Dewiar общий интерфейс выбора следующей задачи и позволить
сравнивать FIFO с `c_good`, не переписывая диспетчеризацию и не меняя права.

**Контракт.** Стратегия получает снимок кандидатов и список ID, уже допущенных Manager,
и безопасный контекст ограничений. Она возвращает `task_id`, `strategy_id`,
`reason_code` и необязательную оценку. Пустой список даёт `no_task`. Manager
перед фактическим запуском заново проверяет зависимости, write-scope, память и
разрешения. Планировщик сам не запускает задачи и модели, не меняет их статусы
и не выдаёт полномочия.

**Стратегии.** FIFO сохраняет очередь Manager. `c_good` выбирает допустимую
задачу с максимальным `S(i) = e(i) + r(i) + max(S(потомки))`; при равенстве
использует FIFO. Ошибка, тайм-аут, некорректный ID или оценка переводят выбор
на FIFO с журналируемой причиной. Никакого автоматического цикла повторов.

**Режимы.** FIFO по умолчанию; ручной выбор стратегии; ограниченный автовыбор
по классу нагрузки только после независимой проверки этого класса. Неизвестный
класс, неполные данные и неоднозначный результат используют FIFO.

**Сравнение.** На одинаковых задачах, ограничениях, исполнителях и seed
считать парное время на принятый результат, долю принятия, p95, повторы,
ожидание и нарушения ограничений. Отдельно показывать независимые задачи,
длинные цепочки, смешанный DAG, медленных исполнителей, частые сбои и дорогой
review. Синтетический FIFO-stress holdout не объединять с общей серией.

**Условия допуска `c_good` для одного класса:** не менее 30 независимых seed,
средний эффект не ниже 15%, нижняя граница 95% интервала выше нуля, нижняя
граница разницы принятия не хуже −2 п.п., отношение p95 не выше 1.10, ноль
нарушений инвариантов и подтверждение на отдельном holdout. Иначе оставить
стратегию экспериментальной; FIFO сохранить общим значением по умолчанию.

**Журнал.** Записывать ID задачи, стратегию и версию, код причины, безопасные
счётчики/оценку, исход и факт fallback. Не записывать ключи, токены, полный
текст проекта или секретные ошибки.

**Проверки.** Контрактные тесты обеих стратегий; FIFO порядок и tie-break;
фильтрация недопущенных задач; invalid-ID/timeout/error fallback; парный
benchmark каждого workload; проверка логов на секреты; интеграционный тест
Manager с mock исполнителем и нулём model calls. Сначала только offline.
В текущем коде hook вызывается с FIFO; ручной c_good доступен только в
контролируемом offline-вызове теста. Подключение к live Manager и рабочим
задачам — отдельный этап.

**Откат.** Удалить регистрацию стратегии и настройки, вернуть FIFO как единственный
путь; сохранить задачу и журналы. Не менять Manager разрешений или статусы задач.

## ENG — specification

Build status: `core/task_scheduler.py` is implemented and has a bounded Manager
hook. FIFO remains the live default. c_good is accepted only in an explicit
`controlled_offline_integration` context; general live-task promotion is not
supported by the current benchmark results.

Add a common interface for selecting the next Manager-approved task. FIFO is
the default; c_good is an optional strategy using `S(i) = e(i) + r(i) + max(child S)`
with FIFO tie-break. The strategy returns a task ID, strategy/version, reason
code and optional score; Manager revalidates every permission and resource gate
before launch. A strategy cannot launch work, alter task status or grant access.

Compare paired runs with identical workloads, constraints, workers and seeds.
Show each workload separately. Keep the controlled FIFO-stress holdout separate.
Enable c_good for a workload only after at least 30 seeds, at least 15% mean
improvement, a positive lower 95% confidence bound, acceptance difference no
worse than -2 percentage points, p95 ratio at most 1.10, zero invariant
violations and an independent holdout. Otherwise retain it as experimental.
Errors and timeouts fall back once to FIFO and are logged without secrets.
Offline tests come first; live Manager integration is a separate gate.

## 中文 — 规格

实现状态：已加入 `core/task_scheduler.py` 和受限的 Manager 接口。实际任务仍
默认使用 FIFO；只有显式指定 `controlled_offline_integration` 才允许 c_good。
当前基准结果不支持将其推广到普通实时任务。

为任务选择增加统一接口。FIFO 为默认策略；c_good 使用
`S(i) = e(i) + r(i) + max(子任务 S)`，同分时按 FIFO。策略只返回任务 ID、
策略版本、原因和可选分数；Manager 启动前仍重新检查依赖、写入范围、内存
和权限。策略不得启动任务、修改状态或授予权限。

在相同任务、限制、执行者和随机种子上配对比较，并分别报告每类负载。
受控 FIFO 压力测试不得与常规结果混合。只有当至少 30 个独立 seed、平均
提升达到 15%、95% 区间下限大于零、接受率差异不低于 -2 个百分点、p95
比例不高于 1.10、没有不变量违规且独立 holdout 通过时，才可在该负载启用
c_good；否则继续实验。错误和超时仅回退一次到 FIFO，并安全记录。先做离线
测试；连接 live Manager 是独立验收阶段。
