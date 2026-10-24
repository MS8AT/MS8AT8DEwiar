# Integration target: Dewiar 0.40.1 / MS8AT build 24

[RU](#ru) | [ENG](#eng) | [CH](#ch)

Official base: `dwr-git/dewiar-app@616e70afada2ca3ebe95d894cb7d836592366aed`.
Integration review: [PR #9](https://github.com/dwr-git/dewiar-app/pull/9).
Payload metadata: [compatibility](../compatibility/dewiar-0.40.1.json).
Next adapter: [AI20 plan / план / 计划](AI20_ADAPTER_PLAN.md).

## RU

Перенеси независимые модули MS8AT на указанную точную базу. Используй новую
локальную копию; сначала прочитай ТЗ и PROMPT нужного PATCH, затем проверь его
manifest и автономные тесты. Сохрани стиль Dewiar: небольшие прямые функции,
явные проверки, отдельные адаптеры, без нового framework.

1. Сохрани исправления OpenAI API, серверных 503/529, установщика, речи и UI
   из upstream. Повторы обычного API не должны распространяться на подписку.
2. PATCH-016: объедини обработку частичной non-Git копии из 0.40.1 с фильтром
   `Pass/Private/Runtime`; тест должен совместить отказ чтения и закрытые корни.
3. PATCH-015/018: не заменяй явный выбор модели; сохрани local-only и отсутствие
   скрытого перехода на Codex. PATCH-017: сохрани резерв на итог задачи.
4. PATCH-005/019: готовность Human Memory не включает scope задачи автоматически.
5. CLI Codex допускай только по проверенному SHA-256. Для build 24 проверены
   подпись OpenAI и протокол `0.164.0-alpha.11.1` без входа и inference.
6. Выполни overlay verification, subscription_suite, новые тесты 0.40.1,
   общий quick suite и синтаксис. Отдели ошибки среды от регрессий сравнением
   с точным upstream. Не называй частичную проверку полным PASS.
7. Подготовь backup и план всех файлов. Устанавливай только по поручению
   человека при закрытом Dewiar; после установки сравни SHA и проверь CLI/API.
   При ошибке используй прежний план и backup для rollback.

Не копируй аккаунты, токены, память, личные журналы и настройки в Git.
AI20 — отдельный следующий адаптер после проверки Manager→Router→Node и прав
на задачу. Текст модели не является полномочием. Автообновление установщиком
остаётся выключенным до доверенного подписанного канала.

## ENG

Integrate independent MS8AT blocks into the exact base above in a new local
checkout. Read each block's spec/prompt, inspect hashes, then run its offline
tests. Preserve Dewiar's small direct functions and separate adapters.

Keep upstream API/overload/installer/speech/UI fixes without extending generic
retries to subscriptions. Combine PATCH-016 protected-root filtering with 0.40.1
partial-copy handling and test both together. Preserve explicit model choices,
local-only continuation, final-request reservation and task-specific memory scope.
Build 24 pins signed Codex CLI `0.164.0-alpha.11.1`; verify its protocol without
login/inference. Run overlay, subscription, 0.40.1 regression, quick and syntax
checks; compare environmental failures against exact upstream.

Prepare a complete hash plan and backup. Install only under the user's instruction
while Dewiar is stopped; verify every file and CLI/API afterward. Roll back with
the same plan and backup. Exclude user data/secrets. AI20 remains a separate next
adapter pending Manager→Router→Node and authorization checks. Model text grants
no authority; automatic installers remain disabled pending a trusted signed channel.

## CH

在新的本地副本中，将各独立 MS8AT 模块集成到上述精确版本。先读模块规格和提示词、
检查哈希，再运行离线测试。保持 Dewiar 的简洁函数和独立适配器风格。

保留上游 API、繁忙重试、安装、语音及界面修复，但不把通用重试用于订阅。
把 PATCH-016 的目录保护与 0.40.1 的部分复制处理结合，并联合测试。
保留明确的模型选择、本地任务限制、收尾预算和任务专属记忆范围。
build 24 固定已签名的 Codex CLI `0.164.0-alpha.11.1`；不登录、不推理地验证协议。
运行 overlay、订阅、0.40.1 回归、quick 和语法检查，并用精确上游区分环境错误。

生成完整哈希计划和备份。仅按用户授权、关闭 Dewiar 后安装，再核验文件及 CLI/API；
使用相同计划和备份回滚。不得提交用户数据或秘密。AI20 作为后续独立适配器，先验证
Manager→Router→Node 及授权。模型文本不是授权；可信签名渠道就绪前保持自动安装关闭。
