[RU](README.md) · [ENG](README.en.md) · [CH 中文](README.zh.md)

# PATCH-021 — управление Android для Dewiar

Dewiar — приложение AI-помощника. Этот отдельный модуль добавляет управление подготовленным Android-стендом: HTTPS API, CLI, SSH, меню, автозапуск, размер окна, блокировку и WireGuard. Дополнение [ANDROID-001](../../android/ANDROID-005/README.md) добавляет переключатель языка разговора/распознавания/голоса RU/ENG/CH.

Это **исходники адаптера для существующей VM**, не установщик Android с нуля. APK, QEMU, Android payload, виртуальный диск, учётные данные и правила вашего роутера в блок не входят. Codex и Human Memory из Python-версии Dewiar в Android APK пока не перенесены.

## ТЗ: что входит

| Часть | Вход → результат | Проверка |
|---|---|---|
| HTTPS API | Bearer + JSON → статус, действия, до 100 записей журнала | очередь/API-контракт offline; работающий исходный стенд проверен отдельно |
| CLI | команда → JSON и exit code 0/1/3 | ошибки, таймауты и идентификаторы запросов |
| SSH | ключ → Android shell пользователя `android` | исходный стенд: UID 2000, отказ чужому ключу, forwarding запрещён |
| Очередь | атомарный файл запроса → результат по ID | FIFO, конкуренция, повреждённый JSON |
| Меню/Startup | фиксированное действие → проверка результата | Windows PS-команды; для другой установки требуется live-приёмка |
| WireGuard | локальный endpoint + шаблон → отдельный guard | проверка адреса/порта, атомарное обновление своих правил |
| Android-конструктор | RU/ENG/CH, задачи, память | отдельный актуальный модуль ANDROID-005 |

Файлы `control.py`, `control_cli.py`, `command_queue.py` работают независимо от Python Dewiar. `Start.ps1`/`Stop.ps1` подключаются к **уже существующему** `runtime.py`. Контракт описан в [INTEGRATION.md](INTEGRATION.md). Нельзя импортировать VM runner в unit-тесты.

## Проверка одного блока

Из корня patch-kit:

```text
python patches/PATCH-010/src/tools/patch_block.py inspect PATCH-021
python patches/PATCH-010/src/tools/patch_block.py test PATCH-021
```

Сначала `inspect`, затем `test`. Для control-тестов нужен Python 3.10+ и зависимости из `src/android_control/control-requirements.txt` в отдельном окружении. Их установка — отдельный сетевой шаг; тесты сами ничего не скачивают. Для stdlib-проверки конфигурации достаточно `python patches/PATCH-021/tests/deployment_test.py`.

## Локальная конфигурация

Изначально API/SSH слушают только `127.0.0.1`. Адреса сети и домен задаются в локальном `control-deployment.json`. Генератор создаёт **новый** каталог и не устанавливает файлы:

```text
python patches/PATCH-021/src/android_control/configure.py --output android-config-candidate --endpoint-ipv4 192.0.2.7 --endpoint-port 51820 --certificate-host localhost --certificate-host 127.0.0.1 --certificate-host android.example
```

`192.0.2.7` и `android.example` — примеры; замените фактическими значениями. `--bind-host 0.0.0.0` включают явно для внешнего доступа. Отдельно настраиваются firewall/NAT и сертификат. Генератор не подключается к MikroTik и не создаёт WireGuard-ключи. Существующий сертификат автоматически не заменяется: при смене SAN требуется управляемая перевыдача и обновление доверия клиента.

## Команды после интеграции

В каталоге подготовленного runtime:

```powershell
.\Cli.ps1 -Action status
.\Cli.ps1 -Action capabilities
.\Cli.ps1 -Action logs
.\Cli.ps1 -Action screen -Size 960x600
.\Cli.ps1 -Action lock -Enabled false
.\Cli.ps1 -Action autostart -Enabled true
.\Cli.ps1 -Action vpn-status
.\Cli.ps1 -Action vpn -Enabled true
.\SSH.ps1 -Command 'id -u'
```

HTTPS: `18769`; SSH: `2222`. Токен берётся из защищённого локального файла, не из аргументов команды. SSH использует закреплённый host key. Сеть Android через WireGuard и входящее управление на Windows — разные пути. При VPN down прямой выход Android остаётся закрыт, управление сохраняется.

## Приёмка и оставшееся

[WORK_LOG](../../WORK_LOG_2026-10-25.md) различает проверку переносимого блока и live-проверку исходного стенда. Блок имеет локальные конфигурационные изменения, поэтому старые live-тесты не доказывают работу этого кандидата на другом ПК.

Не выполнены: установка блока на чистом ПК, физический телефон, реальный выход/вход Windows, прослушивание голосовых пакетов, вход/запрос модели, полный restore диска. ANDROID-001 не переводит весь интерфейс. Открытая публикация этого блока не выполнялась.


Публикация 2026-10-25: только переносимый control adapter. Старый ANDROID-001 и локальные квитанции исключены; актуальный Android — `android/ANDROID-005`. Установка в этой поставке NOT_RUN.


### Additive patch / Только новые файлы / 仅新增文件

Where `module-files.patch` exists, first inspect it, then use `git -c core.autocrlf=false apply --check module-files.patch` in a separate source copy. Apply with the same `-c core.autocrlf=false` option to preserve the LF hashes. Reverse uses `git -c core.autocrlf=false apply --reverse module-files.patch`. Existing app hooks still require the integration prompt; this is not an automatic application upgrade.
