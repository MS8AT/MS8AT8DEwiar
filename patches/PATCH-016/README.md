# PATCH-016 — Защищённые корни / Protected roots / 受保护目录

[RU](#ru) | [ENG](#eng) | [CH](#ch)

## RU

Одна ответственность: исключать корневые Pass, Private и Runtime из обзора и рабочей копии проекта.
Вход — относительный путь либо корень с лимитом списка. Выход — признак защищённого пути или список файлов.
Сеть, модель и запись отсутствуют. Недоступная ветка не прерывает os.walk.

Интеграция: core/codework.py использует protected() перед копированием untracked-файла и walk() для обзора.
Остальные ошибки доступа при копировании обрабатываются отдельно; незавершённая git-копия получает baseline только после подготовки.
Проверка пути не заменяет контроль секретов внутри разрешённого файла.

## ENG

One responsibility: exclude top-level Pass, Private and Runtime from project listing and work-copy preparation.
Inputs are a relative path or a root with a listing limit. Outputs are a protection flag or a file list.
No network, model or writes. Integrate protected() into untracked copying and walk() into codework listing;
handle other copy errors and incomplete Git preparation in the adapter.

## CH

单一职责：从项目列表和工作副本中排除根目录下的 Pass、Private 和 Runtime。
输入为相对路径或带数量限制的根目录，输出为保护标记或文件列表。
不访问网络、不调用模型、不写文件。适配器负责处理其他复制错误和未完成的 Git 准备过程。

## Проверка / Verification / 验证

Standalone: python verify.py; python tests/public_contract_test.py.
Integration: codework_protected_test.py and subscription_suite_test.py.
Rollback: restore the previous verified overlay. This block contains only the added helper, not the upstream application.
