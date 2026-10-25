# PATCH-021 integration prompt

## RU

Интегрируй только Android control adapter в подготовленный тестовый runtime. Сначала прочитай README, INTEGRATION и manifest, выполни PATCH-010 inspect/test. Сверь контракт существующего runner, владельца диска и защищённую папку credentials. Работай в отдельном кандидате. Скопируй явный список собственных source-файлов; endpoint и SAN задай локально через configure.py. Не импортируй runtime.py в тестах. Не включай ключи, личный диск, APK и RouterOS deployment в публичный патч. ANDROID-001 применяй отдельно к записанной базе. Проверь API-отказы, положительный запрос, очередь, SSH UID/запрет forwarding, stop/start и сохранность данных; отдельно VPN off/on и сохранение управления. Не считай offline проверку доказательством live-установки. Codex/Human Memory Android, голосовые пакеты, чистая установка и физический телефон — отдельные задачи. Сначала покажи diff, тесты и фактические ограничения; новые публикации не выполняй автоматически.

## ENG

Integrate only this control adapter into a provisioned test runtime. Read README, INTEGRATION and manifest, then inspect/test with PATCH-010. Verify the existing runner contract, disk ownership and protected credentials directory. Use an isolated candidate and an explicit source allowlist. Generate local endpoint/SAN metadata with configure.py. Never import the VM runner in unit tests. Keep keys, private disks, APKs and router deployment out of the public patch. Apply ANDROID-001 separately to its recorded base. Validate API denial and success, queue results, Android SSH UID and forwarding rejection, graceful restart/persistence, VPN off/on and management continuity. Separate offline evidence from live acceptance. Android Codex/Human Memory, real voices, clean installation and physical devices remain separate work. Present the diff, evidence and limits before any new external publication.

## CH 中文

只把控制适配器集成到已经配置好的测试环境。先阅读 README、INTEGRATION、manifest，再用 PATCH-010 执行 inspect/test。检查现有运行程序契约、磁盘所有权和受保护凭据目录，在独立候选副本中操作。使用明确的源文件清单，通过 configure.py 生成本地端点和证书配置。单元测试不得导入虚拟机运行程序。不得公开密钥、私人磁盘、APK 或路由器部署文件。ANDROID-001 必须单独应用到指定基础版本。验证 API 拒绝与成功、队列、Android SSH 身份与禁止转发、正常重启和数据持久化，以及 VPN 开关后管理通道仍可用。离线测试不能替代实机验证。Android Codex/Human Memory、真实语音、新电脑安装和实体设备另行处理。先展示差异、测试和限制，不自动发布。
