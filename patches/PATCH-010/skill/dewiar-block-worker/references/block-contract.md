# Block contract

One block is one folder: `patches/PATCH-NNN`.

Required files:

- `README.md` — purpose, boundary, usage, and honest verification status;
- `PROMPT.md` — narrow integration task for another agent;
- `manifest.json` — exact file list and SHA-256;
- `src/` — standalone implementation;
- `tests/` — standalone contract tests;
- `verify.py` — offline hash verification.

Commands from the repository root:

```text
python patches/PATCH-010/src/tools/patch_block.py inspect PATCH-007
python patches/PATCH-010/src/tools/patch_block.py test PATCH-007
python patches/PATCH-010/src/tools/patch_block.py pack PATCH-007
python patches/PATCH-010/src/tools/patch_block.py new PATCH-011 task_router
```

`inspect` never executes block code. `test` executes only `verify.py`, `tests/*_test.py`, and `tests/*.test.mjs` listed in the manifest. `pack` tests first and then creates a deterministic ZIP. None of the commands publishes or installs anything.

A block is complete when its hashes match, standalone tests pass, integration targets are named, and live checks not performed are marked `NOT_RUN`.
