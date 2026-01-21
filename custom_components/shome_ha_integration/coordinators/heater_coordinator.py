import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from ..shome_client.dto.heater import SHomeHeaterInfo
from ..shome_client.dto.device import SHomeDevice
from ..shome_client.dto.status import OnOffStatus
from ..utils import get_or_create_client


_LOGGER = logging.getLogger(__name__)


class HeaterCoordinator(DataUpdateCoordinator):

    def __init__(self, hass: HomeAssistant, credential: dict, devices: list[SHomeDevice]):
        super().__init__(
            hass,
            _LOGGER,
            name="heater_coordinator",
            update_method=self._async_update_data,
            update_interval=None,
            request_refresh_debouncer=Debouncer(
                hass, _LOGGER, cooldown=1.0, immediate=False
            )
        )
        self._hass = hass
        self._credential = credential
        self._devices = devices

    def _init_data(self, heater_devices: dict[SHomeDevice, list[SHomeHeaterInfo]]):
        result = {}
        for device, device_heaters in heater_devices.items():
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
            for heater in device_heaters:
                result[device.id]["sub_devices"][str(heater.sub_device_num)] = {
                    "name": heater.sub_device_name,
                    "on": heater.on,
                    "current_temperature": heater.current_temp,
                    "target_temperature": heater.set_temp,
                }
            _LOGGER.debug("Heater device %s initialized with data: %s", device.id, result[device.id])
        return result

    async def _async_update_data(self) -> dict:
        _LOGGER.debug("Starting heater _async_update_data, devices count: %d", len(self._devices))
        try:
            client = await get_or_create_client(self._hass, self._credential)
            heater_device_results: dict[SHomeDevice, list[SHomeHeaterInfo]] = {}
            for device in self._devices:
                heater_infos: list[SHomeHeaterInfo] = await client.get_heater_info(device.id)
                heater_device_results[device] = heater_infos
                _LOGGER.debug("Fetched heater info for device %s: %s", device.id, heater_infos)
            return self._init_data(heater_device_results)
        except Exception as e:
            _LOGGER.error("Error fetching heater data: %s", e)
            raise UpdateFailed(f"Error fetching heater data: {e}") from e

    async def toggle_heater(self, device_id: str, sub_device_num: str, status: OnOffStatus):
        """에어컨 on/off 토글."""
        _LOGGER.debug("Toggling heater %s sub-device %s to status %s", device_id, sub_device_num, status)
        try:
            client = await get_or_create_client(self._hass, self._credential)
            await client.toggle_heater(device_id, sub_device_num, status)
            await self.async_request_refresh()
            _LOGGER.debug("Successfully toggled heater %s sub-device %s to status %s", device_id, sub_device_num, status)
        except Exception as e:
            _LOGGER.error("Error toggling heater %s sub-device %s: %s", device_id, sub_device_num, e)
            raise

    async def set_heater_temperature(self, device_id: str, sub_device_num: str, temperature: int):
        _LOGGER.debug("Setting heater %s sub-device %s temperature to %d", device_id, sub_device_num, temperature)
        try:
            client = await get_or_create_client(self._hass, self._credential)
            await client.set_heater_temp(device_id, sub_device_num, temperature)
            await self.async_request_refresh()
            _LOGGER.debug("Successfully set heater %s sub-device %s temperature to %d", device_id, sub_device_num, temperature)
        except Exception as e:
            _LOGGER.error("Error setting heater %s sub-device %s temperature: %s", device_id, sub_device_num, e)
            raise

