# PATCH-020 — Windows: диагностика и воспроизводимые проверки

[RU](#ru) | [ENG](#eng) | [CH](#ch)

База: Dewiar 0.42.1, `469a10ce0fd01b7ef081e1f3a50d08b5a9adafbb`.
Предыдущий кандидат: build 25, `2f18b04342d1cc7d35d03e6ef4c2095957d77b13`.
Новый кандидат: build 26. Автоматическая установка выключена.

## RU

Проблема: при проверке на Windows недоступный сервер модели иногда даёт таймаут подключения вместо немедленного отказа. Пользователь получал только сообщение о долгом ответе. Замер собственной памяти Dewiar работал через Linux /proc и на Windows возвращал нули. Кроме того, тесты путали системный Bash с Git Bash, предполагали Linux и изображали лишние методы оконного API.

Что меняется:

1. ConnectTimeout объясняется как невозможность соединиться; ReadTimeout по-прежнему означает долгий ответ уже подключённой модели. Это не повтор запроса и не переключение на другой сервис.
2. Память процессов Windows измеряется через уже предусмотренный requirements-win psutil. Ядро и его потомки отделены от окон; завершившиеся и недоступные процессы не ломают снимок. Командные строки читаются только у Python-процессов для поиска окон.
3. В тестах платформу задаёт соответствующая подмена: GTK и Windows проверяются отдельно, Vosk проверяется и через реальный ASCII-путь, и через резервное копирование. PDF без браузера, GNOME и перетаскивание не зависят от реально установленных программ.
4. Девять Android web-тестов принимают явный DEWIAR_TEST_BASH и используют пути с прямыми слешами. Проверяется реальная сборка www и её страницы в headless Chromium; физический телефон этим не проверяется.
5. tools/check_windows_candidate.py запускает блоки в отдельных процессах и новых папках, сохраняет JSON и логи. Python-сеть разрешена только для loopback. PASS, FAIL и пропуски различаются; завершение с кодом 2 означает неполное покрытие, 1 — ошибку.

Пример отдельной проверки в PowerShell, из корня локального кандидата:

```powershell
python tools/check_windows_candidate.py --output C:/Temp/dewiar-check-001 --deps C:/path/to/test-dependencies --tests brain_hint1023_test.py memcap_test.py
```

Папка --output должна быть новой. Git Bash по умолчанию берётся из C:/Program Files/Git/bin; другой путь задаётся --bash. Зависимости — из отдельной тестовой папки; FastAPI, uvicorn и python-multipart нужны тесту сервера речи. Их установка не меняет Python рабочего Dewiar. Без --tests запускается список upstream quick.

Критерии: обязательные тесты overlay проходят; исторические ошибки либо воспроизведены и исправлены, либо явно обозначены как неподдерживаемые платформенные сценарии. Linux/systemd, физический Android, реальный вход и inference не объявляются проверенными на основании подмен.

Промпт для агента: изучи указанный diff и этот контракт, проверь SHA манифеста, затем запусти затронутые блоки через локальный runner. Не ослабляй assertions, чтобы получить зелёный статус. Не повторяй модельные запросы, не меняй профиль пользователя и не устанавливай кандидат автоматически. Сохрани фактические результаты и причины пропусков.

Откат разработки: отдельный build 25 сохранён; новый runtime не установлен. Для любого дальнейшего внедрения используется манифест с 56 файлами и точной upstream-базой.

## ENG

Build 26 distinguishes a connection timeout from a slow model response and measures the Dewiar process tree on Windows using its existing psutil dependency. Tests now explicitly model their intended OS and APIs, use an exact Git Bash path for Android web assembly, and isolate temporary state. The runner retains logs and distinguishes failure from unsupported or skipped checks. No live account, model inference, physical Android, installation or publication is implied. The previous build remains available for development rollback.

Agent task: preserve the upstream contracts, verify manifest hashes, run the affected blocks, and report real PASS/FAIL/SKIP outcomes. Do not weaken assertions or silently install the candidate.

## CH

Build 26 区分连接超时与模型响应缓慢，并使用 Windows 已有的 psutil 依赖测量 Dewiar 进程树内存。测试明确指定模拟的平台和接口，Android 网页构建使用 Git Bash 的完整路径，临时状态相互隔离。运行工具保存日志，并区分失败、跳过与不支持的平台检查。测试不代表实际账号登录、模型调用、实体 Android、安装或发布已经完成；旧版本保留用于开发回退。

代理任务：保留上游接口约定，验证清单哈希，执行受影响的模块测试，如实记录 PASS、FAIL、SKIP。不得为了通过而削弱断言，也不得自动安装候选版本。
