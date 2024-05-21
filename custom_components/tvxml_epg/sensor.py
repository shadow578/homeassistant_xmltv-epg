"""Sensor platform for TVXML."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from .const import DOMAIN
from .coordinator import BlueprintDataUpdateCoordinator
from .entity import IntegrationBlueprintEntity

from .tvxml.model import TVGuide, TVChannel

async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    guide: TVGuide = coordinator.data

    async_add_devices(
        [
            TVXMLChannelSensor(coordinator, channel, is_next)
            for channel in guide.channels
            for is_next in [False, True]
        ]
    )


class TVXMLChannelSensor(IntegrationBlueprintEntity, SensorEntity):
    """TVXML Channel Program Sensor class."""

    def __init__(
        self,
        coordinator: BlueprintDataUpdateCoordinator,
        channel: TVChannel,
        is_next: bool,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = SensorEntityDescription(
            key=f"channel_{channel.id}_{'upcoming' if is_next else 'current'}",
            name=f"{channel.name} {'Upcoming' if is_next else 'Current'} Program",
            icon="mdi:format-quote-close",
        ),

        # store channel id, as object instance may change
        self._channel_id = channel.id
        self._is_next = is_next

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        guide: TVGuide = self.coordinator.data
        channel = guide.get_channel(self._channel_id)
        if channel is None:
            return None

        now = self.coordinator.time

        # get current or next program
        program = channel.get_next_program(now) if self._is_next else channel.get_current_program(now)
        if program is None:
            return None

        # entity attributes contain program details
        self._attr_attrs = {
            "start": program.start,
            "end": program.end,
            "title": program.title,
            "description": program.description,
            "episode": program.episode,
            "subtitle": program.subtitle,
        }

        # native value is program title
        return program.title
