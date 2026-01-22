"""Test Docker manager."""

from http import HTTPStatus
from pathlib import Path
import re
from unittest.mock import AsyncMock, MagicMock, patch

import aiodocker
from aiodocker.containers import DockerContainer
from docker.errors import APIError, NotFound
import pytest

from supervisor.const import DNS_SUFFIX
from supervisor.coresys import CoreSys
from supervisor.docker.const import (
    LABEL_MANAGED,
    DockerMount,
    MountBindOptions,
    MountType,
)
from supervisor.docker.manager import CommandReturn, DockerAPI
from supervisor.exceptions import DockerError


async def test_run_command_success(docker: DockerAPI, container: DockerContainer):
    """Test successful command execution."""
    # Mock container and its methods
    container.wait.return_value = {"StatusCode": 0}
    container.log.return_value = ["command output"]

    # Execute the command
    result = await docker.run_command(
        image="alpine", tag="3.18", command=["echo", "hello"], stdout=True, stderr=True
    )

    # Verify the result
    assert isinstance(result, CommandReturn)
    assert result.exit_code == 0
    assert result.log == ["command output"]

    # Verify docker.containers.run was called correctly
    docker.containers.create.assert_called_once_with(
        {
            "Image": "alpine:3.18",
            "Labels": {"supervisor_managed": ""},
            "OpenStdin": False,
            "StdinOnce": False,
            "AttachStdin": False,
            "AttachStdout": False,
            "AttachStderr": False,
            "HostConfig": {
                "NetworkMode": "hassio",
                "Init": False,
                "Privileged": False,
                "Dns": ["172.30.32.3"],
                "DnsSearch": ["local.hass.io"],
                "DnsOptions": ["timeout:10"],
            },
            "Cmd": ["echo", "hello"],
        },
        name=None,
    )
    container.start.assert_called_once()

    # Verify container cleanup
    container.delete.assert_called_once_with(force=True, v=True)


async def test_run_command_docker_exception(docker: DockerAPI):
    """Test command execution when Docker raises an exception."""
    # Mock docker containers.run to raise aiodocker.DockerError
    docker.containers.create.side_effect = aiodocker.DockerError(
        HTTPStatus.INTERNAL_SERVER_ERROR, {"message": "Docker error"}
    )

    # Execute the command and expect DockerError
    with pytest.raises(
        DockerError,
        match=re.escape(
            "Can't execute command: Can't create container from alpine:latest: DockerError(500, 'Docker error')"
        ),
    ):
        await docker.run_command(image="alpine", command="test")


async def test_run_command_cleanup_on_exception(
    docker: DockerAPI, container: DockerContainer
):
    """Test that container cleanup happens even when an exception occurs."""
    container.wait.side_effect = aiodocker.DockerError(500, {"message": "Wait failed"})

    # Execute the command and expect DockerError
    with pytest.raises(DockerError):
        await docker.run_command(image="alpine", command="test")

    # Verify container cleanup still happened
    container.delete.assert_called_once_with(force=True, v=True)


async def test_run_command_custom_stdout_stderr(
    docker: DockerAPI, container: DockerContainer
):
    """Test command execution with custom stdout/stderr settings."""
    # Mock container and its methods
    container.wait.return_value = {"StatusCode": 0}
    container.log.return_value = ["output"]

    # Execute the command with custom stdout/stderr
    result = await docker.run_command(
        image="alpine", command="test", stdout=False, stderr=True
    )

    # Verify container.logs was called with the correct parameters
    container.log.assert_called_once_with(stdout=False, stderr=True, follow=False)

    # Verify the result
    assert result.exit_code == 0
    assert result.log == ["output"]


