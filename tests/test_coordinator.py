"""Tests for OBDcast coordinator — data parsing and key lookup."""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class MockHomeAssistant:
    """Minimal HA stub for coordinator tests."""

    def __init__(self):
        self.loop = None
        self._listeners = []
        self.data = {}

    def async_add_executor_job(self, func, *args):
        return func(*args)


@pytest.fixture
def mock_hass():
    return MockHomeAssistant()


@pytest.fixture
def coordinator(mock_hass):
    """Create a coordinator with a mocked HA instance."""
    # Patch the parent class __init__ to avoid HA internals
    with patch(
        "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.__init__",
        lambda self, hass, logger, name, update_interval: None,
    ):
        from custom_components.obdcast.coordinator import OBDcastCoordinator

        c = OBDcastCoordinator.__new__(OBDcastCoordinator)
        c.hass = mock_hass
        c.device_id = "obdcast-001"
        c.vehicle_name = "TestCar"
        c.data = {}
        c._last_update = None
        c._listeners = []
        c.logger = MagicMock()
        return c


class TestGetValue:
    """Test dot-notation key path lookup."""

    def test_top_level_key(self, coordinator, sample_payload):
        coordinator.data = sample_payload
        assert coordinator.get_value("ignition") is True
        assert coordinator.get_value("signal_dbm") == -87

    def test_nested_key(self, coordinator, sample_payload):
        coordinator.data = sample_payload
        assert coordinator.get_value("obd.speed") == 65
        assert coordinator.get_value("obd.rpm") == 2100
        assert coordinator.get_value("obd.fuel_pct") == 72
        assert coordinator.get_value("obd.voltage") == 13.8

    def test_gps_nested_key(self, coordinator, sample_payload):
        coordinator.data = sample_payload
        assert coordinator.get_value("gps.lat") == 47.6062
        assert coordinator.get_value("gps.lon") == -122.3321
        assert coordinator.get_value("gps.fix") is True
        assert coordinator.get_value("gps.hdop") == 1.2

    def test_missing_top_level_key(self, coordinator, sample_payload):
        coordinator.data = sample_payload
        assert coordinator.get_value("nonexistent") is None

    def test_missing_nested_key(self, coordinator, sample_payload):
        coordinator.data = sample_payload
        assert coordinator.get_value("obd.nonexistent") is None

    def test_missing_parent_key(self, coordinator, sample_payload):
        coordinator.data = sample_payload
        assert coordinator.get_value("missing.nested.key") is None

    def test_empty_data(self, coordinator):
        coordinator.data = {}
        assert coordinator.get_value("obd.speed") is None

    def test_none_data(self, coordinator):
        coordinator.data = None
        assert coordinator.get_value("obd.speed") is None

    def test_deeply_nested_none_value(self, coordinator):
        coordinator.data = {"obd": {"speed": None}}
        # When value is explicitly None, returns None
        assert coordinator.get_value("obd.speed") is None


class TestPayloadParsing:
    """Test JSON payload parsing."""

    @pytest.mark.asyncio
    async def test_async_receive_raw_valid_json(self, coordinator, sample_payload):
        """Test that valid JSON is parsed correctly."""
        calls = []

        def mock_set_updated(data):
            calls.append(data)
            coordinator.data = data

        coordinator.async_set_updated_data = mock_set_updated

        raw = json.dumps(sample_payload)
        await coordinator.async_receive_raw(raw)

        assert len(calls) == 1
        assert calls[0]["device_id"] == "obdcast-001"
        assert calls[0]["obd"]["speed"] == 65

    @pytest.mark.asyncio
    async def test_async_receive_raw_invalid_json(self, coordinator):
        """Test that invalid JSON is handled gracefully."""
        coordinator.async_set_updated_data = MagicMock()
        coordinator.logger = MagicMock()

        await coordinator.async_receive_raw("not valid json {{{")

        coordinator.async_set_updated_data.assert_not_called()

    @pytest.mark.asyncio
    async def test_async_receive_data_sets_timestamp(self, coordinator, sample_payload):
        """Test that last_update is set when data is received."""
        coordinator.async_set_updated_data = MagicMock()
        assert coordinator._last_update is None

        await coordinator.async_receive_data(sample_payload)
        assert coordinator._last_update is not None

    @pytest.mark.asyncio
    async def test_async_receive_bytes(self, coordinator, sample_payload):
        """Test that bytes payloads are parsed correctly."""
        calls = []

        def mock_set_updated(data):
            calls.append(data)
            coordinator.data = data

        coordinator.async_set_updated_data = mock_set_updated

        raw = json.dumps(sample_payload).encode("utf-8")
        await coordinator.async_receive_raw(raw)
        assert len(calls) == 1
