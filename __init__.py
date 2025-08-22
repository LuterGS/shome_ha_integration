import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinators.light_coordinator import LightsCoordinator
from .coordinators.sensor_coordinator import SensorCoordinator
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
    device_by_type: dict[Platform, list[SHomeDevice]] = {}
    for device in home_info.devices:
        device_type = get_device_type(device)
        _LOGGER.debug("Device %s (model_type_id: %s) classified as %s", 
                     device.nick_name, device.model_type_id, device_type)
        device_by_type.setdefault(device_type, []).append(device)

    # create light coordinator
    light_devices: list[SHomeDevice] = device_by_type.get(Platform.LIGHT, [])
    _LOGGER.debug("Found %d light devices from total %d devices", len(light_devices), len(home_info.devices))
    light_coordinator: LightsCoordinator = LightsCoordinator(hass, credential, light_devices)
    await light_coordinator.async_config_entry_first_refresh()

    # create sensor coordinator
    sensor_devices: list[SHomeDevice] = device_by_type.get(Platform.SENSOR, [])
    _LOGGER.debug("Found %d sensor devices from total %d devices", len(sensor_devices), len(home_info.devices))
    sensor_coordinator: SensorCoordinator = SensorCoordinator(hass, credential, sensor_devices)
    await sensor_coordinator.async_config_entry_first_refresh()

    # save coordinators for future use
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "lights_coordinator": light_coordinator,
        "sensor_coordinator": sensor_coordinator,
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
