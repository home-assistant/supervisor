"""Test DNS plugin container."""

from ipaddress import IPv4Address
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from supervisor.coresys import CoreSys
from supervisor.docker.const import DockerMount, MountType
from supervisor.docker.manager import DockerAPI


@pytest.mark.usefixtures("path_extern")
async def test_start(coresys: CoreSys, tmp_supervisor_data: Path, container: MagicMock):
    """Test starting dns plugin."""
    config_file = tmp_supervisor_data / "dns" / "coredns.json"
    assert not config_file.exists()

    with patch.object(DockerAPI, "run", return_value=container.attrs) as run:
        await coresys.plugins.dns.start()

        run.assert_called_once()
        assert run.call_args.kwargs["ipv4"] == IPv4Address("172.30.32.3")
        assert run.call_args.kwargs["name"] == "hassio_dns"
        assert run.call_args.kwargs["hostname"] == "hassio-dns"
        assert run.call_args.kwargs["dns"] is False
        assert run.call_args.kwargs["oom_score_adj"] == -300
        assert run.call_args.kwargs["mounts"] == [
            DockerMount(
                type=MountType.BIND,
                source=coresys.config.path_extern_dns.as_posix(),
                target="/config",
                read_only=False,
            ),
            DockerMount(
                type=MountType.BIND,
                source="/run/dbus",
                target="/run/dbus",
                read_only=True,
            ),
        ]
        assert "volumes" not in run.call_args.kwargs

    assert config_file.exists()
