"""Support for SHome climate devices."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from ..const import DOMAIN
from ..coordinators.aircon_coordinator import AirconCoordinator
from ..coordinators.heater_coordinator import HeaterCoordinator
from .aircon import Aircon
from .heater import Heater

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up climate entities from a config entry."""

    climates = []

    # Setup aircon entities
    aircon_coordinator: AirconCoordinator = hass.data[DOMAIN][entry.entry_id]["aircon_coordinator"]
    if aircon_coordinator.data is None:
        await aircon_coordinator.async_request_refresh()

    aircon_data = aircon_coordinator.data
    if aircon_data:
        for device_id, device_data in aircon_data.items():
            for sub_device_num, aircon_device in device_data["sub_devices"].items():
                climates.append(Aircon(aircon_coordinator, {
                    "device_info": device_data.get("device_info", {}),
                    "sub_device_num": sub_device_num,
                    "sub_device_name": aircon_device.get("name")
                }))
    else:
        _LOGGER.debug("No aircon data available")

    # Setup heater entities
    heater_coordinator: HeaterCoordinator = hass.data[DOMAIN][entry.entry_id]["heater_coordinator"]
    if heater_coordinator.data is None:
        await heater_coordinator.async_request_refresh()

    heater_data = heater_coordinator.data
    if heater_data:
        for device_id, device_data in heater_data.items():
            for sub_device_num, heater_device in device_data["sub_devices"].items():
                climates.append(Heater(heater_coordinator, {
                    "device_info": device_data.get("device_info", {}),
                    "sub_device_num": sub_device_num,
                    "sub_device_name": heater_device.get("name")
                }))
    else:
        _LOGGER.debug("No heater data available")

    async_add_entities(climates)
