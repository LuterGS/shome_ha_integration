from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .grouped_light import ApiGroupedLight
from .single_light import ApiLight
from ..const import DOMAIN
from ..coordinator import LightsCoordinator
from ..shome_client.dto.light import LightInfo
from ..shome_client.shome_client import SHomeClient


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up grouped light entities from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]

    client: SHomeClient = data["client"]
    coordinator: LightsCoordinator = data["lights_coordinator"]

    light_devices: LightInfo = await client.get_light_info()

    # add all grouped lights first
    async_add_entities([ApiGroupedLight(coordinator, light_devices)])
    # then add individual lights
    async_add_entities([ApiLight(coordinator, light) for light in light_devices.devices])
