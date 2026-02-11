"""Tests for D-Bus tolerant enum base classes."""

import logging
from unittest.mock import patch

import pytest

from supervisor.dbus.const import (
    ConnectionState,
    ConnectionType,
    ConnectivityState,
    DeviceType,
    DNSOverTLSEnabled,
    InterfaceMethod,
    MulticastProtocolEnabled,
    RaucState,
    UnitActiveState,
    WirelessMethodType,
)
from supervisor.dbus.enum import DBusIntEnum, DBusStrEnum, _reported
from supervisor.dbus.udisks2.const import PartitionTableType


@pytest.fixture(autouse=True)
def _clear_reported():
    """Clear the deduplication set between tests."""
    _reported.clear()


# -- Test fixtures: concrete subclasses for isolated testing --


class SampleStrEnum(DBusStrEnum):
    """Sample StrEnum for testing."""

    ALPHA = "alpha"
    BETA = "beta"


class SampleIntEnum(DBusIntEnum):
    """Sample IntEnum for testing."""

    ONE = 1
    TWO = 2


# -- DBusStrEnum tests --


def test_str_known_value():
    """Test known value returns the defined member."""
    assert SampleStrEnum("alpha") is SampleStrEnum.ALPHA
    assert SampleStrEnum("beta") is SampleStrEnum.BETA


def test_str_unknown_value_returns_pseudo_member(caplog):
    """Test unknown value creates a pseudo-member."""
    with caplog.at_level(logging.WARNING):
        result = SampleStrEnum("gamma")

    assert isinstance(result, SampleStrEnum)
    assert result.value == "gamma"
    assert result.name == "gamma"
    assert "Unknown SampleStrEnum value received from D-Bus: gamma" in caplog.text


def test_str_unknown_value_str():
    """Test unknown value behaves as str."""
    result = SampleStrEnum("gamma")
    assert str(result) == "gamma"
    assert result == "gamma"


def test_str_members_not_polluted():
    """Test pseudo-members don't appear in __members__ or list()."""
    SampleStrEnum("gamma")
    assert "gamma" not in SampleStrEnum.__members__
    assert set(SampleStrEnum) == {SampleStrEnum.ALPHA, SampleStrEnum.BETA}


def test_str_non_str_raises_value_error():
    """Test non-string values raise ValueError."""
    with pytest.raises(ValueError):
        SampleStrEnum(123)


def test_str_hash_consistency():
    """Test pseudo-members hash like their string value."""
    result = SampleStrEnum("gamma")
    assert hash(result) == hash("gamma")
    assert {result: True}["gamma"]


def test_str_match_known():
    """Test match statement with known value."""
    val = SampleStrEnum("alpha")
    match val:
        case SampleStrEnum.ALPHA:
            matched = "alpha"
        case _:
            matched = "default"
    assert matched == "alpha"


def test_str_match_unknown_falls_to_default():
    """Test match statement with unknown value falls to default."""
    val = SampleStrEnum("gamma")
    match val:
        case SampleStrEnum.ALPHA:
            matched = "alpha"
        case SampleStrEnum.BETA:
            matched = "beta"
        case _:
            matched = "default"
    assert matched == "default"


# -- DBusIntEnum tests --


def test_int_known_value():
    """Test known value returns the defined member."""
    assert SampleIntEnum(1) is SampleIntEnum.ONE
    assert SampleIntEnum(2) is SampleIntEnum.TWO


def test_int_unknown_value_returns_pseudo_member(caplog):
    """Test unknown value creates a pseudo-member."""
    with caplog.at_level(logging.WARNING):
        result = SampleIntEnum(999)

    assert isinstance(result, SampleIntEnum)
    assert result.value == 999
    assert result.name == "UNKNOWN_999"
    assert "Unknown SampleIntEnum value received from D-Bus: 999" in caplog.text


def test_int_unknown_value_int():
    """Test unknown value behaves as int."""
    result = SampleIntEnum(999)
    assert int(result) == 999
    assert result == 999


def test_int_members_not_polluted():
    """Test pseudo-members don't appear in __members__ or list()."""
    SampleIntEnum(999)
    assert "UNKNOWN_999" not in SampleIntEnum.__members__
    assert set(SampleIntEnum) == {SampleIntEnum.ONE, SampleIntEnum.TWO}


def test_int_non_int_raises_value_error():
    """Test non-integer values raise ValueError."""
    with pytest.raises(ValueError):
        SampleIntEnum("abc")


def test_int_hash_consistency():
    """Test pseudo-members hash like their int value."""
    result = SampleIntEnum(999)
    assert hash(result) == hash(999)
    assert {result: True}[999]


def test_int_match_known():
    """Test match statement with known value."""
    val = SampleIntEnum(1)
    match val:
        case SampleIntEnum.ONE:
            matched = "one"
        case _:
            matched = "default"
    assert matched == "one"


