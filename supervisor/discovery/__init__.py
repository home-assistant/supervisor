"""Handle discover message for Home Assistant."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import logging
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from ..const import (
    ATTR_ADDON,
    ATTR_APP,
    ATTR_CONFIG,
    ATTR_DISCOVERY,
    FILE_HASSIO_DISCOVERY,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import HomeAssistantAPIError
from ..utils.common import FileConfiguration
from .validate import SCHEMA_DISCOVERY_CONFIG

if TYPE_CHECKING:
    from ..apps.app import App

_LOGGER: logging.Logger = logging.getLogger(__name__)

CMD_NEW = "post"
CMD_DEL = "delete"


@dataclass
class Message:
    """Represent a single Discovery message."""

    app: str
    service: str
    config: dict[str, Any] = field(compare=False)
    uuid: str = field(default_factory=lambda: uuid4().hex, compare=False)


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
            messages.append(asdict(message))

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

    async def send(self, app: App, service: str, config: dict[str, Any]) -> Message:
        """Send a discovery message to Home Assistant."""
        # Create message
        message = Message(app.slug, service, config)

        # Already exists?
        for exists_msg in self.list_messages:
            if exists_msg != message:
                continue
            if exists_msg.config != config:
                message = exists_msg
                message.config = config
            else:
                _LOGGER.debug("Duplicate discovery message from %s", app.slug)
                return exists_msg
            break

        _LOGGER.info(
            "Sending discovery to Home Assistant %s from %s", service, app.slug
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
            message.app,
        )
        self.sys_create_task(self._push_discovery(message, CMD_DEL))

    async def _push_discovery(self, message: Message, command: str) -> None:
        """Send a discovery request."""
        if not await self.sys_homeassistant.api.check_api_state():
            _LOGGER.info("Discovery %s message ignore", message.uuid)
            return

        data = asdict(message)
        data.pop(ATTR_CONFIG)
        # Home Assistant expects the legacy "addon" key in the push payload.
        data[ATTR_ADDON] = data.pop(ATTR_APP)

        try:
            async with self.sys_homeassistant.api.make_request(
                command,
                f"api/hassio_push/discovery/{message.uuid}",
                json=data,
                timeout=10,
            ):
                _LOGGER.info("Discovery %s message send", message.uuid)
                return
        except HomeAssistantAPIError as err:
            _LOGGER.error("Discovery %s message failed: %s", message.uuid, err)
