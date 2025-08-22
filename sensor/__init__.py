import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from ..const import DOMAIN
from ..coordinators.sensor_coordinator import SensorCoordinator
from .TemperatureSensor import TemperatureSensor
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
    for device_id, sub_devices in sensor_data.items():
        for sub_device_num, sub_device in sub_devices.items():
            sensors.append(TemperatureSensor(sensor_coordinator, {"device_info": sub_devices["device_info"], "sub_device_num": sub_device_num}))
            sensors.append(HumiditySensor(sensor_coordinator, {"device_info": sub_devices["device_info"], "sub_device_num": sub_device_num}))
            sensors.append(CO2Sensor(sensor_coordinator, {"device_info": sub_devices["device_info"], "sub_device_num": sub_device_num}))
            sensors.append(PM10Sensor(sensor_coordinator, {"device_info": sub_devices["device_info"], "sub_device_num": sub_device_num}))
    async_add_entities(sensors)
