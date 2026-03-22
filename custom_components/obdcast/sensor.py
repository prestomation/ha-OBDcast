"""Sensor platform for OBDcast integration.

Creates sensor entities for all telemetry data from the OBDcast device:

OBD-II Sensors:
- Speed (km/h)
- RPM
- Fuel Level (%)
- Coolant Temperature (°C)
- Engine Load (%)
- Throttle Position (%)

GPS Sensors:
- Altitude (m)
- GPS Speed (km/h)
- Heading (°)
- GPS Accuracy (fix quality)

Device Sensors:
- Battery Voltage (V)
- Device Temperature (°C)
- Acceleration (m/s²)

All sensors use the coordinator for data updates. They don't poll
independently - they subscribe to coordinator updates.

Entity naming convention:
- Entity ID: sensor.obdcast_{device_id}_{sensor_type}
- Name: {vehicle_name} {Sensor Name}
"""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
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
    """Set up OBDcast sensors from a config entry.

    Creates all sensor entities and registers them with Home Assistant.

    Args:
        hass: Home Assistant instance
        entry: Config entry for this OBDcast device
        async_add_entities: Callback to register entities
    """
    pass


class OBDcastSensor(SensorEntity):
    """Base sensor entity for OBDcast telemetry.

    All OBDcast sensors inherit from this base class which provides:
    - Coordinator subscription
    - Device info for registry
    - Common property implementations
    """

    def __init__(self, coordinator, device_id: str, vehicle_name: str) -> None:
        """Initialize the sensor.

        Args:
            coordinator: OBDcastCoordinator instance
            device_id: OBDcast device identifier
            vehicle_name: Friendly name for the vehicle
        """
        pass

    @property
    def device_info(self):
        """Return device info for device registry.

        Links this entity to the OBDcast device entry.
        """
        pass

    @property
    def native_value(self):
        """Return the sensor value from coordinator data."""
        pass
