"""Tests for OBDcast config flow."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.obdcast.const import (
    CONF_DEVICE_ID,
    CONF_MQTT_TOPIC_PREFIX,
    CONF_TRANSPORT,
    CONF_VEHICLE_NAME,
    DEFAULT_MQTT_TOPIC_PREFIX,
    DOMAIN,
    TRANSPORT_MQTT,
    TRANSPORT_WEBHOOK,
)


class MockFlowResult:
    """Simple mock for FlowResult."""

    def __init__(self, type_, **kwargs):
        self.type = type_
        self.data = kwargs


def make_flow():
    """Create a config flow instance with mocked internals."""
    from custom_components.obdcast.config_flow import OBDcastConfigFlow

    flow = OBDcastConfigFlow()
    flow.hass = MagicMock()
    flow.context = {}
    flow._abort_if_unique_id_configured = MagicMock()
    flow.async_set_unique_id = AsyncMock()
    flow.async_show_form = MagicMock(return_value={"type": "form"})
    flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})
    return flow


class TestUserStep:
    """Test the initial transport selection step."""

    @pytest.mark.asyncio
    async def test_shows_form_when_no_input(self):
        flow = make_flow()
        result = await flow.async_step_user(None)
        flow.async_show_form.assert_called_once()
        assert flow.async_show_form.call_args[1]["step_id"] == "user"

    @pytest.mark.asyncio
    async def test_mqtt_transport_routes_to_mqtt_step(self):
        flow = make_flow()
        flow.async_step_mqtt = AsyncMock(return_value={"type": "form"})
        result = await flow.async_step_user({CONF_TRANSPORT: TRANSPORT_MQTT})
        flow.async_step_mqtt.assert_called_once()

    @pytest.mark.asyncio
    async def test_webhook_transport_routes_to_webhook_step(self):
        flow = make_flow()
        flow.async_step_webhook = AsyncMock(return_value={"type": "form"})
        result = await flow.async_step_user({CONF_TRANSPORT: TRANSPORT_WEBHOOK})
        flow.async_step_webhook.assert_called_once()


class TestMqttStep:
    """Test MQTT configuration step."""

    @pytest.mark.asyncio
    async def test_shows_form_when_no_input(self):
        flow = make_flow()
        result = await flow.async_step_mqtt(None)
        flow.async_show_form.assert_called_once()
        assert flow.async_show_form.call_args[1]["step_id"] == "mqtt"

    @pytest.mark.asyncio
    async def test_creates_entry_with_valid_input(self):
        flow = make_flow()
        user_input = {
            CONF_VEHICLE_NAME: "Tesla",
            CONF_DEVICE_ID: "obdcast-001",
            CONF_MQTT_TOPIC_PREFIX: "obdcast",
        }
        result = await flow.async_step_mqtt(user_input)
        flow.async_create_entry.assert_called_once()
        call_kwargs = flow.async_create_entry.call_args[1]
        assert call_kwargs["title"] == "Tesla"
        assert call_kwargs["data"][CONF_TRANSPORT] == TRANSPORT_MQTT
        assert call_kwargs["data"][CONF_DEVICE_ID] == "obdcast-001"
        assert call_kwargs["data"][CONF_VEHICLE_NAME] == "Tesla"
        assert call_kwargs["data"][CONF_MQTT_TOPIC_PREFIX] == "obdcast"

    @pytest.mark.asyncio
    async def test_default_topic_prefix(self):
        flow = make_flow()
        user_input = {
            CONF_VEHICLE_NAME: "Car",
            CONF_DEVICE_ID: "dev-123",
        }
        await flow.async_step_mqtt(user_input)
        call_kwargs = flow.async_create_entry.call_args[1]
        assert call_kwargs["data"][CONF_MQTT_TOPIC_PREFIX] == DEFAULT_MQTT_TOPIC_PREFIX

    @pytest.mark.asyncio
    async def test_strips_whitespace(self):
        flow = make_flow()
        user_input = {
            CONF_VEHICLE_NAME: "  Tesla  ",
            CONF_DEVICE_ID: "  obdcast-001  ",
            CONF_MQTT_TOPIC_PREFIX: "  myprefix  ",
        }
        await flow.async_step_mqtt(user_input)
        call_kwargs = flow.async_create_entry.call_args[1]
        assert call_kwargs["data"][CONF_VEHICLE_NAME] == "Tesla"
        assert call_kwargs["data"][CONF_DEVICE_ID] == "obdcast-001"
        assert call_kwargs["data"][CONF_MQTT_TOPIC_PREFIX] == "myprefix"

    @pytest.mark.asyncio
    async def test_sets_unique_id(self):
        flow = make_flow()
        user_input = {
            CONF_VEHICLE_NAME: "Tesla",
            CONF_DEVICE_ID: "obdcast-001",
        }
        await flow.async_step_mqtt(user_input)
        flow.async_set_unique_id.assert_called_once_with("obdcast-001")


class TestWebhookStep:
    """Test webhook configuration step."""

    @pytest.mark.asyncio
    async def test_shows_form_when_no_input(self):
        flow = make_flow()
        result = await flow.async_step_webhook(None)
        flow.async_show_form.assert_called_once()
        assert flow.async_show_form.call_args[1]["step_id"] == "webhook"

    @pytest.mark.asyncio
    async def test_creates_entry_with_valid_input(self):
        flow = make_flow()
        user_input = {
            CONF_VEHICLE_NAME: "Family Car",
            CONF_DEVICE_ID: "obdcast-002",
        }
        result = await flow.async_step_webhook(user_input)
        flow.async_create_entry.assert_called_once()
        call_kwargs = flow.async_create_entry.call_args[1]
        assert call_kwargs["title"] == "Family Car"
        assert call_kwargs["data"][CONF_TRANSPORT] == TRANSPORT_WEBHOOK
        assert call_kwargs["data"][CONF_DEVICE_ID] == "obdcast-002"

    @pytest.mark.asyncio
    async def test_generates_webhook_id(self):
        flow = make_flow()
        user_input = {
            CONF_VEHICLE_NAME: "Car",
            CONF_DEVICE_ID: "dev-789",
        }
        await flow.async_step_webhook(user_input)
        call_kwargs = flow.async_create_entry.call_args[1]
        webhook_id = call_kwargs["data"].get("webhook_id", "")
        assert webhook_id.startswith("obdcast_")
        assert len(webhook_id) > 10

    @pytest.mark.asyncio
    async def test_webhook_ids_are_unique(self):
        """Each entry should get a different webhook ID."""
        flow1 = make_flow()
        flow2 = make_flow()
        user_input = {"vehicle_name": "Car", "device_id": "dev-1"}
        user_input2 = {"vehicle_name": "Car2", "device_id": "dev-2"}

        await flow1.async_step_webhook(user_input)
        await flow2.async_step_webhook(user_input2)

        id1 = flow1.async_create_entry.call_args[1]["data"]["webhook_id"]
        id2 = flow2.async_create_entry.call_args[1]["data"]["webhook_id"]
        assert id1 != id2
