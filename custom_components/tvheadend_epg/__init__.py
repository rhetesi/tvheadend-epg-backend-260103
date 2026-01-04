import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .coordinator import TVHEPGCoordinator
from .storage import EPGStorage
from .api.http import TVHHttpApi

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up TVHeadend EPG from a config entry."""
    _LOGGER.debug("Setting up TVHeadend EPG entry: %s", entry.entry_id)

    # Initialize API client
    http_api = TVHHttpApi(
        base_url=entry.data["url"],
        username=entry.data["username"],
        password=entry.data["password"],
    )

    # Initialize storage (persistent, not sensor-based)
    storage = EPGStorage(hass, entry.entry_id)

    # Initialize coordinator
    coordinator = TVHEPGCoordinator(
        hass=hass,
        http_api=http_api,
        storage=storage,
    )

    # First refresh (fail fast if config is invalid)
    await coordinator.async_config_entry_first_refresh()

    # Store references
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "storage": storage,
    }

    # Forward setup to platforms (e.g. sensor)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.debug("TVHeadend EPG entry setup complete: %s", entry.entry_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a TVHeadend EPG config entry."""
    _LOGGER.debug("Unloading TVHeadend EPG entry: %s", entry.entry_id)

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)

    return unload_ok