def test_int_match_unknown_falls_to_default():
    """Test match statement with unknown value falls to default."""
    val = SampleIntEnum(999)
    match val:
        case SampleIntEnum.ONE:
            matched = "one"
        case SampleIntEnum.TWO:
            matched = "two"
        case _:
            matched = "default"
    assert matched == "default"


# -- Integration tests with actual D-Bus enums --


def test_device_type_unknown():
    """Test DeviceType handles unknown device types."""
    result = DeviceType(999)
    assert isinstance(result, DeviceType)
    assert result.value == 999
    assert result != DeviceType.UNKNOWN


def test_device_type_known():
    """Test DeviceType still works for known values."""
    assert DeviceType(1) is DeviceType.ETHERNET
    assert DeviceType(2) is DeviceType.WIRELESS


def test_unit_active_state_unknown():
    """Test UnitActiveState handles unknown states."""
    result = UnitActiveState("refreshing")
    assert isinstance(result, UnitActiveState)
    assert result.value == "refreshing"


def test_unit_active_state_known():
    """Test UnitActiveState still works for known values."""
    assert UnitActiveState("active") is UnitActiveState.ACTIVE


def test_rauc_state_unknown():
    """Test RaucState handles unknown states."""
    result = RaucState("testing")
    assert isinstance(result, RaucState)
    assert result.value == "testing"


def test_connection_type_unknown():
    """Test ConnectionType handles unknown types."""
    result = ConnectionType("802-11-olpc-mesh")
    assert isinstance(result, ConnectionType)
    assert result.value == "802-11-olpc-mesh"


def test_connection_state_unknown():
    """Test ConnectionState handles unknown states."""
    result = ConnectionState(99)
    assert isinstance(result, ConnectionState)
    assert result.value == 99


def test_connectivity_state_unknown():
    """Test ConnectivityState handles unknown states."""
    result = ConnectivityState(99)
    assert isinstance(result, ConnectivityState)
    assert result.value == 99


def test_wireless_method_type_unknown():
    """Test WirelessMethodType handles unknown types."""
    result = WirelessMethodType(99)
    assert isinstance(result, WirelessMethodType)
    assert result.value == 99


def test_interface_method_unknown():
    """Test InterfaceMethod handles unknown methods."""
    result = InterfaceMethod("shared")
    assert isinstance(result, InterfaceMethod)
    assert result.value == "shared"


def test_multicast_protocol_enabled_unknown():
    """Test MulticastProtocolEnabled handles unknown values."""
    result = MulticastProtocolEnabled("maybe")
    assert isinstance(result, MulticastProtocolEnabled)
    assert result.value == "maybe"


def test_dns_over_tls_enabled_unknown():
    """Test DNSOverTLSEnabled handles unknown values."""
    result = DNSOverTLSEnabled("strict")
    assert isinstance(result, DNSOverTLSEnabled)
    assert result.value == "strict"


def test_partition_table_type_unknown():
    """Test PartitionTableType handles unknown types."""
    result = PartitionTableType("mbr")
    assert isinstance(result, PartitionTableType)
    assert result.value == "mbr"


# -- Sentry reporting tests --


@patch("supervisor.dbus.enum.fire_and_forget_capture_message")
def test_unknown_str_reports_to_sentry(mock_capture):
    """Test unknown StrEnum value is reported to Sentry."""
    SampleStrEnum("delta")
    mock_capture.assert_called_once_with(
        "Unknown SampleStrEnum value received from D-Bus: delta"
    )


@patch("supervisor.dbus.enum.fire_and_forget_capture_message")
def test_unknown_int_reports_to_sentry(mock_capture):
    """Test unknown IntEnum value is reported to Sentry."""
    SampleIntEnum(777)
    mock_capture.assert_called_once_with(
        "Unknown SampleIntEnum value received from D-Bus: 777"
    )


@patch("supervisor.dbus.enum.fire_and_forget_capture_message")
def test_duplicate_not_reported_twice(mock_capture):
    """Test the same unknown value is only reported to Sentry once."""
    SampleIntEnum(888)
    SampleIntEnum(888)
    SampleIntEnum(888)
    mock_capture.assert_called_once()


@patch("supervisor.dbus.enum.fire_and_forget_capture_message")
def test_different_values_each_reported(mock_capture):
    """Test different unknown values are each reported separately."""
    SampleIntEnum(100)
    SampleIntEnum(200)
    assert mock_capture.call_count == 2


@patch("supervisor.dbus.enum.fire_and_forget_capture_message")
def test_known_value_not_reported(mock_capture):
    """Test known values don't trigger Sentry reports."""
    SampleStrEnum("alpha")
    SampleIntEnum(1)
    mock_capture.assert_not_called()
