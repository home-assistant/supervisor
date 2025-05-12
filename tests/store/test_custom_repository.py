"""Test add custom repository."""

import json
from unittest.mock import PropertyMock, patch

import pytest

from supervisor.addons.addon import Addon
from supervisor.coresys import CoreSys
from supervisor.exceptions import (
    StoreError,
    StoreGitCloneError,
    StoreGitError,
    StoreJobError,
    StoreNotFound,
)
from supervisor.resolution.const import SuggestionType
from supervisor.store import BUILTIN_REPOSITORIES, StoreManager
from supervisor.store.addon import AddonStore
from supervisor.store.repository import Repository


@pytest.fixture(autouse=True)
def _auto_supervisor_internet(supervisor_internet):
    # Use the supervisor_internet fixture to ensure that all tests has internet access
    pass


@pytest.mark.parametrize("use_update", [True, False])
async def test_add_valid_repository(
    coresys: CoreSys, store_manager: StoreManager, use_update: bool
):
    """Test add custom repository."""
    current = coresys.store.repository_urls
    with (
        patch("supervisor.store.repository.Repository.load", return_value=None),
        patch(
            "supervisor.utils.common.read_yaml_file",
            return_value={"name": "Awesome repository"},
        ),
        patch("pathlib.Path.exists", return_value=True),
    ):
        if use_update:
            await store_manager.update_repositories(current + ["http://example.com"])
        else:
            await store_manager.add_repository("http://example.com")

        assert store_manager.get_from_url("http://example.com").validate()

    assert "http://example.com" in coresys.store.repository_urls


async def test_add_invalid_repository(coresys: CoreSys, store_manager: StoreManager):
    """Test add invalid custom repository."""
    current = coresys.store.repository_urls
    with (
        patch("supervisor.store.repository.Repository.load", return_value=None),
        patch(
            "pathlib.Path.read_text",
            return_value="",
        ),
    ):
        await store_manager.update_repositories(
            current + ["http://example.com"], add_with_errors=True
        )

        assert not await coresys.run_in_executor(
            store_manager.get_from_url("http://example.com").validate
        )

    assert "http://example.com" in coresys.store.repository_urls
    assert coresys.resolution.suggestions[-1].type == SuggestionType.EXECUTE_REMOVE


@pytest.mark.parametrize("use_update", [True, False])
async def test_error_on_invalid_repository(
    coresys: CoreSys, store_manager: StoreManager, use_update
):
    """Test invalid repository not added."""
    current = coresys.store.repository_urls
    with (
        patch("supervisor.store.repository.Repository.load", return_value=None),
        patch(
            "pathlib.Path.read_text",
            return_value="",
        ),
        pytest.raises(StoreError),
    ):
        if use_update:
            await store_manager.update_repositories(current + ["http://example.com"])
        else:
            await store_manager.add_repository("http://example.com")

    assert "http://example.com" not in coresys.store.repository_urls
    assert len(coresys.resolution.suggestions) == 0
    with pytest.raises(StoreNotFound):
        store_manager.get_from_url("http://example.com")


async def test_add_invalid_repository_file(
    coresys: CoreSys, store_manager: StoreManager
):
    """Test add invalid custom repository file."""
    current = coresys.store.repository_urls
    with (
        patch("supervisor.store.repository.Repository.load", return_value=None),
        patch(
            "pathlib.Path.read_text",
            return_value=json.dumps({"name": "Awesome repository"}),
        ),
        patch("pathlib.Path.exists", return_value=False),
    ):
        await store_manager.update_repositories(
            current + ["http://example.com"], add_with_errors=True
        )

        assert not store_manager.get_from_url("http://example.com").validate()

    assert "http://example.com" in coresys.store.repository_urls
    assert coresys.resolution.suggestions[-1].type == SuggestionType.EXECUTE_REMOVE


@pytest.mark.parametrize(
    "git_error,suggestion_type",
    [
        (StoreGitCloneError(), SuggestionType.EXECUTE_REMOVE),
        (StoreGitError(), SuggestionType.EXECUTE_RESET),
    ],
)
async def test_add_repository_with_git_error(
    coresys: CoreSys,
    store_manager: StoreManager,
    git_error: StoreGitError,
    suggestion_type: SuggestionType,
):
    """Test repo added with issue on git error."""
    current = coresys.store.repository_urls
    with patch("supervisor.store.repository.Repository.load", side_effect=git_error):
        await store_manager.update_repositories(
            current + ["http://example.com"], add_with_errors=True
        )

    assert "http://example.com" in coresys.store.repository_urls
    assert coresys.resolution.suggestions[-1].type == suggestion_type
    assert isinstance(store_manager.get_from_url("http://example.com"), Repository)


@pytest.mark.parametrize(
    "use_update,git_error",
    [
        (True, StoreGitCloneError()),
        (True, StoreGitError()),
        (False, StoreGitCloneError()),
        (False, StoreGitError()),
    ],
)
async def test_error_on_repository_with_git_error(
    coresys: CoreSys,
    store_manager: StoreManager,
    use_update: bool,
    git_error: StoreGitError,
):
    """Test repo not added on git error."""
    current = coresys.store.repository_urls
    with (
        patch("supervisor.store.repository.Repository.load", side_effect=git_error),
        pytest.raises(StoreError),
    ):
        if use_update:
            await store_manager.update_repositories(current + ["http://example.com"])
        else:
            await store_manager.add_repository("http://example.com")

    assert "http://example.com" not in coresys.store.repository_urls
    assert len(coresys.resolution.suggestions) == 0
    with pytest.raises(StoreNotFound):
        store_manager.get_from_url("http://example.com")


