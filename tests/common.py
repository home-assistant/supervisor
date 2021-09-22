"""Common test functions."""
import json
from pathlib import Path


def load_json_fixture(filename: str) -> dict:
    """Load a json fixture."""
    path = Path(Path(__file__).parent.joinpath("fixtures"), filename)
    return json.loads(path.read_text(encoding="utf-8"))


def load_fixture(filename: str) -> str:
    """Load a fixture."""
    path = Path(Path(__file__).parent.joinpath("fixtures"), filename)
    return path.read_text(encoding="utf-8")


def exists_fixture(filename: str) -> bool:
    """Check if a fixture exists."""
    path = Path(Path(__file__).parent.joinpath("fixtures"), filename)
    return path.exists()
