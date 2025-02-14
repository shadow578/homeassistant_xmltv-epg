"""Sensor platform for XMLTV."""

from __future__ import annotations

import uuid
from datetime import datetime

from homeassistant.components.image import (
    ImageEntity,
    ImageEntityDescription,
)

from .const import DOMAIN, LOGGER
from .coordinator import XMLTVDataUpdateCoordinator
from .entity import XMLTVEntity
from .helper import program_get_normalized_identification
from .model import TVChannel, TVGuide


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator: XMLTVDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    guide: TVGuide = coordinator.data

    LOGGER.debug(
        f"Setting up image entities for {len(guide.channels)} channels (enable_upcoming: {coordinator.enable_upcoming_sensor})."
    )

    # add current / upcoming program images for each channel
    images: list[ImageEntity] = []
    for channel in guide.channels:
        # TODO channel icon
        images.append(XMLTVChannelProgramImage(coordinator, channel, False))
        if coordinator.enable_upcoming_sensor:
            images.append(XMLTVChannelProgramImage(coordinator, channel, True))

    async_add_devices(images)


class XMLTVChannelProgramImage(XMLTVEntity, ImageEntity):
    """XMLTV Channel Program Image class."""

    coordinator: XMLTVDataUpdateCoordinator

    def __init__(
        self,
        coordinator: XMLTVDataUpdateCoordinator,
        channel: TVChannel,
        is_next: bool,
    ) -> None:
        """Initialize the image class."""
        XMLTVEntity.__init__(self, coordinator, channel)
        ImageEntity.__init__(self, coordinator.hass)

        translation_key, entity_id = program_get_normalized_identification(
            channel, is_next, "program_image"
        )

        self.entity_id = entity_id
        self._attr_unique_id = str(uuid.uuid5(uuid.NAMESPACE_X500, self.entity_id))

        self._attr_has_entity_name = True
        self.entity_description = ImageEntityDescription(
            key=translation_key,
            translation_key=translation_key,
        )

        self._channel = channel
        self._program = None
        self._is_next = is_next

        LOGGER.debug(f"Setup image '{self.entity_id}' for channel '{channel.id}'.")

    @property
    def image_last_updated(self) -> datetime | None:
        """Time the image was last updated."""
        if self._program is None:
            return None

        return self._program.start

    @property
    def image_url(self) -> str | None:
        """Return URL of image."""
        guide: TVGuide = self.coordinator.data

        # refresh channel from guide
        channel = guide.get_channel(self._channel.id)
        if channel is None:
            return None

        self._channel = channel

        now = self.coordinator.current_time

        # get current or next program
        self._program = (
            self._channel.get_next_program(now)
            if self._is_next
            else channel.get_current_program(now)
        )
        if self._program is None:
            return None

        return self._program.image_url
