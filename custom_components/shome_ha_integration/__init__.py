import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinators.aircon_coordinator import AirconCoordinator
from .coordinators.heater_coordinator import HeaterCoordinator
from .coordinators.light_coordinator import LightsCoordinator
from .coordinators.sensor_coordinator import SensorCoordinator
from .coordinators.ventilation_coordinator import VentilationCoordinator
from .shome_client.dto.device import SHomeDevice
from .shome_client.dto.home_info import SHomeInfo
from .shome_client.shome_client import SHomeClient
from .shome_client.utils.device_type import get_device_type
from .utils import unload_client, get_or_create_client

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):

    credential: dict = entry.data.get("credential")
    client: SHomeClient = await get_or_create_client(hass, credential)

    # get devices
    home_info: SHomeInfo = await client.get_devices()
    device_by_type: dict[Platform, dict[str, list[SHomeDevice]]] = {}
    for device in home_info.devices:
        if (device_type := get_device_type(device)) is None:
            _LOGGER.warning("Device %s (model_type_id: %s) is not supported, skipping",
                            device.nick_name, device.model_type_id)
            continue
        _LOGGER.debug("device_type: %s", device_type)
        platform, shome_device_type = device_type
        _LOGGER.debug("Device %s (model_type_id: %s) classified as %s",
                     device.nick_name, device.model_type_id, (platform, shome_device_type))
        device_by_type.setdefault(platform, {}).setdefault(shome_device_type, []).append(device)

    # create light coordinator
    light_devices: list[SHomeDevice] = device_by_type.get(Platform.LIGHT, {}).get("light", [])
    _LOGGER.debug("Found %d light devices from total %d devices", len(light_devices), len(home_info.devices))
    light_coordinator: LightsCoordinator = LightsCoordinator(hass, credential, light_devices)
    await light_coordinator.async_config_entry_first_refresh()

    # create sensor coordinator
    sensor_devices: list[SHomeDevice] = device_by_type.get(Platform.SENSOR, {}).get("environment-sensor", [])
    _LOGGER.debug("Found %d sensor devices from total %d devices", len(sensor_devices), len(home_info.devices))
    sensor_coordinator: SensorCoordinator = SensorCoordinator(hass, credential, sensor_devices)
    await sensor_coordinator.async_config_entry_first_refresh()

    # create ventilation coordinator
    fan_devices: list[SHomeDevice] = device_by_type.get(Platform.FAN, {}).get("ventilator", [])
    _LOGGER.debug("Found %d fan devices from total %d devices", len(fan_devices), len(home_info.devices))
    ventilation_coordinator: VentilationCoordinator = VentilationCoordinator(hass, credential, fan_devices)
    await ventilation_coordinator.async_config_entry_first_refresh()

    # create aircon coordinator
    aircon_devices: list[SHomeDevice] = device_by_type.get(Platform.CLIMATE, {}).get("aircon", [])
    _LOGGER.debug("Found %d aircon devices from total %d devices", len(aircon_devices), len(home_info.devices))
    aircon_coordinator: AirconCoordinator = AirconCoordinator(hass, credential, aircon_devices)
    await aircon_coordinator.async_config_entry_first_refresh()

    # create heater coordinator
    heater_devices: list[SHomeDevice] = device_by_type.get(Platform.CLIMATE, {}).get("heater", [])
    _LOGGER.debug("Found %d heater devices from total %d devices", len(heater_devices), len(home_info.devices))
    heater_coordinator: HeaterCoordinator = HeaterCoordinator(hass, credential, heater_devices)
    await heater_coordinator.async_config_entry_first_refresh()


    # save coordinators for future use
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "lights_coordinator": light_coordinator,
        "sensor_coordinator": sensor_coordinator,
        "ventilation_coordinator": ventilation_coordinator,
        "aircon_coordinator": aircon_coordinator,
    }

    # launch devices
    await hass.config_entries.async_forward_entry_setups(entry, device_by_type.keys())
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""

    hass.data.setdefault(DOMAIN, {})
    if entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN][entry.entry_id] = None

    credential: dict = entry.data.get("credential")
    if not credential:
        _LOGGER.error("No credential found in entry data for unloading: %s", entry.entry_id)
        return False
    await unload_client(hass, credential)

    _LOGGER.info("Unloading SHome integration entry: %s", entry.entry_id)
    return True
