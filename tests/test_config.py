"""Test Supervisor core config."""

import json
from pathlib import Path

import pytest

from supervisor.config import CoreConfig
from supervisor.const import FeatureFlag


async def _read_config(config_file: Path) -> CoreConfig:
    config = CoreConfig()
    config._file = config_file  # pylint: disable=protected-access
    await config.read_data()
    return config


async def test_new_installation_feature_flags(tmp_path: Path):
    """Test security feature flags are enabled by default on new installations."""
    config = await _read_config(tmp_path / "config.json")

    assert config.feature_flags[FeatureFlag.APP_DROP_NET_RAW] is True
    assert config.feature_flags[FeatureFlag.APP_REDUCED_CAPABILITIES] is True


@pytest.mark.parametrize(
    "existing",
    [
        pytest.param({}, id="unset"),
        pytest.param({"feature_flags": {"app_drop_net_raw": False}}, id="explicit"),
    ],
)
async def test_existing_installation_feature_flags(tmp_path: Path, existing: dict):
    """Test security feature flags stay disabled on existing installations."""
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(existing))

    config = await _read_config(config_file)

    assert config.feature_flags.get(FeatureFlag.APP_DROP_NET_RAW, False) is False
    assert (
        config.feature_flags.get(FeatureFlag.APP_REDUCED_CAPABILITIES, False) is False
    )
