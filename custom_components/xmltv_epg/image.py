"""Sensor platform for XMLTV."""

from __future__ import annotations

import uuid

from homeassistant.components.image import (
    ImageEntity,
    ImageEntityDescription,
)
from homeassistant.core import callback

from .const import DOMAIN, LOGGER, ChannelSensorMode
from .coordinator import XMLTVDataUpdateCoordinator
from .entity import XMLTVEntity, XMLTVProgramEntity
from .helper import program_get_normalized_identification
from .model import TVChannel, TVGuide


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator: XMLTVDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    guide: TVGuide = coordinator.data

    LOGGER.debug(
        f"Setting up image entities for {len(guide.channels)} channels (enable_upcoming: {coordinator.enable_upcoming_sensor}, enable_channel_icon: {coordinator.enable_channel_icon}, enable_program_image: {coordinator.enable_program_image})."
    )

    images: list[ImageEntity] = []
    for channel in guide.channels:
        # channel icon
        if coordinator.enable_channel_icon:
            images.append(XMLTVChannelIconImage(coordinator, channel))

        if coordinator.enable_program_image:
            # current
            if coordinator.enable_current_sensor:
                images.append(
                    XMLTVChannelProgramImage(
                        coordinator, channel, ChannelSensorMode.CURRENT
                    )
                )

            # upcoming
            if coordinator.enable_upcoming_sensor:
                images.append(
                    XMLTVChannelProgramImage(
                        coordinator, channel, ChannelSensorMode.NEXT
                    )
                )

            # primetime
            if coordinator.enable_primetime_sensor:
                images.append(
                    XMLTVChannelProgramImage(
                        coordinator, channel, ChannelSensorMode.PRIMETIME
                    )
                )

    async_add_devices(images)


class XMLTVChannelProgramImage(XMLTVProgramEntity, ImageEntity):
    """XMLTV Channel Program Image class."""

    def __init__(
        self,
        coordinator: XMLTVDataUpdateCoordinator,
        channel: TVChannel,
        mode: ChannelSensorMode,
    ) -> None:
        """Initialize the image class."""
        XMLTVProgramEntity.__init__(self, coordinator, channel, mode)
        ImageEntity.__init__(self, coordinator.hass)

        translation_key, entity_id = program_get_normalized_identification(
            channel, mode, "program_image"
        )

        self.entity_id = entity_id
        self._attr_unique_id = str(uuid.uuid5(uuid.NAMESPACE_X500, self.entity_id))

        self._attr_has_entity_name = True
        self.entity_description = ImageEntityDescription(
            key=translation_key,
            translation_key=translation_key,
        )

        LOGGER.debug(f"Setup image '{self.entity_id}' for channel '{channel.id}'.")

    @property
    def available(self) -> bool:  # pyright: ignore[reportIncompatibleVariableOverride] -- Entity.available and CoordinatorEntity.available are defined incompatible
        """Return if entity is available."""
        return self._attr_image_url is not None and XMLTVEntity.available.__get__(self)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if not self._update_from_coordinator() or self._program is None:
            self._attr_state = None
            self._attr_image_url = None
            self._attr_image_last_updated = self.coordinator.current_time

            super()._handle_coordinator_update()
            return

        image = self._program.image
        self._attr_image_url = image.url if image is not None else None
        self._attr_image_last_updated = self.coordinator.current_time

        super()._handle_coordinator_update()


class XMLTVChannelIconImage(XMLTVEntity, ImageEntity):
    """XMLTV Channel Icon Image class."""

    coordinator: XMLTVDataUpdateCoordinator

    __channel: TVChannel

    def __init__(
        self, coordinator: XMLTVDataUpdateCoordinator, channel: TVChannel
    ) -> None:
        """Initialize the image class."""
        XMLTVEntity.__init__(self, coordinator, channel)
        ImageEntity.__init__(self, coordinator.hass)

        translation_key, entity_id = program_get_normalized_identification(
            channel, ChannelSensorMode.NONE, "channel_icon"
        )

        self.entity_id = entity_id
        self._attr_unique_id = str(uuid.uuid5(uuid.NAMESPACE_X500, self.entity_id))

        self._attr_has_entity_name = True
        self.entity_description = ImageEntityDescription(
            key=translation_key,
            translation_key=translation_key,
        )

        self.__channel = channel

        LOGGER.debug(f"Setup image '{self.entity_id}' for channel '{channel.id}'.")

    @property
    def available(self) -> bool:  # pyright: ignore[reportIncompatibleVariableOverride] -- Entity.available and CoordinatorEntity.available are defined incompatible
        """Return if entity is available."""
        return self._attr_image_url is not None and XMLTVEntity.available.__get__(self)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        guide: TVGuide = self.coordinator.data

        channel = guide.get_channel(self.__channel.id)
        if channel is None:
            self._attr_state = None
            self._attr_image_url = None
            self._attr_image_last_updated = self.coordinator.current_time
        else:
            self.__channel = channel

            icon = channel.icon
            self._attr_image_url = icon.url if icon is not None else None
            self._attr_image_last_updated = self.coordinator.current_time

        super()._handle_coordinator_update()
