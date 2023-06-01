"""Test Homeassistant module."""

from pathlib import Path
from unittest.mock import patch

from supervisor.coresys import CoreSys
from supervisor.docker.interface import DockerInterface
from supervisor.homeassistant.secrets import HomeAssistantSecrets


async def test_load(coresys: CoreSys, tmp_supervisor_data: Path):
    """Test homeassistant module load."""
    with open(tmp_supervisor_data / "homeassistant" / "secrets.yaml", "w") as secrets:
        secrets.write("hello: world\n")

    # Unwrap read_secrets to prevent throttling between tests
    with patch.object(DockerInterface, "attach") as attach, patch.object(
        HomeAssistantSecrets,
        "_read_secrets",
        new=HomeAssistantSecrets._read_secrets.__wrapped__,
    ):
        await coresys.homeassistant.load()

        attach.assert_called_once()

    assert coresys.homeassistant.secrets.secrets == {"hello": "world"}
