import logging

from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from ..shome_client.dto.ventilation import SHomeVentilationInfo, VentilationSpeed
from ..shome_client.dto.device import SHomeDevice
from ..shome_client.dto.status import OnOffStatus
from ..utils import get_or_create_client


_LOGGER = logging.getLogger(__name__)


class VentilationCoordinator(DataUpdateCoordinator[dict]):

    def __init__(self, hass, credential: dict, devices: list[SHomeDevice]):
        super().__init__(
            hass,
            _LOGGER,
            name="ventilation_coordinator",
            update_method=self._async_update_data,
            update_interval=None,
            request_refresh_debouncer=Debouncer(
                hass, _LOGGER, cooldown=1.0, immediate=False
            )
        )
        self._hass = hass
        self._credential = credential
        self._devices = devices

    def _init_data(self, ventilation_devices: dict[SHomeDevice, list[SHomeVentilationInfo]]):
        result = {}
        for device, device_ventilations in ventilation_devices.items():
            result.setdefault(device.id, {
                "device_info": {
                    "id": device.unique_num,
                    "name": device.nick_name,
                    "shome_id": device.id,
                    "model": device.model_name,
                    "model_id": device.model_id,
                    "created_at": device.created_at,
                    "manufacturer": "SHome",
                },
                "sub_devices": {}
            })
            for ventilation in device_ventilations:
                result[device.id]["sub_devices"][str(ventilation.sub_device_num)] = {
                    "name": ventilation.sub_device_name,
                    "status": ventilation.current_speed.value
                }
            _LOGGER.debug("Ventilation device %s initialized with data: %s", device.id, result[device.id])
        return result

    async def _async_update_data(self) -> dict:
        _LOGGER.debug("Starting ventilation _async_update_data, devices count: %d", len(self._devices))
        try:
            client = await get_or_create_client(self._hass, self._credential)
            ventilation_device_results: dict[SHomeDevice, list[SHomeVentilationInfo]] = {}
            for device in self._devices:
                _LOGGER.debug("Fetching ventilation info for device: %s (id: %s)", device.nick_name, device.id)
                ventilation_info = await client.get_ventilation_info(device.id)
                ventilation_device_results[device] = ventilation_info
            _LOGGER.debug("Fetched ventilation info for %d devices", len(ventilation_device_results))
            return self._init_data(ventilation_device_results)
        except Exception as e:
            _LOGGER.error("Error updating ventilation data: %s", str(e))
            raise UpdateFailed(str(e)) from e

    async def toggle_ventilation(self, device_id: str, sub_device_num: str, status: OnOffStatus):
        try:
            client = await get_or_create_client(self._hass, self._credential)
            await client.toggle_ventilation(device_id, sub_device_num, status)
        except Exception as e:
            raise UpdateFailed(str(e)) from e

    async def set_ventilation_speed(self, device_id: str, sub_device_num: str, speed: VentilationSpeed):
        try:
            client = await get_or_create_client(self._hass, self._credential)
            await client.set_ventilation_speed(device_id, sub_device_num, speed)
        except Exception as e:
            raise UpdateFailed(str(e)) from e
