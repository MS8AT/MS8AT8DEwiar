# PATCH-019 integration prompt

## RU

Добавь stdio-адаптер и staging helper. Существующие Human Memory и Semantic Memory остаются владельцами данных.
Не включай их частный корпус или клиентские настройки в публикацию.
Запускай только проверенную локальную копию фасада с явными HOME/CONFIG/DB и read-only.
Сохраняй полный settings.mcp.servers при регистрации. Проверь handshake, tools/list, health и неизменность базы.
Доступный connector не включает scope задачи автоматически; recall требует точных session/object/keys/time.

## ENG

Add the stdio adapter and source-staging helper. Keep the existing memory facade and storage as data owners.
Publish no private corpus or client configuration. Run a hash-verified local facade with explicit paths and read-only settings.
Preserve the full mcp.servers mapping. Check handshake, tools, health and the database hash.
A ready connector does not opt a task into memory; recall requires an explicit scope.

## CH

添加 stdio 适配器和源码 staging 工具，现有记忆服务与存储继续拥有数据。
不要发布私有语料或客户端配置。仅运行哈希验证后的本地副本，使用明确路径及只读设置。
保留完整 mcp.servers 映射，检查握手、工具、health 和数据库哈希。
连接就绪不会自动启用任务记忆，recall 必须有明确范围。
