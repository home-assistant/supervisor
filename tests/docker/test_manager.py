"""Test Docker manager."""

import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch

from docker.errors import APIError, DockerException, NotFound
import pytest
from requests import RequestException

from supervisor.coresys import CoreSys
from supervisor.docker.manager import CommandReturn, DockerAPI
from supervisor.exceptions import DockerError


async def test_run_command_success(docker: DockerAPI):
    """Test successful command execution."""
    # Mock container and its methods
    mock_container = MagicMock()
    mock_container.wait.return_value = {"StatusCode": 0}
    mock_container.logs.return_value = b"command output"

    # Mock docker containers.run to return our mock container
    docker.dockerpy.containers.run.return_value = mock_container

    # Execute the command
    result = docker.run_command(
        image="alpine", version="3.18", command="echo hello", stdout=True, stderr=True
    )

    # Verify the result
    assert isinstance(result, CommandReturn)
    assert result.exit_code == 0
    assert result.output == b"command output"

    # Verify docker.containers.run was called correctly
    docker.dockerpy.containers.run.assert_called_once_with(
        "alpine:3.18",
        command="echo hello",
        detach=True,
        network=docker.network.name,
        use_config_proxy=False,
        stdout=True,
        stderr=True,
    )

    # Verify container cleanup
    mock_container.remove.assert_called_once_with(force=True, v=True)


async def test_run_command_with_defaults(docker: DockerAPI):
    """Test command execution with default parameters."""
    # Mock container and its methods
    mock_container = MagicMock()
    mock_container.wait.return_value = {"StatusCode": 1}
    mock_container.logs.return_value = b"error output"

    # Mock docker containers.run to return our mock container
    docker.dockerpy.containers.run.return_value = mock_container

    # Execute the command with minimal parameters
    result = docker.run_command(image="ubuntu")

    # Verify the result
    assert isinstance(result, CommandReturn)
    assert result.exit_code == 1
    assert result.output == b"error output"

    # Verify docker.containers.run was called with defaults
    docker.dockerpy.containers.run.assert_called_once_with(
        "ubuntu:latest",  # default tag
        command=None,  # default command
        detach=True,
        network=docker.network.name,
        use_config_proxy=False,
    )

    # Verify container.logs was called with default stdout/stderr
    mock_container.logs.assert_called_once_with(stdout=True, stderr=True)


async def test_run_command_docker_exception(docker: DockerAPI):
    """Test command execution when Docker raises an exception."""
    # Mock docker containers.run to raise DockerException
    docker.dockerpy.containers.run.side_effect = DockerException("Docker error")

    # Execute the command and expect DockerError
    with pytest.raises(DockerError, match="Can't execute command: Docker error"):
        docker.run_command(image="alpine", command="test")


async def test_run_command_request_exception(docker: DockerAPI):
    """Test command execution when requests raises an exception."""
    # Mock docker containers.run to raise RequestException
    docker.dockerpy.containers.run.side_effect = RequestException("Connection error")

    # Execute the command and expect DockerError
    with pytest.raises(DockerError, match="Can't execute command: Connection error"):
        docker.run_command(image="alpine", command="test")


async def test_run_command_cleanup_on_exception(docker: DockerAPI):
    """Test that container cleanup happens even when an exception occurs."""
    # Mock container
    mock_container = MagicMock()

    # Mock docker.containers.run to return container, but container.wait to raise exception
    docker.dockerpy.containers.run.return_value = mock_container
    mock_container.wait.side_effect = DockerException("Wait failed")

    # Execute the command and expect DockerError
    with pytest.raises(DockerError):
        docker.run_command(image="alpine", command="test")

    # Verify container cleanup still happened
    mock_container.remove.assert_called_once_with(force=True, v=True)


async def test_run_command_custom_stdout_stderr(docker: DockerAPI):
    """Test command execution with custom stdout/stderr settings."""
    # Mock container and its methods
    mock_container = MagicMock()
    mock_container.wait.return_value = {"StatusCode": 0}
    mock_container.logs.return_value = b"output"

    # Mock docker containers.run to return our mock container
    docker.dockerpy.containers.run.return_value = mock_container

    # Execute the command with custom stdout/stderr
    result = docker.run_command(
        image="alpine", command="test", stdout=False, stderr=True
    )

    # Verify container.logs was called with the correct parameters
    mock_container.logs.assert_called_once_with(stdout=False, stderr=True)

    # Verify the result
    assert result.exit_code == 0
    assert result.output == b"output"


