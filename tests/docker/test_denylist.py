"""Test tags in denylist."""

from unittest.mock import MagicMock, patch


def test_has_images_in_denylist(docker):
    """Test tags in denylist exsist."""
    images = [MagicMock(tags=["containrrr/watchtower:latest"])]
    with patch("supervisor.docker.DockerAPI.images.list", return_value=images):
        assert docker.check_denylist_images()


def test_no_images_in_denylist(docker):
    """Test tags in denylist does not exsist."""
    assert not docker.check_denylist_images()
