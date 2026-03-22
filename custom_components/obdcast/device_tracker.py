"""Device tracker platform for OBDcast integration.

Creates a device_tracker entity for GPS location from the OBDcast device.
This entity:
- Shows the vehicle on Home Assistant's map
- Supports zone detection (home/away/custom zones)
- Updates in real-time as GPS data arrives

The device tracker uses source_type=GPS and reports:
- latitude/longitude from GPS data
- GPS accuracy from fix quality
- Additional attributes: altitude, heading, speed

Entity naming:
- Entity ID: device_tracker.obdcast_{device_id}
- Name: {vehicle_name}
"""

from __future__ import annotations

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OBDcast device tracker from a config entry.

    Creates the GPS-based device tracker entity.

    Args:
        hass: Home Assistant instance
        entry: Config entry for this OBDcast device
        async_add_entities: Callback to register entities
    """
    pass


class OBDcastDeviceTracker(TrackerEntity):
    """Device tracker entity for OBDcast GPS location.

    Reports vehicle location based on GPS data from the OBDcast device.
    Updates are push-based via the coordinator.
    """

    def __init__(self, coordinator, device_id: str, vehicle_name: str) -> None:
        """Initialize the device tracker.

        Args:
            coordinator: OBDcastCoordinator instance
            device_id: OBDcast device identifier
            vehicle_name: Friendly name for the vehicle
        """
        pass

    @property
    def source_type(self) -> SourceType:
        """Return the source type as GPS."""
        return SourceType.GPS

    @property
    def latitude(self) -> float | None:
        """Return latitude from GPS data."""
        pass

    @property
    def longitude(self) -> float | None:
        """Return longitude from GPS data."""
        pass

    @property
    def location_accuracy(self) -> int:
        """Return GPS accuracy in meters.

        Derived from GPS fix quality - higher quality = lower number.
        """
        pass

    @property
    def extra_state_attributes(self):
        """Return additional GPS attributes.

        Includes altitude, heading, speed, and satellites.
        """
        pass

    @property
    def device_info(self):
        """Return device info for device registry."""
        pass
