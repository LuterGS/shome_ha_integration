import logging
from datetime import timedelta

from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

# top-level imports
from ..shome_client.dto.sensor import SHomeSensorInfo
from ..shome_client.dto.device import SHomeDevice
from ..utils import get_or_create_client


_LOGGER = logging.getLogger(__name__)

class SensorCoordinator(DataUpdateCoordinator[dict]):

    def __init__(self, hass, credential: dict, devices: list[SHomeDevice]):
        super().__init__(
            hass,
            _LOGGER,
            name="sensor_coordinator",
            update_method=self._async_update_data,
            update_interval=timedelta(minutes=1),  # Update every 1 minutes
            request_refresh_debouncer=Debouncer(
                hass, _LOGGER, cooldown=1.0, immediate=False
            )
        )
        self._hass = hass
        self._credential = credential
        self._devices = devices

    def _init_data(self, sensor_devices: dict[SHomeDevice, list[SHomeSensorInfo]]):
        result = {}
        for device, device_sensors in sensor_devices.items():
            result.setdefault(device.id, {
                "device_info": {
                    "id": device.unique_num,
                    "name": device.nick_name,
                    "shome_id": device.id,
                    "model": device.model_name,
                    "model_id": device.model_id,
                    "created_at": device.created_at,
                    "manufacturer": "SHome",
                }
            })
            for sensor in device_sensors:
                result[device.id].setdefault(sensor.sub_device_num, {})
                result[device.id][str(sensor.sub_device_num)] = {
                    "name": sensor.sub_device_name,
                    "temperature": sensor.temperature,
                    "humidity": sensor.humidity,
                    "co2": sensor.co2,
                    "pm10": sensor.pm10,
                }
            _LOGGER.debug("Sensor device %s initialized with data: %s", device.id, result[device.id])
        return result

    async def _async_update_data(self) -> dict:
        _LOGGER.debug("Starting sensor _async_update_data, devices count: %d", len(self._devices))
        try:
            client = await get_or_create_client(self._hass, self._credential)
            sensor_device_results: dict[SHomeDevice, list[SHomeSensorInfo]] = {}
            for device in self._devices:
                _LOGGER.debug("Fetching sensor info for device: %s (id: %s)", device.nick_name, device.id)
                sensor_info = await client.get_sensor_info(device.id)
                sensor_device_results[device] = sensor_info
            _LOGGER.debug("Fetched sensor info for %d devices", len(sensor_device_results))
            return self._init_data(sensor_device_results)
        except Exception as e:
            _LOGGER.error("Error updating sensor data: %s", str(e))
            raise UpdateFailed(str(e)) from e
