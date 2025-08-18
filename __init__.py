import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinators.light_coordinator import LightsCoordinator
from .shome_client.dto.light import LightInfo
from .shome_client.shome_client import SHomeClient
from .const import DOMAIN
from .utils import unload_client, get_or_create_client

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):

    credential: dict = entry.data.get("credential")
    client: SHomeClient = await get_or_create_client(hass, credential)

    # create light coordinator
    light_devices: LightInfo = await client.get_light_info()
    light_coordinator: LightsCoordinator = LightsCoordinator(hass, credential, light_devices)

    # save light_coordinator for future use
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "lights_coordinator": light_coordinator,
    }

    # launch devices
    await hass.config_entries.async_forward_entry_setups(entry, [Platform.LIGHT, Platform.BUTTON])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""

    hass.data.setdefault(DOMAIN, {})
    if entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN][entry.entry_id] = None

    credential: dict = entry.data.get("credential")
    if not credential:
        _LOGGER.error("No credential found in entry data for unloading: %s", entry.entry_id)
        return False
    await unload_client(hass, credential)

    _LOGGER.info("Unloading SHome integration entry: %s", entry.entry_id)
    return True