async def test_run_container_with_cidfile(
    coresys: CoreSys, docker: DockerAPI, path_extern, tmp_supervisor_data
):
    """Test container creation with cidfile and bind mount."""
    # Mock container
    mock_container = MagicMock()
    mock_container.id = "test_container_id_12345"

    container_name = "test_container"
    cidfile_path = coresys.config.path_cid_files / f"{container_name}.cid"
    extern_cidfile_path = coresys.config.path_extern_cid_files / f"{container_name}.cid"

    docker.dockerpy.containers.run.return_value = mock_container

    # Mock container creation
    with patch.object(
        docker.containers, "create", return_value=mock_container
    ) as create_mock:
        # Execute run with a container name
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda kwrgs: docker.run(**kwrgs),
            {"image": "test_image", "tag": "latest", "name": container_name},
        )

        # Check the container creation parameters
        create_mock.assert_called_once()
        kwargs = create_mock.call_args[1]

        assert "volumes" in kwargs
        assert str(extern_cidfile_path) in kwargs["volumes"]
        assert kwargs["volumes"][str(extern_cidfile_path)]["bind"] == "/run/cid"
        assert kwargs["volumes"][str(extern_cidfile_path)]["mode"] == "ro"

        # Verify container start was called
        mock_container.start.assert_called_once()

        # Verify cidfile was written with container ID
        assert cidfile_path.exists()
        assert cidfile_path.read_text() == mock_container.id

        assert result == mock_container


async def test_run_container_with_leftover_cidfile(
    coresys: CoreSys, docker: DockerAPI, path_extern, tmp_supervisor_data
):
    """Test container creation removes leftover cidfile before creating new one."""
    # Mock container
    mock_container = MagicMock()
    mock_container.id = "test_container_id_new"

    container_name = "test_container"
    cidfile_path = coresys.config.path_cid_files / f"{container_name}.cid"

    # Create a leftover cidfile
    cidfile_path.touch()

    # Mock container creation
    with patch.object(
        docker.containers, "create", return_value=mock_container
    ) as create_mock:
        # Execute run with a container name
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda kwrgs: docker.run(**kwrgs),
            {"image": "test_image", "tag": "latest", "name": container_name},
        )

        # Verify container was created
        create_mock.assert_called_once()

        # Verify new cidfile was written with container ID
        assert cidfile_path.exists()
        assert cidfile_path.read_text() == mock_container.id

        assert result == mock_container


async def test_stop_container_with_cidfile_cleanup(
    coresys: CoreSys, docker: DockerAPI, path_extern, tmp_supervisor_data
):
    """Test container stop with cidfile cleanup."""
    # Mock container
    mock_container = MagicMock()
    mock_container.status = "running"

    container_name = "test_container"
    cidfile_path = coresys.config.path_cid_files / f"{container_name}.cid"

    # Create a cidfile
    cidfile_path.touch()

    # Mock the containers.get method and cidfile cleanup
    with (
        patch.object(docker.containers, "get", return_value=mock_container),
    ):
        # Call stop_container with remove_container=True
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda kwrgs: docker.stop_container(**kwrgs),
            {"timeout": 10, "remove_container": True, "name": container_name},
        )

        # Verify container operations
        mock_container.stop.assert_called_once_with(timeout=10)
        mock_container.remove.assert_called_once_with(force=True, v=True)

        assert not cidfile_path.exists()


async def test_stop_container_without_removal_no_cidfile_cleanup(docker: DockerAPI):
    """Test container stop without removal doesn't clean up cidfile."""
    # Mock container
    mock_container = MagicMock()
    mock_container.status = "running"

    container_name = "test_container"

    # Mock the containers.get method and cidfile cleanup
    with (
        patch.object(docker.containers, "get", return_value=mock_container),
        patch("pathlib.Path.unlink") as mock_unlink,
    ):
        # Call stop_container with remove_container=False
        docker.stop_container(container_name, timeout=10, remove_container=False)

        # Verify container operations
        mock_container.stop.assert_called_once_with(timeout=10)
        mock_container.remove.assert_not_called()

        # Verify cidfile cleanup was NOT called
        mock_unlink.assert_not_called()


