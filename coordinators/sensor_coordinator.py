import logging
from enum import Enum

from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

# top-level imports
from ..shome_client.dto.light import LightStatus, SHomeLightInfo
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
            update_interval=None,
            request_refresh_debouncer=Debouncer(
                hass, _LOGGER, cooldown=1.0, immediate=False
            )
        )
        self._hass = hass
        self._credential = credential
        self._devices = devices
