import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .utils import get_or_create_client
from .const import DOMAIN
from .coordinator import LightsCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up SHome integration from a config entry."""
    _LOGGER.info("Setting up SHome integration for entry: %s", entry.entry_id)
    _LOGGER.debug("Entry data: %s", entry.data)
    
    try:
        # Get or create client (singleton pattern)
        client = await get_or_create_client(
            hass, 
            entry.data["username"], 
            entry.data["password"]
        )

        # create coordinator for lights
        _LOGGER.debug("Creating LightsCoordinator for entry: %s", entry.entry_id)
        lights_coordinator = LightsCoordinator(hass, entry.data["username"], entry.data["password"])
        
        # Store client and devices for this entry
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = {
            "client": client,
            "devices": entry.data["device_ids"],
            "username": entry.data["username"],

            # lights
            "lights_coordinator": lights_coordinator,
        }
        _LOGGER.debug("Stored %d devices for entry: %s", len(entry.data["device_ids"]), entry.entry_id)


        await hass.config_entries.async_forward_entry_setups(entry, [Platform.LIGHT])
        _LOGGER.info("SHome integration setup completed successfully")
        return True
        
    except Exception as e:
        _LOGGER.error("Failed to setup SHome integration: %s", str(e))
        raise


async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    hass.data.setdefault(DOMAIN, {})
    _LOGGER.info("Unloading SHome integration entry: %s", entry.entry_id)
    return True
