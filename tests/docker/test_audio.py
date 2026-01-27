"""Test audio plugin container."""

from ipaddress import IPv4Address
from pathlib import Path
from unittest.mock import patch

from aiodocker.containers import DockerContainer
import pytest

from supervisor.coresys import CoreSys
from supervisor.docker.const import DockerMount, MountType, Ulimit
from supervisor.docker.manager import DockerAPI

from . import DEV_MOUNT


@pytest.mark.usefixtures("path_extern")
async def test_start(
    coresys: CoreSys, tmp_supervisor_data: Path, container: DockerContainer
):
    """Test starting audio plugin."""
    config_file = tmp_supervisor_data / "audio" / "pulse_audio.json"
    assert not config_file.exists()

    with patch.object(
        DockerAPI, "run", return_value=container.show.return_value
    ) as run:
        await coresys.plugins.audio.start()

        run.assert_called_once()
        assert run.call_args.kwargs["ipv4"] == IPv4Address("172.30.32.4")
        assert run.call_args.kwargs["name"] == "hassio_audio"
        assert run.call_args.kwargs["hostname"] == "hassio-audio"
        assert run.call_args.kwargs["cap_add"] == ["SYS_NICE", "SYS_RESOURCE"]
        assert run.call_args.kwargs["ulimits"] == [
            Ulimit(name="rtprio", soft=10, hard=10)
        ]

        assert run.call_args.kwargs["mounts"] == [
            DEV_MOUNT,
            DockerMount(
                type=MountType.BIND,
                source=coresys.config.path_extern_audio.as_posix(),
                target="/data",
                read_only=False,
            ),
            DockerMount(
                type=MountType.BIND,
                source="/run/dbus",
                target="/run/dbus",
                read_only=True,
            ),
            DockerMount(
                type=MountType.BIND,
                source="/run/udev",
                target="/run/udev",
                read_only=True,
            ),
            DockerMount(
                type=MountType.BIND,
                source="/etc/machine-id",
                target="/etc/machine-id",
                read_only=True,
            ),
        ]
        assert "volumes" not in run.call_args.kwargs

    assert config_file.exists()
