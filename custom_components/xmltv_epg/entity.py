"""XMLTV Entity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.xmltv_epg.model.program import TVProgram

from .const import DOMAIN, ChannelSensorMode
from .coordinator import XMLTVDataUpdateCoordinator
from .model import TVChannel, TVGuide


class XMLTVEntity(CoordinatorEntity[XMLTVDataUpdateCoordinator]):
    """XMLTV Entity class."""

    coordinator: XMLTVDataUpdateCoordinator

    def __init__(
        self, coordinator: XMLTVDataUpdateCoordinator, channel: TVChannel | None
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)

        guide: TVGuide = coordinator.data

        self._attr_attribution = f"Data provided by {guide.name}"  # TODO localize

        if channel is not None:
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, channel.id)}, name=channel.display_name
            )


class XMLTVProgramEntity(XMLTVEntity):
    """XMLTV Entity with Program information."""

    _channel: TVChannel
    _program: TVProgram | None
    _mode: ChannelSensorMode

    def __init__(
        self,
        coordinator: XMLTVDataUpdateCoordinator,
        channel: TVChannel,
        mode: ChannelSensorMode,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, channel)

        self._channel = channel
        self._program = None
        self._mode = mode

    def _update_from_coordinator(self) -> None:
        """Update channel and program data from the coordinator.

        :note To be called from _handle_coordinator_update.
        """
        channel = self.coordinator.data.get_channel(self._channel.id)
        if channel is None:
            self._program = None
            self._attr_state = None
            self._attr_image_url = None
            self._attr_image_last_updated = self.coordinator.current_time
            return

        self._channel = channel

        # get program based on mode
        if self._mode == ChannelSensorMode.CURRENT:
            self._program = channel.get_current_program(self.coordinator.current_time)
        elif self._mode == ChannelSensorMode.NEXT:
            self._program = channel.get_next_program(self.coordinator.current_time)
        elif self._mode == ChannelSensorMode.PRIMETIME:
            self._program = channel.get_current_program(self.coordinator.primetime_time)
        else:
            raise ValueError(
                f"Unsupported mode: {self._mode}. Please report this issue."
            )
