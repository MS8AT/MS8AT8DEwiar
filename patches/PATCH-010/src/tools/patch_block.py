"""Простой жизненный цикл независимого PATCH-блока: new, inspect, test, pack.

Статическая проверка ничего не исполняет. test и pack запускают только явно
перечисленные в manifest файлы этого блока. Сеть и публикация не используются.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile

PATCH_ID = re.compile(r"PATCH-[0-9]{3}")
SLUG = re.compile(r"[a-z][a-z0-9_]{1,48}")
SHA256 = re.compile(r"[a-f0-9]{64}")
IGNORED_PARTS = {"__pycache__", ".DS_Store"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}


def fail(message):
    raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def project_root(start=None):
    start = Path(start or __file__).resolve()
    for parent in (start, *start.parents):
        if (parent / "patches").is_dir():
            return parent
    fail("не найден каталог patches")


def patch_dir(root, patch_id):
    if not isinstance(patch_id, str) or not PATCH_ID.fullmatch(patch_id):
        fail("идентификатор должен иметь вид PATCH-010")
    return Path(root).resolve() / "patches" / patch_id


def safe_relative(value):
    if not isinstance(value, str) or not value or "\\" in value:
        fail("небезопасный путь в manifest")
    path = Path(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        fail("небезопасный путь в manifest")
    return path


def load_manifest(folder):
    path = folder / "manifest.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail("не читается manifest.json: " + str(exc))
    if data.get("schema") != 1 or data.get("id") != folder.name:
        fail("manifest относится к другому блоку")
    files = data.get("files")
    if not isinstance(files, list) or not files:
        fail("manifest не содержит files")
    return data


def listed_files(folder, manifest):
    result = []
    seen = set()
    for item in manifest["files"]:
        if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
            fail("неверная запись files в manifest")
        relative = safe_relative(item["path"])
        folded = relative.as_posix().casefold()
        if folded in seen or not SHA256.fullmatch(item.get("sha256", "")):
            fail("повторный путь или неверный SHA-256")
        seen.add(folded)
        path = folder / relative
        if not path.is_file() or path.is_symlink():
            fail("нет обычного файла: " + relative.as_posix())
        actual = digest(path.read_bytes())
        if actual != item["sha256"]:
            fail("SHA-256 не совпадает: " + relative.as_posix())
        result.append(relative)
    return result


def source_files(folder):
    files = set()
    for path in folder.rglob("*"):
        relative = path.relative_to(folder)
        if any(part in IGNORED_PARTS for part in relative.parts) or path.suffix in IGNORED_SUFFIXES:
            continue
        if path.is_file():
            files.add(relative.as_posix())
    return files


def inspect(root, patch_id):
    folder = patch_dir(root, patch_id)
    if not folder.is_dir():
        fail("блок не найден: " + patch_id)
    manifest = load_manifest(folder)
    files = listed_files(folder, manifest)
    expected = {path.as_posix() for path in files} | {"manifest.json"}
    extra = source_files(folder) - expected
    missing = expected - source_files(folder)
    if extra or missing:
        fail("состав блока не совпадает с manifest: " + ", ".join(sorted(extra | missing)))
    return {"ok": True, "id": patch_id, "files": len(files), "code_executed": False}


def test_files(folder, manifest):
    listed = {safe_relative(item["path"]).as_posix() for item in manifest["files"]}
    tests = []
    if "verify.py" in listed:
        tests.append((sys.executable, "verify.py"))
    for name in sorted(listed):
        if name.startswith("tests/") and name.endswith("_test.py"):
            tests.append((sys.executable, name))
        elif name.startswith("tests/") and name.endswith(".test.mjs"):
            if not shutil.which("node"):
                fail("для JavaScript-теста не найден node")
            tests.append(("node", name))
    if not tests:
        fail("в блоке нет проверяемых тестов")
    return tests


def run_tests(root, patch_id):
    info = inspect(root, patch_id)
    folder = patch_dir(root, patch_id)
    manifest = load_manifest(folder)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    results = []
    for executable, relative in test_files(folder, manifest):
        run = subprocess.run([executable, relative], cwd=folder, env=env,
                             capture_output=True, text=True, timeout=120)
        if run.returncode:
            message = (run.stdout + "\n" + run.stderr).strip()
            fail(relative + " завершился с ошибкой\n" + message[-4000:])
        results.append(relative)
    return dict(info, tests=results, code_executed=True)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def verifier_source():
    return '''"""Проверка SHA-256 этого блока без сети и импортов Dewiar."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
