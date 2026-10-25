# PATCH-023 — OpenAI/Codex промпты по назначению

Статус: ТЗ, профильный prompt pack и Responses API адаптеры PC/Android реализованы в локальном build 30 кандидате; не установлены.

Машиночитаемый пакет профилей: [openai_prompt_profiles.json](src/integrations/ms8at/openai_prompt_profiles.json).
База кандидата: Dewiar 0.45.3 / Android 0.7.1. Никакие реальные запросы не выполнялись.

## ТЗ (RU)

**Цель.** При выборе API Codex или официального OpenAI API подбирать короткий
промпт OpenAI по назначению: разговор, план, выполнение задачи, проверка кода,
сводка или память. Для локальных моделей и других провайдеров сохранять их
отдельный профиль. Общие ограничения безопасности задаются один раз; добавляется
только короткий слой выбранной задачи.

**Выбор профиля.** Источник истины — явный тип подключения и возможности текущего
сервера, а не название модели из сохранённого списка:

- `Codex` / app-server → `openai_codex`;
- официальный OpenAI API → `openai_api`;
- OpenAI-совместимый прокси или локальная модель → общий совместимый профиль,
  пока провайдер явно не подтвердил нужные возможности;
- явный выбор человека всегда важнее автовыбора.

Актуальный каталог моделей получают от выбранного сервиса. Не держать в коде
«вечный» список model ID. В качестве тестовых примеров для проверки этой редакции
документа использованы `gpt-6-astra`, `gpt-6.1-sol` и `gpt-6-luna` (проверены
25.10.2026); это не означает, что каждый аккаунт или шлюз предоставляет их.

**Транспорт и возможности.** Codex-подписка и OpenAI API — разные способы входа;
не копировать между ними токены или состояние аккаунта. Выбор профиля Codex
подключает OpenAI/Codex промпт-пакет, но сам по себе не включает инструменты.
Перед передачей tools приложение сверяет возможность текущего API и выбранной
модели. Для моделей GPT-6 с tools использовать Responses API после отдельной
реализации и проверки адаптера. Пока Android-клиент поддерживает только
Chat Completions для этого пути, не показывать GPT-6 как проверенный tool-runner;
не отправлять tools-поле неподдерживаемому endpoint и не имитировать успешное
выполнение.

**Экономия токенов.** Применять общий системный слой один раз, затем только один
профиль назначения. Не просить скрытые рассуждения или «думать вслух». Передавать
только цель, необходимый контекст, свежие факты и открытые пункты. Для простого
шага брать краткий режим; расширять ответ только по критерию задачи. Счётчик токенов
и reasoning effort настраиваются API по возможностям модели, а не текстом промпта.
При неизвестном размере контекста использовать текущий безопасный лимит приложения.

### Короткие RU-профили

- **Разговор:** «Ответь прямо на просьбу. Учитывай язык и стиль пользователя.
  Если нужна операция — вызови только доступный инструмент. Не описывай
  внутренние рассуждения. Если данных не хватает, задай один конкретный вопрос.»
- **План:** «Сформулируй проверяемый результат и 3–7 коротких шагов. Укажи
  зависимости и риск только если они меняют порядок работы. Не повторяй цель.»
- **Выполнение:** «Выполни один следующий шаг через доступные инструменты. После
  действия проверь результат, запиши только новое состояние и продолжай. Не
  заявляй об успехе без результата инструмента.»
- **Проверка кода:** «Сначала перечисли подтверждённые дефекты с важностью и
  точной привязкой к файлу. Для каждого укажи последствие. Не пересказывай код и
  не выдавай предположения за найденные ошибки.»
- **Память:** «Сохрани только устойчивый факт или явное предпочтение, нужное для
  будущей работы. Кратко, без секретов, полного текста переписки и временных
  подробностей.»
- **Сводка:** «Передай только изменения с прошлого резюме, решения, открытые
  вопросы и следующий шаг. Удали повторения; не теряй точные имена и значения.»

## Integration prompt (EN)

Add a compact OpenAI prompt router shared by the PC and Android integration
contracts. A selected Codex app-server profile selects `openai_codex`; the official
OpenAI API selects `openai_api`; other compatible providers keep their own profile
unless capabilities are explicitly verified. A user's explicit choice always wins.
Select one purpose layer (chat, plan, execute, code review, memory, or summary) and
reuse common safety rules once. Keep prompts concise, omit hidden chain-of-thought
requests, and include only necessary context and new facts. Do not hardcode a
permanent model catalog; query the selected service and check capabilities. Treat
Codex subscription and OpenAI API credentials as separate transports. Before using
tools, verify endpoint support: GPT-6 tool use requires a Responses API adapter and
tests; do not claim Android Chat Completions tool support until that adapter exists.
Respect explicit model selection and fail closed on unsupported capabilities.

