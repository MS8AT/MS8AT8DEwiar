---
name: dewiar-block-worker
description: Create, change, test, and package one independent MS8AT8DEwiar PATCH block without modifying adjacent blocks or publishing automatically.
---

# Dewiar block worker

Work on exactly one `patches/PATCH-NNN` directory at a time. Preserve the author's small, direct Python/JavaScript style and avoid adding a framework when a pure function is enough.

## Workflow

1. Read `manifest.json`, `README.md`, and only the source and tests of the selected block.
2. Run `inspect` before executing code.
3. State the block's one responsibility, input, output, side effects, and integration targets.
4. Change only that block unless the user explicitly asks for integration work.
5. Update or add a standalone test. Unit tests must not call networks, accounts, models, or user files.
6. Update SHA-256 entries in `manifest.json`.
7. Run `test`; run `pack` only when a distributable ZIP is requested.
8. Report `PASS`, `PARTIAL`, and `NOT_RUN` honestly. Never publish, install, or push without separate authority.

Use the commands and file contract in [block-contract.md](references/block-contract.md). Before writing code, read [code-style.md](references/code-style.md).

If two blocks require a shared change, stop and describe the adapter boundary. Do not silently couple them.
