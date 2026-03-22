"""OBDcast integration for Home Assistant.

This is the main entry point for the OBDcast integration. It handles:
- Integration setup and teardown via async_setup_entry/async_unload_entry
- Platform forwarding to sensor, binary_sensor, and device_tracker
- Coordinator initialization based on transport mode (MQTT or Webhook)
- Webhook registration/deregistration for webhook transport
- MQTT subscription setup for MQTT transport

The integration follows Home Assistant's config entry pattern for
UI-based configuration without YAML.
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OBDcast from a config entry.

    This function:
    1. Creates the OBDcastCoordinator for this device
    2. Registers webhook or MQTT subscription based on transport
    3. Forwards setup to all entity platforms

    Args:
        hass: Home Assistant instance
        entry: Config entry for this OBDcast device

    Returns:
        True if setup was successful
    """
    # TODO: Initialize coordinator
    # TODO: Set up transport (webhook or MQTT)
    # TODO: Store coordinator in hass.data
    # TODO: Forward to platforms
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an OBDcast config entry.

    Cleans up:
    - Webhook registration (if webhook transport)
    - MQTT subscriptions (if MQTT transport)
    - Coordinator and entity resources

    Args:
        hass: Home Assistant instance
        entry: Config entry being unloaded

    Returns:
        True if unload was successful
    """
    # TODO: Unregister webhook/MQTT
    # TODO: Unload platforms
    # TODO: Clean up hass.data
    return True
