"""DataUpdateCoordinator for integration_blueprint."""
from __future__ import annotations

from datetime import datetime, timedelta

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
        update_interval: int,
        lookahead: int,
    ) -> None:
        """Initialize."""
        self.client = client
        self._lookahead = timedelta(minutes=lookahead)
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=update_interval),
        )

    async def _async_update_data(self):
        """Update data."""
        try:
            guide = await self.client.async_get_data()
            LOGGER.debug(f"Updated TVXML guide /w {len(guide.channels)} channels and {len(guide.programs)} programs.")
            return guide
        except TVXMLClientError as exception:
            raise UpdateFailed(exception) from exception

    def get_current_time(self) -> datetime:
        """Get effective current time."""
        return datetime.now() + self._lookahead
