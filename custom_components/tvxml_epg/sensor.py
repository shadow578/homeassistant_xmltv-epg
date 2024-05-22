"""Sensor platform for TVXML."""
from __future__ import annotations
import uuid

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
)

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
            TVXMLChannelSensor(coordinator, channel, is_next)
            for channel in guide.channels
            for is_next in [False, True]
        ]
    )

    # add sensor for coordinator status
    async_add_devices([TVXMLStatusSensor(coordinator, guide)])


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
            name=f"{channel.name} {'Upcoming' if is_next else 'Current'} Program", # TODO localize
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

        now = self.coordinator.get_current_time()

        # get current or next program
        program = channel.get_next_program(now) if self._is_next else channel.get_current_program(now)
        if program is None:
            return None

        LOGGER.debug(f"Updated Channel Sensor '{self.entity_description.key}': {program.title} ({program.start} - {program.end}).")

        # format duration to HH:MM
        duration_seconds = program.duration.total_seconds()
        duration_hours = int(duration_seconds // 3600)
        duration_minutes = int((duration_seconds % 3600) // 60)

        # entity attributes contain program details
        self._attr_extra_state_attributes = {
            "start": program.start,
            "end": program.end,
            "duration": f"{duration_hours:02d}:{duration_minutes:02d}",
            "title": program.title,
            "description": program.description,
            "episode": program.episode,
            "subtitle": program.subtitle,
        }

        # native value is full program title
        return program.full_title

class TVXMLStatusSensor(TVXMLEntity, SensorEntity):
    """TVXML Coordinator Status Sensor class."""

    def __init__(
        self,
        coordinator: TVXMLDataUpdateCoordinator,
        guide: TVGuide
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)

        key = f"{guide.generator_name}_last_update"
        self._attr_unique_id = str(
            uuid.uuid5(
                uuid.NAMESPACE_X500,
                key
            )
        )

        self.entity_description = SensorEntityDescription(
            key=key,
            name=f"{guide.generator_name} Last Update Time", # TODO localize
            device_class=SensorDeviceClass.TIMESTAMP,
        )

        LOGGER.debug(f"Setup sensor for coordinator '{guide.generator_name}' status.")

    @property
    def native_value(self) -> str:
        """Return the native value of the sensor."""
        coordinator: TVXMLDataUpdateCoordinator = self.coordinator
        guide: TVGuide = coordinator.data

        # entity attributes contain program details
        self._attr_extra_state_attributes = {
            "generator_name": guide.generator_name,
            "generator_url": guide.generator_url,
        }

        # native value is last update time
        return coordinator.last_update_time.astimezone()
