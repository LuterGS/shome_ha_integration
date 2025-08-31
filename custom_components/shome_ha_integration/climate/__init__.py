"""Support for SHome fan devices."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from ..const import DOMAIN
from ..coordinators.aircon_coordinator import AirconCoordinator
from .aircon import Aircon

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up fan entities from a config entry."""

    aircon_coordinator: AirconCoordinator = hass.data[DOMAIN][entry.entry_id]["aircon_coordinator"]
    if aircon_coordinator.data is None:
        await aircon_coordinator.async_request_refresh()

    aircon_data = aircon_coordinator.data
    if not aircon_data:
        _LOGGER.warning("No aircon data available")
        return

    climates = []
    for device_id, device_data in aircon_data.items():
        for sub_device_num, aircon_device in device_data["sub_devices"].items():
            # Create the climate entity
            climates.append(Aircon(aircon_coordinator, {
                "device_info": device_data.get("device_info", {}),
                "sub_device_num": sub_device_num,
                "sub_device_name": aircon_device.get("name")
            }))
    async_add_entities(climates)
