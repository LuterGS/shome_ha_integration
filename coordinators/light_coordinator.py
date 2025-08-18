import logging

from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

# top-level imports
from ..shome_client.dto.light import LightStatus, LightInfo
from ..utils import get_or_create_client

_LOGGER = logging.getLogger(__name__)

class LightsCoordinator(DataUpdateCoordinator[dict]):

    def __init__(self, hass, credential: dict, light_info: LightInfo):
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
        # initial setting
        self.data = {str(light.id): {"on": light.on} for light in light_info.devices}

    async def _async_update_data(self) -> dict:
        try:
            client = await get_or_create_client(self._hass, self._credential)
            raw_result = await client.get_light_info()
            result = {}
            for light in raw_result.devices:
                result[str(light.id)] = {
                    "on": light.on
                }
            return result
        except Exception as e:
            raise UpdateFailed(str(e)) from e

    async def toggle_light(self, light_id: str, state: LightStatus):
        try:
            client = await get_or_create_client(self._hass, self._credential)
            await client.toggle_single_light(light_id, state)
        except Exception as e:
            raise UpdateFailed(str(e)) from e
