"""Sensor platform for TVXML."""
from __future__ import annotations
import uuid
from datetime import datetime

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorStateClass

from .const import DOMAIN, LOGGER
from .coordinator import TVXMLDataUpdateCoordinator
from .entity import TVXMLEntity

from .tvxml.model import TVGuide, TVChannel

async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    guide: TVGuide = coordinator.data

    LOGGER.debug(f"Setting up Channel Sensors for {len(guide.channels)} channels.")

    async_add_devices(
        [
            TVXMLChannelSensor(coordinator, channel, False) # TODO: is_next true
            for channel in guide.channels
        ]
    )


class TVXMLChannelSensor(TVXMLEntity, SensorEntity):
    """TVXML Channel Program Sensor class."""

    def __init__(
        self,
        coordinator: TVXMLDataUpdateCoordinator,
        channel: TVChannel,
        is_next: bool,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)

        key = f"channel_{channel.id}_{'upcoming' if is_next else 'current'}"
        self._attr_unique_id = str(
            uuid.uuid5(
                uuid.NAMESPACE_X500,
                key
            )
        )

        self.entity_description = SensorEntityDescription(
            key=key,
            name=f"{channel.name} {'Upcoming' if is_next else 'Current'} Program",
            icon="mdi:format-quote-close",
        )

        # store channel id, as object instance may change
        self._channel_id = channel.id
        self._is_next = is_next

        LOGGER.debug(f"Setup sensor for channel '{channel.id}' {'NEXT' if is_next else 'CURRENT'} program.")

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        guide: TVGuide = self.coordinator.data
        channel = guide.get_channel(self._channel_id)
        if channel is None:
            return None

        now = datetime.now()

        # get current or next program
        program = channel.get_next_program(now) if self._is_next else channel.get_current_program(now)
        if program is None:
            return None

        LOGGER.debug(f"Updated Channel Sensor '{self.entity_description.key}': {program.title} ({program.start} - {program.end}).")

        # entity attributes contain program details
        self._attr_extra_state_attributes = {
            "start": program.start,
            "end": program.end,
            "title": program.title,
            "description": program.description,
            "episode": program.episode,
            "subtitle": program.subtitle,
        }

        # native value is program title
        return program.title
