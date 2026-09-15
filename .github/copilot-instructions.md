# GitHub Copilot & Claude Code Instructions

This repository contains the Home Assistant Supervisor, a Python 3 based container orchestration and management system for Home Assistant. It manages the Home Assistant Core, app and plugin containers through the Docker daemon and integrates with the host OS through D-Bus.

## Pull Requests

- When opening a pull request, always use the description format from `.github/PULL_REQUEST_TEMPLATE.md`.

## Development Commands

- Install development dependencies with `pip install -r requirements.txt -r requirements_tests.txt`.
- `.vscode/tasks.json` contains useful commands used for development.
- Lint and format with `ruff check --fix supervisor tests`, `ruff format supervisor tests` and `pylint supervisor`.
- Type check with `mypy --ignore-missing-imports supervisor/`.
- After finishing a code session, run `pre-commit run --all-files` to check for linting and formatting issues.

## Python Syntax Notes

- Supervisor officially supports Python 3.14 as its minimum version. Do not flag syntax or features that require Python 3.14 as issues, and do not suggest workarounds for older Python versions.
- Python 3.14 explicitly allows `except TypeA, TypeB:` without parentheses. Never flag this as an issue.
- Python 3.14 evaluates annotations lazily (PEP 649). Forward references in annotations do not need to be quoted — annotations can reference names defined later in the module without quoting them or using `from __future__ import annotations`. Do not flag unquoted forward references in annotations as issues.

## Testing

- Use `pytest -qsx tests/` to run tests, narrowing the path as needed. Tests mirror the `supervisor/` module layout.
- Write plain `test_` functions with pytest fixtures. Do not add `Test*` classes, they are considered legacy style in this project.
- Mock external dependencies (Docker, D-Bus, network calls). The fixtures in `tests/conftest.py` provide a mocked `CoreSys`.
- Ensure all test function parameters have type annotations.
- Prefer `@pytest.mark.usefixtures` over arguments, if the argument is not going to be used.
- Avoid using conditions/branching in tests. Instead, either split tests or adjust the test parametrization to cover all cases without branching.
- If multiple tests share most of their code, use `pytest.mark.parametrize` to merge them into a single parameterized test instead of duplicating the body. Use `pytest.param` with an `id` parameter to name the test cases clearly.

## Good practices

- Apps are the containerized applications installed from stores. "Add-on" is the legacy term for the same thing. Use "app" in new code, comments and docs, and keep "addon" only where an existing API field, config key or class name still uses it.
- Use relative imports within the `supervisor/` package (e.g. `from ..docker.manager import ExecReturn`), never absolute `from supervisor...` imports.
- Use constants from `supervisor/const.py` instead of hardcoding values. Module-specific constants go in a per-module `const.py` (e.g. `supervisor/store/const.py`).
- Classes that need system access inherit from `CoreSysAttributes` and use the `self.sys_*` properties (`sys_docker`, `sys_homeassistant`, `sys_host`, `sys_dbus`, `sys_bus`, `sys_config`, ...). Access Docker through `self.sys_docker`, never through the Docker SDK directly.
- All I/O must be async. Run blocking calls through `self.sys_run_in_executor()`. Put sync setup in `__init__` and async initialization in `post_init()` or `load()`.
- Raise the exceptions defined in `supervisor/exceptions.py` and chain them with `from`. Wrap D-Bus and Docker exceptions in Supervisor-specific ones.
- API handlers use the `@api_process` decorator and validate input with `api_validate()` from `supervisor/api/utils.py`. The decorator converts `APIError` and `HassioError` into responses, so do not add manual error handling in handlers.
- When catching exceptions, try-clauses should be as small as possible, i.e. avoid wrapping large blocks of code in a try-clause, and avoid catching exceptions from functions that are not expected to raise them.
- Keep comments concise. Prefer one short line stating the non-obvious constraint, or no comment at all.
- Do not add comments that just restate the code on the following line(s). Comments should only explain why (non-obvious constraints, surprising behavior, or workarounds), never what. Never add comments that justify a change by referencing what the code looked like before.
- Use American English for all code, comments, and documentation.

## AI policy

This project follows the [Open Home Foundation AI Policy](../AI_POLICY.md). Autonomous contributions are not accepted: a human must review, understand, and be able to explain every change before it is submitted. Do not open issues or pull requests autonomously, and do not post comments on behalf of a user without their review.
