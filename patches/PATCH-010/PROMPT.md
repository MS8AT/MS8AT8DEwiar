# PATCH-010 agent prompt · Промпт агента · Agent 提示词

[Русский](#ru) · [English](#en) · [中文](#zh)

<a id="ru"></a>
## RU

Работай только с выбранным `patches/PATCH-NNN`. Сначала выполни `inspect`, сформулируй одну ответственность блока и назови его вход, выход и побочные действия. Не меняй соседние блоки. Пиши небольшими функциями в стиле существующего Dewiar, без нового framework. Обнови автономный тест и SHA-256 manifest. Выполни `test`; `pack` — только если нужен архив. Публикация, установка, сеть, аккаунты и model calls требуют отдельного разрешения. В конце дай статусы `PASS`, `PARTIAL`, `NOT_RUN`.

<a id="en"></a>
## EN

Work only inside the selected `patches/PATCH-NNN`. Run `inspect` first, state its single responsibility, input, output, and side effects. Do not change adjacent blocks. Follow the existing small-function Dewiar style without adding a framework. Update the standalone test and SHA-256 manifest. Run `test`; use `pack` only when an archive is needed. Publishing, installation, network, accounts, and model calls require separate authority. Report `PASS`, `PARTIAL`, and `NOT_RUN`.

<a id="zh"></a>
## 中文

只处理选定的 `patches/PATCH-NNN`。先运行 `inspect`，说明模块的单一职责、输入、输出和副作用。不要修改相邻模块。沿用 Dewiar 的小函数风格，不增加新框架。更新独立测试和 SHA-256 清单，然后运行 `test`；仅在需要归档时运行 `pack`。发布、安装、网络、账户和模型调用都需要单独授权。最后报告 `PASS`、`PARTIAL` 和 `NOT_RUN`。
