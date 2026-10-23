# PATCH-015 integration prompt / 集成提示词

## RU

Интегрируй только чистый выбор модели по назначению. Вызывай `choose(models, purpose)` лишь когда профиль не содержит
явного `model`. Для обычного чата передавай `chat`, для фоновых задач — `tasks`. Раздели кэш по `(endpoint, purpose)`.
Не запускай capability-probe автоматически и не меняй настройки. Сначала запусти автономный тест блока.

## EN

Integrate only the pure purpose-aware model selector. Call `choose(models, purpose)` only when the profile has no
explicit `model`. Use `chat` for ordinary conversation and `tasks` for background tasks. Key the cache by
`(endpoint, purpose)`. Do not start a capability probe automatically and do not change settings.

## 中文

仅集成纯粹的按用途模型选择器。只有配置中没有明确 `model` 时才调用 `choose(models, purpose)`。普通聊天使用
`chat`，后台任务使用 `tasks`；缓存键必须包含 `(endpoint, purpose)`。不要自动运行能力探测，也不要修改设置。
