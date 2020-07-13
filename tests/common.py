"""Common test functions."""
import json
from pathlib import Path


def load_json_fixture(filename):
    """Load a fixture."""
    path = Path(Path(__file__).parent.joinpath("fixtures"), filename)
    return json.loads(path.read_text())
