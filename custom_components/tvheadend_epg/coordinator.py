import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

class TVHEPGCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api, storage):
        super().__init__(
            hass,
            logger=_LOGGER,
            name="TVHeadend EPG",
            update_interval=timedelta(minutes=15),
        )
        self.api = api
        self.storage = storage

    async def _async_update_data(self):
        epg = await self.api.get_epg()
        await self.storage.save(epg)
        return epg
