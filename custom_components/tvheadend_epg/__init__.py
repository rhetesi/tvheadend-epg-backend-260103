from .const import DOMAIN, PLATFORMS
from .coordinator import TVHEPGCoordinator
from .storage import EPGStorage
from .services import async_register_services
from .api.http import TVHHttpAPI
from .ws import async_register_ws

async def async_setup_entry(hass, entry):
    api = TVHHttpAPI(
        entry.data["host"],
        entry.data["port"],
        entry.data["username"],
        entry.data["password"],
    )

    storage = EPGStorage(hass, entry.entry_id)
    coordinator = TVHEPGCoordinator(hass, api, storage)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    async_register_services(hass, coordinator)
    async_register_ws(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass, entry):
    hass.services.async_remove(DOMAIN, "refresh")
    hass.services.async_remove(DOMAIN, "record")

    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    hass.data[DOMAIN].pop(entry.entry_id)
    return True