@pytest.mark.asyncio
async def test_preinstall_valid_repository(
    coresys: CoreSys, store_manager: StoreManager
):
    """Test add core repository valid."""
    with patch("supervisor.store.repository.Repository.load", return_value=None):
        await store_manager.update_repositories(BUILTIN_REPOSITORIES)

        def validate():
            assert store_manager.get("core").validate()
            assert store_manager.get("local").validate()
            assert store_manager.get("a0d7b954").validate()
            assert store_manager.get("5c53de3b").validate()
            assert store_manager.get("d5369777").validate()

        await coresys.run_in_executor(validate)


@pytest.mark.parametrize("use_update", [True, False])
async def test_remove_repository(
    coresys: CoreSys,
    store_manager: StoreManager,
    repository: Repository,
    use_update: bool,
):
    """Test removing a custom repository."""
    assert repository.source in coresys.store.repository_urls
    assert repository.slug in coresys.store.repositories

    if use_update:
        await store_manager.update_repositories([])
    else:
        await store_manager.remove_repository(repository)

    assert repository.source not in coresys.store.repository_urls
    assert repository.slug not in coresys.addons.store
    assert repository.slug not in coresys.store.repositories


@pytest.mark.parametrize("use_update", [True, False])
async def test_remove_used_repository(
    coresys: CoreSys,
    store_manager: StoreManager,
    store_addon: AddonStore,
    use_update: bool,
):
    """Test removing used custom repository."""
    await coresys.addons.data.install(store_addon)
    addon = Addon(coresys, store_addon.slug)
    coresys.addons.local[addon.slug] = addon

    assert store_addon.repository in coresys.store.repositories

    with pytest.raises(
        StoreError,
        match="Can't remove 'https://github.com/awesome-developer/awesome-repo'. It's used by installed add-ons",
    ):
        if use_update:
            await store_manager.update_repositories([])
        else:
            await store_manager.remove_repository(
                coresys.store.repositories[store_addon.repository]
            )


async def test_update_partial_error(coresys: CoreSys, store_manager: StoreManager):
    """Test partial error on update does partial save and errors."""
    with patch("supervisor.store.repository.Repository.validate", return_value=True):
        with patch("supervisor.store.repository.Repository.load", return_value=None):
            await store_manager.update_repositories([])

        store_manager.data.update.assert_called_once()
        store_manager.data.update.reset_mock()

        current = coresys.store.repository_urls
        initial = len(current)

        with (
            patch(
                "supervisor.store.repository.Repository.load",
                side_effect=[None, StoreGitError()],
            ),
            pytest.raises(StoreError),
        ):
            await store_manager.update_repositories(
                current + ["http://example.com", "http://example2.com"]
            )

    assert len(coresys.store.repository_urls) == initial + 1
    store_manager.data.update.assert_called_once()


async def test_error_adding_duplicate(
    coresys: CoreSys, store_manager: StoreManager, repository: Repository
):
    """Test adding a duplicate repository causes an error."""
    assert repository.source in coresys.store.repository_urls
    with (
        patch("supervisor.store.repository.Repository.validate", return_value=True),
        patch("supervisor.store.repository.Repository.load", return_value=None),
        pytest.raises(StoreError),
    ):
        await store_manager.add_repository(repository.source)


async def test_add_with_update_repositories(
    coresys: CoreSys, store_manager: StoreManager, repository: Repository
):
    """Test adding repositories to existing ones using update."""
    assert repository.source in coresys.store.repository_urls
    assert "http://example.com" not in coresys.store.repository_urls

    with (
        patch("supervisor.store.repository.Repository.load", return_value=None),
        patch(
            "supervisor.utils.common.read_yaml_file",
            return_value={"name": "Awesome repository"},
        ),
        patch("pathlib.Path.exists", return_value=True),
    ):
        await store_manager.update_repositories(["http://example.com"], replace=False)

    assert repository.source in coresys.store.repository_urls
    assert "http://example.com" in coresys.store.repository_urls


@pytest.mark.parametrize("use_update", [True, False])
async def test_add_repository_fails_if_out_of_date(
    coresys: CoreSys, store_manager: StoreManager, use_update: bool
):
    """Test adding a repository fails when supervisor not updated."""
    with (
        patch.object(
            type(coresys.supervisor), "need_update", new=PropertyMock(return_value=True)
        ),
        pytest.raises(StoreJobError),
    ):
        if use_update:
            await store_manager.update_repositories(
                coresys.store.repository_urls + ["http://example.com"],
            )
        else:
            await store_manager.add_repository("http://example.com")


@pytest.mark.parametrize("need_update", [True, False])
async def test_repositories_loaded_ignore_updates(
    coresys: CoreSys, store_manager: StoreManager, need_update: bool
):
    """Test repositories loaded whether or not supervisor needs an update."""
    with (
        patch("supervisor.store.repository.Repository.load", return_value=None),
        patch.object(
            type(coresys.supervisor),
            "need_update",
            new=PropertyMock(return_value=need_update),
        ),
    ):
        await store_manager.load()

    assert len(coresys.resolution.issues) == 0
    assert (
        "https://github.com/hassio-addons/repository" in coresys.store.repository_urls
    )
    assert (
        "https://github.com/hassio-addons/repository" in coresys.store.repository_urls
    )
