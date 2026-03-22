"""Binary sensor platform for OBDcast integration.

Creates binary sensor entities for on/off states from the OBDcast device.

Currently implemented:
- Ignition sensor: Indicates whether the vehicle engine is running

The ignition state is derived from battery voltage:
- ON (True): Battery voltage >= 13.0V (alternator charging = engine running)
- OFF (False): Battery voltage < 13.0V (engine off, battery only)

Entity naming:
- Entity ID: binary_sensor.obdcast_{device_id}_ignition
- Name: {vehicle_name} Ignition
"""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OBDcast binary sensors from a config entry.

    Creates the ignition binary sensor entity.

    Args:
        hass: Home Assistant instance
        entry: Config entry for this OBDcast device
        async_add_entities: Callback to register entities
    """
    pass


class OBDcastIgnitionSensor(BinarySensorEntity):
    """Binary sensor for vehicle ignition state.

    Reports True when the engine is running (battery voltage indicates
    alternator is charging).
    """

    def __init__(self, coordinator, device_id: str, vehicle_name: str) -> None:
        """Initialize the ignition sensor.

        Args:
            coordinator: OBDcastCoordinator instance
            device_id: OBDcast device identifier
            vehicle_name: Friendly name for the vehicle
        """
        pass

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return the device class."""
        return BinarySensorDeviceClass.RUNNING

    @property
    def is_on(self) -> bool:
        """Return True if ignition is on (engine running).

        Determined by battery voltage threshold in coordinator.
        """
        pass

    @property
    def device_info(self):
        """Return device info for device registry."""
        pass
