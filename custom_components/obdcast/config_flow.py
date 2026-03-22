"""Config flow for OBDcast integration.

Handles the UI-based configuration wizard for setting up OBDcast devices.

Flow steps:
1. Transport selection (MQTT or Webhook)
2. Device configuration:
   - Device ID (must match OBDcast firmware)
   - Vehicle name (friendly name for HA)
   - MQTT topic prefix (MQTT only)

For webhook transport, the flow also displays the generated webhook URL
that must be configured in the OBDcast firmware.

Validation:
- Device ID: required, alphanumeric, unique across entries
- Vehicle name: required
- Topic prefix: optional, defaults to 'obdcast'
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_DEVICE_ID,
    CONF_MQTT_TOPIC_PREFIX,
    CONF_TRANSPORT,
    CONF_VEHICLE_NAME,
    DEFAULT_MQTT_TOPIC_PREFIX,
    DOMAIN,
    TRANSPORT_MQTT,
    TRANSPORT_WEBHOOK,
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
        """Handle the initial step - transport selection.

        Presents the user with a choice between MQTT and Webhook transport.
        """
        # TODO: Implement transport selection step
        # TODO: Route to MQTT or Webhook config step based on selection
        pass

    async def async_step_mqtt(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle MQTT configuration step.

        Collects:
        - Device ID
        - Vehicle name
        - MQTT topic prefix (optional)
        """
        # TODO: Implement MQTT configuration form
        # TODO: Validate device ID uniqueness
        # TODO: Create config entry
        pass

    async def async_step_webhook(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle Webhook configuration step.

        Collects:
        - Device ID
        - Vehicle name

        Displays the generated webhook URL for firmware configuration.
        """
        # TODO: Implement webhook configuration form
        # TODO: Generate and display webhook URL
        # TODO: Validate device ID uniqueness
        # TODO: Create config entry
        pass
