"""TVXML Entity class."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME, VERSION
from .coordinator import TVXMLDataUpdateCoordinator

from .tvxml.model import TVGuide


class TVXMLEntity(CoordinatorEntity):
    """TVXML Entity class."""

    def __init__(self, coordinator: TVXMLDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)

        guide: TVGuide = coordinator.data

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, guide.generator_name)},
            name=NAME,
            model=VERSION,
            manufacturer=NAME,
        )

        self._attr_attribution = f"Data provided by {guide.generator_name}"
