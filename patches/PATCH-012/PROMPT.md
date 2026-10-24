# PATCH-012 integration prompt · Интеграционный промпт · 集成提示词

## RU

Работай только в легально доступной точной базе Dewiar 0.40.1 commit
`616e70afada2ca3ebe95d894cb7d836592366aed`. В `probe_tools_bg` сразу после чтения активного профиля вернись,
если `kind == "chatgpt_subscription"`. Не создавай поток, не вызывай `probe_tools`, `/models`, inference, login,
задачу или автоматическое переключение профиля. Обычные API/локальные профили должны сохранить прежнее поведение.
Добавь автономный тест нулевых побочных эффектов и включи его в subscription suite. Обнови manifest/overlay build,
прогони offline suite, установи только после штатного выхода и резервной копии. После перезапуска явно запроси список
моделей без генерации и проверь только новый хвост журнала.

## EN

In authorized exact upstream Dewiar 0.40.1 commit `616e70afada2ca3ebe95d894cb7d836592366aed`,
add an early return in `probe_tools_bg` for `kind=chatgpt_subscription`. Do not
start the probe thread or call tools, model inference, login, tasks or profile switching. Preserve generic probing for
ordinary profiles. Add a zero-side-effect unit test, run the offline suite, install only after verified backup, then
validate explicit model listing and the fresh log without inference.

## 中文

仅在已获授权的 Dewiar 0.40.1 精确上游提交 `616e70afada2ca3ebe95d894cb7d836592366aed` 中集成。在 `probe_tools_bg` 读取活动配置后，如果
`kind=chatgpt_subscription`，立即返回。不得创建探测线程，也不得调用 tools、模型推理、登录、任务或自动切换。
普通配置必须保持原行为。添加零副作用单元测试；离线测试、备份和正常退出完成后再安装，并以显式模型列表
请求和新增日志进行验证，不发送推理。
