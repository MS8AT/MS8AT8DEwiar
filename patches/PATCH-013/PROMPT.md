# PATCH-013 integration prompt · Интеграционный промпт · 集成提示词

## RU

Работай только в легально доступной точной базе Dewiar 0.40.0 commit
`0e5917abf71e6d92a67b013c6fe5031f22a8af74`. Интегрируй чистый модуль `task_doctor.py` в цикл обычных фоновых
задач. Сначала сохрани штатное сокращение истории. Только после подтверждённого context overflow один раз собери
компактную подсказку и отфильтрованные инструменты, запиши в журнал число знаков и инструментов до/после и повтори
шаг. После успеха продолжай этот запуск в компактном режиме. После второй ошибки остановись с точным сообщением.
Не меняй настройки LM Studio/Ollama, права, параметры инструментов, профиль модели или соседние контуры.

Добавь автономные тесты: pure contract; полный синтетический поток «полный запрос отклонён → компактный принят»;
отрицательный поток «компактный тоже отклонён → одна запись лечения и остановка». Вызовы реальной модели, аккаунта,
сети и пользовательских файлов запрещены. Затем обнови overlay/build/SHA и прогони полный offline suite.

## EN

In the authorized exact upstream, integrate the pure `task_doctor.py` into ordinary background tasks. Keep normal
history compaction first. On confirmed context overflow, make exactly one compact retry, log only safe size counters,
and keep the current run compact after recovery. A second overflow must stop. Never alter model settings, permissions,
tool parameter schemas, profiles or adjacent contours. Cover success and fail-closed paths with zero-network tests.

## 中文

仅在已获授权的精确上游版本中，将纯函数模块 `task_doctor.py` 接入普通后台任务。先保留原有历史压缩；确认
上下文溢出后只进行一次精简重试，日志仅记录安全的大小统计，修复后本次运行保持精简模式。第二次溢出必须
停止。不得修改模型设置、权限、工具参数结构、配置或相邻模块，并用零网络测试覆盖成功与安全失败路径。
