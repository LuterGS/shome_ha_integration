import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from ..shome_client.dto.aircon import SHomeAirconInfo
from ..shome_client.dto.device import SHomeDevice
from ..shome_client.dto.status import OnOffStatus
from ..utils import get_or_create_client


_LOGGER = logging.getLogger(__name__)


class AirconCoordinator(DataUpdateCoordinator):

    def __init__(self, hass: HomeAssistant, credential: dict, devices: list[SHomeDevice]):
        super().__init__(
            hass,
            _LOGGER,
            name="aircon_coordinator",
            update_method=self._async_update_data,
            update_interval=None,
            request_refresh_debouncer=Debouncer(
                hass, _LOGGER, cooldown=1.0, immediate=False
            )
        )
        self._hass = hass
        self._credential = credential
        self._devices = devices

    def _init_data(self, aircon_devices: dict[SHomeDevice, list[SHomeAirconInfo]]):
        result = {}
        for device, device_aircons in aircon_devices.items():
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
            for aircon in device_aircons:
                result[device.id]["sub_devices"][str(aircon.sub_device_num)] = {
                    "name": aircon.sub_device_name,
                    "on": aircon.on,
                    "current_temperature": aircon.current_temp,
                    "target_temperature": aircon.set_temp,
                }
            _LOGGER.debug("Aircon device %s initialized with data: %s", device.id, result[device.id])
        return result

    async def _async_update_data(self) -> dict:
        _LOGGER.debug("Starting aircon _async_update_data, devices count: %d", len(self._devices))
        try:
            client = await get_or_create_client(self._hass, self._credential)
            aircon_device_results: dict[SHomeDevice, list[SHomeAirconInfo]] = {}
            for device in self._devices:
                aircon_infos: list[SHomeAirconInfo] = await client.get_aircon_info(device.id)
                aircon_device_results[device] = aircon_infos
                _LOGGER.debug("Fetched aircon info for device %s: %s", device.id, aircon_infos)
            return self._init_data(aircon_device_results)
        except Exception as e:
            _LOGGER.error("Error fetching aircon data: %s", e)
            raise UpdateFailed(f"Error fetching aircon data: {e}") from e

    async def toggle_aircon(self, device_id: str, sub_device_num: str, status: OnOffStatus):
        """에어컨 on/off 토글."""
        _LOGGER.debug("Toggling aircon %s sub-device %s to status %s", device_id, sub_device_num, status)
        try:
            client = await get_or_create_client(self._hass, self._credential)
            await client.toggle_aircon(device_id, sub_device_num, status)
            await self.async_request_refresh()
            _LOGGER.debug("Successfully toggled aircon %s sub-device %s to status %s", device_id, sub_device_num, status)
        except Exception as e:
            _LOGGER.error("Error toggling aircon %s sub-device %s: %s", device_id, sub_device_num, e)
            raise

    async def set_aircon_temperature(self, device_id: str, sub_device_num: str, temperature: int):
        _LOGGER.debug("Setting aircon %s sub-device %s temperature to %d", device_id, sub_device_num, temperature)
        try:
            client = await get_or_create_client(self._hass, self._credential)
            await client.set_aircon_temp(device_id, sub_device_num, temperature)
            await self.async_request_refresh()
            _LOGGER.debug("Successfully set aircon %s sub-device %s temperature to %d", device_id, sub_device_num, temperature)
        except Exception as e:
            _LOGGER.error("Error setting aircon %s sub-device %s temperature: %s", device_id, sub_device_num, e)
            raise

