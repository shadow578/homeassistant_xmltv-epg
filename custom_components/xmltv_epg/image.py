"""Sensor platform for XMLTV."""

from __future__ import annotations

import uuid
from datetime import datetime

from homeassistant.components.image import (
    ImageEntity,
    ImageEntityDescription,
)
from homeassistant.core import callback

from .const import DOMAIN, LOGGER
from .coordinator import XMLTVDataUpdateCoordinator
from .entity import XMLTVEntity
from .helper import program_get_normalized_identification
from .model import TVChannel, TVGuide, TVProgram


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator: XMLTVDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    guide: TVGuide = coordinator.data

    LOGGER.debug(
        f"Setting up image entities for {len(guide.channels)} channels (enable_upcoming: {coordinator.enable_upcoming_sensor}, enable_channel_icon: {coordinator.enable_channel_icon}, enable_program_image: {coordinator.enable_program_image})."
    )

    # add current / upcoming program images for each channel
    images: list[ImageEntity] = []
    for channel in guide.channels:
        if coordinator.enable_channel_icon:
            images.append(XMLTVChannelIconImage(coordinator, channel))

        if coordinator.enable_program_image:
            images.append(XMLTVChannelProgramImage(coordinator, channel, False))
            if coordinator.enable_upcoming_sensor:
                images.append(XMLTVChannelProgramImage(coordinator, channel, True))

    async_add_devices(images)


class XMLTVChannelProgramImage(XMLTVEntity, ImageEntity):
    """XMLTV Channel Program Image class."""

    coordinator: XMLTVDataUpdateCoordinator

    __channel: TVChannel
    __program: TVProgram | None
    __is_next: bool

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

        self.__channel = channel
        self.__program = None
        self.__is_next = is_next

        LOGGER.debug(f"Setup image '{self.entity_id}' for channel '{channel.id}'.")

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        guide: TVGuide = self.coordinator.data

        # refresh channel from guide
        channel = guide.get_channel(self.__channel.id)
        if channel is None:
            self.__program = None
            super()._handle_coordinator_update()
            return

        self.__channel = channel

        now = self.coordinator.current_time

        # get current or next program
        self.__program = (
            self.__channel.get_next_program(now)
            if self.__is_next
            else channel.get_current_program(now)
        )

        super()._handle_coordinator_update()

    @property
    def image_last_updated(self) -> datetime | None:
        """Time the image was last updated."""
        program = self.__program
        if program is None:
            return None
        return program.start

    @property
    def image_url(self) -> str | None:
        """Return URL of image."""
        program = self.__program
        if program is None:
            return None
        return program.image_url

    @property
    def state(self) -> str | None:
        """Get the state value of the image entity."""
        program = self.__program
        if program is None:
            return None
        return program.full_title


class XMLTVChannelIconImage(XMLTVEntity, ImageEntity):
    """XMLTV Channel Icon Image class."""

    coordinator: XMLTVDataUpdateCoordinator

    __channel: TVChannel
    __last_icon_url: str | None
    __last_updated: datetime | None

    def __init__(
        self, coordinator: XMLTVDataUpdateCoordinator, channel: TVChannel
    ) -> None:
        """Initialize the image class."""
        XMLTVEntity.__init__(self, coordinator, channel)
        ImageEntity.__init__(self, coordinator.hass)

        translation_key, entity_id = program_get_normalized_identification(
            channel, False, "channel_icon"
        )

        self.entity_id = entity_id
        self._attr_unique_id = str(uuid.uuid5(uuid.NAMESPACE_X500, self.entity_id))

        self._attr_has_entity_name = True
        self.entity_description = ImageEntityDescription(
            key=translation_key,
            translation_key=translation_key,
        )

        self.__channel = channel
        self.__last_icon_url = None
        self.__last_updated = None

        LOGGER.debug(f"Setup image '{self.entity_id}' for channel '{channel.id}'.")

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        guide: TVGuide = self.coordinator.data

        # refresh channel from guide
        channel = guide.get_channel(self.__channel.id)
        if channel is not None:
            self.__channel = channel

        super()._handle_coordinator_update()

    @property
    def image_last_updated(self) -> datetime | None:
        """Time the image was last updated."""
        return self.__last_updated

    @property
    def image_url(self) -> str | None:
        """Return URL of image."""
        channel = self.__channel
        if channel is None:
            return None

        icon_url = channel.icon_url
        if icon_url is None:
            return None

        if icon_url != self.__last_icon_url:
            self.__last_icon_url = icon_url
            self.__last_updated = self.coordinator.current_time

        return icon_url

    @property
    def state(self) -> str | None:
        """Get the state value of the image entity."""
        channel = self.__channel
        if channel is None:
            return None
        return channel.name
