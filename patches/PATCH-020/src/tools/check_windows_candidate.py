"""Локальные проверки кандидата: временные данные, Git Bash, без сети к моделям.

--tests задаёт отдельные tests/*.py; без него проверяется список run_quick.sh.
Логи остаются в новой папке --output. Пропуск не считается успешной проверкой.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
PLATFORM = {
    "lmstudio_start1020_test.py": "Linux: проверка запуска lms и pkill",
    "linux_install1019_test.py": "Linux: установка пакета",
    "server_setup_test.py": "Linux: пользователь службы и pwd",
}


def classify(code, text):
    if code != 0 or "❌" in text:
        return "FAIL"
    if re.search(r"нет javac — пропуск|Windows — пропускаю|✅ пропуск:|живую проверку пропускаю", text):
        return "PARTIAL_SKIP" if "живую проверку" in text else "SKIP"
    return "PASS" if "✅" in text or "ALL OK" in text or re.search(r"^OK$", text, re.M) else "FAIL"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deps", type=Path, help="Отдельная папка тестовых Python-зависимостей")
    parser.add_argument("--bash", type=Path, default=Path("C:/Program Files/Git/bin/bash.exe"))
    parser.add_argument("--tests", nargs="+")
    args = parser.parse_args()
    if os.name != "nt":
        parser.error("Этот запускатель предназначен для Windows")
    names = args.tests or re.findall(r'^run .*?\$T/([A-Za-z0-9_]+\.py)"',
                                    (ROOT / "tests/run_quick.sh").read_text(encoding="utf-8"), re.M)
    if not names or len(set(names)) != len(names) or any(not re.fullmatch(r"[A-Za-z0-9_]+\.py", n)
            or not (ROOT / "tests" / n).is_file() for n in names):
        parser.error("Нужны существующие имена tests/*.py без повторов")
    if not args.bash.is_file():
        parser.error("Не найден Git Bash; задайте --bash")
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    guard = out / "guard"
    guard.mkdir()
    # Только Python-процессы теста; браузерные страницы должны подменять внешние API сами.
    (guard / "sitecustomize.py").write_text('''import socket
def allowed(address):
    if isinstance(address, tuple) and str(address[0]).lower() not in ('127.0.0.1', 'localhost', '::1'):
        raise OSError('OFFLINE_TEST: external network is blocked')
old_connect, old_connect_ex = socket.socket.connect, socket.socket.connect_ex
def connect(self, address):
    allowed(address)
    return old_connect(self, address)
def connect_ex(self, address):
    allowed(address)
    return old_connect_ex(self, address)
socket.socket.connect, socket.socket.connect_ex = connect, connect_ex
''', encoding="utf-8", newline="\n")
    bash_env = guard / "bash-env.sh"
    bash_env.write_text('python3() { "$DEWIAR_PY" "$@"; }\n', encoding="utf-8", newline="\n")
    paths = [str(guard)] + ([str(args.deps.resolve())] if args.deps else [])
    if os.environ.get("PYTHONPATH"):
        paths.append(os.environ["PYTHONPATH"])

    def run(name):
        if name in PLATFORM:
            return {"test": name, "status": "NOT_RUN_PLATFORM", "reason": PLATFORM[name]}
        folder = out / name.removesuffix(".py")
        folder.mkdir()
        env = dict(os.environ, PYTHONUTF8="1", PYTHONUNBUFFERED="1", PYTHONDONTWRITEBYTECODE="1",
                   PYTHONPATH=os.pathsep.join(paths), PATH=str(args.bash.parent) + os.pathsep + os.environ["PATH"],
                   BASH_ENV=bash_env.as_posix(), DEWIAR_TEST_BASH=args.bash.resolve().as_posix(),
                   DEWIAR_PY=Path(sys.executable).as_posix(), DEWIAR_ROOT=str(ROOT),
                   DEWIAR_CONFIG_DIR=str(folder / "config"), DEWIAR_STATE_DIR=str(folder / "state"),
                   DEWIAR_WORKSPACE_DIR=str(folder / "workspace"), DEWIAR_FAKE_RAM_GB="16", DEWIAR_FAKE_CORES="8",
                   NO_PROXY="127.0.0.1,localhost,::1", no_proxy="127.0.0.1,localhost,::1")
        log = folder / "output.log"
        start = time.monotonic()
        try:
            with log.open("wb") as stream:
                result = subprocess.run([sys.executable, "-B", str(ROOT / "tests" / name)], cwd=ROOT, env=env,
                                        stdout=stream, stderr=subprocess.STDOUT, timeout=300,
                                        creationflags=subprocess.CREATE_NO_WINDOW)
            status = classify(result.returncode, log.read_text(encoding="utf-8", errors="replace"))
            code = result.returncode
        except subprocess.TimeoutExpired:
            status, code = "TIMEOUT", None
        return {"test": name, "status": status, "exit": code,
                "seconds": round(time.monotonic() - start, 2), "log": str(log)}

    rows = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        for future in as_completed([pool.submit(run, name) for name in names]):
            row = future.result()
            rows.append(row)
            (out / "results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
            print(json.dumps({"test": row["test"], "status": row["status"]}, ensure_ascii=False), flush=True)
    return 1 if any(r["status"] in {"FAIL", "TIMEOUT"} for r in rows) else 2 if any(r["status"] != "PASS" for r in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
