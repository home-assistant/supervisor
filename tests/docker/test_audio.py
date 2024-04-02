"""Test audio plugin container."""

from ipaddress import IPv4Address
from pathlib import Path
from unittest.mock import patch

from docker.types import Mount

from supervisor.coresys import CoreSys
from supervisor.docker.manager import DockerAPI

from . import DEV_MOUNT


async def test_start(coresys: CoreSys, tmp_supervisor_data: Path, path_extern):
    """Test starting audio plugin."""
    config_file = tmp_supervisor_data / "audio" / "pulse_audio.json"
    assert not config_file.exists()

    with patch.object(DockerAPI, "run") as run:
        await coresys.plugins.audio.start()

        run.assert_called_once()
        assert run.call_args.kwargs["ipv4"] == IPv4Address("172.30.32.4")
        assert run.call_args.kwargs["name"] == "hassio_audio"
        assert run.call_args.kwargs["hostname"] == "hassio-audio"
        assert run.call_args.kwargs["cap_add"] == ["SYS_NICE", "SYS_RESOURCE"]
        assert run.call_args.kwargs["ulimits"] == [
            {"Name": "rtprio", "Soft": 10, "Hard": 10}
        ]

        assert run.call_args.kwargs["mounts"] == [
            DEV_MOUNT,
            Mount(
                type="bind",
                source=coresys.config.path_extern_audio.as_posix(),
                target="/data",
                read_only=False,
            ),
            Mount(type="bind", source="/run/dbus", target="/run/dbus", read_only=True),
            Mount(type="bind", source="/run/udev", target="/run/udev", read_only=True),
            Mount(
                type="bind",
                source="/etc/machine-id",
                target="/etc/machine-id",
                read_only=True,
            ),
        ]
        assert "volumes" not in run.call_args.kwargs

    assert config_file.exists()
