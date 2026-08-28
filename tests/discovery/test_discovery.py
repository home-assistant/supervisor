"""Test discovery message handling."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from supervisor.apps.app import App
from supervisor.coresys import CoreSys
from supervisor.discovery import CMD_NEW, Message

BACKUP_UUID = "e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3"
MCP_CONFIG = {"url": "http://local-ssh:8099/mcp"}


@pytest.fixture(name="app_with_discovery")
async def fixture_app_with_discovery(install_app_ssh: App) -> App:
    """Return an app which provides a discoverable service."""
    install_app_ssh.data["discovery"] = ["mcp"]
    return install_app_ssh


async def test_restore_app_messages_keeps_uuid(
    coresys: CoreSys, app_with_discovery: App
):
    """Test a restored message keeps the uuid Home Assistant knows it by."""
    message = Message(
        app=app_with_discovery.slug,
        service="mcp",
        config=MCP_CONFIG,
        uuid=BACKUP_UUID,
    )

    with patch.object(
        type(coresys.discovery), "_push_discovery", new=AsyncMock()
    ) as push:
        await coresys.discovery.restore_app_messages(app_with_discovery, [message])
        await asyncio.sleep(0)

    assert coresys.discovery.get(BACKUP_UUID) == message
    assert coresys.discovery.get(BACKUP_UUID).config == MCP_CONFIG
    # The service behind the message is not up yet, only the app knows when it
    # is, so Home Assistant is not told here
    push.assert_not_called()


async def test_restore_app_messages_announced_by_app(
    coresys: CoreSys, app_with_discovery: App
):
    """Test the app announcing a restored message pushes it, uuid included.

    An app sends its discovery message again on every start. send() drops such
    a message as a duplicate when its config did not change, which for a
    restored message would leave Home Assistant unaware of it until its next
    start. That never comes when a single app is restored while Home Assistant
    keeps running, so a restored message pushes on the first send instead.
    """
    message = Message(
        app=app_with_discovery.slug,
        service="mcp",
        config=MCP_CONFIG,
        uuid=BACKUP_UUID,
    )
    await coresys.discovery.restore_app_messages(app_with_discovery, [message])

    with patch.object(
        type(coresys.discovery), "_push_discovery", new=AsyncMock()
    ) as push:
        # App starts after the restore and sends the config it always sends.
        # Message equality ignores the uuid, so compare it explicitly
        resent = await coresys.discovery.send(
            app_with_discovery, "mcp", dict(MCP_CONFIG)
        )
        await asyncio.sleep(0)

        assert resent.uuid == BACKUP_UUID
        push.assert_called_once_with(message, CMD_NEW)

        # Every following start is a duplicate again
        push.reset_mock()
        await coresys.discovery.send(app_with_discovery, "mcp", dict(MCP_CONFIG))
        await asyncio.sleep(0)

    push.assert_not_called()
    assert [
        message.uuid
        for message in coresys.discovery.messages_for_app(app_with_discovery.slug)
    ] == [BACKUP_UUID]


async def test_restore_app_messages_keeps_live_message(
    coresys: CoreSys, app_with_discovery: App
):
    """Test a live message wins, it already carries the uuid in use."""
    live = await coresys.discovery.send(app_with_discovery, "mcp", dict(MCP_CONFIG))
    assert live.uuid != BACKUP_UUID

    await coresys.discovery.restore_app_messages(
        app_with_discovery,
        [
            Message(
                app=app_with_discovery.slug,
                service="mcp",
                config={"url": "http://local-ssh:9999/mcp"},
                uuid=BACKUP_UUID,
            )
        ],
    )

    assert coresys.discovery.get(BACKUP_UUID) is None
    assert coresys.discovery.messages_for_app(app_with_discovery.slug) == [live]


async def test_restore_app_messages_skips_dropped_service(
    coresys: CoreSys, app_with_discovery: App, caplog: pytest.LogCaptureFixture
):
    """Test a message is not restored for a service the app no longer provides."""
    await coresys.discovery.restore_app_messages(
        app_with_discovery,
        [
            Message(
                app=app_with_discovery.slug,
                service="adguard",
                config={"host": "127.0.0.1", "port": 3000},
                uuid=BACKUP_UUID,
            )
        ],
    )

    assert coresys.discovery.get(BACKUP_UUID) is None
    assert "app local_ssh does not provide it anymore" in caplog.text


async def test_restore_app_messages_skips_uuid_in_use(
    coresys: CoreSys, app_with_discovery: App, caplog: pytest.LogCaptureFixture
):
    """Test a message does not overwrite the message another app owns.

    Messages are keyed by uuid across all apps, so restoring a uuid which is
    already taken would drop the message it collides with.
    """
    other = Message(app="core_mosquitto", service="mqtt", config={}, uuid=BACKUP_UUID)
    coresys.discovery.message_obj[other.uuid] = other

    await coresys.discovery.restore_app_messages(
        app_with_discovery,
        [
            Message(
                app=app_with_discovery.slug,
                service="mcp",
                config=MCP_CONFIG,
                uuid=BACKUP_UUID,
            )
        ],
    )

    assert coresys.discovery.get(BACKUP_UUID) is other
    assert coresys.discovery.messages_for_app(app_with_discovery.slug) == []
    assert f"uuid {BACKUP_UUID} is already in use" in caplog.text


async def test_restore_app_messages_service_only_once(
    coresys: CoreSys, app_with_discovery: App
):
    """Test a service repeated in a backup only gets a single message.

    Two messages for one service would both be handed to Home Assistant, and
    only one of them can ever be updated or removed again, as send() and
    remove() match on app and service.
    """
    await coresys.discovery.restore_app_messages(
        app_with_discovery,
        [
            Message(
                app=app_with_discovery.slug,
                service="mcp",
                config=MCP_CONFIG,
                uuid=BACKUP_UUID,
            ),
            Message(
                app=app_with_discovery.slug,
                service="mcp",
                config={"url": "http://local-ssh:9999/mcp"},
                uuid="a1b2c3d4e5f60718293a4b5c6d7e8f90",
            ),
        ],
    )

    assert [
        message.uuid
        for message in coresys.discovery.messages_for_app(app_with_discovery.slug)
    ] == [BACKUP_UUID]


async def test_messages_for_app(coresys: CoreSys, app_with_discovery: App):
    """Test listing the messages of a single app."""
    message = await coresys.discovery.send(app_with_discovery, "mcp", dict(MCP_CONFIG))
    other = Message(app="core_mosquitto", service="mqtt", config={})
    coresys.discovery.message_obj[other.uuid] = other

    assert coresys.discovery.messages_for_app(app_with_discovery.slug) == [message]
    assert coresys.discovery.messages_for_app("core_mosquitto") == [other]
    assert coresys.discovery.messages_for_app("local_example") == []
