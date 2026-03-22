"""OBDcast integration for Home Assistant."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components import webhook
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_DEVICE_ID,
    CONF_MQTT_TOPIC_PREFIX,
    CONF_TRANSPORT,
    CONF_VEHICLE_NAME,
    CONF_WEBHOOK_ID,
    DEFAULT_MQTT_TOPIC_PREFIX,
    DOMAIN,
    PLATFORMS,
    TRANSPORT_MQTT,
    TRANSPORT_WEBHOOK,
)
from .coordinator import OBDcastCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OBDcast from a config entry."""
    device_id: str = entry.data[CONF_DEVICE_ID]
    vehicle_name: str = entry.data[CONF_VEHICLE_NAME]
    transport: str = entry.data[CONF_TRANSPORT]

    coordinator = OBDcastCoordinator(hass, device_id, vehicle_name)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    if transport == TRANSPORT_MQTT:
        from homeassistant.components import mqtt  # noqa: PLC0415

        topic_prefix = entry.data.get(CONF_MQTT_TOPIC_PREFIX, DEFAULT_MQTT_TOPIC_PREFIX)
        topic = f"{topic_prefix}/{device_id}/telemetry"
        _LOGGER.info("OBDcast %s subscribing to MQTT topic: %s", device_id, topic)

        async def async_mqtt_message_received(msg: Any) -> None:
            """Handle incoming MQTT message."""
            await coordinator.async_receive_raw(msg.payload)

        entry.async_on_unload(
            await mqtt.async_subscribe(hass, topic, async_mqtt_message_received)
        )

    elif transport == TRANSPORT_WEBHOOK:
        webhook_id: str = entry.data[CONF_WEBHOOK_ID]
        _LOGGER.info("OBDcast %s registering webhook: %s", device_id, webhook_id)

        async def async_handle_webhook(
            hass: HomeAssistant, webhook_id: str, request: Any
        ) -> None:
            """Handle incoming webhook POST."""
            try:
                payload = await request.json()
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.error("OBDcast %s webhook failed to parse JSON: %s", device_id, err)
                return
            if not isinstance(payload, dict):
                _LOGGER.error("OBDcast %s webhook payload is not a JSON object", device_id)
                return
            await coordinator.async_receive_data(payload)

        webhook.async_register(
            hass,
            DOMAIN,
            f"OBDcast {vehicle_name}",
            webhook_id,
            async_handle_webhook,
        )

        def _unregister_webhook() -> None:
            webhook.async_unregister(hass, webhook_id)

        entry.async_on_unload(_unregister_webhook)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an OBDcast config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
