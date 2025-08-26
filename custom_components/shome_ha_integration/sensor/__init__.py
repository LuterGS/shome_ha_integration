import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from ..const import DOMAIN
from ..coordinators.sensor_coordinator import SensorCoordinator
from .temperature_sensor import TemperatureSensor
from .humidity_sensor import HumiditySensor
from .co2_sensor import CO2Sensor
from .dust_sensor import PM10Sensor

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities from a config entry."""
    
    sensor_coordinator: SensorCoordinator = hass.data[DOMAIN][entry.entry_id]["sensor_coordinator"]
    if sensor_coordinator.data is None:
        await sensor_coordinator.async_request_refresh()
    
    sensor_data = sensor_coordinator.data
    if not sensor_data:
        _LOGGER.warning("No sensor data available")
        return

    sensors = []
    for device_id, device in sensor_data.items():
        for sub_device_num, sub_device in device["sub_devices"].items():
            params = {
                "device_info": device["device_info"],
                "sub_device_num": sub_device_num,
                "sub_device_name": sub_device.get("name")
            }
            # Only add sensors if data exists
            if sub_device.get("temperature") is not None:
                sensors.append(TemperatureSensor(sensor_coordinator, params))
            if sub_device.get("humidity") is not None:
                sensors.append(HumiditySensor(sensor_coordinator, params))
            if sub_device.get("co2") is not None:
                sensors.append(CO2Sensor(sensor_coordinator, params))
            if sub_device.get("pm10") is not None:
                sensors.append(PM10Sensor(sensor_coordinator, params))
    async_add_entities(sensors)
