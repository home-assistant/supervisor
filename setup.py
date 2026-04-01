"""Home Assistant Supervisor setup."""

from pathlib import Path
import re

from setuptools import setup

RE_SUPERVISOR_VERSION = re.compile(
    r'^SUPERVISOR_VERSION =\s*"?((?P<git_sha>[0-9a-f]{40})|[^"]+)"?$'
)

SUPERVISOR_DIR = Path(__file__).parent
REQUIREMENTS_FILE = SUPERVISOR_DIR / "requirements.txt"
CONST_FILE = SUPERVISOR_DIR / "supervisor/const.py"

REQUIREMENTS = REQUIREMENTS_FILE.read_text(encoding="utf-8")
CONSTANTS = CONST_FILE.read_text(encoding="utf-8")


def _get_supervisor_version():
    for line in CONSTANTS.split("\n"):
        if match := RE_SUPERVISOR_VERSION.match(line):
            if git_sha := match.group("git_sha"):
                return f"9999.09.9.dev9999+{git_sha}"
            return match.group(1)
    return "9999.09.9.dev9999"


setup(
    version=_get_supervisor_version(),
    dependencies=REQUIREMENTS.split("\n"),
)