for item in data["files"]:
    path = ROOT / item["path"]
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != item["sha256"]:
        raise SystemExit("REFUSED: SHA-256 не совпадает: " + item["path"])
print("PASS: " + data["id"] + "; model_calls=0; network=0")
'''


def new_block(root, patch_id, slug):
    if not SLUG.fullmatch(slug or ""):
        fail("slug: латиница в snake_case, например task_router")
    folder = patch_dir(root, patch_id)
    if folder.exists():
        fail("каталог уже существует: " + str(folder))
    title = slug.replace("_", " ")
    files = {
        "README.md": f"# {patch_id} — {title}\n\nОдна ответственность: TODO.\n\n## Проверка\n\n`python verify.py`\n`python tests/public_contract_test.py`\n",
        "PROMPT.md": f"# {patch_id} integration prompt\n\nИнтегрируй только блок `{slug}`. Не меняй соседние контуры. Сначала запусти автономный тест.\n",
        f"src/core/{slug}.py": f'''"""{title}: одна ответственность, без скрытых побочных действий."""\n\n\ndef status():\n    return {{"ok": True, "module": "{slug}"}}\n''',
        "tests/public_contract_test.py": f'''"""Автономный контракт {patch_id}: без сети и моделей."""\nfrom pathlib import Path\nimport sys\n\nsys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "core"))\nimport {slug}\n\nassert {slug}.status() == {{"ok": True, "module": "{slug}"}}\nprint("ALL OK: {patch_id}; model_calls=0; network=0")\n''',
        "verify.py": verifier_source(),
    }
    for relative, text in files.items():
        write(folder / relative, text)
    manifest = {
        "schema": 1,
        "id": patch_id,
        "title": {"ru": title, "en": title, "zh": title},
        "publication_mode": "separate_patch_kit_without_upstream_redistribution",
        "files": [{"path": name, "sha256": digest((folder / name).read_bytes())}
                  for name in sorted(files)],
        "integration_targets": [],
        "verification": {"public_contract_tests": "NOT_RUN", "live_model_calls": 0},
    }
    write(folder / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return {"ok": True, "id": patch_id, "created": len(files) + 1, "code_executed": False}


def pack(root, patch_id, output=None):
    info = run_tests(root, patch_id)
    folder = patch_dir(root, patch_id)
    manifest = load_manifest(folder)
    files = [Path("manifest.json"), *listed_files(folder, manifest)]
    output = Path(output) if output else Path(root) / "dist" / (patch_id + ".zip")
    if not output.is_absolute():
        output = Path(root) / output
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative in sorted(files, key=lambda item: item.as_posix()):
            item = zipfile.ZipInfo((Path(patch_id) / relative).as_posix(), (1980, 1, 1, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = 0o100644 << 16
            archive.writestr(item, (folder / relative).read_bytes())
    return dict(info, package=str(output), package_sha256=digest(output.read_bytes()))


def emit(result, as_json=False):
    if as_json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return
    details = "; ".join(f"{key}={value}" for key, value in result.items() if key != "ok")
    print("PASS: " + details)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=project_root())
    parser.add_argument("--json", action="store_true")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("inspect", "test", "pack"):
        command = commands.add_parser(name)
        command.add_argument("patch_id")
        if name == "pack":
            command.add_argument("--output")
    create = commands.add_parser("new")
    create.add_argument("patch_id")
    create.add_argument("slug")
    args = parser.parse_args(argv)
    try:
        if args.command == "new":
            result = new_block(args.root, args.patch_id, args.slug)
        elif args.command == "inspect":
            result = inspect(args.root, args.patch_id)
        elif args.command == "test":
            result = run_tests(args.root, args.patch_id)
        else:
            result = pack(args.root, args.patch_id, args.output)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print("REFUSED: " + str(exc))
        return 2
    emit(result, args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
