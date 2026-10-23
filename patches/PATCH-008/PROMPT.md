# PATCH-008 integration prompt · Интеграционный промпт · 集成提示词

[Русский](#ru) · [English](#en) · [中文](#zh)

<a id="ru"></a>
## RU

Интегрируй только в авторизованный exact upstream. В parser tool-call после обычного строгого `json.loads` разреши
один узкий fallback: удвоить нечётные серии `\` только внутри quoted value, начинающегося с `[A-Za-z]:\`.
Никакие другие строки и поля не исправляй. На Windows после guard/подтверждения замени только ведущий token
`python3` или `python` на `sys.executable`; не выполняй shell до проверки. В PowerShell явно установи рабочую копию
через экранированный `Set-Location -LiteralPath`. Добавь тест неэкранированного пути, файла в outputs и успешного
вывода теста в журнале. Не использовать пользовательский проект или внешний inference.

<a id="en"></a>
## EN

Integrate into the authorized exact upstream only. After strict JSON decoding fails, allow one narrow fallback for
odd backslash runs inside a quoted drive-path value. Do not repair arbitrary JSON. After guard and confirmation,
map only a leading Python command to `sys.executable` and set the isolated worktree with LiteralPath. Verify with
offline task/tool-call regressions and no external inference.

<a id="zh"></a>
## 中文

仅在获得授权的精确上游中集成。严格 JSON 解码失败后，只允许修复带引号盘符路径中的奇数反斜杠序列，
不得修复任意 JSON。完成 guard 和人工确认后，仅将开头的 Python 命令映射到 `sys.executable`，并使用
LiteralPath 进入隔离工作树。通过离线任务和工具调用回归测试验证，不使用外部推理。
