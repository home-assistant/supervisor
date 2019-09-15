"""Handle Home Assistant secrets to add-ons."""
from datetime import timedelta
import logging
from pathlib import Path
from typing import Dict

from ruamel.yaml import YAML, YAMLError
import voluptuous as vol

from .coresys import CoreSys, CoreSysAttributes
from .utils import AsyncThrottle

_LOGGER: logging.Logger = logging.getLogger(__name__)

SECRETS_SCHEMA = vol.Schema({str: vol.Any(str, int, None, float)})


class SecretsManager(CoreSysAttributes):
    """Manage Home Assistant secrets."""

    def __init__(self, coresys: CoreSys):
        """Initialize secret manager."""
        self.coresys: CoreSys = coresys
        self.secrets: Dict[str, str] = {}

    @property
    def path_secrets(self) -> Path:
        """Return path to secret file."""
        return Path(self.sys_config.path_homeassistant, "secrets.yaml")

    def get(self, secret: str) -> str:
        """Get secret from store."""
        _LOGGER.info("Request secret %s", secret)
        return self.secrets.get(secret)

    async def load(self) -> None:
        """Load secrets on start."""
        await self._read_secrets()

        _LOGGER.info("Load Home Assistant secrets: %s", len(self.secrets))

    async def reload(self) -> None:
        """Reload secrets."""
        await self._read_secrets()

    @AsyncThrottle(timedelta(seconds=60))
    async def _read_secrets(self):
        """Read secrets.yaml into memory."""
        if not self.path_secrets.exists():
            _LOGGER.debug("Home Assistant secrets not exists")
            return

        # Read secrets
        try:
            yaml = YAML()
            data = await self.sys_run_in_executor(yaml.load, self.path_secrets)

            self.secrets = SECRETS_SCHEMA(data)
        except YAMLError as err:
            _LOGGER.error("Can't process Home Assistant secrets: %s", err)
        except vol.Invalid:
            _LOGGER.warning("Home Assistant secrets have a invalid format")
        else:
            _LOGGER.debug("Reload Home Assistant secrets: %s", len(self.secrets))
