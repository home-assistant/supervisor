"""Test tags in denylist."""

from unittest.mock import MagicMock, patch

from supervisor.docker import DockerAPI


def test_has_images_in_denylist():
    """Test tags in denylist exsist."""
    with patch("docker.DockerClient", return_value=MagicMock()):
        docker = DockerAPI()
        with patch(
            "supervisor.docker.DockerAPI.images", return_value=MagicMock()
        ) as mock_method:
            images = [MagicMock(tags=["containrrr/watchtower:latest"])]

            mock_method.list.return_value = images
            assert docker.check_denylist_images()


def test_no_images_in_denylist():
    """Test tags in denylist does not exsist."""
    with patch("docker.DockerClient", return_value=MagicMock()):
        docker = DockerAPI()
        with patch(
            "supervisor.docker.DockerAPI.images", return_value=MagicMock()
        ) as mock_method:
            images = [MagicMock(tags=["test:latest"])]

            mock_method.list.return_value = images
            assert not docker.check_denylist_images()
