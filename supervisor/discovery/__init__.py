"""Handle discover message for Home Assistant."""

from __future__ import annotations

from contextlib import suppress
import logging
from typing import TYPE_CHECKING, Any
from uuid import uuid4

import attr

from ..const import ATTR_CONFIG, ATTR_DISCOVERY, FILE_HASSIO_DISCOVERY
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import HomeAssistantAPIError
from ..utils.common import FileConfiguration
from .validate import SCHEMA_DISCOVERY_CONFIG

if TYPE_CHECKING:
    from ..addons.addon import Addon

_LOGGER: logging.Logger = logging.getLogger(__name__)

CMD_NEW = "post"
CMD_DEL = "delete"


@attr.s
class Message:
    """Represent a single Discovery message."""

    addon: str = attr.ib()
    service: str = attr.ib()
    config: dict[str, Any] = attr.ib(eq=False)
    uuid: str = attr.ib(factory=lambda: uuid4().hex, eq=False)


class Discovery(CoreSysAttributes, FileConfiguration):
    """Home Assistant Discovery handler."""

    def __init__(self, coresys: CoreSys):
        """Initialize discovery handler."""
        super().__init__(FILE_HASSIO_DISCOVERY, SCHEMA_DISCOVERY_CONFIG)
        self.coresys: CoreSys = coresys
        self.message_obj: dict[str, Message] = {}

    async def load(self) -> None:
        """Load exists discovery message into storage."""
        messages = {}
        for message in self._data[ATTR_DISCOVERY]:
            discovery = Message(**message)
            messages[discovery.uuid] = discovery

        _LOGGER.info("Loaded %d messages", len(messages))
        self.message_obj = messages

    async def save(self) -> None:
        """Write discovery message into data file."""
        messages: list[dict[str, Any]] = []
        for message in self.list_messages:
            messages.append(attr.asdict(message))

        self._data[ATTR_DISCOVERY].clear()
        self._data[ATTR_DISCOVERY].extend(messages)
        await self.save_data()

    def get(self, uuid: str) -> Message | None:
        """Return discovery message."""
        return self.message_obj.get(uuid)

    @property
    def list_messages(self) -> list[Message]:
        """Return list of available discovery messages."""
        return list(self.message_obj.values())

    async def send(self, addon: Addon, service: str, config: dict[str, Any]) -> Message:
        """Send a discovery message to Home Assistant."""
        # Create message
        message = Message(addon.slug, service, config)

        # Already exists?
        for exists_msg in self.list_messages:
            if exists_msg != message:
                continue
            if exists_msg.config != config:
                message = exists_msg
                message.config = config
            else:
                _LOGGER.debug("Duplicate discovery message from %s", addon.slug)
                return exists_msg
            break

        _LOGGER.info(
            "Sending discovery to Home Assistant %s from %s", service, addon.slug
        )
        self.message_obj[message.uuid] = message
        await self.save()

        self.sys_create_task(self._push_discovery(message, CMD_NEW))
        return message

    async def remove(self, message: Message) -> None:
        """Remove a discovery message from Home Assistant."""
        self.message_obj.pop(message.uuid, None)
        await self.save()

        _LOGGER.info(
            "Delete discovery to Home Assistant %s from %s",
            message.service,
            message.addon,
        )
        self.sys_create_task(self._push_discovery(message, CMD_DEL))

    async def _push_discovery(self, message: Message, command: str) -> None:
        """Send a discovery request."""
        if not await self.sys_homeassistant.api.check_api_state():
            _LOGGER.info("Discovery %s message ignore", message.uuid)
            return

        data = attr.asdict(message)
        data.pop(ATTR_CONFIG)

        with suppress(HomeAssistantAPIError):
            async with self.sys_homeassistant.api.make_request(
                command,
                f"api/hassio_push/discovery/{message.uuid}",
                json=data,
                timeout=10,
            ):
                _LOGGER.info("Discovery %s message send", message.uuid)
                return

        _LOGGER.warning("Discovery %s message fail", message.uuid)
