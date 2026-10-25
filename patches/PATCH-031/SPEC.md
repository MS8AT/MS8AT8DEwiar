# PATCH-031 / ANDROID-005 · RU / ENG / CH

## RU

Цель: выбранные ENG/CH продолжают работать после обновления Dewiar до 0.45.3 / Android 0.7.1.

На PC новый фильтр китайского текста учитывал лишь последнюю реплику пользователя. При CH и вопросе «Привет» он удалял весь китайский ответ, иногда вызывая повторный запрос. Теперь фильтр учитывает последнее явное языковое правило настроек. Русский режим и явно запрошенный перевод сохраняют прежнее поведение. Проверены Chat Completions, Responses с инструментами, Ollama и Anthropic через подменённый транспорт.

На Android новая проверка «распознано не по-русски» конфликтовала с выбранными ENG/CH: отклоняла фразу и могла переключить распознавание на сервер. Для ENG/CH русская проверка не запускается; обе native-подсказки языка используют выбранный язык. При смене языка счётчик несовпадений сбрасывается. Русская обработка ошибок сохранена.

ANDROID-004 имеет семь несовпадений SHA-256 после применения: Git перевёл CRLF в LF, а манифест описывал исходные Windows-байты. Содержимое после нормализации совпало во всех семи случаях. ANDROID-005 рассчитан по применяемым байтам и проверен свежей копией.

Интерфейс: прежняя кнопка RU / ENG / CH; новых настроек, служб и автоматических подключений нет. Кодекс, Human Memory, модели, аккаунты и установленная система этим пакетом не подключаются.

Приёмка: тест до исправления воспроизводит проблему; после исправления сохранены китайский ответ и распознанная ENG/CH-фраза, нет лишнего запроса/смены сервера; RU работает; все SHA-256 совпадают после применения; обратный патч восстанавливает проверенную базу.

## ENG

Target: preserve selected ENG/CH behavior on Dewiar 0.45.3 / Android 0.7.1. PC response filtering now respects the current explicit language setting instead of inspecting only the last user message. Android no longer treats intentionally selected English or Chinese recognition as a Russian recognition failure. Both native language hints use the selected language; changing language resets the mismatch counter. Russian behavior is retained.

The previous Android package had seven byte-hash mismatches caused solely by CRLF-to-LF patch normalization. This package hashes the bytes produced by patch application and verifies a fresh apply and rollback. No installation, accounts, model inference or publication. The existing RU / ENG / CH button is unchanged.

## CH

目标：在 Dewiar 0.45.3 / Android 0.7.1 中保留用户选择的英语和中文行为。电脑端的中文过滤器现在会考虑当前明确选择的回答语言，不再只检查最后一条用户消息。Android 不会把主动选择的英语或中文识别结果当作俄语识别故障，也不会因此切换到服务器。两个原生语言参数都使用所选语言；切换语言时重置故障计数。俄语行为保持不变。

旧 Android 补丁应用后有七个哈希不匹配，原因仅为 CRLF 转 LF。新包按补丁实际生成的字节计算哈希，并验证重新应用和回滚。没有安装、登录、模型调用或发布。继续使用现有 RU / ENG / CH 按钮。
