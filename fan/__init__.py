"""Support for SHome fan devices."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from ..const import DOMAIN
from ..coordinators.ventilation_coordinator import VentilationCoordinator
from .ventilation_fan import VentilationFan

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up fan entities from a config entry."""
    
    ventilation_coordinator: VentilationCoordinator = hass.data[DOMAIN][entry.entry_id]["ventilation_coordinator"]
    if ventilation_coordinator.data is None:
        await ventilation_coordinator.async_request_refresh()
    
    ventilation_data = ventilation_coordinator.data
    if not ventilation_data:
        _LOGGER.warning("No ventilation data available")
        return
    
    fans = []
    for device_id, device_data in ventilation_data.items():
        for sub_device_num, ventilation in device_data.items():

            # Create the fan entity
            fans.append(VentilationFan(ventilation_coordinator, {
                "device_info": device_data.get("device_info", {}),
                "sub_device_num": sub_device_num,
                "sub_device_name": ventilation["name"]
            }))
    async_add_entities(fans)
