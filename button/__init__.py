from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .refresh_button import RefreshButton
# top-level imports
from ..utils import get_or_create_client
from ..const import DOMAIN
from ..coordinators.light_coordinator import LightsCoordinator
from ..shome_client.shome_client import SHomeClient

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the refresh button entity."""

    credential: dict = entry.data.get("credential")
    client: SHomeClient = await get_or_create_client(hass, credential)

    light_coordinator: LightsCoordinator = hass.data[DOMAIN][entry.entry_id]["lights_coordinator"]

    # Add the refresh button entity
    async_add_entities([RefreshButton(light_coordinator)])
