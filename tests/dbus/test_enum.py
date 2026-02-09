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


class TestDBusStrEnum:
    """Tests for DBusStrEnum."""

    def test_known_value(self):
        """Test known value returns the defined member."""
        assert SampleStrEnum("alpha") is SampleStrEnum.ALPHA
        assert SampleStrEnum("beta") is SampleStrEnum.BETA

    def test_unknown_value_returns_pseudo_member(self, caplog):
        """Test unknown value creates a pseudo-member."""
        with caplog.at_level(logging.WARNING):
            result = SampleStrEnum("gamma")

        assert isinstance(result, SampleStrEnum)
        assert result.value == "gamma"
        assert result.name == "gamma"
        assert "Unknown SampleStrEnum value received from D-Bus: gamma" in caplog.text

    def test_unknown_value_str(self):
        """Test unknown value behaves as str."""
        result = SampleStrEnum("gamma")
        assert str(result) == "gamma"
        assert result == "gamma"

    def test_members_not_polluted(self):
        """Test pseudo-members don't appear in __members__ or list()."""
        SampleStrEnum("gamma")
        assert "gamma" not in SampleStrEnum.__members__
        assert set(SampleStrEnum) == {SampleStrEnum.ALPHA, SampleStrEnum.BETA}

    def test_non_str_raises_value_error(self):
        """Test non-string values raise ValueError."""
        with pytest.raises(ValueError):
            SampleStrEnum(123)

    def test_hash_consistency(self):
        """Test pseudo-members hash like their string value."""
        result = SampleStrEnum("gamma")
        assert hash(result) == hash("gamma")
        assert {result: True}["gamma"]

    def test_match_known(self):
        """Test match statement with known value."""
        val = SampleStrEnum("alpha")
        match val:
            case SampleStrEnum.ALPHA:
                matched = "alpha"
            case _:
                matched = "default"
        assert matched == "alpha"

    def test_match_unknown_falls_to_default(self):
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


class TestDBusIntEnum:
    """Tests for DBusIntEnum."""

    def test_known_value(self):
        """Test known value returns the defined member."""
        assert SampleIntEnum(1) is SampleIntEnum.ONE
        assert SampleIntEnum(2) is SampleIntEnum.TWO

    def test_unknown_value_returns_pseudo_member(self, caplog):
        """Test unknown value creates a pseudo-member."""
        with caplog.at_level(logging.WARNING):
            result = SampleIntEnum(999)

        assert isinstance(result, SampleIntEnum)
        assert result.value == 999
        assert result.name == "UNKNOWN_999"
        assert "Unknown SampleIntEnum value received from D-Bus: 999" in caplog.text

    def test_unknown_value_int(self):
        """Test unknown value behaves as int."""
        result = SampleIntEnum(999)
        assert int(result) == 999
        assert result == 999

    def test_members_not_polluted(self):
        """Test pseudo-members don't appear in __members__ or list()."""
        SampleIntEnum(999)
        assert "UNKNOWN_999" not in SampleIntEnum.__members__
        assert set(SampleIntEnum) == {SampleIntEnum.ONE, SampleIntEnum.TWO}

    def test_non_int_raises_value_error(self):
        """Test non-integer values raise ValueError."""
        with pytest.raises(ValueError):
            SampleIntEnum("abc")

    def test_hash_consistency(self):
        """Test pseudo-members hash like their int value."""
        result = SampleIntEnum(999)
        assert hash(result) == hash(999)
        assert {result: True}[999]

    def test_match_known(self):
        """Test match statement with known value."""
        val = SampleIntEnum(1)
        match val:
            case SampleIntEnum.ONE:
                matched = "one"
            case _:
                matched = "default"
        assert matched == "one"

    def test_match_unknown_falls_to_default(self):
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


