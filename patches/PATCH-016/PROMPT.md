# PATCH-016 integration prompt

[RU](#ru) | [ENG](#eng) | [CH](#ch)

## RU

Добавь project_scope.py. В codework.py импортируй PROTECTED_ROOTS, protected и walk.
Исключай закрытые корни перед копированием untracked-файлов; не перечисляй их содержимое в логе.
При OSError другого untracked-файла продолжай копирование доступных исходников.
Проверь восстановление partial git worktree: не считать пустую метаинформацию завершённым baseline.
Для non-git копии исключай те же корни. Не меняй пользовательский проект и ACL.

## ENG

Add project_scope.py and use it in the codework adapter. Skip protected roots before copying untracked files;
continue after unrelated inaccessible files. Recover partial worktree preparation before declaring a baseline.
Apply the same exclusions to non-Git copies. Preserve the user's source and ACLs.

## CH

添加 project_scope.py 并接入 codework。复制未跟踪文件前排除受保护目录；
其他文件不可访问时继续处理可读源码。未完成的工作树必须完成 baseline 准备后才能使用。
非 Git 副本使用相同规则。保留用户源码和访问权限。
