---
name: mypy-cache-fix
description: >-
  Diagnose and fix mypy pre-commit failures in this repo. Use when: mypy hook
  crashes with INTERNAL ERROR, mypy exits with code 2, mypy fails silently, or
  you suspect mypy cache corruption after seeing sqlite3 DatabaseError.
---

# Fix mypy Cache Corruption

When the mypy pre-commit hook exits with an INTERNAL ERROR, the most common cause
is a corrupted `.mypy_cache` SQLite database.

## Diagnose

Run mypy directly with `--show-traceback` to see the real error:

```bash
script/run-in-env.sh mypy --ignore-missing-imports --show-traceback supervisor
```

### Interpret the traceback

- **`sqlite3.DatabaseError: database disk image is malformed`** — cache corruption.
  Proceed to the fix below.
- **Any other error** — unrelated mypy issue. Read the traceback and either debug
  the type error or report it to the team.

## Fix (cache corruption only)

```bash
rm -rf .mypy_cache
```

Then re-run pre-commit to confirm the hook passes:

```bash
pre-commit run --files <changed files>
```
