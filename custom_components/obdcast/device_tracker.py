"""Device tracker platform for OBDcast integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_DEVICE_ID,
    CONF_VEHICLE_NAME,
    DOMAIN,
)
from .coordinator import OBDcastCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OBDcast device tracker from a config entry."""
    coordinator: OBDcastCoordinator = hass.data[DOMAIN][entry.entry_id]
    device_id: str = entry.data[CONF_DEVICE_ID]
    vehicle_name: str = entry.data[CONF_VEHICLE_NAME]

    async_add_entities([OBDcastDeviceTracker(coordinator, device_id, vehicle_name)])


class OBDcastDeviceTracker(CoordinatorEntity[OBDcastCoordinator], TrackerEntity):
    """Device tracker entity for OBDcast GPS location."""

    def __init__(
        self,
        coordinator: OBDcastCoordinator,
        device_id: str,
        vehicle_name: str,
    ) -> None:
        """Initialize the device tracker."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._vehicle_name = vehicle_name
        self._attr_unique_id = f"{device_id}_tracker"
        self._attr_name = vehicle_name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=vehicle_name,
            manufacturer="Freematics",
            model="ONE+ Model B",
        )

    @property
    def source_type(self) -> SourceType:
        """Return the source type as GPS."""
        return SourceType.GPS

    @property
    def latitude(self) -> float | None:
        """Return latitude from GPS data."""
        return self.coordinator.get_value("gps.lat")

    @property
    def longitude(self) -> float | None:
        """Return longitude from GPS data."""
        return self.coordinator.get_value("gps.lon")

    @property
    def location_accuracy(self) -> int:
        """Return GPS accuracy derived from HDOP.

        HDOP * 5 gives a rough accuracy in meters.
        Returns 0 (unknown) if no HDOP data.
        """
        hdop = self.coordinator.get_value("gps.hdop")
        if hdop is None:
            return 0
        try:
            return int(float(hdop) * 5)
        except (TypeError, ValueError):
            return 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional GPS attributes."""
        attrs: dict[str, Any] = {}
        coord = self.coordinator

        alt = coord.get_value("gps.alt_m")
        if alt is not None:
            attrs["altitude"] = alt

        heading = coord.get_value("gps.heading")
        if heading is not None:
            attrs["heading"] = heading

        speed = coord.get_value("obd.speed")
        if speed is not None:
            attrs["speed"] = speed

        return attrs
