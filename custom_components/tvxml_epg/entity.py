"""TVXML Entity class."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, NAME, VERSION
from .coordinator import TVXMLDataUpdateCoordinator


class TVXMLEntity(CoordinatorEntity):
    """TVXML Entity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: TVXMLDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "TODO")}, # TODO device identifier
            name=NAME,
            model=VERSION,
            manufacturer=NAME,
        )
