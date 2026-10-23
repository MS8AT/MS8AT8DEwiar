# PATCH-014 integration prompt / 集成提示词

## RU

Интегрируй только модуль строгого восстановления Markdown-вызова. После ответа модели и только при отсутствии native
`tool_calls` передай текст и имена инструментов именно текущего запроса в `recover_one`. Если получен вызов, сохрани
только безопасный префикс и выполни вызов через существующий путь разрешений. Не исполняй второй вызов и не доверяй
напечатанным моделью результатам. Сначала запусти автономный тест блока, затем синтетический flow-тест адаптера.

## EN

Integrate only the strict Markdown tool-call recovery module. After a model response, and only when native `tool_calls`
are absent, pass the text and the exact tool names offered in that request to `recover_one`. If a call is returned,
keep only the safe prefix and route the call through the existing permission path. Never execute a second printed call
or trust a printed tool result. Run the standalone block test first, then a synthetic adapter flow test.

## 中文

仅集成严格的 Markdown 工具调用恢复模块。模型回复后，只有在没有原生 `tool_calls` 时，才把文本和该请求实际提供的
工具名传给 `recover_one`。如果返回调用，只保留安全前缀，并通过现有权限流程执行。不要执行第二个打印的调用，也不
要信任模型打印的工具结果。先运行独立模块测试，再运行适配器的合成流程测试。