async def test_run_command_with_mounts(docker: DockerAPI):
    """Test command execution with mounts are correctly converted."""
    # Mock container and its methods
    mock_container = MagicMock()
    mock_container.wait.return_value = {"StatusCode": 0}
    mock_container.logs.return_value = ["output"]

    # Mock docker containers.run to return our mock container
    docker.dockerpy.containers.run.return_value = mock_container

    # Create test mounts
    mounts = [
        DockerMount(
            type=MountType.BIND,
            source="/dev",
            target="/dev",
            read_only=True,
            bind_options=MountBindOptions(read_only_non_recursive=True),
        ),
        DockerMount(
            type=MountType.VOLUME,
            source="my_volume",
            target="/data",
            read_only=False,
        ),
    ]

    # Execute the command with mounts
    result = await docker.run_command(image="alpine", command="test", mounts=mounts)

    # Verify the result
    assert result.exit_code == 0

    # Check that mounts were converted correctly
    docker.containers.create.assert_called_once_with(
        {
            "Image": "alpine:latest",
            "Labels": {LABEL_MANAGED: ""},
            "OpenStdin": False,
            "StdinOnce": False,
            "AttachStdin": False,
            "AttachStdout": False,
            "AttachStderr": False,
            "Cmd": "test",
            "HostConfig": {
                "NetworkMode": docker.network.name,
                "Init": False,
                "Privileged": False,
                "Dns": [str(docker.network.dns)],
                "DnsSearch": [DNS_SUFFIX],
                "DnsOptions": ["timeout:10"],
                "Mounts": [
                    {
                        "Type": "bind",
                        "Source": "/dev",
                        "Target": "/dev",
                        "ReadOnly": True,
                        "BindOptions": {"ReadOnlyNonRecursive": True},
                    },
                    {
                        "Type": "volume",
                        "Source": "my_volume",
                        "Target": "/data",
                        "ReadOnly": False,
                    },
                ],
            },
        },
        name=None,
    )


@pytest.mark.usefixtures("path_extern", "tmp_supervisor_data")
async def test_run_container_with_cidfile(
    coresys: CoreSys, docker: DockerAPI, container: DockerContainer
):
    """Test container creation with cidfile and bind mount."""
    container.id = "test_container_id_12345"
    container.show.return_value = mock_metadata = {"Id": container.id}

    container_name = "test_container"
    cidfile_path = coresys.config.path_cid_files / f"{container_name}.cid"
    extern_cidfile_path = coresys.config.path_extern_cid_files / f"{container_name}.cid"

    # Execute run with a container name
    result = await docker.run("test_image", tag="latest", name=container_name)

    # Check the container creation parameters
    docker.containers.create.assert_called_once()
    create_config = docker.containers.create.call_args.args[0]

    assert "HostConfig" in create_config
    assert "Mounts" in create_config["HostConfig"]
    assert {
        "Type": "bind",
        "Source": str(extern_cidfile_path),
        "Target": "/run/cid",
        "ReadOnly": True,
    } in create_config["HostConfig"]["Mounts"]

    # Verify container start was called
    container.start.assert_called_once()

    # Verify cidfile was written with container ID
    assert cidfile_path.exists()
    assert cidfile_path.read_text() == container.id

    assert result == mock_metadata


@pytest.mark.usefixtures("path_extern", "tmp_supervisor_data")
async def test_run_container_with_leftover_cidfile(
    coresys: CoreSys, docker: DockerAPI, container: DockerContainer
):
    """Test container creation removes leftover cidfile before creating new one."""
    container.id = "test_container_id_12345"
    container.show.return_value = mock_metadata = {"Id": container.id}

    container_name = "test_container"
    cidfile_path = coresys.config.path_cid_files / f"{container_name}.cid"

    # Create a leftover cidfile
    cidfile_path.touch()

    # Execute run with a container name
    result = await docker.run("test_image", tag="latest", name=container_name)

    # Verify container was created
    docker.containers.create.assert_called_once()

    # Verify new cidfile was written with container ID
    assert cidfile_path.exists()
    assert cidfile_path.read_text() == container.id

    assert result == mock_metadata


