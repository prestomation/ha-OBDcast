"""Tests for OBDcast config flow."""
from __future__ import annotations

import hashlib
import hmac as hmac_lib
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.obdcast.const import (
    CONF_DEVICE_ID,
    CONF_MQTT_TOPIC_PREFIX,
    CONF_TRANSPORT,
    CONF_VEHICLE_NAME,
    CONF_WEBHOOK_HMAC_ENABLED,
    CONF_WEBHOOK_HMAC_SECRET,
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

    @pytest.mark.asyncio
    async def test_hmac_secret_forces_hmac_enabled(self):
        """Providing a non-empty HMAC secret should force hmac_enabled=True."""
        flow = make_flow()
        user_input = {
            CONF_VEHICLE_NAME: "Car",
            CONF_DEVICE_ID: "dev-hmac-1",
            CONF_WEBHOOK_HMAC_SECRET: "mysecret",
            CONF_WEBHOOK_HMAC_ENABLED: False,  # should be overridden
        }
        await flow.async_step_webhook(user_input)
        call_kwargs = flow.async_create_entry.call_args[1]
        assert call_kwargs["data"][CONF_WEBHOOK_HMAC_ENABLED] is True
        assert call_kwargs["data"][CONF_WEBHOOK_HMAC_SECRET] == "mysecret"

    @pytest.mark.asyncio
    async def test_no_secret_keeps_hmac_disabled(self):
        """Leaving HMAC secret blank keeps hmac_enabled=False."""
        flow = make_flow()
        user_input = {
            CONF_VEHICLE_NAME: "Car",
            CONF_DEVICE_ID: "dev-hmac-2",
            CONF_WEBHOOK_HMAC_SECRET: "",
            CONF_WEBHOOK_HMAC_ENABLED: False,
        }
        await flow.async_step_webhook(user_input)
        call_kwargs = flow.async_create_entry.call_args[1]
        assert call_kwargs["data"][CONF_WEBHOOK_HMAC_ENABLED] is False
        assert call_kwargs["data"][CONF_WEBHOOK_HMAC_SECRET] == ""


def _make_hmac_sig(secret: str, body: bytes) -> str:
    """Compute the HMAC-SHA256 hex digest for a webhook body."""
    return hmac_lib.new(secret.encode(), body, hashlib.sha256).hexdigest()


def _make_mock_request(body: bytes, sig: str | None = None):
    """Build a mock aiohttp Request with the given body and optional signature."""
    request = MagicMock()
    request.read = AsyncMock(return_value=body)

    headers = {}
    if sig is not None:
        headers["X-OBDcast-Signature"] = sig
    request.headers = headers
    return request


def _make_mock_entry(hmac_enabled: bool, hmac_secret: str, device_id: str = "dev-test"):
    """Build a mock ConfigEntry with the given HMAC settings."""
    entry = MagicMock()
    entry.data = {
        "device_id": device_id,
        "vehicle_name": "Test Car",
        "transport": TRANSPORT_WEBHOOK,
        "webhook_id": "obdcast_testhook",
        CONF_WEBHOOK_HMAC_ENABLED: hmac_enabled,
        CONF_WEBHOOK_HMAC_SECRET: hmac_secret,
    }
    return entry


async def _invoke_webhook_handler(entry, request):
    """
    Simulate async_setup_entry registering the webhook handler, then call it.

    We capture the handler passed to webhook.async_register and invoke it directly.
    """
    import custom_components.obdcast as obdcast_module

    hass = MagicMock()
    hass.data = {}
    coordinator = MagicMock()
    coordinator.async_receive_data = MagicMock()

    captured_handler = None

    def fake_async_register(hass_, domain, name, wh_id, handler):
        nonlocal captured_handler
        captured_handler = handler

    with (
        patch("custom_components.obdcast.webhook.async_register", side_effect=fake_async_register),
        patch("custom_components.obdcast.webhook.async_unregister"),
        patch("custom_components.obdcast.OBDcastCoordinator", return_value=coordinator),
        patch.object(
            type(entry),
            "async_on_unload",
            lambda self, cb: None,
            create=True,
        ),
    ):
        # Patch async_forward_entry_setups to avoid full HA stack
        hass.config_entries = MagicMock()
        hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)

        await obdcast_module.async_setup_entry(hass, entry)

    assert captured_handler is not None, "webhook handler was not registered"
    await captured_handler(hass, "obdcast_testhook", request)
    return coordinator


class TestWebhookHmacVerification:
    """Integration-style tests for HMAC verification in the webhook handler."""

    SECRET = "super-secret-key"
    PAYLOAD = json.dumps({"obd.speed": 42}).encode()

    @pytest.mark.asyncio
    async def test_correct_signature_is_accepted(self):
        """A POST with a valid HMAC signature should be processed."""
        sig = _make_hmac_sig(self.SECRET, self.PAYLOAD)
        request = _make_mock_request(self.PAYLOAD, sig)
        entry = _make_mock_entry(hmac_enabled=True, hmac_secret=self.SECRET)

        coordinator = await _invoke_webhook_handler(entry, request)

        coordinator.async_receive_data.assert_called_once_with({"obd.speed": 42})

    @pytest.mark.asyncio
    async def test_wrong_signature_is_rejected(self):
        """A POST with an incorrect HMAC signature should be rejected."""
        request = _make_mock_request(self.PAYLOAD, "badsignature")
        entry = _make_mock_entry(hmac_enabled=True, hmac_secret=self.SECRET)

        coordinator = await _invoke_webhook_handler(entry, request)

        coordinator.async_receive_data.assert_not_called()

    @pytest.mark.asyncio
    async def test_missing_signature_is_rejected_when_hmac_enabled(self):
        """A POST without a signature header should be rejected when HMAC is enabled."""
        request = _make_mock_request(self.PAYLOAD, sig=None)
        entry = _make_mock_entry(hmac_enabled=True, hmac_secret=self.SECRET)

        coordinator = await _invoke_webhook_handler(entry, request)

        coordinator.async_receive_data.assert_not_called()

    @pytest.mark.asyncio
    async def test_no_signature_accepted_when_hmac_disabled(self):
        """A POST without a signature should be accepted when HMAC is disabled (default)."""
        request = _make_mock_request(self.PAYLOAD, sig=None)
        entry = _make_mock_entry(hmac_enabled=False, hmac_secret="")

        coordinator = await _invoke_webhook_handler(entry, request)

        coordinator.async_receive_data.assert_called_once_with({"obd.speed": 42})