async def test_cidfile_cleanup_handles_oserror(
    coresys: CoreSys, docker: DockerAPI, path_extern, tmp_supervisor_data
):
    """Test that cidfile cleanup handles OSError gracefully."""
    # Mock container
    mock_container = MagicMock()
    mock_container.status = "running"

    container_name = "test_container"
    cidfile_path = coresys.config.path_cid_files / f"{container_name}.cid"

    # Create a cidfile
    cidfile_path.touch()

    # Mock the containers.get method and cidfile cleanup to raise OSError
    with (
        patch.object(docker.containers, "get", return_value=mock_container),
        patch("pathlib.Path.is_dir", return_value=False),
        patch("pathlib.Path.is_file", return_value=True),
        patch(
            "pathlib.Path.unlink", side_effect=OSError("File not found")
        ) as mock_unlink,
    ):
        # Call stop_container - should not raise exception
        docker.stop_container(container_name, timeout=10, remove_container=True)

        # Verify container operations completed
        mock_container.stop.assert_called_once_with(timeout=10)
        mock_container.remove.assert_called_once_with(force=True, v=True)

        # Verify cidfile cleanup was attempted
        mock_unlink.assert_called_once_with(missing_ok=True)


async def test_run_container_with_leftover_cidfile_directory(
    coresys: CoreSys, docker: DockerAPI, path_extern, tmp_supervisor_data
):
    """Test container creation removes leftover cidfile directory before creating new one.

    This can happen when Docker auto-starts a container with restart policy
    before Supervisor could write the CID file, causing Docker to create
    the bind mount source as a directory.
    """
    # Mock container
    mock_container = MagicMock()
    mock_container.id = "test_container_id_new"

    container_name = "test_container"
    cidfile_path = coresys.config.path_cid_files / f"{container_name}.cid"

    # Create a leftover directory (simulating Docker's behavior)
    cidfile_path.mkdir()
    assert cidfile_path.is_dir()

    # Mock container creation
    with patch.object(
        docker.containers, "create", return_value=mock_container
    ) as create_mock:
        # Execute run with a container name
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda kwrgs: docker.run(**kwrgs),
            {"image": "test_image", "tag": "latest", "name": container_name},
        )

        # Verify container was created
        create_mock.assert_called_once()

        # Verify new cidfile was written as a file (not directory)
        assert cidfile_path.exists()
        assert cidfile_path.is_file()
        assert cidfile_path.read_text() == mock_container.id

        assert result == mock_container


async def test_repair(coresys: CoreSys, caplog: pytest.LogCaptureFixture):
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
    coresys.docker.dockerpy.containers.get.side_effect = [
        MagicMock(),
        NotFound("corrupt"),
        DockerException("fail"),
    ]

    await coresys.run_in_executor(coresys.docker.repair)

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

    await coresys.run_in_executor(coresys.docker.repair)

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
    coresys.docker.images.import_image.return_value = [
        {"stream": f"{log_starter}: imported"}
    ]
    coresys.docker.images.inspect.return_value = {"Id": "imported"}

    image = await coresys.docker.import_image(test_tar)

    assert image["Id"] == "imported"
    coresys.docker.images.inspect.assert_called_once_with("imported")


async def test_import_image_error(coresys: CoreSys, tmp_path: Path):
    """Test failure importing an image into docker."""
    (test_tar := tmp_path / "test.tar").touch()
    coresys.docker.images.import_image.return_value = [
        {"errorDetail": {"message": "fail"}}
    ]

    with pytest.raises(DockerError, match="Can't import image from tar: fail"):
        await coresys.docker.import_image(test_tar)

    coresys.docker.images.inspect.assert_not_called()


async def test_import_multiple_images_in_tar(
    coresys: CoreSys, tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    """Test importing an image into docker."""
    (test_tar := tmp_path / "test.tar").touch()
    coresys.docker.images.import_image.return_value = [
        {"stream": "Loaded image: imported-1"},
        {"stream": "Loaded image: imported-2"},
    ]

    assert await coresys.docker.import_image(test_tar) is None

    assert "Unexpected image count 2 while importing image from tar" in caplog.text
    coresys.docker.images.inspect.assert_not_called()
