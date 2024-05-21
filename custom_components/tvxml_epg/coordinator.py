"""DataUpdateCoordinator for integration_blueprint."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import (
    TVXMLClient,
    TVXMLClientError,
)
from .const import DOMAIN, LOGGER


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class TVXMLDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from TVXML."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: TVXMLClient,
    ) -> None:
        """Initialize."""
        self.client = client
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5), # TODO configure update interval
        )

    async def _async_update_data(self):
        """Update data."""
        try:
            return await self.client.async_get_data()
        except TVXMLClientError as exception:
            raise UpdateFailed(exception) from exception
