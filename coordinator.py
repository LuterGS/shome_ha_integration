# coordinator.py
import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .shome_client.dto.light import LightStatus
from .utils import get_or_create_client

_LOGGER = logging.getLogger(__name__)

class LightsCoordinator(DataUpdateCoordinator[dict]):
    """data 예: {"light_1": {...}, "light_2": {...}, ...}"""

    def __init__(self, hass, username, password):
        super().__init__(
            hass,
            _LOGGER,
            name="your_api_lights",
            update_interval=timedelta(seconds=5),
        )
        self.hass = hass
        self.username = username
        self.password = password

    async def _async_update_data(self) -> dict:
        try:
            client = await get_or_create_client(self.hass, self.username, self.password)
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
            client = await get_or_create_client(self.hass, self.username, self.password)
            await client.toggle_single_light(light_id, state)
        except Exception as e:
            raise UpdateFailed(str(e)) from e