- **Chat:** Answer the request directly in the user's language. Call only an
  available tool when an operation is requested. Ask one focused question only if
  required. Do not reveal internal reasoning.
- **Plan:** State a verifiable outcome and 3–7 short steps. Include dependencies
  only when they affect the order.
- **Execute:** Take the next permitted action, verify its result, record only new
  state, and continue. Never claim success without tool evidence.
- **Code review:** Lead with confirmed findings, severity, file location, and
  consequence. Keep assumptions separate from findings.
- **Memory:** Store only durable facts or explicit preferences needed later; omit
  secrets, full transcripts, and temporary details.
- **Summary:** Include only changes since the prior summary, decisions, open items,
  and next action. Remove repetition without losing exact names or values.

## 集成提示词 (ZH)

为 PC 和 Android 集成层添加精简的 OpenAI 提示词路由。用户选择 Codex
app-server 时使用 `openai_codex`；选择官方 OpenAI API 时使用 `openai_api`；
其他兼容服务保留自己的提示词配置，除非已明确验证其能力。用户手动选择
始终优先。每次只添加一个用途层：对话、计划、执行、代码审查、记忆或摘要；
通用安全规则只保留一份。提示词保持简短，不要求展示隐藏推理，只传入完成任务
所需的上下文和新事实。不要在代码中永久固定模型列表；从所选服务读取模型目录，
并检查能力。Codex 订阅和 OpenAI API 是不同的连接方式，凭据与登录状态不得互相
复制。使用工具前先确认 endpoint 支持：GPT-6 工具调用需要单独实现并测试
Responses API 适配器；在该适配器完成前，不得宣称 Android Chat Completions
支持 GPT-6 工具调用。明确的模型选择优先；能力不支持时安全停止。

- **对话：** 用用户的语言直接回答。只有用户要求操作且工具确实可用时才调用工具；
  必要时只问一个具体问题。不输出内部推理。
- **计划：** 给出可验证的结果和 3–7 个短步骤；只有影响顺序时才列出依赖。
- **执行：** 采取下一个获准的操作，验证结果，只记录新状态并继续；没有工具证据时
  不得声称成功。
- **代码审查：** 先列出已确认问题、严重度、文件位置和后果；将假设与发现分开。
- **记忆：** 只保存以后需要的长期事实或明确偏好；不保存秘密、完整对话或临时细节。
- **摘要：** 只包含上次摘要之后的变化、决定、未完成事项和下一步；去掉重复但保留
  精确名称和值。

## Runtime target и проверки

**Отдельные блоки PC и Android:**

1. Prompt router принимает `transport`, `provider`, проверенные `capabilities`,
   `purpose` и язык; возвращает профиль, короткий prompt и безопасный лимит вывода.
2. PC подключает router к Codex app-server и задачам OpenAI API, не меняя upstream
   системные инструкции и подтверждения действий.
3. Android использует тот же контракт и те же текстовые профили. Текущий
   Chat Completions путь остаётся для совместимых задач; поддержка GPT-6 tools
   включается только отдельным Responses API блоком.
4. Для каждого PATCH-001—PATCH-022 добавляется ссылка на этот общий профиль, а не
   копия длинного OpenAI промпта в каждом патче. Явные локальные правила конкретного
   патча остаются обязательными.

**Offline acceptance:** тесты выбора Codex/OpenAI/другого провайдера; каждый
purpose × RU/ENG/CH; явный выбор против auto; пустая модель и неизвестные capabilities;
неподдерживаемые tools fail closed; короткий профиль не содержит дубликатов общей
политики; лимит ответа выбран по назначению без превышения лимита провайдера; PC и
Android fixtures совпадают. Использовать mock API и счётчик токенов/символов; ноль
сетевых запросов и ноль model calls в unit-тестах. Отдельно проверить Responses API
с mock event stream до любых live-тестов.

**Откат:** выключить prompt router, вернуть прежний prompt builder для каждого
провайдера; сохранить профиль пользователя и журнал. Не переключать автоматически
на другой аккаунт, endpoint, модель или API при ошибке.

**Ограничение текущего кандидата:** PC/Android runtime-адаптеры и manifest включены;
mock-проверки выполнены. Связь выбора Codex app-server с `openai_codex` prompt profile
описана в JSON, но runtime prompt selector для Codex и live API-проверка ещё не выполнены.

## Официальные источники

- [OpenAI model catalog](https://developers.openai.com/api/docs/models)
- [GPT-6 guide and prompting guidance](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6.1-sol)
- [GPT-6.1 Sol capabilities and endpoint guidance](https://developers.openai.com/api/docs/models/gpt-6.1-sol)