class TestDBusEnumIntegration:
    """Integration tests verifying actual D-Bus enums handle unknown values."""

    def test_device_type_unknown(self):
        """Test DeviceType handles unknown device types."""
        result = DeviceType(999)
        assert isinstance(result, DeviceType)
        assert result.value == 999
        assert result != DeviceType.UNKNOWN

    def test_device_type_known(self):
        """Test DeviceType still works for known values."""
        assert DeviceType(1) is DeviceType.ETHERNET
        assert DeviceType(2) is DeviceType.WIRELESS

    def test_unit_active_state_unknown(self):
        """Test UnitActiveState handles unknown states."""
        result = UnitActiveState("refreshing")
        assert isinstance(result, UnitActiveState)
        assert result.value == "refreshing"

    def test_unit_active_state_known(self):
        """Test UnitActiveState still works for known values."""
        assert UnitActiveState("active") is UnitActiveState.ACTIVE

    def test_rauc_state_unknown(self):
        """Test RaucState handles unknown states."""
        result = RaucState("testing")
        assert isinstance(result, RaucState)
        assert result.value == "testing"

    def test_connection_type_unknown(self):
        """Test ConnectionType handles unknown types."""
        result = ConnectionType("802-11-olpc-mesh")
        assert isinstance(result, ConnectionType)
        assert result.value == "802-11-olpc-mesh"

    def test_connection_state_unknown(self):
        """Test ConnectionState handles unknown states."""
        result = ConnectionState(99)
        assert isinstance(result, ConnectionState)
        assert result.value == 99

    def test_connectivity_state_unknown(self):
        """Test ConnectivityState handles unknown states."""
        result = ConnectivityState(99)
        assert isinstance(result, ConnectivityState)
        assert result.value == 99

    def test_wireless_method_type_unknown(self):
        """Test WirelessMethodType handles unknown types."""
        result = WirelessMethodType(99)
        assert isinstance(result, WirelessMethodType)
        assert result.value == 99

    def test_interface_method_unknown(self):
        """Test InterfaceMethod handles unknown methods."""
        result = InterfaceMethod("shared")
        assert isinstance(result, InterfaceMethod)
        assert result.value == "shared"

    def test_multicast_protocol_enabled_unknown(self):
        """Test MulticastProtocolEnabled handles unknown values."""
        result = MulticastProtocolEnabled("maybe")
        assert isinstance(result, MulticastProtocolEnabled)
        assert result.value == "maybe"

    def test_dns_over_tls_enabled_unknown(self):
        """Test DNSOverTLSEnabled handles unknown values."""
        result = DNSOverTLSEnabled("strict")
        assert isinstance(result, DNSOverTLSEnabled)
        assert result.value == "strict"

    def test_partition_table_type_unknown(self):
        """Test PartitionTableType handles unknown types."""
        result = PartitionTableType("mbr")
        assert isinstance(result, PartitionTableType)
        assert result.value == "mbr"


# -- Sentry reporting tests --


class TestSentryReporting:
    """Tests for Sentry event reporting on unknown values."""

    @patch("supervisor.dbus.enum.sentry_sdk")
    def test_unknown_str_reports_to_sentry(self, mock_sentry):
        """Test unknown StrEnum value is reported to Sentry."""
        mock_sentry.is_initialized.return_value = True
        SampleStrEnum("delta")
        mock_sentry.capture_message.assert_called_once_with(
            "Unknown SampleStrEnum value received from D-Bus: delta", level="warning"
        )

    @patch("supervisor.dbus.enum.sentry_sdk")
    def test_unknown_int_reports_to_sentry(self, mock_sentry):
        """Test unknown IntEnum value is reported to Sentry."""
        mock_sentry.is_initialized.return_value = True
        SampleIntEnum(777)
        mock_sentry.capture_message.assert_called_once_with(
            "Unknown SampleIntEnum value received from D-Bus: 777", level="warning"
        )

    @patch("supervisor.dbus.enum.sentry_sdk")
    def test_duplicate_not_reported_twice(self, mock_sentry):
        """Test the same unknown value is only reported to Sentry once."""
        mock_sentry.is_initialized.return_value = True
        SampleIntEnum(888)
        SampleIntEnum(888)
        SampleIntEnum(888)
        mock_sentry.capture_message.assert_called_once()

    @patch("supervisor.dbus.enum.sentry_sdk")
    def test_different_values_each_reported(self, mock_sentry):
        """Test different unknown values are each reported separately."""
        mock_sentry.is_initialized.return_value = True
        SampleIntEnum(100)
        SampleIntEnum(200)
        assert mock_sentry.capture_message.call_count == 2

    @patch("supervisor.dbus.enum.sentry_sdk")
    def test_not_reported_when_sentry_not_initialized(self, mock_sentry):
        """Test nothing is reported when Sentry is not initialized."""
        mock_sentry.is_initialized.return_value = False
        SampleStrEnum("epsilon")
        mock_sentry.capture_message.assert_not_called()

    @patch("supervisor.dbus.enum.sentry_sdk")
    def test_known_value_not_reported(self, mock_sentry):
        """Test known values don't trigger Sentry reports."""
        mock_sentry.is_initialized.return_value = True
        SampleStrEnum("alpha")
        SampleIntEnum(1)
        mock_sentry.capture_message.assert_not_called()
