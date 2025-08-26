from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .grouped_light import ApiGroupedLight
from .room_light import ApiRoomLight
from .single_light import ApiLight
# top-level imports
from ..const import DOMAIN
from ..coordinators.light_coordinator import LightsCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up grouped light entities from a config entry."""

    light_coordinator: LightsCoordinator = hass.data[DOMAIN][entry.entry_id]["lights_coordinator"]
    if light_coordinator.data is None:
        await light_coordinator.async_request_refresh()

    light_info = light_coordinator.data

    for light_device_id, light_device_info in light_info.items():

        # init single light
        single_lights = []
        for light_id, light_attributes in light_device_info["sub_device_info"].items():
            single_lights.append(ApiLight(light_coordinator, {
                "id": light_id,
                "name": light_attributes["name"],
                "device_info": light_device_info["device_info"]
            }))
        async_add_entities(single_lights)

        # init room light
        room_lights = []
        for group_id, group_info in light_device_info["group_info"].items():
            room_lights.append(ApiRoomLight(light_coordinator, {
                "id": group_id,
                "name": group_info["name"],
                "devices": group_info["devices"],
                "device_info": light_device_info["device_info"]
            }))
        async_add_entities(room_lights)

        # add grouped light entity
        async_add_entities([ApiGroupedLight(light_coordinator, {
            "device_info": light_device_info["device_info"]
        })])
