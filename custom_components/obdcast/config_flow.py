"""Config flow for OBDcast integration."""
from __future__ import annotations

import secrets
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_DEVICE_ID,
    CONF_MQTT_TOPIC_PREFIX,
    CONF_TRANSPORT,
    CONF_VEHICLE_NAME,
    CONF_WEBHOOK_ID,
    DEFAULT_MQTT_TOPIC_PREFIX,
    DOMAIN,
    TRANSPORT_MQTT,
    TRANSPORT_WEBHOOK,
)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TRANSPORT, default=TRANSPORT_MQTT): vol.In(
            [TRANSPORT_MQTT, TRANSPORT_WEBHOOK]
        ),
    }
)

STEP_MQTT_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_VEHICLE_NAME): str,
        vol.Required(CONF_DEVICE_ID): str,
        vol.Optional(CONF_MQTT_TOPIC_PREFIX, default=DEFAULT_MQTT_TOPIC_PREFIX): str,
    }
)

STEP_WEBHOOK_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_VEHICLE_NAME): str,
        vol.Required(CONF_DEVICE_ID): str,
    }
)


class OBDcastConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OBDcast."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._transport: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step — transport selection."""
        if user_input is not None:
            self._transport = user_input[CONF_TRANSPORT]
            if self._transport == TRANSPORT_MQTT:
                return await self.async_step_mqtt()
            return await self.async_step_webhook()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
        )

    async def async_step_mqtt(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle MQTT configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            device_id = user_input[CONF_DEVICE_ID].strip()
            vehicle_name = user_input[CONF_VEHICLE_NAME].strip()
            topic_prefix = user_input.get(CONF_MQTT_TOPIC_PREFIX, DEFAULT_MQTT_TOPIC_PREFIX).strip()

            # Check unique device_id across entries
            await self.async_set_unique_id(device_id)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=vehicle_name,
                data={
                    CONF_TRANSPORT: TRANSPORT_MQTT,
                    CONF_VEHICLE_NAME: vehicle_name,
                    CONF_DEVICE_ID: device_id,
                    CONF_MQTT_TOPIC_PREFIX: topic_prefix,
                },
            )

        return self.async_show_form(
            step_id="mqtt",
            data_schema=STEP_MQTT_SCHEMA,
            errors=errors,
        )

    async def async_step_webhook(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle Webhook configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            device_id = user_input[CONF_DEVICE_ID].strip()
            vehicle_name = user_input[CONF_VEHICLE_NAME].strip()

            await self.async_set_unique_id(device_id)
            self._abort_if_unique_id_configured()

            webhook_id = f"obdcast_{secrets.token_hex(16)}"

            return self.async_create_entry(
                title=vehicle_name,
                data={
                    CONF_TRANSPORT: TRANSPORT_WEBHOOK,
                    CONF_VEHICLE_NAME: vehicle_name,
                    CONF_DEVICE_ID: device_id,
                    CONF_WEBHOOK_ID: webhook_id,
                },
            )

        return self.async_show_form(
            step_id="webhook",
            data_schema=STEP_WEBHOOK_SCHEMA,
            errors=errors,
            description_placeholders={
                "webhook_info": "A unique webhook URL will be generated after setup."
            },
        )
