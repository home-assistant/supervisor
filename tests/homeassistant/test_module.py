"""Test Homeassistant module."""

from pathlib import Path
from unittest.mock import patch

from supervisor.coresys import CoreSys
from supervisor.docker.interface import DockerInterface


async def test_load(coresys: CoreSys, tmp_supervisor_data: Path):
    """Test homeassistant module load."""
    with open(tmp_supervisor_data / "homeassistant" / "secrets.yaml", "w") as secrets:
        secrets.write("hello: world\n")

    with patch.object(DockerInterface, "attach") as attach:
        await coresys.homeassistant.load()

        attach.assert_called_once()

    assert coresys.homeassistant.secrets.secrets == {"hello": "world"}
