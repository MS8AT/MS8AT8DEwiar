"""Pure PATCH-008 helpers. They do not execute a command."""
from pathlib import Path
import re


def repair_drive_path_json(raw):
    r"""Make odd backslash runs even only in quoted C:\... values."""
    def repair(match):
        value = re.sub(r"\\+", lambda run: "\\" * (len(run.group(0)) + len(run.group(0)) % 2), match.group(1))
        return '"' + value + '"'
    return re.sub(r'"([A-Za-z]:\\[^"\r\n]*)"', repair, str(raw or ""))


def powershell_command(command, executable, worktree):
    """Normalize a leading Python token and return a LiteralPath PowerShell script."""
    command = str(command or "")
    executable = str(Path(executable))
    command = re.sub(r"^\s*(?:python3|python)(?=\s|$)", lambda _m: '& "' + executable + '"', command, flags=re.I)
    work = str(Path(worktree)).replace("'", "''")
    return ("[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
            f"Set-Location -LiteralPath '{work}'; " + command)
