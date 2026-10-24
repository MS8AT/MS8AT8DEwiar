# PATCH-016 integration prompt

[RU](#ru) | [ENG](#eng) | [CH](#ch)

## RU

Добавь project_scope.py. В codework.py импортируй PROTECTED_ROOTS, protected и walk.
Исключай закрытые корни перед копированием untracked-файлов; не перечисляй их содержимое в логе.
При OSError другого untracked-файла продолжай копирование доступных исходников.
Проверь восстановление partial git worktree: не считать пустую метаинформацию завершённым baseline.
Для non-git копии исключай те же корни. Не меняй пользовательский проект и ACL.

Совместимость с Dewiar 0.40.1: сохрани upstream try/except shutil.Error вокруг non-git shutil.copytree,
но передавай ignore=ignore, объединяющий существующие IGNORE_DIRS с исключением корневых Pass, Private и Runtime без учёта регистра.
После ошибки копирования доступные уже скопированные файлы должны оставаться рабочими; защищённые корни не должны попадать в копию.
Проверь это на синтетическом сбое копирования: доступный исходник остаётся пригодным для работы, все три защищённых корня отсутствуют.

## ENG

Add project_scope.py and use it in the codework adapter. Skip protected roots before copying untracked files;
continue after unrelated inaccessible files. Recover partial worktree preparation before declaring a baseline.
Apply the same exclusions to non-Git copies. Preserve the user's source and ACLs.

Dewiar 0.40.1 compatibility: preserve the upstream try/except shutil.Error around non-Git shutil.copytree,
but pass ignore=ignore, combining the existing IGNORE_DIRS with case-insensitive exclusions for top-level Pass, Private and Runtime.
After a copy error, accessible files already copied must remain usable; protected roots must never enter the work copy.
Verify with a synthetic copy failure: the accessible source remains usable and all three protected roots are absent.

## CH

添加 project_scope.py 并接入 codework。复制未跟踪文件前排除受保护目录；
其他文件不可访问时继续处理可读源码。未完成的工作树必须完成 baseline 准备后才能使用。
非 Git 副本使用相同规则。保留用户源码和访问权限。

Dewiar 0.40.1 兼容要求：保留 upstream 在非 Git shutil.copytree 外层的 try/except shutil.Error，
但传入 ignore=ignore，将现有 IGNORE_DIRS 与不区分大小写的根目录 Pass、Private 和 Runtime 排除规则合并。
复制出错后，已经复制的可访问文件必须仍可使用；受保护目录绝不能进入工作副本。
使用模拟复制故障验证：可访问的源码仍可使用，三个受保护目录均不存在。