@pytest.mark.usefixtures("tmp_supervisor_data", "path_extern")
async def test_stop_container_with_cidfile_cleanup(
    coresys: CoreSys, docker: DockerAPI, container: DockerContainer
):
    """Test container stop with cidfile cleanup."""
    container.show.return_value["State"]["Status"] = "running"
    container.show.return_value["State"]["Running"] = True

    container_name = "test_container"
    cidfile_path = coresys.config.path_cid_files / f"{container_name}.cid"

    # Create a cidfile
    cidfile_path.touch()

    # Call stop_container with remove_container=True
    await docker.stop_container(timeout=10, remove_container=True, name=container_name)

    # Verify container operations
    container.stop.assert_called_once_with(timeout=10)
    container.delete.assert_called_once_with(force=True, v=True)

    assert not cidfile_path.exists()


async def test_stop_container_without_removal_no_cidfile_cleanup(
    docker: DockerAPI, container: DockerContainer
):
    """Test container stop without removal doesn't clean up cidfile."""
    container.show.return_value["State"]["Status"] = "running"
    container.show.return_value["State"]["Running"] = True

    container_name = "test_container"

    # Mock the containers.get method and cidfile cleanup
    with patch("pathlib.Path.unlink") as mock_unlink:
        # Call stop_container with remove_container=False
        await docker.stop_container(container_name, timeout=10, remove_container=False)

        # Verify container operations
        container.stop.assert_called_once_with(timeout=10)
        container.delete.assert_not_called()

        # Verify cidfile cleanup was NOT called
        mock_unlink.assert_not_called()


@pytest.mark.usefixtures("path_extern", "tmp_supervisor_data")
async def test_cidfile_cleanup_handles_oserror(
    coresys: CoreSys, docker: DockerAPI, container: DockerContainer
):
    """Test that cidfile cleanup handles OSError gracefully."""
    container.show.return_value["State"]["Status"] = "running"
    container.show.return_value["State"]["Running"] = True

    container_name = "test_container"
    cidfile_path = coresys.config.path_cid_files / f"{container_name}.cid"

    # Create a cidfile
    cidfile_path.touch()

    # Mock the containers.get method and cidfile cleanup to raise OSError
    with (
        patch("pathlib.Path.is_dir", return_value=False),
        patch("pathlib.Path.is_file", return_value=True),
        patch(
            "pathlib.Path.unlink", side_effect=OSError("File not found")
        ) as mock_unlink,
    ):
        # Call stop_container - should not raise exception
        await docker.stop_container(container_name, timeout=10, remove_container=True)

        # Verify container operations completed
        container.stop.assert_called_once_with(timeout=10)
        container.delete.assert_called_once_with(force=True, v=True)

        # Verify cidfile cleanup was attempted
        mock_unlink.assert_called_once_with(missing_ok=True)


@pytest.mark.usefixtures("path_extern", "tmp_supervisor_data")
async def test_run_container_with_leftover_cidfile_directory(
    coresys: CoreSys, docker: DockerAPI, container: DockerContainer
):
    """Test container creation removes leftover cidfile directory before creating new one.

    This can happen when Docker auto-starts a container with restart policy
    before Supervisor could write the CID file, causing Docker to create
    the bind mount source as a directory.
    """
    container.id = "test_container_id_12345"
    container.show.return_value = mock_metadata = {"Id": container.id}

    container_name = "test_container"
    cidfile_path = coresys.config.path_cid_files / f"{container_name}.cid"

    # Create a leftover directory (simulating Docker's behavior)
    cidfile_path.mkdir()
    assert cidfile_path.is_dir()

    # Execute run with a container name
    result = await docker.run("test_image", tag="latest", name=container_name)

    # Verify container was created
    docker.containers.create.assert_called_once()

    # Verify new cidfile was written as a file (not directory)
    assert cidfile_path.exists()
    assert cidfile_path.is_file()
    assert cidfile_path.read_text() == container.id

    assert result == mock_metadata


