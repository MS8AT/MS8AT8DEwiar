# PATCH-018 integration prompt

## RU

Добавь local_task_mode.py и команду task_use_local. Выбор stopped/paused/failed/done задачи не запускает inference.
Сохрани прежнюю Codex-привязку и счётчики в previous_codex, архивируй старую историю при новом локальном контексте.
Используй task_profile() для основного цикла, перевода и самопроверки.
Режим изучения допускает только READ_TOOLS; проверяй allowlist и в диспетчере.
Для code_list/code_read используй безопасный read-only reader проекта без копирования всего дерева.
Не принимай finish без успешного чтения и при незакрытом плане. Самопроверка изучения не требует diff.
Добавь tasks.local_only в UI и запрет cloud fallback в brain_routes.
При обновлении llm.profiles передавай полный словарь профилей: Dewiar заменяет его целиком.
Проверь автономный блок, затем полный local_task_mode_test.py приложения.

## ENG

Wire task_use_local and its local profile into the task loop, translation and review.
Preserve Codex audit metadata and archive stale history on a fresh local context.
Enforce the study-mode READ_TOOLS allowlist at dispatch, protect source paths and block finish before successful reads or an unfinished plan.
Use a study-specific review prompt. Add tasks.local_only and reject cloud inheritance.
Always preserve the full llm.profiles mapping when saving settings. Run standalone and application flow tests.

## CH

接入 task_use_local，并在任务循环、翻译和复查中使用绑定的本地模型。
保留 Codex 审计信息，新本地上下文启动时归档旧历史。
在执行层验证只读研究工具白名单，保护源码路径；未成功读取或计划未完成时拒绝 finish。
复查研究任务时不要要求修改代码。添加 tasks.local_only，禁止继承云端模型。
保存设置时保留完整 llm.profiles 映射。运行独立测试和应用流程测试。
