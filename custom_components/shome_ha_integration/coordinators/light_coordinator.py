import logging
from enum import Enum

from homeassistant.core import HomeAssistant
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

# top-level imports
from ..shome_client.dto.light import SHomeLightInfo
from ..shome_client.dto.status import OnOffStatus
from ..shome_client.dto.device import SHomeDevice
from ..utils import get_or_create_client

_LOGGER = logging.getLogger(__name__)


class LightToggleType(Enum):
    ALL = "ALL"
    ROOM = "ROOM"
    SINGLE = "SINGLE"


class LightsCoordinator(DataUpdateCoordinator[dict]):

    def __init__(self, hass: HomeAssistant, credential: dict, devices: list[SHomeDevice]):
        super().__init__(
            hass,
            _LOGGER,
            name="light_coordinator",
            update_method=self._async_update_data,
            update_interval=None,
            request_refresh_debouncer=Debouncer(
                hass, _LOGGER, cooldown=1.0, immediate=False
            )
        )
        self._hass = hass
        self._credential = credential
        self._devices = devices

    def _init_data(self, light_devices: dict[SHomeDevice, SHomeLightInfo]):
        result = {}
        for device, light_info in light_devices.items():
            groups = {}
            for group in light_info.groups:
                groups[str(group.group_id)] = {
                    "name": group.nick_name,
                    "devices": group.devices,
                }
            sub_devices = {}
            for light in light_info.devices:
                sub_devices[str(light.id)] = {
                    "name": light.nick_name,
                    "on": light.on
                }
            result[device.id] = {
                "group_info": groups,
                "sub_device_info": sub_devices,
                "device_info": {
                    "id": device.unique_num,
                    "name": device.nick_name,
                    "shome_id": device.id,
                    "model": device.model_name,
                    "model_id": device.model_id,
                    "created_at": device.created_at,
                    "root_device_id": device.root_id,
                    "type": device.model_type_id
                }
            }
            _LOGGER.debug("Light device %s initialized with info: %s", device.id, result[device.id])
        return result

    async def _async_update_data(self) -> dict:
        _LOGGER.debug("Starting _async_update_data, devices count: %d", len(self._devices))
        try:
            client = await get_or_create_client(self._hass, self._credential)
            light_device_results: dict[SHomeDevice, SHomeLightInfo] = {}
            for device in self._devices:
                _LOGGER.debug("Fetching light info for device: %s (id: %s)", device.nick_name, device.id)
                light_info = await client.get_light_info(device.id)
                light_device_results[device] = light_info
            _LOGGER.debug("Fetched light info for %d devices", len(light_device_results))
            return self._init_data(light_device_results)
        except Exception as e:
            raise UpdateFailed(str(e)) from e

    async def toggle_light(self, light_shome_id: str, light_type: LightToggleType, light_id: str, state: OnOffStatus):
        try:
            client = await get_or_create_client(self._hass, self._credential)
            if light_type == LightToggleType.ALL:
                await client.toggle_all_light(light_shome_id, state)
            if light_type == LightToggleType.ROOM:
                await client.toggle_room_light(light_shome_id, light_id, state)
            if light_type == LightToggleType.SINGLE:
                await client.toggle_single_light(light_shome_id, light_id, state)
        except Exception as e:
            raise UpdateFailed(str(e)) from e