async def test_repair(
    coresys: CoreSys, caplog: pytest.LogCaptureFixture, container: DockerContainer
):
    """Test repair API."""
    coresys.docker.dockerpy.networks.get.side_effect = [
        hassio := MagicMock(
            attrs={
                "Containers": {
                    "good": {"Name": "good"},
                    "corrupt": {"Name": "corrupt"},
                    "fail": {"Name": "fail"},
                }
            }
        ),
        host := MagicMock(attrs={"Containers": {}}),
    ]
    coresys.docker.containers.get.side_effect = [
        container,
        aiodocker.DockerError(HTTPStatus.NOT_FOUND, {"message": "corrupt"}),
        aiodocker.DockerError(HTTPStatus.INTERNAL_SERVER_ERROR, {"message": "fail"}),
    ]

    await coresys.docker.repair()

    coresys.docker.dockerpy.api.prune_containers.assert_called_once()
    coresys.docker.dockerpy.api.prune_images.assert_called_once_with(
        filters={"dangling": False}
    )
    coresys.docker.dockerpy.api.prune_builds.assert_called_once()
    coresys.docker.dockerpy.api.prune_volumes.assert_called_once()
    coresys.docker.dockerpy.api.prune_networks.assert_called_once()
    hassio.disconnect.assert_called_once_with("corrupt", force=True)
    host.disconnect.assert_not_called()
    assert "Docker fatal error on container fail on hassio" in caplog.text


async def test_repair_failures(coresys: CoreSys, caplog: pytest.LogCaptureFixture):
    """Test repair proceeds best it can through failures."""
    coresys.docker.dockerpy.api.prune_containers.side_effect = APIError("fail")
    coresys.docker.dockerpy.api.prune_images.side_effect = APIError("fail")
    coresys.docker.dockerpy.api.prune_builds.side_effect = APIError("fail")
    coresys.docker.dockerpy.api.prune_volumes.side_effect = APIError("fail")
    coresys.docker.dockerpy.api.prune_networks.side_effect = APIError("fail")
    coresys.docker.dockerpy.networks.get.side_effect = NotFound("missing")

    await coresys.docker.repair()

    assert "Error for containers prune: fail" in caplog.text
    assert "Error for images prune: fail" in caplog.text
    assert "Error for builds prune: fail" in caplog.text
    assert "Error for volumes prune: fail" in caplog.text
    assert "Error for networks prune: fail" in caplog.text
    assert "Error for networks hassio prune: missing" in caplog.text
    assert "Error for networks host prune: missing" in caplog.text


@pytest.mark.parametrize("log_starter", [("Loaded image ID"), ("Loaded image")])
async def test_import_image(coresys: CoreSys, tmp_path: Path, log_starter: str):
    """Test importing an image into docker."""
    (test_tar := tmp_path / "test.tar").touch()
    coresys.docker.images.import_image = AsyncMock(
        return_value=[{"stream": f"{log_starter}: imported"}]
    )
    coresys.docker.images.inspect.return_value = {"Id": "imported"}

    image = await coresys.docker.import_image(test_tar)

    assert image["Id"] == "imported"
    coresys.docker.images.inspect.assert_called_once_with("imported")


async def test_import_image_error(coresys: CoreSys, tmp_path: Path):
    """Test failure importing an image into docker."""
    (test_tar := tmp_path / "test.tar").touch()
    coresys.docker.images.import_image = AsyncMock(
        return_value=[{"errorDetail": {"message": "fail"}}]
    )

    with pytest.raises(DockerError, match="Can't import image from tar: fail"):
        await coresys.docker.import_image(test_tar)

    coresys.docker.images.inspect.assert_not_called()


async def test_import_multiple_images_in_tar(
    coresys: CoreSys, tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    """Test importing an image into docker."""
    (test_tar := tmp_path / "test.tar").touch()
    coresys.docker.images.import_image = AsyncMock(
        return_value=[
            {"stream": "Loaded image: imported-1"},
            {"stream": "Loaded image: imported-2"},
        ]
    )

    assert await coresys.docker.import_image(test_tar) is None

    assert "Unexpected image count 2 while importing image from tar" in caplog.text
    coresys.docker.images.inspect.assert_not_called()
